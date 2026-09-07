#!/usr/bin/env python3
"""Migra fontes já existentes para a política de revisão de vigência.

Não altera ementa, tribunal, processo, URL nem a data histórica de conferência.
Registra uma revisão de vigência realizada hoje, sua base declarada e o próximo
prazo. Use apenas com uma razão auditável -- nunca para presumir que uma fonte
antiga continua atual sem conferência.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

DEFAULT_CEREBRO_ROOT = Path(os.environ.get("RDAA_CEREBRO_PATH", r"C:\Users\ricar\cerebro-ricar"))
_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _insert_review_fields(text: str, *, reviewed_at: str, due: str, review_days: int, basis: str) -> str:
    match = _FRONTMATTER.match(text)
    if not match:
        raise ValueError("frontmatter YAML ausente")
    frontmatter = match.group(1)
    if re.search(r"(?m)^review_due:\s*\S+", frontmatter):
        return text
    fields = (
        f"last_currency_review: {reviewed_at}\n"
        f"review_interval_days: {review_days}\n"
        f"review_due: {due}\n"
        "review_status: vigente\n"
        f"review_basis: {_yaml_quote(basis)}\n"
    )
    # Mantém a data de criação e acrescenta os campos imediatamente após ela.
    if re.search(r"(?m)^created:.*$", frontmatter):
        frontmatter = re.sub(r"(?m)^(created:.*)$", r"\1\n" + fields.rstrip("\n"), frontmatter, count=1)
    else:
        frontmatter = frontmatter.rstrip("\n") + "\n" + fields.rstrip("\n")
    return "---\n" + frontmatter + "\n---\n" + text[match.end():]


def migrate(*, cerebro_root: Path, review_days: int, basis: str, dry_run: bool) -> dict:
    if review_days < 1:
        raise ValueError("review_days deve ser maior ou igual a 1")
    sources = cerebro_root / "wiki" / "sources"
    now = _now()
    due = (datetime.now(timezone.utc) + timedelta(days=review_days)).date().isoformat()
    updated: list[str] = []
    skipped: list[str] = []
    for path in sorted(sources.glob("*.md")):
        if path.name == "_index.md":
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?m)^review_due:\s*\S+", text):
            skipped.append(path.stem)
            continue
        changed = _insert_review_fields(text, reviewed_at=now, due=due, review_days=review_days, basis=basis)
        if not dry_run:
            path.write_text(changed, encoding="utf-8")
        updated.append(path.stem)
    return {
        "dry_run": dry_run,
        "reviewed_at": now,
        "review_due": due,
        "review_days": review_days,
        "updated_count": len(updated),
        "updated": updated,
        "skipped_count": len(skipped),
        "skipped": skipped,
        "basis": basis,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Migra fontes existentes para revisão de vigência")
    parser.add_argument("--cerebro", type=Path, default=DEFAULT_CEREBRO_ROOT)
    parser.add_argument("--review-days", type=int, default=365)
    parser.add_argument("--basis", required=True, help="base auditável da revisão de vigência")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(json.dumps(migrate(
        cerebro_root=args.cerebro.resolve(), review_days=args.review_days,
        basis=args.basis, dry_run=args.dry_run,
    ), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
