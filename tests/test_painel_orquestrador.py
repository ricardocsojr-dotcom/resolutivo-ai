import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "orquestrar-rdaa" / "scripts" / "painel_status.py"
SPEC = importlib.util.spec_from_file_location("painel_status", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_painel_mostra_estado_e_escapa_dados_do_manifesto():
    html = MODULE.render_panel(
        {
            "matter_id": "caso-<123>",
            "phase": "drafting",
            "status": "ready",
            "route": {"declared_piece_level": "B", "effective_piece_level": "B"},
            "approvals": [{"gate": "skeleton_approval", "approved_by": "Ricardo"}],
            "executions": [{"role": "writer", "motor": "codex", "duration_ms": 1250, "model_ids": ["gpt-5.6-codex"]}],
            "vault": {
                "lookups": [{"vault": "ementario-resolutivo", "domain": "dano-moral", "documents_count": 3, "status": "informada"}],
                "syncs": [{"vault": "procedimentos-informacoes", "status": "registered"}],
            },
            "transitions": [{"to": "drafting", "at": "2026-09-02T02:24:00+00:00"}],
        }
    )

    assert "caso-&lt;123&gt;" in html
    assert "drafting" in html
    assert "skeleton_approval" in html
    assert "Codex" in html
    assert "gpt-5.6-codex" in html
    assert "1,25 s" in html
    assert "Ementário / Obsidian" in html
    assert "ementario-resolutivo" in html
    assert "dano-moral" in html
    assert "procedimentos-informacoes" in html
