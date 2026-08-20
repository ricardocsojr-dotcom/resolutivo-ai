"""Regressões da identidade técnica e pública do plugin Resolutivo.AI."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["name"] == "resolutivo-ai"
    assert manifest["version"] == "3.0.0"
    assert "Resolutivo.AI" in manifest["description"]
    assert re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", manifest["name"])

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert readme.startswith("# Resolutivo.AI")
    assert "`resolutivo-ai`" in readme
    assert "/resolutivo-ai:redigir-peca" in readme

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix == ".pyc":
            continue
        if path.name == "test_plugin_identity.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert "rdaa-contencioso" not in text, f"slug antigo encontrado em {path}"

    print("[OK] identidade Resolutivo.AI validada")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
