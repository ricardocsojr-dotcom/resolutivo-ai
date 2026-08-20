#!/usr/bin/env python3
"""Diagnóstico e manutenção segura do estado local RDAA.

A limpeza é simulada por padrão. A ação efetiva exige --apply e move estados
para quarentena local; não há exclusão automática. Backups só são tocados por
comando explícito.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from .seguro import criar_backup, restaurar
    from .estado_rdaa import _safe_matter_id, _write_json
except ImportError:
    from seguro import criar_backup, restaurar
    from estado_rdaa import _safe_matter_id, _write_json


def _iso_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else (default or {})
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default or {}


def discover_state_dirs(root: Path) -> list[Path]:
    root = Path(root)
    if (root / "matter_state.json").is_file() and (root / "run_manifest.json").is_file():
        return [root]
    if not root.exists():
        return []
    return sorted(
        {
            path.parent
            for path in root.rglob("matter_state.json")
            if path.parent.is_dir()
            and path.parent.name != "candidate"
            and (path.parent / "run_manifest.json").is_file()
        }
    )


def summarize_state(state_dir: Path) -> dict[str, Any]:
    state = _read_json(state_dir / "matter_state.json")
    manifest = _read_json(state_dir / "run_manifest.json")
    provenance = state_dir / "provenance.jsonl"
    provenance_count = sum(1 for line in provenance.read_text(encoding="utf-8").splitlines() if line.strip()) if provenance.exists() else 0
    files = [path for path in state_dir.rglob("*") if path.is_file()]
    total_bytes = sum(path.stat().st_size for path in files)
    metrics = state.get("metrics") if isinstance(state.get("metrics"), dict) else {}
    candidate_dir = state_dir / "candidate"
    candidate_manifest = _read_json(candidate_dir / "run_manifest.json") if candidate_dir.is_dir() else {}
    return {
        "matter_id": state.get("matter_id") or manifest.get("matter_id") or state_dir.name,
        "path": str(state_dir),
        "status": manifest.get("status", "desconhecido"),
        "phase": manifest.get("phase"),
        "updated_at": state.get("updated_at") or manifest.get("updated_at") or _iso_mtime(state_dir),
        "attempt": manifest.get("attempt", 0),
        "publish_attempts": manifest.get("publish_attempts", 0),
        "blocked_attempts": manifest.get("blocked_attempts", 0),
        "candidate_status": manifest.get("candidate_status"),
        "candidate_path": str(candidate_dir) if candidate_dir.is_dir() else None,
        "candidate_hash": manifest.get("candidate_hash"),
        "confirmed_state_status": manifest.get("confirmed_state_status", "UNKNOWN"),
        "candidate_manifest_status": candidate_manifest.get("status"),
        "provenance_records": provenance_count,
        "semantic_reviews": len(state.get("semantic_reviews", [])) if isinstance(state.get("semantic_reviews"), list) else 0,
        "context_packs": len(metrics.get("context_packs", {})) if isinstance(metrics.get("context_packs"), dict) else 0,
        "files": len(files),
        "bytes": total_bytes,
    }


def inspect(root: Path) -> dict[str, Any]:
    states = [summarize_state(path) for path in discover_state_dirs(root)]
    return {
        "root": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "states": states,
        "count": len(states),
        "total_bytes": sum(item["bytes"] for item in states),
    }


def _cutoff(path: Path, older_than_days: int) -> float:
    return path.stat().st_mtime < (datetime.now(timezone.utc).timestamp() - older_than_days * 86400)


def plan_clean(root: Path, older_than_days: int, matter_id: str | None = None) -> list[dict[str, Any]]:
    candidates = []
    for path in discover_state_dirs(root):
        summary = summarize_state(path)
        if matter_id and summary["matter_id"] != matter_id:
            continue
        if not _cutoff(path, older_than_days):
            continue
        candidates.append({
            "matter_id": summary["matter_id"],
            "path": str(path),
            "bytes": summary["bytes"],
            "updated_at": summary["updated_at"],
            "action": "mover_para_quarentena",
        })
    return candidates


def clean(root: Path, older_than_days: int, matter_id: str | None, apply: bool, quarantine: Path) -> dict[str, Any]:
    candidates = plan_clean(root, older_than_days, matter_id)
    moved: list[dict[str, Any]] = []
    if apply:
        quarantine.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        for candidate in candidates:
            source = Path(candidate["path"])
            target = quarantine / f"{_safe_matter_id(candidate['matter_id'])}.{stamp}"
            if target.exists():
                target = quarantine / f"{_safe_matter_id(candidate['matter_id'])}.{stamp}.{len(moved)+1}"
            shutil.move(str(source), str(target))
            moved.append({**candidate, "quarantine_path": str(target)})
        manifest = quarantine / f"cleanup-manifest.{stamp}.json"
        _write_json(manifest, {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "root": str(root),
            "older_than_days": older_than_days,
            "matter_id": matter_id,
            "candidates": candidates,
            "moved": moved,
        })
    return {
        "root": str(root),
        "older_than_days": older_than_days,
        "apply": apply,
        "quarantine": str(quarantine),
        "candidates": candidates,
        "moved": moved,
        "status": "APPLIED" if apply else "DRY_RUN",
    }


def list_backups(root: Path) -> dict[str, Any]:
    backups = []
    for path in sorted(Path(root).rglob("*.bak")) if Path(root).exists() else []:
        backups.append({"path": str(path), "bytes": path.stat().st_size, "modified_at": _iso_mtime(path), "sha256": _hash_file(path)})
    return {"root": str(root), "count": len(backups), "backups": backups}


def restore_test(backup: Path) -> dict[str, Any]:
    backup = Path(backup)
    if not backup.is_file():
        raise FileNotFoundError(f"Backup não encontrado: {backup}")
    original_hash = _hash_file(backup)
    with tempfile.TemporaryDirectory(prefix="rdaa-restore-test-") as temp:
        target = Path(temp) / backup.name.removesuffix(".bak")
        shutil.copy2(backup, target)
        restored_hash = _hash_file(target)
    return {
        "backup": str(backup),
        "original_sha256": original_hash,
        "restored_sha256": restored_hash,
        "match": original_hash == restored_hash,
        "destination_touched": False,
        "status": "PASS" if original_hash == restored_hash else "FAIL",
    }


def restore_protected(backup: Path, destination: Path, backup_dir: Path | None) -> dict[str, Any]:
    backup = Path(backup)
    destination = Path(destination)
    created_backup = None
    if destination.exists():
        if backup_dir is None:
            raise ValueError("--backup-dir é obrigatório quando o destino já existe")
        created_backup = criar_backup(destination, Path(backup_dir))
    restaurar(backup, destination)
    return {
        "backup": str(backup),
        "destination": str(destination),
        "created_backup_before_restore": str(created_backup) if created_backup else None,
        "restored_sha256": _hash_file(destination),
        "status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnóstico e manutenção segura do estado RDAA")
    sub = parser.add_subparsers(dest="command", required=True)
    p_inspect = sub.add_parser("inspect")
    p_inspect.add_argument("root", type=Path)
    p_clean = sub.add_parser("clean")
    p_clean.add_argument("root", type=Path)
    p_clean.add_argument("--older-than-days", type=int, required=True)
    p_clean.add_argument("--matter-id", default=None)
    p_clean.add_argument("--apply", action="store_true")
    p_clean.add_argument("--quarantine", type=Path, default=None)
    p_backups = sub.add_parser("list-backups")
    p_backups.add_argument("root", type=Path)
    p_test = sub.add_parser("restore-test")
    p_test.add_argument("backup", type=Path)
    p_restore = sub.add_parser("restore")
    p_restore.add_argument("backup", type=Path)
    p_restore.add_argument("destination", type=Path)
    p_restore.add_argument("--backup-dir", type=Path, default=None)
    args = parser.parse_args()

    if args.command == "inspect":
        result = inspect(args.root)
    elif args.command == "clean":
        quarantine = args.quarantine or (args.root.parent / f"{args.root.name}.quarantine")
        result = clean(args.root, args.older_than_days, args.matter_id, args.apply, quarantine)
    elif args.command == "list-backups":
        result = list_backups(args.root)
    elif args.command == "restore-test":
        result = restore_test(args.backup)
    else:
        result = restore_protected(args.backup, args.destination, args.backup_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") not in {"FAIL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
