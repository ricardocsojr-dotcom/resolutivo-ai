#!/usr/bin/env python3
"""Busca local instantânea de Súmulas e Jurisprudência em Teses (STJ, STF, Vinculantes).

Utiliza a base consolidada em dados-juridicos/ (extraída de fontes oficiais).
Permite busca direta por número ou busca temática por palavras-chave com retorno literal.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

DADOS_DIR = Path(__file__).resolve().parents[3] / "dados-juridicos"


def _carregar_json(nome_arquivo: str) -> dict[str, Any]:
    caminho = DADOS_DIR / nome_arquivo
    if not caminho.is_file():
        return {}
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def buscar_sumula(*, termo: str | None = None, numero: int | None = None, tribunal: str = "todos") -> list[dict[str, Any]]:
    resultados = []
    tribunal_norm = tribunal.lower().strip()

    # 1. Súmulas Vinculantes STF
    if tribunal_norm in ("todos", "vinculante", "sv", "stf"):
        data = _carregar_json("sumulas_vinculantes.json")
        sumulas = data.get("sumulas", {})
        for num_str, item in sumulas.items():
            try:
                n = int(num_str)
            except ValueError:
                continue
            if numero is not None and n != numero:
                continue
            enunciado = item.get("enunciado", "")
            if termo and termo.lower() not in enunciado.lower():
                continue
            resultados.append({
                "tipo": "Súmula Vinculante",
                "tribunal": "STF",
                "numero": n,
                "enunciado": enunciado,
                "status": item.get("status", "aprovada"),
                "url": item.get("url", "https://portal.stf.jus.br"),
            })

    # 2. Súmulas STJ
    if tribunal_norm in ("todos", "stj"):
        data = _carregar_json("sumulas_stj.json")
        sumulas = data.get("sumulas", {})
        for num_str, item in sumulas.items():
            try:
                n = int(num_str)
            except ValueError:
                continue
            if numero is not None and n != numero:
                continue
            enunciado = item.get("enunciado", "")
            tema = item.get("tema", "")
            area = item.get("area", "")
            texto_busca = f"{enunciado} {tema} {area}".lower()
            if termo and termo.lower() not in texto_busca:
                continue
            resultados.append({
                "tipo": "Súmula",
                "tribunal": "STJ",
                "numero": n,
                "enunciado": enunciado,
                "status": item.get("status", "ativa"),
                "area": area,
                "tema": tema,
                "orgao": item.get("orgao", ""),
                "data": item.get("data", ""),
                "url": item.get("url", ""),
            })

    # 3. Súmulas STF
    if tribunal_norm in ("todos", "stf"):
        data = _carregar_json("sumulas_stf.json")
        sumulas = data.get("sumulas", {})
        for num_str, item in sumulas.items():
            try:
                n = int(num_str)
            except ValueError:
                continue
            if numero is not None and n != numero:
                continue
            enunciado = item.get("enunciado", "")
            if termo and termo.lower() not in enunciado.lower():
                continue
            resultados.append({
                "tipo": "Súmula",
                "tribunal": "STF",
                "numero": n,
                "enunciado": enunciado,
                "status": item.get("status", "ativa"),
                "url": item.get("url", ""),
            })

    return resultados


def main() -> int:
    parser = argparse.ArgumentParser(description="Busca local de súmulas do STF e STJ")
    parser.add_argument("termo", nargs="?", help="termo de busca por assunto")
    parser.add_argument("--numero", "-n", type=int, help="número da súmula")
    parser.add_argument("--tribunal", "-t", choices=["todos", "stj", "stf", "vinculante"], default="todos")
    parser.add_argument("--limit", "-l", type=int, default=10)
    args = parser.parse_args()

    if not args.termo and args.numero is None:
        parser.print_help()
        return 1

    itens = buscar_sumula(termo=args.termo, numero=args.numero, tribunal=args.tribunal)
    itens = itens[:args.limit]
    print(json.dumps(itens, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
