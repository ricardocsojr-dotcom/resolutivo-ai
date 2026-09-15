import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "buscar-jurisprudencia" / "scripts" / "registrar_fonte_verificada.py"
SPEC = importlib.util.spec_from_file_location("registrar_fonte_verificada", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_fonte_verificada_registra_no_cerebro(tmp_path):
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
    assert result["cerebro_registered"] is True
    assert "openviking_sync" not in result
    assert Path(result["path"]).is_file()
