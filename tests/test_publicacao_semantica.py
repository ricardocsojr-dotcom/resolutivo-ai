#!/usr/bin/env python3
"""Integração do gate semântico com a publicação protegida."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "skills" / "formatar-peca" / "scripts" / "construir_peca.py"
PUBLISH = ROOT / "skills" / "revisor-rdaa" / "scripts" / "publicar_docx.py"
FIXTURE = ROOT / "tests" / "fixtures" / "context_happy.json"


def test_semantic_block_preserves_previous_output() -> None:
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        context = json.loads(FIXTURE.read_text(encoding="utf-8"))
        context["numero_processo"] = "2222222-22.2222.8.26.2222"
        context["teses"] = [
            {
                "id": "T-1",
                "texto": "Tese com fonte ausente",
                "source_ids": ["SRC-INEXISTENTE"],
            }
        ]
        context_path = folder / "context.json"
        context_path.write_text(json.dumps(context, ensure_ascii=False), encoding="utf-8")
        candidate = folder / "candidate.docx"
        output = folder / "final.docx"
        output.write_bytes(b"versao-anterior")

        build_result = subprocess.run(
            [sys.executable, str(BUILD), "--context", str(context_path), "--output", str(candidate)],
            text=True,
            capture_output=True,
        )
        assert build_result.returncode == 0, build_result.stdout + build_result.stderr
        publish_result = subprocess.run(
            [
                sys.executable,
                str(PUBLISH),
                "--input",
                str(candidate),
                "--output",
                str(output),
                "--context",
                str(context_path),
            ],
            text=True,
            capture_output=True,
        )
        assert publish_result.returncode == 1, publish_result.stdout + publish_result.stderr
        assert output.read_bytes() == b"versao-anterior"
        state_dir = folder / ".rdaa-run" / "2222222-22.2222.8.26.2222"
        state = json.loads((state_dir / "matter_state.json").read_text(encoding="utf-8"))
        candidate_state_dir = state_dir / "candidate"
        candidate_state = json.loads((candidate_state_dir / "matter_state.json").read_text(encoding="utf-8"))
        manifest = json.loads((state_dir / "run_manifest.json").read_text(encoding="utf-8"))
        candidate_manifest = json.loads((candidate_state_dir / "run_manifest.json").read_text(encoding="utf-8"))
        assert state["semantic_reviews"] == []
        assert candidate_state["semantic_reviews"]
        assert candidate_state["semantic_reviews"][-1]["status"] == "BLOCK"
        assert manifest["candidate_status"] == "REJECTED"
        assert manifest["confirmed_state_status"] == "PRESERVED"
        assert candidate_manifest["state_role"] == "candidate"


if __name__ == "__main__":
    test_semantic_block_preserves_previous_output()
    print("[OK] bloqueio semântico preserva a publicação anterior")
