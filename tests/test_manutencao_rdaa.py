"""Regressões de operação e manutenção do estado local RDAA."""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "revisor-rdaa" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from estado_rdaa import initialize_state  # noqa: E402
from manutencao_rdaa import clean, inspect, restore_protected, restore_test  # noqa: E402
from seguro import criar_backup  # noqa: E402


def test_inspect_and_clean_are_safe_and_isolated() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / ".rdaa-run"
        old_dir = root / "matter-old"
        new_dir = root / "matter-new"
        initialize_state(old_dir, matter_id="matter-old")
        initialize_state(new_dir, matter_id="matter-new")
        old_state = json.loads((old_dir / "matter_state.json").read_text(encoding="utf-8"))
        old_state["matter_id"] = "matter-old"
        (old_dir / "matter_state.json").write_text(json.dumps(old_state), encoding="utf-8")
        old_time = time.time() - 10 * 86400
        os.utime(old_dir, (old_time, old_time))

        summary = inspect(root)
        assert summary["count"] == 2
        assert {item["matter_id"] for item in summary["states"]} == {"matter-old", "matter-new"}

        dry_run = clean(root, older_than_days=2, matter_id=None, apply=False, quarantine=Path(temp) / "quarantine")
        assert dry_run["status"] == "DRY_RUN"
        assert len(dry_run["candidates"]) == 1
        assert old_dir.is_dir()

        applied = clean(root, older_than_days=2, matter_id=None, apply=True, quarantine=Path(temp) / "quarantine")
        assert applied["status"] == "APPLIED"
        assert len(applied["moved"]) == 1
        assert not old_dir.exists()
        assert new_dir.exists()
        assert list((Path(temp) / "quarantine").glob("cleanup-manifest.*.json"))


def test_restore_test_does_not_touch_destination_and_restore_protects_current_file() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        source = root / "source.docx"
        source.write_bytes(b"versao-anterior")
        backup_dir = root / ".rdaa-backups"
        backup = criar_backup(source, backup_dir)
        check = restore_test(backup)
        assert check["status"] == "PASS"
        assert check["destination_touched"] is False

        destination = root / "final.docx"
        destination.write_bytes(b"versao-atual")
        result = restore_protected(backup, destination, backup_dir)
        assert result["status"] == "PASS"
        assert destination.read_bytes() == b"versao-anterior"
        assert result["created_backup_before_restore"]
        assert len(list(backup_dir.glob("*.bak"))) >= 2


def main() -> int:
    test_inspect_and_clean_are_safe_and_isolated()
    test_restore_test_does_not_touch_destination_and_restore_protects_current_file()
    print("[OK] diagnóstico, limpeza segura, quarentena e restauração passaram")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
