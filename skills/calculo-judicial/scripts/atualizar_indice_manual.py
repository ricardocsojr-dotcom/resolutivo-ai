#!/usr/bin/env python3
"""Atualiza um CSV de índice local a partir de um arquivo enviado manualmente
(sem API oficial disponível — ex.: TJRJ). Mesma regra de segurança do
atualizar_indice_bcb.py: nunca sobrescreve um valor já existente que
divirja, só adiciona data nova.

Formato esperado do arquivo de entrada: CSV com colunas data,valor
(mesmo formato dos arquivos em referencias/indices/).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path


class AtualizacaoError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def erro(code: str, message: str) -> AtualizacaoError:
    return AtualizacaoError(code, message)


def ler_csv(path: Path) -> dict[date, Decimal]:
    registros: dict[date, Decimal] = {}
    if not path.is_file():
        return registros
    with path.open(encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            registros[date.fromisoformat(linha["data"])] = Decimal(linha["valor"])
    return registros


def atualizar(indice: str, csv_path: Path, novo_arquivo: Path) -> tuple[int, int]:
    existentes = ler_csv(csv_path)
    novos = ler_csv(novo_arquivo)
    if not novos:
        raise erro("arquivo_novo_vazio", f"{novo_arquivo} não tem registros data,valor.")
    adicionados = 0
    repetidos_iguais = 0
    for dt, valor in novos.items():
        if dt not in existentes:
            existentes[dt] = valor
            adicionados += 1
        elif existentes[dt] == valor:
            repetidos_iguais += 1
        else:
            raise erro(
                "valor_divergente",
                f"{indice} em {dt.isoformat()}: local tem {existentes[dt]}, arquivo novo tem {valor}. "
                "Não sobrescrevo — confira manualmente qual está certo.",
            )
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["data", "valor"])
        for dt in sorted(existentes):
            w.writerow([dt.isoformat(), format(existentes[dt], "f")])
    return adicionados, repetidos_iguais


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--indice", required=True)
    p.add_argument("--csv", required=True, type=Path, help="CSV local do índice (será atualizado)")
    p.add_argument("--arquivo-novo", required=True, type=Path, help="CSV com os registros novos, formato data,valor")
    args = p.parse_args(argv)
    try:
        adicionados, repetidos = atualizar(args.indice, args.csv, args.arquivo_novo)
        print(json.dumps({
            "status": "ok", "indice": args.indice,
            "linhas_adicionadas": adicionados, "linhas_ja_identicas": repetidos,
        }, ensure_ascii=False))
        return 0
    except AtualizacaoError as exc:
        print(json.dumps({"status": "erro", "codigo": exc.code, "mensagem": exc.message}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
