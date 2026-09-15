from pathlib import Path
import json
import pytest
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "redigir-peca" / "scripts" / "registrar_cerebro.py"

SPEC = importlib.util.spec_from_file_location("registrar_cerebro", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_registrar_sync_no_manifesto(tmp_path):
    manifest_path = tmp_path / "run_manifest.json"
    manifest_data = {"vault": {"syncs": []}}
    manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")

    receipt = tmp_path / "RECIBO.json"
    receipt.write_text('{"status": "ok"}', encoding="utf-8")

    result = MODULE._registrar_sync_no_manifesto(tmp_path, receipt)

    assert result["success"] is True
    
    updated = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(updated["vault"]["syncs"]) == 1
    sync_entry = updated["vault"]["syncs"][0]
    
    assert sync_entry["vault"] == "cerebro-ricar"
    assert sync_entry["direction"] == "push"
    assert sync_entry["artifact_path"] == str(receipt)

def test_registrar_sync_manifesto_vazio(tmp_path):
    # Missing run_manifest.json
    receipt = tmp_path / "RECIBO.json"
    result = MODULE._registrar_sync_no_manifesto(tmp_path, receipt)
    
    assert result["success"] is False
    assert "não encontrado" in result["error"]
