"""Testes unitários para orquestracao/prompts.py."""

import json
from pathlib import Path

import pytest

from orquestracao.contracts import ContractError, Packet, RDAAState, load_route
from orquestracao.prompts import (
    build_critic_packet,
    build_planner_packet,
    build_validator_packet,
    build_writer_packet,
    resolve_combo,
    resolve_engine,
)


ROUTE_PATH = Path(__file__).resolve().parents[1] / "orquestracao" / "roteamento.json"


def _state(level: str = "A", phase: str = "intake_ready", **extra) -> RDAAState:
    route = load_route(level, ROUTE_PATH)
    base: RDAAState = {
        "matter_id": "test-001",
        "nivel_peca": level,
        "phase": phase,
        "route": route,
        "outputs": {},
    }
    base.update(extra)
    return base


# ---------------------------------------------------------------------------
# resolve_combo / resolve_engine
# ---------------------------------------------------------------------------

def test_resolve_combo_writer_a():
    route = load_route("A", ROUTE_PATH)
    combo = resolve_combo("writer", route)
    assert combo  # não vazio
    assert isinstance(combo, str)


def test_resolve_combo_planner_b():
    route = load_route("B", ROUTE_PATH)
    combo = resolve_combo("planner", route)
    assert combo == "RJ-Planejamento"


def test_resolve_combo_writer_b_usa_escrita_pesada():
    route = load_route("B", ROUTE_PATH)
    assert resolve_combo("writer", route) == "RJ-Escrita-Pesada"


def test_resolve_combo_papel_inexistente():
    route = load_route("C", ROUTE_PATH)
    with pytest.raises(ContractError, match="não configurado"):
        resolve_combo("critic", route)  # C não tem critic


def test_resolve_engine_a():
    route = load_route("A", ROUTE_PATH)
    assert resolve_engine("planner", route) == "omniroute"
    assert resolve_engine("writer", route) == "omniroute"
    assert resolve_engine("critic", route) == "omniroute"
    assert resolve_engine("validator", route) == "omniroute"


def test_combos_em_reserva_nao_sao_rotas():
    payload = json.loads(ROUTE_PATH.read_text(encoding="utf-8"))
    standby = set(payload["standby_combos"])
    routed = {
        worker["model"]
        for level in payload["levels"].values()
        for worker in level["workers"].values()
    } | {task["model"] for task in payload["standalone_tasks"].values()}
    assert standby == {"static-best-free", "static-best-coding"}
    assert standby.isdisjoint(routed)


# ---------------------------------------------------------------------------
# build_planner_packet
# ---------------------------------------------------------------------------

def test_planner_packet_valido():
    state = _state("A")
    pkt = build_planner_packet(state, facts="Fatos do caso.", sources="Jusbrasil.")
    assert isinstance(pkt, Packet)
    assert pkt.role == "planner"
    assert "Fatos do caso" in pkt.user_prompt
    assert "Jusbrasil" in pkt.user_prompt
    assert pkt.output_contract == "skeleton_v1"


def test_planner_packet_com_vault():
    state = _state("A")
    pkt = build_planner_packet(state, vault_context="Cérebro-Ricar read-only.")
    assert "Cérebro-Ricar read-only" in pkt.user_prompt


# ---------------------------------------------------------------------------
# build_writer_packet
# ---------------------------------------------------------------------------

def test_writer_packet_valido():
    state = _state("A", phase="drafting")
    pkt = build_writer_packet(
        state,
        skeleton="## Estrutura da peça\n1. Fatos\n2. Direito",
        skeleton_hash="abc123",
        style_guide="Tom direto e assertivo.",
    )
    assert isinstance(pkt, Packet)
    assert pkt.role == "writer"
    assert "Estrutura da peça" in pkt.user_prompt
    assert "abc123" in pkt.user_prompt
    assert pkt.output_contract == "draft_v1"


def test_writer_packet_usa_output_planner():
    state = _state("A", phase="drafting",
                   outputs={"planner": {"content": "Esqueleto do planner."}})
    pkt = build_writer_packet(state)
    assert "Esqueleto do planner" in pkt.user_prompt


# ---------------------------------------------------------------------------
# build_critic_packet
# ---------------------------------------------------------------------------

def test_critic_packet_valido():
    state = _state("A", phase="criticizing")
    pkt = build_critic_packet(
        state,
        draft="Rascunho da peça.",
        theses="Dano moral por negativação.",
        adversarial_contract="Verificar completude.",
    )
    assert isinstance(pkt, Packet)
    assert pkt.role == "critic"
    assert "Rascunho da peça" in pkt.user_prompt
    assert "adversarial" in pkt.system_prompt.lower() or "Verificar completude" in pkt.system_prompt
    assert pkt.output_contract == "critique_v1"


# ---------------------------------------------------------------------------
# build_validator_packet
# ---------------------------------------------------------------------------

def test_validator_packet_valido():
    state = _state("A", phase="validating")
    pkt = build_validator_packet(
        state,
        draft="Rascunho final.",
        skeleton="Esqueleto.",
        critique="Falha na referência §3.",
        checklist="Verificar citações.",
    )
    assert isinstance(pkt, Packet)
    assert pkt.role == "validator"
    assert "Rascunho final" in pkt.user_prompt
    assert "Falha na referência" in pkt.user_prompt
    assert "Verificar citações" in pkt.system_prompt
    assert pkt.output_contract == "candidate_v1"


def test_validator_packet_sem_critica_rota_b():
    state = _state("B", phase="validating")
    pkt = build_validator_packet(state, draft="Rascunho.")
    assert "sem crítica" in pkt.user_prompt.lower() or "rota B/C" in pkt.user_prompt


# ---------------------------------------------------------------------------
# Pacotes são Packets válidos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("level", ["A", "B"])
def test_todos_os_pacotes_sao_validos(level):
    """Garante que build_*_packet gera Packets válidos para cada nível."""
    state = _state(level)

    planner = build_planner_packet(state, facts="Fatos.")
    assert planner.sha256()

    state_w = _state(level, phase="drafting",
                     outputs={"planner": "Esqueleto."})
    writer = build_writer_packet(state_w)
    assert writer.sha256()

    if level == "A":
        state_c = _state(level, phase="criticizing",
                         outputs={"writer": "Rascunho."})
        critic = build_critic_packet(state_c)
        assert critic.sha256()

    state_v = _state(level, phase="validating",
                     outputs={"writer": "Rascunho.", "critic": "Crítica."})
    validator = build_validator_packet(state_v)
    assert validator.sha256()
