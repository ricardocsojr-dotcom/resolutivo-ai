#!/usr/bin/env python3
"""Wrapper para o compilador Markdown -> RDAA JSON."""

from pathlib import Path
import sys

TARGET = Path(__file__).resolve().parents[1] / "skills" / "formatar-peca" / "scripts" / "md2rdaa.py"

if __name__ == "__main__":
    import subprocess
    cmd = [sys.executable, str(TARGET)] + sys.argv[1:]
    sys.exit(subprocess.run(cmd).returncode)
