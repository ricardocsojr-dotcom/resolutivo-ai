import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "scripts" / "session-end.mjs"


def test_session_end_le_o_manifesto_canonico(tmp_path):
    if not shutil.which("node"):
        return
    matter = tmp_path / ".rdaa-run" / "caso-1"
    matter.mkdir(parents=True)
    (matter / "run_manifest.json").write_text(
        json.dumps({"phase": "draft", "status": "active"}), encoding="utf-8"
    )
    result = subprocess.run(["node", str(HOOK)], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0
    pending = json.loads((tmp_path / ".rdaa-run" / ".pending_vault_sync.json").read_text(encoding="utf-8"))
    assert pending["pending"] == [
        {"matter_id": "caso-1", "phase": "draft", "status": "active", "output": None}
    ]
