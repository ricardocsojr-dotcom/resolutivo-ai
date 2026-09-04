import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "estudo-juridico-rdaa" / "scripts" / "registrar_estudo_cerebro.py"
SPEC = importlib.util.spec_from_file_location("registrar_estudo_cerebro", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _cerebro(tmp_path: Path) -> Path:
    cerebro = tmp_path / "cerebro"
    for directory in ("domains", "concepts", "sources", "entities", "operacional", "pessoal"):
        (cerebro / "wiki" / directory).mkdir(parents=True, exist_ok=True)
    return cerebro


def test_criar_source_rejeita_id_que_sai_do_diretorio_de_fontes(tmp_path, monkeypatch):
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)
    victim = cerebro / "wiki" / "operacional" / "matter-victim.md"
    victim.write_text("registro íntegro", encoding="utf-8")

    with pytest.raises(ValueError, match="fonte"):
        MODULE.criar_source("../operacional/matter-victim", "ementa literal", "STJ", "2026-09-03")

    assert victim.read_text(encoding="utf-8") == "registro íntegro"


def test_registrar_estudo_recusa_fonte_sem_ementa_literal(tmp_path, monkeypatch):
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)

    result = MODULE.registrar("Tema", "https://artifact.test/1", [], ["PREC-999"], "direito-civil")

    assert result["success"] is False
    assert not (cerebro / "wiki" / "sources" / "PREC-999.md").exists()
