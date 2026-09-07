#!/usr/bin/env python3
"""Índice temático de fontes (jurisprudência) do cérebro-ricar.

Índice invertido local (SQLite FTS5/BM25) sobre wiki/sources/*.md. Existe
para buscar por tema sem depender de acertar um domain.md — problema real:
uma tese de recuperação judicial (art. 49 §3º LFRE) pode não ter domínio
correspondente ainda, ou cair num domínio genérico errado, e isso não deveria
impedir achar uma ementa já verificada em matéria anterior.

Não é fonte de verdade. Os arquivos .md em wiki/sources/ continuam sendo a
fonte; este índice é derivado e reconstruível a qualquer momento via
`reindex`. Não requer infraestrutura além do sqlite3 da stdlib.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

DEFAULT_CEREBRO_ROOT = Path(os.environ.get("RDAA_CEREBRO_PATH", r"C:\Users\ricar\cerebro-ricar"))
_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_BODY_FIELD = re.compile(
    r"(?im)^\s*(?:-\s*)?\*{0,2}(tribunal|n[uú]mero do processo|relator|data)\*{0,2}\s*:\*{0,2}\s*(.+)$"
)


def _db_path(cerebro_root: Path) -> Path:
    return cerebro_root / "wiki" / "sources" / ".index" / "fontes.db"


def _parse_frontmatter(text: str) -> dict[str, str]:
    match = _FRONTMATTER.match(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"')
    return fields


def _parse_body_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for match in _BODY_FIELD.finditer(text):
        key = match.group(1).strip().lower()
        key = {"número do processo": "numero_processo", "numero do processo": "numero_processo"}.get(key, key)
        fields[key] = match.group(2).strip()
    return fields


def _review_state(path: Path) -> dict[str, Any]:
    """Informa se uma fonte pode ser reutilizada sem revisão de entendimento."""
    frontmatter = _parse_frontmatter(path.read_text(encoding="utf-8"))
    due_raw = frontmatter.get("review_due", "")
    if not due_raw:
        return {
            "status": "sem_prazo",
            "automatic_reuse": False,
            "action": "revisar antes de reutilizar; fonte criada antes da política de vigência",
        }
    try:
        due = date.fromisoformat(due_raw)
    except ValueError:
        return {
            "status": "data_invalida",
            "automatic_reuse": False,
            "action": "corrigir review_due e revisar antes de reutilizar",
        }
    days = (due - date.today()).days
    if days < 0:
        return {
            "status": "revisao_vencida",
            "automatic_reuse": False,
            "review_due": due.isoformat(),
            "days_overdue": abs(days),
            "action": "confirmar entendimento atual antes de citar",
        }
    return {
        "status": "vigente",
        "automatic_reuse": True,
        "review_due": due.isoformat(),
        "days_until_review": days,
    }


def _connect(cerebro_root: Path) -> sqlite3.Connection:
    db_path = _db_path(cerebro_root)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS sources_fts USING fts5(
            source_id UNINDEXED,
            title,
            tribunal,
            numero_processo UNINDEXED,
            relator UNINDEXED,
            data_julgamento UNINDEXED,
            content,
            path UNINDEXED
        )
        """
    )
    return conn


def _row_for(root: Path, path: Path) -> tuple:
    text = path.read_text(encoding="utf-8")
    frontmatter = _parse_frontmatter(text)
    body_fields = _parse_body_fields(text)
    return (
        path.stem,
        frontmatter.get("title", path.stem),
        frontmatter.get("court") or body_fields.get("tribunal", ""),
        body_fields.get("numero_processo", ""),
        body_fields.get("relator", ""),
        frontmatter.get("date") or body_fields.get("data", ""),
        text,
        str(path.relative_to(root)),
    )


def reindex(cerebro_root: Path | str = DEFAULT_CEREBRO_ROOT) -> dict[str, Any]:
    """Reconstrói o índice inteiro a partir de wiki/sources/*.md. Idempotente."""
    root = Path(cerebro_root).resolve()
    sources_dir = root / "wiki" / "sources"
    conn = _connect(root)
    conn.execute("DELETE FROM sources_fts")
    count = 0
    if sources_dir.is_dir():
        for path in sorted(sources_dir.glob("*.md")):
            if path.name == "_index.md":
                continue
            conn.execute(
                "INSERT INTO sources_fts (source_id, title, tribunal, numero_processo, relator, "
                "data_julgamento, content, path) VALUES (?,?,?,?,?,?,?,?)",
                _row_for(root, path),
            )
            count += 1
    conn.commit()
    conn.close()
    return {"indexed": count, "db": str(_db_path(root))}


def index_one(path: Path | str, cerebro_root: Path | str = DEFAULT_CEREBRO_ROOT) -> dict[str, Any]:
    """Indexa (ou reindexa) um único arquivo, sem reconstruir tudo.

    Chame após criar/atualizar uma fonte — mais barato que `reindex` completo
    quando você acabou de registrar uma única ementa nova.
    """
    root = Path(cerebro_root).resolve()
    source_path = Path(path).resolve()
    conn = _connect(root)
    conn.execute("DELETE FROM sources_fts WHERE source_id = ?", (source_path.stem,))
    conn.execute(
        "INSERT INTO sources_fts (source_id, title, tribunal, numero_processo, relator, "
        "data_julgamento, content, path) VALUES (?,?,?,?,?,?,?,?)",
        _row_for(root, source_path),
    )
    conn.commit()
    conn.close()
    return {"indexed": source_path.stem}


def buscar(query: str, limit: int = 5, cerebro_root: Path | str = DEFAULT_CEREBRO_ROOT) -> list[dict[str, Any]]:
    """Busca por tema/termo nas fontes já verificadas no cérebro (FTS5 + BM25).

    Use ANTES de disparar nova busca no Jusbrasil — se já houver ementa
    verificada aderente ao tema, reaproveite em vez de re-pesquisar e
    re-conferir literalidade do zero.
    """
    root = Path(cerebro_root).resolve()
    conn = _connect(root)
    terms = re.findall(r"[\wÀ-ÿ]+", query)
    if not terms:
        conn.close()
        return []
    fts_query = " OR ".join(f'"{t}"' for t in terms)
    try:
        cur = conn.execute(
            """
            SELECT source_id, title, tribunal, numero_processo, relator, data_julgamento, path,
                   snippet(sources_fts, 6, '[', ']', '...', 24) AS trecho,
                   bm25(sources_fts) AS score
            FROM sources_fts
            WHERE sources_fts MATCH ?
            ORDER BY score
            LIMIT ?
            """,
            (fts_query, limit),
        )
        rows = [dict(zip([c[0] for c in cur.description], row)) for row in cur.fetchall()]
        for row in rows:
            row["revisao"] = _review_state(root / row["path"])
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Índice temático de fontes do cérebro-ricar (FTS5/BM25)")
    parser.add_argument("--cerebro", type=Path, default=DEFAULT_CEREBRO_ROOT)
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("reindex", help="reconstrói o índice inteiro a partir de wiki/sources/*.md")

    index_one_parser = commands.add_parser("index-one", help="indexa um único arquivo de fonte")
    index_one_parser.add_argument("path", type=Path)

    search = commands.add_parser("buscar", help="busca por tema/termo nas fontes indexadas")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=5)

    args = parser.parse_args()
    if args.command == "reindex":
        result = reindex(args.cerebro)
    elif args.command == "index-one":
        result = index_one(args.path, args.cerebro)
    else:
        result = buscar(args.query, args.limit, args.cerebro)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
