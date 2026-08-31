#!/usr/bin/env python3
"""Gate único de QA do plugin RDAA.

Executa os validadores existentes, preserva sua saída original e produz um
resultado estruturado. O gate não cria uma nova regra de redação: ele apenas
impede que a entrega seja considerada concluída quando um validador objetivo
falha.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ponytail: mesmo fix de construir_peca.py/verificar_formatacao.py — sem
# isso, este script relê a saída UTF-8 dos validadores corretamente, mas ao
# reimprimir na própria stdout sem reconfigurar, o Windows grava em cp1252;
# quem capturar esta saída como UTF-8 (ex.: o publicador, ou um teste) recebe
# mojibake ou caractere de substituição no lugar do acento.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parents[2]
FORMAT_SCRIPT = PLUGIN_ROOT / "skills" / "formatar-peca" / "scripts" / "verificar_formatacao.py"
STYLE_SCRIPT = SCRIPT_DIR / "verificar_estilo.py"


def _run_check(name: str, script: Path, docx: Path) -> dict:
    command = [sys.executable, str(script), str(docx)]
    # ponytail: sem encoding explícito, o Windows decodifica a saída do
    # subprocesso com o codepage ANSI do console (cp1252), corrompendo acento
    # de mensagem em UTF-8 ("não está" -> "nÃ£o estÃ¡") antes mesmo de chegar
    # no agregador do gate.
    completed = subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    output = completed.stdout
    if completed.stderr:
        output += ("\n" if output else "") + completed.stderr
    return {
        "name": name,
        "script": str(script),
        "command": command,
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0,
        "output": output.rstrip(),
    }


def run_gate(docx: Path) -> dict:
    checks = [
        _run_check("formatacao", FORMAT_SCRIPT, docx),
        _run_check("estilo", STYLE_SCRIPT, docx),
    ]
    errors = [check for check in checks if not check["passed"]]
    return {
        "schema_version": "1",
        "status": "PASS" if not errors else "FAIL",
        "docx": str(docx),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "errors": [check["name"] for check in errors],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate único de QA do RDAA")
    parser.add_argument("docx", type=Path, help="DOCX final a verificar")
    parser.add_argument(
        "--json",
        dest="json_path",
        type=Path,
        help="caminho para salvar o resultado estruturado",
    )
    args = parser.parse_args()

    if not args.docx.is_file():
        print(f"[ERRO] DOCX não encontrado: {args.docx}", file=sys.stderr)
        return 2

    result = run_gate(args.docx)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    if result["status"] == "PASS":
        print(f"[OK] Gate RDAA aprovado: {args.docx}")
        return 0

    print(f"[ERRO] Gate RDAA bloqueou a entrega: {', '.join(result['errors'])}")
    for check in result["checks"]:
        if not check["passed"]:
            print(f"\n--- {check['name']} ---\n{check['output']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
