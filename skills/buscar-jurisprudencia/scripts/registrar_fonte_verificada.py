#!/usr/bin/env python3
"""Registra fonte de jurisprudência verificada no cérebro-ricar imediatamente.

Desacoplado de publicação de peça e de domínio/conceito. Uma ementa conferida
literalmente contra o site do tribunal é conhecimento válido por si só,
independente do destino da matéria em que foi buscada (a matéria pode travar,
pausar ou nunca publicar — a ementa já verificada não deveria evaporar junto).

Uso típico: chamado pela skill buscar-jurisprudencia/jusbrasil-jurisprudencia
assim que uma ementa é confirmada, antes mesmo do esqueleto estar pronto.

Complementar a `estudo-juridico-rdaa/scripts/registrar_estudo_cerebro.py`
(que cria concept+source+domain ao fim de um estudo publicado). Este script
cobre o caso mais comum e mais urgente: só a fonte, só quando confirmada,
sem esperar o resto do pipeline.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

DEFAULT_CEREBRO_ROOT = Path(os.environ.get("RDAA_CEREBRO_PATH", r"C:\Users\ricar\cerebro-ricar"))
_PREC_PATTERN = re.compile(r"prec-(\d+)\.md$", re.IGNORECASE)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _review_due(review_days: int) -> str:
    """Data em que a fonte exige nova conferência de entendimento atual."""
    if review_days < 1:
        raise ValueError("review_days deve ser maior ou igual a 1")
    return (datetime.now(timezone.utc) + timedelta(days=review_days)).date().isoformat()


def _proximo_prec_id(sources_dir: Path) -> str:
    maior = 0
    if sources_dir.is_dir():
        for path in sources_dir.glob("prec-*.md"):
            match = _PREC_PATTERN.search(path.name)
            if match:
                maior = max(maior, int(match.group(1)))
    return f"PREC-{maior + 1:03d}"


def registrar_fonte_verificada(
    *,
    ementa_literal: str,
    tribunal: str,
    numero_processo: str,
    relator: str,
    data_julgamento: str,
    url: str,
    tema: str,
    matter_id: str | None = None,
    source_id: str | None = None,
    review_days: int = 365,
    cerebro_root: Path | str = DEFAULT_CEREBRO_ROOT,
) -> dict[str, Any]:
    """Grava PREC-NNN.md com a ementa literal, já indexada para busca temática.

    Não exige domínio nem conceito — vinculação a domain/concept continua
    sendo feita depois, por `registrar_estudo_cerebro.py`, se e quando a
    matéria virar estudo/peça publicada. Aqui o objetivo é não perder a
    verificação feita, mesmo que o resto do pipeline nunca conclua.
    """
    root = Path(cerebro_root).resolve()
    sources_dir = root / "wiki" / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)

    prec_id = (source_id or _proximo_prec_id(sources_dir)).strip()
    if not re.fullmatch(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*", prec_id):
        raise ValueError(f"source_id inválido: {prec_id!r}")

    path = sources_dir / f"{prec_id.lower()}.md"
    if path.is_file():
        raise ValueError(f"fonte já existe, use outro id: {path}")

    registered_at = _now()
    review_due = _review_due(review_days)
    frontmatter = (
        "---\n"
        "type: source\n"
        f"title: \"{prec_id}\"\n"
        f"court: {tribunal}\n"
        f"date: {data_julgamento}\n"
        "origin: buscar-jurisprudencia\n"
        f"created: {registered_at}\n"
        f"verified_at: {registered_at}\n"
        f"review_interval_days: {review_days}\n"
        f"review_due: {review_due}\n"
        "review_status: vigente\n"
        "status: verificada_externamente\n"
        "---\n"
    )
    corpo = (
        f"# {prec_id} — {tribunal}\n\n"
        f"- **Tribunal:** {tribunal}\n"
        f"- **Número do processo:** {numero_processo}\n"
        f"- **Relator:** {relator}\n"
        f"- **Data:** {data_julgamento}\n"
        f"- **Tema:** {tema}\n\n"
        "## Ementa literal\n\n"
        f"> {ementa_literal}\n\n"
        f"Disponível em: {url}\n"
    )
    if matter_id:
        corpo += f"\n## Origem (proveniência)\n- Matéria: {matter_id}\n- Registrado antes de publicação: sim\n"

    path.write_text(frontmatter + "\n" + corpo, encoding="utf-8")

    indexado = False
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from indexador_fontes import index_one

        index_one(path, root)
        indexado = True
    except Exception:
        pass

    return {
        "success": True,
        "source_id": prec_id,
        "path": str(path),
        "indexed": indexado,
        "review_due": review_due,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Registra fonte de jurisprudência verificada, imediatamente após confirmação"
    )
    parser.add_argument("--cerebro", type=Path, default=DEFAULT_CEREBRO_ROOT)
    parser.add_argument("--ementa-literal", required=True)
    parser.add_argument("--tribunal", required=True)
    parser.add_argument("--numero-processo", required=True)
    parser.add_argument("--relator", required=True)
    parser.add_argument("--data-julgamento", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--tema", required=True, help="tema/tese para facilitar busca futura, ex: 'art. 49 §3º LFRE'")
    parser.add_argument("--matter-id")
    parser.add_argument("--source-id", help="PREC-NNN explícito; se omitido, aloca o próximo disponível")
    parser.add_argument(
        "--review-days", type=int, default=365,
        help="prazo para nova conferência de vigência (padrão: 365 dias)",
    )

    args = parser.parse_args()
    result = registrar_fonte_verificada(
        ementa_literal=args.ementa_literal,
        tribunal=args.tribunal,
        numero_processo=args.numero_processo,
        relator=args.relator,
        data_julgamento=args.data_julgamento,
        url=args.url,
        tema=args.tema,
        matter_id=args.matter_id,
        source_id=args.source_id,
        review_days=args.review_days,
        cerebro_root=args.cerebro,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
