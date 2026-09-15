"""Testes unitários para orquestracao/contracts.py."""

import json
from pathlib import Path

import pytest

from orquestracao.contracts import (
    ContractError,
    HUMAN_GATES,
    Packet,
    Receipt,
    ROLE_OUTPUT_PHASE,
    VALID_ROLES,
    load_route,
    sha256_file,
    sha256_text,
    validate_level,
    validate_phase_for_role,
)


# ---------------------------------------------------------------------------
# validate_level
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [("a", "A"), ("B", "B"), (" c ", "C")])
def test_validate_level_aceita_validos(raw, expected):
    assert validate_level(raw) == expected


@pytest.mark.parametrize("bad", ["D", "X", "", "AB"])
def test_validate_level_recusa_invalidos(bad):
    with pytest.raises(ContractError, match="nivel_peca"):
        validate_level(bad)


# ---------------------------------------------------------------------------
# load_route
# ---------------------------------------------------------------------------

ROUTE_PATH = Path(__file__).resolve().parents[1] / "orquestracao" / "roteamento.json"


@pytest.mark.parametrize("level", ["A", "B", "C"])
def test_load_route_carrega_niveis_validos(level):
    route = load_route(level, ROUTE_PATH)
    assert "stages" in route
    assert "workers" in route or level == "C"


def test_load_route_nivel_invalido():
    with pytest.raises(ContractError):
        load_route("X", ROUTE_PATH)


# ---------------------------------------------------------------------------
# Packet
# ---------------------------------------------------------------------------

def _packet(**overrides) -> Packet:
    defaults = dict(
        role="writer",
        combo="RJ-Escrita-Pesada",
        system_prompt="regras da etapa",
        user_prompt="pacote da matéria",
        matter_id="test-001",
        phase="drafting",
    )
    defaults.update(overrides)
    return Packet(**defaults)


def test_packet_valido():
    p = _packet()
    assert p.role == "writer"
    assert p.sha256()
    payload = p.to_omniroute_payload()
    assert payload["model"] == "RJ-Escrita-Pesada"
    assert len(payload["input"]) == 2


def test_packet_papel_invalido():
    with pytest.raises(ContractError, match="papel inválido"):
        _packet(role="hacker")


def test_packet_combo_vazio():
    with pytest.raises(ContractError, match="combo"):
        _packet(combo="")


def test_packet_prompt_vazio():
    with pytest.raises(ContractError, match="system_prompt"):
        _packet(system_prompt="")
    with pytest.raises(ContractError, match="user_prompt"):
        _packet(user_prompt="   ")


def test_packet_sha256_deterministic():
    p1 = _packet()
    p2 = _packet()
    assert p1.sha256() == p2.sha256()


def test_packet_sha256_muda_com_conteudo():
    p1 = _packet(user_prompt="versão 1")
    p2 = _packet(user_prompt="versão 2")
    assert p1.sha256() != p2.sha256()


# ---------------------------------------------------------------------------
# Receipt
# ---------------------------------------------------------------------------

def test_receipt_criacao():
    r = Receipt(role="writer", requested_combo="RJ-Escrita-Pesada")
    assert r.started_at
    assert r.outcome == "ok"
    assert r.duration_ms == 0


def test_receipt_finalize(tmp_path):
    out = tmp_path / "output.md"
    out.write_text("conteúdo", encoding="utf-8")
    r = Receipt(role="writer")
    r.finalize(output_path=out, http_status=200, outcome="ok")
    assert r.finished_at
    assert r.output_sha256
    assert r.duration_ms >= 0


def test_receipt_to_dict():
    r = Receipt(role="critic", requested_combo="RJ-Leitura")
    d = r.to_dict()
    assert d["role"] == "critic"
    assert d["requested_combo"] == "RJ-Leitura"
    assert isinstance(d, dict)


# ---------------------------------------------------------------------------
# Hash utils
# ---------------------------------------------------------------------------

def test_sha256_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("conteúdo de teste", encoding="utf-8")
    h = sha256_file(f)
    assert len(h) == 64
    assert h == sha256_file(f)  # determinístico


def test_sha256_text():
    h = sha256_text("teste")
    assert len(h) == 64
    assert h == sha256_text("teste")
    assert h != sha256_text("outro")


# ---------------------------------------------------------------------------
# validate_phase_for_role
# ---------------------------------------------------------------------------

def test_validate_phase_for_role_aceita():
    route = load_route("A", ROUTE_PATH)
    # planner é autorizado em intake_ready
    validate_phase_for_role("planner", "intake_ready", route)


def test_validate_phase_for_role_recusa():
    route = load_route("A", ROUTE_PATH)
    with pytest.raises(ContractError, match="não autorizado"):
        validate_phase_for_role("writer", "intake_ready", route)


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

def test_role_output_phase_inclui_papeis_principais():
    assert "planner" in ROLE_OUTPUT_PHASE
    assert "writer" in ROLE_OUTPUT_PHASE
    assert "critic" in ROLE_OUTPUT_PHASE
    assert "validator" in ROLE_OUTPUT_PHASE


def test_human_gates_mapeados():
    assert "awaiting_skeleton_approval" in HUMAN_GATES
    assert "release_ready" in HUMAN_GATES


def test_valid_roles_completo():
    for role in ("planner", "writer", "critic", "validator", "research", "reader"):
        assert role in VALID_ROLES
