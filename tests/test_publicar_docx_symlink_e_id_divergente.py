from pathlib import Path
import json
import pytest
import sys
import tempfile
import os

from test_qa_engineering import FIXTURE

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = PLUGIN_ROOT / "skills" / "revisor-rdaa" / "scripts" / "publicar_docx.py"

import subprocess

def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PLUGIN_ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def test_id_divergente_falha(tmp_path):
    """(b) publicar duas vezes no mesmo --state-dir cannonico com --context trazendo matter_id diferente -> falha antes de escrever"""
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        context = folder / "context.json"
        
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        data["matter_id"] = "1111"
        context.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        
        candidate = folder / "candidate.docx"
        from test_qa_engineering import GENERATOR
        run([sys.executable, str(GENERATOR), "--context", str(context), "--output", str(candidate)])
        
        state_dir = folder / ".rdaa-run" / "1111"
        state_dir.mkdir(parents=True)
        manifest = state_dir / "run_manifest.json"
        manifest.write_text(json.dumps({"matter_id": "1111", "status": "PUBLISHED"}))
        
        # Agora muda o ID no contexto e tenta aprovar na mesma pasta
        data["matter_id"] = "2222"
        context.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        
        res = run([sys.executable, str(PUBLISHER), "--input", str(candidate), "--context", str(context), "--output", str(candidate), "--state-dir", str(state_dir)])
        
        assert res.returncode != 0
        assert "divergente" in res.stderr
        
        # Manifesto antigo deve estar intacto
        assert json.loads(manifest.read_text())["matter_id"] == "1111"

