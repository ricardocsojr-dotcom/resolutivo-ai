import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "redigir-peca" / "scripts" / "registrar_cerebro.py"
SPEC = importlib.util.spec_from_file_location("registrar_cerebro", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _cerebro(tmp_path: Path) -> Path:
    cerebro = tmp_path / "cerebro"
    for directory in ("domains", "concepts", "sources", "entities", "operacional", "pessoal"):
        (cerebro / "wiki" / directory).mkdir(parents=True, exist_ok=True)
    return cerebro


def test_registrar_recusa_materia_ainda_nao_publicada(tmp_path, monkeypatch):
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)
    monkeypatch.setattr(MODULE, "WIKI_OPERACIONAL", cerebro / "wiki" / "operacional")
    (tmp_path / "contexto_peca.json").write_text(
        json.dumps({"titulo_peca": "Manifestação", "partes": {"autor": {"nome": "Cliente"}}}),
        encoding="utf-8",
    )
    (tmp_path / "run_manifest.json").write_text(json.dumps({"phase": "drafting"}), encoding="utf-8")

    result = MODULE.registrar(tmp_path, "caso-123", "B")

    assert result["success"] is False
    assert "published" in result["error"]
    assert not list((cerebro / "wiki" / "operacional").glob("*.md"))


def test_registrar_publicado_emite_recibo_para_vault_registered(tmp_path, monkeypatch):
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)
    monkeypatch.setattr(MODULE, "WIKI_OPERACIONAL", cerebro / "wiki" / "operacional")
    (tmp_path / "contexto_peca.json").write_text(
        json.dumps({"titulo_peca": "Manifestação", "partes": {"autor": {"nome": "Cliente"}}}),
        encoding="utf-8",
    )
    (tmp_path / "run_manifest.json").write_text(json.dumps({"phase": "published"}), encoding="utf-8")

    result = MODULE.registrar(tmp_path, "caso-123", "B")

    receipt = json.loads((tmp_path / "CEREBRO-RECIBO.json").read_text(encoding="utf-8"))
    assert result["success"] is True
    assert receipt["vault"] == "cerebro-ricar"
    assert receipt["status"] == "registered"


def test_registrar_normaliza_campos_para_nao_forjar_frontmatter(tmp_path, monkeypatch):
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)
    monkeypatch.setattr(MODULE, "WIKI_OPERACIONAL", cerebro / "wiki" / "operacional")
    (tmp_path / "contexto_peca.json").write_text(
        json.dumps({"titulo_peca": "Título\nstatus: forjado", "partes": {"autor": {"nome": "Cliente\n---"}}}),
        encoding="utf-8",
    )
    (tmp_path / "run_manifest.json").write_text(json.dumps({"phase": "published"}), encoding="utf-8")

    result = MODULE.registrar(tmp_path, "caso-123", "B")

    content = Path(result["file"]).read_text(encoding="utf-8")
    assert "\nstatus: forjado\n" not in content
    assert 'title: "Título status: forjado"' in content
    assert content.count("---\n") == 2
