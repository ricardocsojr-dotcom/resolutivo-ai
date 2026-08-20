#!/usr/bin/env python3
"""Verificação de IDs semânticos invisíveis no DOCX RDAA."""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
BOOKMARK_START = f"{{{W_NS}}}bookmarkStart"
MARK_RE = re.compile(r"^rdaa_(?P<id>.+)__\d+$")


def _safe_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9-]+", "-", str(value)).strip("-")
    return safe or "sem-id"


def _id_list(value: Any) -> list[str]:
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    return [str(item).strip() for item in values if str(item).strip()]


def expected_ids_from_context(context: dict[str, Any]) -> tuple[set[str], list[dict[str, Any]]]:
    expected: set[str] = set()
    blocks: list[dict[str, Any]] = []
    for index, block in enumerate(context.get("blocos", []), start=1):
        if not isinstance(block, dict):
            continue
        ids: list[str] = []
        for key in ("id", "semantic_ids", "fact_ids", "thesis_ids", "request_ids", "source_ids", "risk_ids"):
            ids.extend(_id_list(block.get(key)))
        ids = list(dict.fromkeys(ids))
        if not ids:
            continue
        blocks.append({"index": index, "tipo": block.get("tipo"), "ids": ids})
        expected.update(_safe_id(item) for item in ids)
    return expected, blocks


def actual_ids_from_docx(docx_path: Path | str) -> dict[str, list[str]]:
    path = Path(docx_path)
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ET.fromstring(xml)
    actual: dict[str, list[str]] = {}
    for element in root.iter(BOOKMARK_START):
        name = element.get(f"{{{W_NS}}}name") or ""
        match = MARK_RE.match(name)
        if not match:
            continue
        semantic_id = match.group("id")
        actual.setdefault(semantic_id, []).append(name)
    return actual


def verify_docx_semantics(
    docx_path: Path | str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Comparar IDs declarados com bookmarks presentes, sem inferir texto."""
    actual = actual_ids_from_docx(docx_path)
    if context is None:
        return {
            "status": "SKIPPED",
            "docx": str(docx_path),
            "expected": [],
            "present": sorted(actual),
            "missing": [],
            "findings": [],
        }

    expected, blocks = expected_ids_from_context(context)
    present = set(actual)
    missing = sorted(expected - present)
    duplicate_block_ids: list[str] = []
    seen_block_ids: set[str] = set()
    for block in blocks:
        for semantic_id in block["ids"]:
            if semantic_id in seen_block_ids and semantic_id == block.get("block_id"):
                duplicate_block_ids.append(semantic_id)
            seen_block_ids.add(semantic_id)

    findings: list[dict[str, Any]] = []
    for semantic_id in missing:
        locations = [
            f"contexto.blocos[{block['index']}]"
            for block in blocks
            if _safe_id(semantic_id) in {_safe_id(item) for item in block["ids"]}
        ]
        findings.append(
            {
                "id": f"DOCX-SEM-MISSING-{semantic_id}",
                "kind": "semantic_id_missing_in_docx",
                "severity": "erro",
                "message": f"ID semântico não localizado no DOCX: {semantic_id}",
                "entity_ids": [semantic_id],
                "localizacao": locations[0] if locations else None,
                "requires_human_review": False,
                "status": "aberto",
            }
        )
    for semantic_id in duplicate_block_ids:
        findings.append(
            {
                "id": f"DOCX-SEM-DUP-{_safe_id(semantic_id)}",
                "kind": "semantic_id_duplicate_block",
                "severity": "alerta",
                "message": f"ID de bloco semântico repetido: {semantic_id}",
                "entity_ids": [semantic_id],
                "localizacao": "contexto.blocos",
                "requires_human_review": True,
                "status": "aberto",
            }
        )
    blocking = [item for item in findings if item["severity"] == "erro"]
    return {
        "status": "BLOCK" if blocking else "PASS",
        "docx": str(docx_path),
        "expected": sorted(expected),
        "present": sorted(present),
        "missing": missing,
        "findings": findings,
        "counts": {
            "total": len(findings),
            "blocking": len(blocking),
            "alerts": sum(1 for item in findings if item["severity"] == "alerta"),
        },
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Verificar IDs semânticos no DOCX")
    parser.add_argument("docx", type=Path)
    parser.add_argument("--context", type=Path, default=None)
    args = parser.parse_args()
    context = None
    if args.context:
        context = json.loads(args.context.read_text(encoding="utf-8"))
    report = verify_docx_semantics(args.docx, context)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
