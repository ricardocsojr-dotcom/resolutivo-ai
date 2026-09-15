"""Montagem de pacotes mínimos por papel.

Cada função devolve um ``Packet`` com system prompt e user prompt
prontos para envio ao OmniRoute.  O motor nunca injeta histórico bruto;
cada etapa recebe somente o contexto necessário.

Regra V4 §6:
- Planner: fatos, fontes autorizadas, pendências, teses candidatas e regras
- Writer:  esqueleto aprovado + hash, fatos/fontes, decisões, núcleo RDAA
- Critic:  rascunho, fatos/fontes, teses, pedidos, contrato adversarial
- Validator: rascunho, esqueleto, fontes, crítica aplicável, checklist RDAA
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from orquestracao.contracts import ContractError, Packet, RDAAState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_artifact(state: RDAAState, key: str) -> str:
    """Lê o conteúdo de um artefato a partir dos outputs do estado."""
    outputs = state.get("outputs", {})
    artifact = outputs.get(key)
    if isinstance(artifact, dict):
        # Se o output é um dict com chave 'content'
        return str(artifact.get("content", artifact.get("text", json.dumps(artifact, ensure_ascii=False))))
    if isinstance(artifact, str):
        return artifact
    return ""


def _read_file_if_exists(path: Path | str | None) -> str:
    """Lê um arquivo se ele existir, ou devolve string vazia."""
    if not path:
        return ""
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _state_dir_path(state: RDAAState) -> Path | None:
    """Resolve o diretório de estado, se informado."""
    sd = state.get("state_dir")
    return Path(sd) if sd else None


# ---------------------------------------------------------------------------
# Resolução de Combo por papel e rota
# ---------------------------------------------------------------------------

def resolve_combo(role: str, route: dict[str, Any]) -> str:
    """Resolve o nome do Combo para um papel a partir da rota."""
    workers = route.get("workers", {})
    worker = workers.get(role)
    if not isinstance(worker, dict):
        raise ContractError(f"papel {role} não configurado na rota")
    model = worker.get("model", "")
    if not model:
        raise ContractError(f"modelo/combo não definido para o papel {role}")
    return str(model)


def resolve_engine(role: str, route: dict[str, Any]) -> str:
    """Resolve o engine do worker para um papel."""
    workers = route.get("workers", {})
    worker = workers.get(role)
    if not isinstance(worker, dict):
        raise ContractError(f"papel {role} não configurado na rota")
    return str(worker.get("engine", "chat"))


# ---------------------------------------------------------------------------
# Pacotes por papel
# ---------------------------------------------------------------------------

def build_planner_packet(
    state: RDAAState,
    *,
    facts: str = "",
    sources: str = "",
    pending: str = "",
    theses: str = "",
    rules: str = "",
    vault_context: str = "",
) -> Packet:
    """Monta o pacote do planner (§6: fatos, fontes, pendências, teses, regras)."""
    route = state.get("route", {})
    combo = resolve_combo("planner", route)

    system = (
        "Você é o planejador do escritório RDAA.  Seu papel é organizar o "
        "contexto jurídico e produzir um esqueleto da peça.  Não redija a "
        "peça — entregue apenas a estrutura.\n\n"
        "## Regras de planejamento\n" + (rules or "Aplicar padrão RDAA.")
    )

    user_parts = [
        "## Fatos relevantes",
        facts or "(nenhum fato fornecido)",
        "",
        "## Fontes autorizadas",
        sources or "(nenhuma fonte fornecida)",
        "",
        "## Pendências",
        pending or "(nenhuma pendência)",
        "",
        "## Teses candidatas",
        theses or "(nenhuma tese candidata)",
    ]
    if vault_context:
        user_parts += ["", "## Contexto do Cérebro-Ricar (read-only)", vault_context]

    return Packet(
        role="planner",
        combo=combo,
        system_prompt=system,
        user_prompt="\n".join(user_parts),
        matter_id=state.get("matter_id", ""),
        phase=state.get("phase", ""),
        output_contract="skeleton_v1",
        timeout_seconds=_timeout(route, "planner"),
        effort=_effort(route, "planner"),
    )


def build_writer_packet(
    state: RDAAState,
    *,
    skeleton: str = "",
    skeleton_hash: str = "",
    facts: str = "",
    sources: str = "",
    decisions: str = "",
    style_guide: str = "",
) -> Packet:
    """Monta o pacote do writer (§6: esqueleto+hash, fatos, fontes, decisões, núcleo)."""
    route = state.get("route", {})

    # Writer pode ser writer, writer_heavy ou writer_light
    writer_role = "writer"
    for candidate in ("writer_heavy", "writer", "writer_light"):
        if candidate in route.get("workers", {}):
            writer_role = candidate
            break

    combo = resolve_combo(writer_role, route)

    system = (
        "Você é o redator do escritório RDAA.  Redija a peça processual "
        "seguindo rigorosamente o esqueleto aprovado e o núcleo de escrita.\n\n"
        "## Estilo RDAA\n" + (style_guide or "Linguagem direta, ordem direta, sem firulas.")
    )

    user_parts = [
        "## Esqueleto aprovado",
        skeleton or _read_artifact(state, "planner"),
        "",
        f"SHA-256 do esqueleto: {skeleton_hash}" if skeleton_hash else "",
        "",
        "## Fatos e fontes",
        facts or "(usar fatos do esqueleto)",
        "",
        "## Fontes selecionadas",
        sources or "(fontes do planejamento)",
        "",
        "## Decisões do Ricardo",
        decisions or "(nenhuma decisão adicional)",
    ]

    return Packet(
        role="writer",
        combo=combo,
        system_prompt=system,
        user_prompt="\n".join(user_parts),
        matter_id=state.get("matter_id", ""),
        phase=state.get("phase", ""),
        output_contract="draft_v1",
        timeout_seconds=_timeout(route, writer_role),
        effort=_effort(route, writer_role),
    )


def build_critic_packet(
    state: RDAAState,
    *,
    draft: str = "",
    facts: str = "",
    sources: str = "",
    theses: str = "",
    claims: str = "",
    adversarial_contract: str = "",
) -> Packet:
    """Monta o pacote do critic (§6: rascunho, fatos, fontes, teses, pedidos, contrato adversarial)."""
    route = state.get("route", {})
    combo = resolve_combo("critic", route)

    system = (
        "Você é o crítico adversarial do escritório RDAA.  Identifique "
        "vulnerabilidades no rascunho sem corrigi-lo.  Entregue apenas "
        "diagnóstico estruturado.\n\n"
        "## Contrato adversarial\n" + (adversarial_contract or "Apontar falhas, não redigir correções.")
    )

    user_parts = [
        "## Rascunho a criticar",
        draft or _read_artifact(state, "writer"),
        "",
        "## Fatos e fontes necessários",
        facts or "(usar fatos do planejamento)",
        "",
        "## Teses sustentadas",
        theses or "(extrair do rascunho)",
        "",
        "## Pedidos da peça",
        claims or "(extrair do rascunho)",
    ]

    return Packet(
        role="critic",
        combo=combo,
        system_prompt=system,
        user_prompt="\n".join(user_parts),
        matter_id=state.get("matter_id", ""),
        phase=state.get("phase", ""),
        output_contract="critique_v1",
        timeout_seconds=_timeout(route, "critic"),
        effort=_effort(route, "critic"),
    )


def build_validator_packet(
    state: RDAAState,
    *,
    draft: str = "",
    skeleton: str = "",
    sources: str = "",
    critique: str = "",
    checklist: str = "",
) -> Packet:
    """Monta o pacote do validator (§6: rascunho, esqueleto, fontes, crítica, checklist)."""
    route = state.get("route", {})
    combo = resolve_combo("validator", route)

    system = (
        "Você é o validador final do escritório RDAA.  Aplique a checklist "
        "de qualidade e corrija problemas objetivos.  Não altere tese, "
        "pedido ou estratégia.\n\n"
        "## Checklist RDAA\n" + (checklist or "Verificar formatação, referências e consistência.")
    )

    user_parts = [
        "## Rascunho a validar",
        draft or _read_artifact(state, "writer"),
        "",
        "## Esqueleto aprovado",
        skeleton or _read_artifact(state, "planner"),
        "",
        "## Fontes",
        sources or "(fontes do planejamento)",
        "",
        "## Crítica aplicável",
        critique or _read_artifact(state, "critic") or "(sem crítica – rota B/C)",
    ]

    return Packet(
        role="validator",
        combo=combo,
        system_prompt=system,
        user_prompt="\n".join(user_parts),
        matter_id=state.get("matter_id", ""),
        phase=state.get("phase", ""),
        output_contract="candidate_v1",
        timeout_seconds=_timeout(route, "validator"),
        effort=_effort(route, "validator"),
    )


# ---------------------------------------------------------------------------
# Timeout por papel
# ---------------------------------------------------------------------------

def _timeout(route: dict[str, Any], role: str, default: int = 600) -> int:
    """Resolve timeout do worker, com fallback para default."""
    workers = route.get("workers", {})
    worker = workers.get(role, {})
    return int(worker.get("timeout_seconds", default))


def _effort(route: dict[str, Any], role: str, default: str = "medium") -> str:
    """Resolve esforço de raciocínio do worker, com fallback para default."""
    workers = route.get("workers", {})
    worker = workers.get(role, {})
    return str(worker.get("effort", default))
