"""Handlers de sistema (nao-IA) do motor RDAA V4.

Conecta as fases deterministicas do grafo -- QA, publicacao, registro no
vault -- aos servicos em ``services/``.  Handlers seguem a assinatura
``SystemHandler`` de ``orquestracao.engine``: recebem o ``RDAAState``
completo e devolvem um dict de saida (ou levantam excecao, tratada pelo
mesmo disjuntor que workers de IA).

Contrato de dados entre fases (via ``state["outputs"]``):
- Quem produz o candidato (writer em C; validator em B/A) deve gravar em
  ``outputs[<role>]["docx_path"]`` o caminho do DOCX candidato gerado por
  ``skills/formatar-peca/scripts/construir_peca.py``.
- O handler de ``qa_passed`` le esse caminho e roda o gate QA real.
- O handler de ``published`` le o mesmo caminho e publica via o pipeline
  real (``publicar_docx.py``), determinando o destino final a partir de
  ``state["outputs"]["publish_target"]`` quando fornecido, ou de uma
  convencao <state_dir>/../<matter_id>.docx caso contrario.
- O handler de ``vault_registered`` registra no Cerebro-Ricar (que por
  sua vez sincroniza o OpenViking internamente).

Nenhum handler decide a proxima fase -- apenas produz saida ou levanta
excecao.  A transicao continua sendo responsabilidade exclusiva do grafo.
"""

from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any

from orquestracao.contracts import ContractError, RDAAState
from services.memoria import registrar_cerebro
from services.publicacao import publicar_docx
from services.qa import run_qa_gate


def _find_candidate_artifacts(state: RDAAState) -> tuple[Path, Path]:
    """Localiza o DOCX e o JSON de contexto produzidos pelo mesmo worker.

    Procura em outputs de qualquer role pelas chaves 'docx_path' e 'context_path',
    na ordem validator -> writer (apenas quem produz a versão final).
    Ambos os arquivos devem existir fisicamente no disco.
    """
    outputs = state.get("outputs", {})
    for role in ("validator", "writer"):
        candidate = outputs.get(role, {})
        if isinstance(candidate, dict) and candidate.get("docx_path") and candidate.get("context_path"):
            docx_path = Path(candidate["docx_path"])
            context_path = Path(candidate["context_path"])

            if not docx_path.is_file():
                raise ContractError(f"docx candidato declarado mas ausente em disco: {docx_path}")
            if not context_path.is_file():
                raise ContractError(f"contexto declarado mas ausente em disco: {context_path}")

            return docx_path, context_path

    raise ContractError(
        "docx_path e/ou context_path ausente em outputs. O worker (validator ou writer) "
        "deve gravar ambos os caminhos no mesmo pacote de saída."
    )


def handle_qa_passed(state: RDAAState) -> dict[str, Any]:
    """Executa o gate de QA real sobre o DOCX candidato."""
    docx_path, context_path = _find_candidate_artifacts(state)

    result = run_qa_gate(docx_path, context_path)
    if result.get("status") != "PASS":
        raise ContractError(f"QA reprovado: {result.get('errors')}")

    return {"docx_path": str(docx_path), "qa_result": result}


def handle_published(state: RDAAState) -> dict[str, Any]:
    """Publica o DOCX candidato via o pipeline real e protegido."""
    docx_path, context_path = _find_candidate_artifacts(state)
    state_dir = Path(str(state.get("state_dir", "")))
    if not state_dir:
        raise ContractError("state_dir ausente no estado do motor")

    outputs = state.get("outputs", {})
    publish_target = outputs.get("publish_target")
    if publish_target:
        output_path = Path(publish_target)
    else:
        matter_id = state.get("matter_id", "peca")
        output_path = state_dir.parent / f"{matter_id}.docx"

    result = publicar_docx(
        docx_path,
        output_path,
        state_dir=state_dir,
        context_path=context_path,
        skip_cerebro=True,  # o registro no Cerebro e um nó de sistema separado
    )
    if result.get("status") != "PUBLISHED":
        raise ContractError(f"publicação sem confirmação PUBLISHED: {result}")
    if not output_path.is_file():
        raise ContractError(f"publicação não criou o arquivo final: {output_path}")
    shutil.copyfile(context_path, state_dir / "contexto_peca.json")
    return result


def handle_vault_registered(state: RDAAState) -> dict[str, Any]:
    """Registra a materia publicada no Cerebro-Ricar (+ OpenViking)."""
    state_dir = Path(str(state.get("state_dir", "")))
    if not state_dir:
        raise ContractError("state_dir ausente no estado do motor")

    matter_id = state.get("matter_id", "")
    nivel_peca = state.get("nivel_peca", "C")
    if not matter_id:
        raise ContractError("matter_id ausente no estado do motor")

    result = registrar_cerebro(state_dir, matter_id, nivel_peca)
    if result.get("success") is not True:
        raise ContractError(f"registro no Cérebro-Ricar falhou: {result}")
    return result


DEFAULT_SYSTEM_HANDLERS: dict[str, Any] = {
    "qa_passed": handle_qa_passed,
    "published": handle_published,
    "vault_registered": handle_vault_registered,
}
"""Mapeamento fase -> handler pronto para uso em producao.

Uso:
    from orquestracao.system_handlers import DEFAULT_SYSTEM_HANDLERS
    engine = RDAAEngine(state_dir, level, worker=meu_worker_ia,
                         system_handlers=DEFAULT_SYSTEM_HANDLERS)
"""
