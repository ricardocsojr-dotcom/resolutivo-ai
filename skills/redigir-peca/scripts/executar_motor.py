#!/usr/bin/env python3
"""Executa Codex ou Antigravity diretamente, sem agente-wrapper."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# ponytail: mesmo fix de construir_peca.py/verificar_formatacao.py/qa_gate.py
# — sem isso, mensagem de erro com acento sai como mojibake no Windows.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]


def executar(
    motor: str, prompt_path: Path, output_path: Path, schema: Path | None, timeout: int, effort: str = "medium"
) -> None:
    prompt = prompt_path.read_text(encoding="utf-8")
    if not prompt.strip():
        raise ValueError("prompt vazio")

    if motor == "codex":
        cmd = [
            "codex", "exec", "--ephemeral", "--sandbox", "read-only",
            "--color", "never", "-C", str(ROOT), "-",
        ]
        stdin = prompt
    else:
        cmd = [
            "agy", "--input-format", "stream-json", "--output-format", "stream-json",
            "--effort", effort,
        ]
        if schema:
            cmd += ["--json-schema", str(schema)]
        stdin = json.dumps({"event": "user", "message": {"content": prompt}}, ensure_ascii=False) + "\n"

    result = subprocess.run(
        cmd,
        cwd=ROOT,
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"{motor} encerrou com código {result.returncode}")

    content = result.stdout.strip() if motor == "codex" else _resultado_antigravity(result.stdout, bool(schema))
    if not content:
        raise RuntimeError(f"{motor} não devolveu conteúdo")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content + "\n", encoding="utf-8")


def _resultado_antigravity(stdout: str, structured: bool) -> str:
    events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    event = next((item for item in reversed(events) if item.get("event") == "result"), None)
    final = event.get("result") if event else None
    if not final or final.get("status") != "SUCCESS":
        raise RuntimeError("Antigravity não devolveu um resultado válido")
    value = final.get("structured_output") if structured else final.get("response")
    return json.dumps(value, ensure_ascii=False, indent=2) if structured else str(value or "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("motor", choices=("codex", "antigravity"))
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--effort", choices=("low", "medium", "high"), default="medium")
    args = parser.parse_args()
    if args.schema and args.motor != "antigravity":
        parser.error("--schema só pode ser usado com antigravity")
    executar(args.motor, args.prompt, args.output, args.schema, args.timeout, args.effort)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
