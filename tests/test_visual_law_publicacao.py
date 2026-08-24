#!/usr/bin/env python3
"""Integração do Visual Law rastreável com publicação protegida."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "skills" / "formatar-peca" / "scripts" / "construir_peca.py"
PUBLISH = ROOT / "skills" / "revisor-rdaa" / "scripts" / "publicar_docx.py"
FIXTURE = ROOT / "tests" / "fixtures" / "context_happy.json"


def _context() -> dict:
    context = json.loads(FIXTURE.read_text(encoding="utf-8"))
    context["blocos"].append(
        {
            "tipo": "visual",
            "visual_tipo": "matrix",
            "funcao_visual": "Comparar elementos explicitamente fornecidos",
            "texto_pesquisavel": "Elemento A, elemento B, comparação informada",
            "cabecalho": ["Elemento", "Comparação"],
            "linhas": [["Elemento A", "elemento B, comparação informada"]],
            "semantic_ids": ["VISUAL-PUBLISH-1"],
        }
    )
    return context


def test_visual_law_publish_and_block() -> None:
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        context = _context()
        context_path = folder / "context.json"
        context_path.write_text(json.dumps(context, ensure_ascii=False), encoding="utf-8")
        candidate = folder / "candidate.docx"
        output = folder / "final.docx"

        build = subprocess.run([sys.executable, str(BUILD), "--context", str(context_path), "--output", str(candidate)], text=True, capture_output=True)
        assert build.returncode == 0, build.stdout + build.stderr
        publish = subprocess.run([sys.executable, str(PUBLISH), "--input", str(candidate), "--output", str(output), "--context", str(context_path)], text=True, capture_output=True)
        assert publish.returncode == 0, publish.stdout + publish.stderr
        previous = output.read_bytes()

        invalid_context = copy.deepcopy(context)
        invalid_context["blocos"][-1]["texto_pesquisavel"] = "Texto inexistente no DOCX"
        context_path.write_text(json.dumps(invalid_context, ensure_ascii=False), encoding="utf-8")
        blocked = subprocess.run([sys.executable, str(PUBLISH), "--input", str(candidate), "--output", str(output), "--context", str(context_path)], text=True, capture_output=True)
        assert blocked.returncode == 1, blocked.stdout + blocked.stderr
        assert output.read_bytes() == previous


if __name__ == "__main__":
    test_visual_law_publish_and_block()
    print("[OK] publicação Visual Law e bloqueio protegido passaram")
