"""Regressões do contrato operacional C/B/A do RDAA."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "revisor-rdaa" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from classificacao_peca import validate_piece_contract  # noqa: E402
from contexto_rdaa import build_context_pack  # noqa: E402
from estado_rdaa import initialize_state, persist_context  # noqa: E402


def test_a_is_premium_and_allows_blocks() -> None:
    report = validate_piece_contract(
        {
            "nivel_peca": "A",
            "exigir_esqueleto": True,
            "modo_redacao": "blocos",
            "redacao_por_blocos": True,
            "nivel_risco": "alto",
        }
    )
    assert report["status"] == "PASS"
    assert report["nivel_peca"] == "A"
    assert report["redacao_por_blocos"] is True


def test_b_is_process_based_and_allows_selected_model() -> None:
    report = validate_piece_contract(
        {
            "nivel_peca": "B",
            "exigir_esqueleto": True,
            "modo_redacao": "blocos",
            "modelo_estrutura": {
                "modelo_id": "manifestacao-complexa-v1",
                "versao": 1,
                "niveis_recomendados": ["B"],
            },
        }
    )
    assert report["status"] == "PASS"
    assert report["nivel_peca"] == "B"


def test_c_defaults_to_direct_short_paragraphs() -> None:
    report = validate_piece_contract({"nivel_peca": "C"})
    assert report["status"] == "PASS"
    assert report["modo_redacao"] == "direta"
    assert report["redacao_por_blocos"] is False


def test_c_cannot_use_block_writing() -> None:
    report = validate_piece_contract(
        {"nivel_peca": "C", "modo_redacao": "blocos", "redacao_por_blocos": True}
    )
    assert report["status"] == "BLOCK"
    assert any(item["id"] == "tipo_c_sem_blocos" for item in report["findings"])


def test_vault_automatico_is_blocked_for_every_level() -> None:
    report = validate_piece_contract({"nivel_peca": "B", "vault_automatico": True})
    assert report["status"] == "BLOCK"
    assert any(item["id"] == "vault_automatico_proibido" for item in report["findings"])


def test_piece_level_is_not_risk_level() -> None:
    report = validate_piece_contract({"nivel_peca": "B", "nivel_risco": "alto", "exigir_esqueleto": True})
    assert report["status"] == "PASS"
    assert report["nivel_peca"] == "B"


def test_legacy_context_remains_accepted_without_piece_level() -> None:
    report = validate_piece_contract({"nivel_risco": "medio"})
    assert report["status"] == "SKIPPED"
    assert report["compatibilidade_legada"] is True


def test_piece_metadata_is_persisted_and_projected() -> None:
    with tempfile.TemporaryDirectory() as temp:
        state_dir = Path(temp) / "caso-tipo-b"
        context = {
            "matter_id": "caso-tipo-b",
            "nivel_peca": "B",
            "nivel_risco": "medio",
            "modo_redacao": "blocos",
            "redacao_por_blocos": True,
            "modelo_estrutura": {
                "modelo_id": "manifestacao-complexa-v1",
                "versao": 1,
                "niveis_recomendados": ["B"],
            },
        }
        persist_context(state_dir, context)
        state = json.loads((state_dir / "matter_state.json").read_text(encoding="utf-8"))
        assert state["nivel_peca"] == "B"
        assert state["declared_risk_level"] == "medio"
        assert state["modo_redacao"] == "blocos"
        pack = build_context_pack(state_dir, "redator")
        assert pack["nivel_peca"] == "B"
        assert pack["redacao_por_blocos"] is True
        assert pack["modelo_estrutura"]["modelo_id"] == "manifestacao-complexa-v1"


def test_model_must_declare_id_and_version() -> None:
    report = validate_piece_contract({"nivel_peca": "B", "modelo_estrutura": {}})
    assert report["status"] == "BLOCK"
    ids = {item["id"] for item in report["findings"]}
    assert {"modelo_id_ausente", "modelo_versao_ausente"}.issubset(ids)


if __name__ == "__main__":
    test_a_is_premium_and_allows_blocks()
    test_b_is_process_based_and_allows_selected_model()
    test_c_defaults_to_direct_short_paragraphs()
    test_c_cannot_use_block_writing()
    test_vault_automatico_is_blocked_for_every_level()
    test_piece_level_is_not_risk_level()
    test_legacy_context_remains_accepted_without_piece_level()
    test_piece_metadata_is_persisted_and_projected()
    test_model_must_declare_id_and_version()
    print("[OK] contrato C/B/A, blocos, modelo e ausência de vault automático passaram")
