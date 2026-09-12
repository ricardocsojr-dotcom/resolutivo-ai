from pathlib import Path
import json
import pytest
import shutil

import sys
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "revisor-rdaa" / "scripts"))

try:
    from manutencao_rdaa import reconcile_state
except ImportError:
    pytest.skip("Dependencia nao encontrada", allow_module_level=True)


def test_reconciliacao_dry_run_nao_altera_aninhado(tmp_path):
    root = tmp_path / "projetos"
    
    # Valido
    valido = root / "valido" / ".rdaa-run" / "v1"
    valido.mkdir(parents=True)
    (valido / "matter_state.json").write_text('{"matter_id": "v1"}')
    
    # Aninhado
    aninhado = root / "invalido" / ".rdaa-run" / "inv" / ".rdaa-run" / "inv"
    aninhado.mkdir(parents=True)
    (aninhado / "matter_state.json").write_text('{"matter_id": "inv"}')
    
    res = reconcile_state(root, apply=False, quarantine=tmp_path / "quarentena")
    assert res["status"] == "DRY_RUN"
    assert len(res["results"]) == 2
    
    status_map = {r["matter_id"]: r["status"] for r in res["results"]}
    assert status_map["v1"] == "ok"
    assert status_map["inv"] == "aninhado"
    
    assert aninhado.exists()  # n foi apagado

def test_reconciliacao_apply_move_apenas_aninhado_para_quarentena(tmp_path):
    root = tmp_path / "projetos2"
    
    valido = root / "valido" / ".rdaa-run" / "v1"
    valido.mkdir(parents=True)
    (valido / "matter_state.json").write_text('{"matter_id": "v1"}')
    
    aninhado = root / "invalido" / ".rdaa-run" / "inv" / ".rdaa-run" / "inv"
    aninhado.mkdir(parents=True)
    (aninhado / "matter_state.json").write_text('{"matter_id": "inv"}')
    
    quarantine = tmp_path / "quarentena2"
    res = reconcile_state(root, apply=True, quarantine=quarantine)
    
    assert res["status"] == "APPLIED"
    assert len(res["moved"]) == 1
    assert res["moved"][0]["matter_id"] == "inv"
    
    assert valido.exists()
    assert not aninhado.exists()
    
    manifestos = list(quarantine.glob("cleanup-manifest*.json"))
    assert len(manifestos) == 1
