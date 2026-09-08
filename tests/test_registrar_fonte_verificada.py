import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "buscar-jurisprudencia" / "scripts" / "registrar_fonte_verificada.py"
SPEC = importlib.util.spec_from_file_location("registrar_fonte_verificada", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_fonte_verificada_dispara_sincronizacao_openviking(tmp_path, monkeypatch):
    calls = []

    def fake_sync(*args, **kwargs):
        calls.append((args, kwargs))
        return {"success": True, "root_uri": "viking://resources"}

    monkeypatch.setattr(MODULE, "_sincronizar_openviking", fake_sync)

    result = MODULE.registrar_fonte_verificada(
        ementa_literal="Ementa literal verificada.",
        tribunal="STJ",
        numero_processo="REsp 1",
        relator="Ministro X",
        data_julgamento="2026-09-08",
        url="https://example.test/prec",
        tema="fraude à execução",
        source_id="PREC-999",
        cerebro_root=tmp_path / "cerebro",
    )

    assert result["success"] is True
    assert result["openviking_sync"]["success"] is True
    assert calls
    assert calls[0][0][0].name == "sources"
    assert calls[0][1]["processing_mode"] == "vectors_only"
