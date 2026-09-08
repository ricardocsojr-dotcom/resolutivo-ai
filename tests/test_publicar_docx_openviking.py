import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "revisor-rdaa" / "scripts" / "publicar_docx.py"
SPEC = importlib.util.spec_from_file_location("publicar_docx", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_hook_pos_publicacao_chama_registro_com_nivel_explicito(tmp_path):
    calls = []

    def fake_registrar(state_dir, matter_id, level):
        calls.append((state_dir, matter_id, level))
        return {"success": True, "openviking_sync": {"success": True}}

    result = MODULE._registrar_cerebro_pos_publicacao(
        tmp_path,
        "caso-123",
        {"nivel_peca": "B"},
        registrar_fn=fake_registrar,
    )

    assert result["success"] is True
    assert calls == [(tmp_path, "caso-123", "B")]


def test_hook_pos_publicacao_recusa_contexto_sem_nivel(tmp_path):
    result = MODULE._registrar_cerebro_pos_publicacao(
        tmp_path,
        "caso-123",
        {},
        registrar_fn=lambda *args: {"success": True},
    )

    assert result["success"] is False
    assert "nivel_peca" in result["error"]
