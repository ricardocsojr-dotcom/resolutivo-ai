"""Worker de produção do motor RDAA V4.

Conecta papéis lógicos (planner, writer, critic, validator) à fonte real
de conteúdo de cada um, conforme o `engine` declarado em
``orquestracao/roteamento.json`` para o papel:

- ``engine != "chat"`` (claude, codex, antigravity, ...): o motor envia o
  pacote mínimo ao Combo via HTTP OmniRoute (``orquestracao/omniroute.py``)
  e usa a resposta como conteúdo do papel.
- ``engine == "chat"``: o próprio Codex/chat que conduz a sessão é quem
  produz o conteúdo -- a V4 (§1) proíbe chamar ``codex exec``, ``claude``,
  ``agy`` ou Hermes como CLIs a partir do motor.  Nesse caso o worker lê
  um artefato que o Codex grava manualmente em
  ``<state_dir>/packages/<role>-input.{md,json,txt}`` ANTES de iniciar ou
  retomar a fase.  Se o artefato não existir, o worker levanta
  ``ContractError`` com o caminho exato esperado -- nunca inventa
  conteúdo nem deixa a fase avançar sem ele.

Contrato de saída (consumido por ``orquestracao/system_handlers.py``):
O papel que produz o candidato final da peça (o último papel na rota
antes de ``qa_passed`` -- ``writer`` no nível C; ``validator`` nos
níveis B/A) tem seu conteúdo compilado para DOCX via o pipeline nativo
real:
  ``skills/formatar-peca/scripts/md2rdaa.py``      (Markdown -> contexto JSON)
  ``skills/formatar-peca/scripts/construir_peca.py`` (contexto JSON -> DOCX)
e grava ``outputs[<role>]["docx_path"]`` / ``["context_path"]``.  Sem
esse contrato os handlers de QA e publicação não encontram o documento
(ver ``_find_candidate_docx`` em ``system_handlers.py``).
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from orquestracao.contracts import ContractError, RDAAState, ROLE_OUTPUT_PHASE
from orquestracao.omniroute import OmniRouteClient
from orquestracao.prompts import (
    build_critic_packet,
    build_planner_packet,
    build_validator_packet,
    build_writer_packet,
    resolve_engine,
)

ROOT = Path(__file__).resolve().parents[1]
MD2RDAA_SCRIPT = ROOT / "skills" / "formatar-peca" / "scripts" / "md2rdaa.py"
CONSTRUIR_SCRIPT = ROOT / "skills" / "formatar-peca" / "scripts" / "construir_peca.py"

_PACKET_BUILDERS: dict[str, Any] = {
    "planner": build_planner_packet,
    "writer": build_writer_packet,
    "critic": build_critic_packet,
    "validator": build_validator_packet,
}


def _load_module(path: Path, name: str):
    """Carrega um script standalone como módulo, sem executar seu __main__."""
    if not path.is_file():
        raise FileNotFoundError(f"script não encontrado: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise ImportError(f"falha ao carregar {name}: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _is_doc_producer_role(role: str, route: dict[str, Any]) -> bool:
    """Determina se ``role`` é o papel que produz o candidato final (DOCX).

    É o papel cujo ``ROLE_OUTPUT_PHASE`` ocorre por último, entre os
    papéis configurados na rota, na ordem das ``stages`` -- ou seja, o
    último a tocar o texto antes do fluxo seguir para ``qa_passed``.
    Genérico por nível: writer no C (único papel), validator no B/A
    (revisão final), sem hardcode de nome de papel.
    """
    stages = route.get("stages", [])
    workers = route.get("workers", {})
    role_phases = [
        (stages.index(phase), r)
        for r, phase in ROLE_OUTPUT_PHASE.items()
        if r in workers and phase in stages
    ]
    if not role_phases:
        return False
    role_phases.sort()
    return role_phases[-1][1] == role


def _manual_artifact_path(state_dir: Path, role: str) -> Path | None:
    """Localiza o artefato que o Codex grava manualmente para um papel de chat."""
    packages = state_dir / "packages"
    for suffix in (".md", ".json", ".txt"):
        candidate = packages / f"{role}-input{suffix}"
        if candidate.is_file():
            return candidate
    return None


def _compile_docx(state: RDAAState, role: str, markdown_text: str) -> dict[str, str]:
    """Compila markdown -> contexto JSON -> DOCX pelo pipeline nativo protegido."""
    state_dir = Path(str(state.get("state_dir", "")))
    if not state_dir:
        raise ContractError("state_dir ausente no estado do motor")
    matter_id = state.get("matter_id", "peca")

    candidate_dir = state_dir / "candidate"
    candidate_dir.mkdir(parents=True, exist_ok=True)

    context_path = candidate_dir / f"{role}-context.json"
    docx_path = candidate_dir / f"{matter_id}.docx"

    md2rdaa = _load_module(MD2RDAA_SCRIPT, "md2rdaa_production")
    contexto = md2rdaa.compilar_markdown_para_contexto(
        markdown_text,
        matter_id=matter_id,
        nivel_peca=state.get("nivel_peca", "C"),
    )
    context_path.write_text(
        json.dumps(contexto, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    construir = _load_module(CONSTRUIR_SCRIPT, "construir_peca_production")
    construir.construir_peca(contexto, str(docx_path))

    return {"docx_path": str(docx_path), "context_path": str(context_path)}


def production_worker(role: str, state: RDAAState) -> dict[str, Any]:
    """Worker de produção real, para injeção em ``RDAAEngine(worker=...)``.

    HTTP OmniRoute para papéis com Combo externo; artefato manual do
    Codex para papéis com ``engine: "chat"``.  Compila o candidato DOCX
    quando ``role`` é o papel que produz o texto final da peça.
    """
    route = state.get("route", {})
    state_dir = Path(str(state.get("state_dir", "")))
    engine = resolve_engine(role, route)

    if engine == "chat":
        artifact = _manual_artifact_path(state_dir, role)
        if artifact is None:
            expected = state_dir / "packages" / f"{role}-input.md"
            raise ContractError(
                f"papel {role!r} usa engine=chat -- o conteúdo é produzido "
                f"pelo próprio Codex nesta sessão, não por CLI externa. "
                f"Grave o resultado em {expected} antes de iniciar ou "
                f"retomar esta fase."
            )
        content = artifact.read_text(encoding="utf-8")
    else:
        builder = _PACKET_BUILDERS.get(role)
        if builder is None:
            raise ContractError(f"papel {role!r} sem builder de pacote conhecido")
        packet = builder(state)
        client = OmniRouteClient()
        output_dir = state_dir / "packages" if state_dir else None
        content, _receipt = client.send(packet, output_dir=output_dir)

    result: dict[str, Any] = {"content": content}
    if _is_doc_producer_role(role, route):
        result.update(_compile_docx(state, role, content))
    return result
