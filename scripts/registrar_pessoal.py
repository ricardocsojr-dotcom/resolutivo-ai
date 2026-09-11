#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Registra anotações, decisões, metas e reflexões pessoais no Cérebro-Ricar e sincroniza no OpenViking.

Uso:
    py -3.14 scripts/registrar_pessoal.py --title "Meta Q4 2026" --category metas --content "Texto da meta..."
    py -3.14 scripts/registrar_pessoal.py --title "Exames Cardíacos" --category saude --file caminho/exame.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CEREBRO_PATH = Path(r"C:\Users\ricar\cerebro-ricar")
WIKI_PESSOAL = CEREBRO_PATH / "wiki" / "pessoal"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)[:60]


def registrar_nota_pessoal(
    title: str,
    content: str,
    category: str = "reflexao",
    status: str = "ativo",
    *,
    cerebro_root: Path = CEREBRO_PATH,
) -> dict[str, Any]:
    if not cerebro_root.exists():
        return {"success": False, "error": f"Cérebro não encontrado em {cerebro_root}"}

    pessoal_dir = cerebro_root / "wiki" / "pessoal"
    pessoal_dir.mkdir(parents=True, exist_ok=True)

    slug = _slugify(title)
    if not slug:
        slug = f"nota-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    file_path = pessoal_dir / f"{slug}.md"
    now_str = _now()

    # Monta frontmatter
    doc = (
        f"---\n"
        f"type: personal\n"
        f"title: \"{title}\"\n"
        f"category: {category}\n"
        f"status: {status}\n"
        f"created: {now_str}\n"
        f"updated: {now_str}\n"
        f"---\n\n"
        f"# {title}\n\n"
        f"{content.strip()}\n"
    )

    file_path.write_text(doc, encoding="utf-8")

    # Atualiza index.json
    try:
        scripts_dir = Path(__file__).resolve().parent.parent / "skills" / "redigir-peca" / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from registrar_cerebro import atualizar_index
        atualizar_index(slug)
    except Exception as exc:
        print(f"[AVISO] Falha ao atualizar index.json: {exc}", file=sys.stderr)

    # Sincroniza OpenViking
    openviking_result = {}
    try:
        from sincronizar_openviking import sync_path
        receipt_path = pessoal_dir / ".sync-receipt.json"
        openviking_result = sync_path(
            pessoal_dir,
            cerebro_root=cerebro_root,
            receipt_path=receipt_path,
            processing_mode="vectors_only",
            timeout=300,
        )
    except Exception as exc:
        openviking_result = {"success": False, "error": str(exc)}

    return {
        "success": True,
        "file": str(file_path),
        "slug": slug,
        "title": title,
        "category": category,
        "openviking_sync": openviking_result,
        "timestamp": now_str,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Registra notas pessoais no Cérebro-Ricar")
    parser.add_argument("--title", required=True, help="Título da anotação/reflexão/decisão")
    parser.add_argument(
        "--category",
        default="reflexao",
        choices=["decisao", "saude", "metas", "rotina", "reflexao", "governanca", "infraestrutura"],
        help="Categoria temática da nota",
    )
    parser.add_argument("--status", default="ativo", help="Status da nota (ativo, aprovado, arquivado, etc.)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--content", help="Texto da nota diretamente via CLI")
    group.add_argument("--file", type=Path, help="Arquivo markdown com o conteúdo da nota")

    args = parser.parse_args()

    content = args.content
    if args.file:
        if not args.file.is_file():
            print(f"[ERRO] Arquivo não encontrado: {args.file}", file=sys.stderr)
            return 1
        content = args.file.read_text(encoding="utf-8")

    res = registrar_nota_pessoal(
        title=args.title,
        content=content,
        category=args.category,
        status=args.status,
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
