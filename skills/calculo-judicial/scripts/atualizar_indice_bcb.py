#!/usr/bin/env python3
"""Busca uma série mensal do SGS/Banco Central e escreve/estende o CSV local
no formato data,valor (decimal, não percentual) que a skill usa.

Não altera manifesto nem promove índice — só atualiza o arquivo de dados.
Aprovação continua exigindo caso dourado, como qualquer outra fonte.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.request
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

SERIES_BCB = {
    "selic": 4390,
    "cdi": 4391,
    "ipca": 433,
    "inpc": 188,
    "igp-m": 189,
    # poupança tem uma linha por dia de aniversário do depósito, não por mês —
    # a série já vem assim do BCB, então o restante do script (data + valor)
    # funciona sem alteração. Confirmado sem perda de precisão em 2026-08-27
    # (% do BCB com 4 casas bate exato com o decimal local de 6 casas).
    "poupanca-nova": 195,
}


class AtualizacaoError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def erro(code: str, message: str) -> AtualizacaoError:
    return AtualizacaoError(code, message)


def buscar_serie(codigo: int, data_inicial: date, data_final: date) -> list[tuple[date, Decimal]]:
    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
        f"?dataInicial={data_inicial:%d/%m/%Y}&dataFinal={data_final:%d/%m/%Y}&formato=json"
    )
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # rede indisponível, série inexistente, etc.
        raise erro("bcb_indisponivel", f"Falha ao consultar BCB SGS {codigo}: {exc}") from exc
    if not isinstance(payload, list):
        raise erro("resposta_invalida", f"Resposta inesperada do BCB para série {codigo}.")
    registros = []
    for item in payload:
        dt = datetime.strptime(item["data"], "%d/%m/%Y").date()
        valor = Decimal(item["valor"]) / Decimal(100)  # BCB publica em % ; CSV local guarda decimal
        registros.append((dt, valor))
    return sorted(registros)


def atualizar_csv(indice: str, csv_path: Path, novos: list[tuple[date, Decimal]]) -> int:
    existentes: dict[date, Decimal] = {}
    if csv_path.is_file():
        with csv_path.open(encoding="utf-8") as f:
            for linha in csv.DictReader(f):
                existentes[date.fromisoformat(linha["data"])] = Decimal(linha["valor"])
    adicionados = 0
    for dt, valor in novos:
        if dt not in existentes:
            existentes[dt] = valor
            adicionados += 1
        elif existentes[dt] != valor:
            raise erro(
                "valor_divergente",
                f"{indice} em {dt.isoformat()}: local tem {existentes[dt]}, BCB tem {valor}. "
                "Não sobrescrevo silenciosamente — confira manualmente.",
            )
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["data", "valor"])
        for dt in sorted(existentes):
            w.writerow([dt.isoformat(), format(existentes[dt], "f")])
    return adicionados


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--indice", required=True, choices=sorted(SERIES_BCB))
    p.add_argument("--csv", required=True, type=Path)
    p.add_argument("--data-inicial", required=True, help="AAAA-MM-DD")
    p.add_argument("--data-final", default=date.today().isoformat(), help="AAAA-MM-DD (padrão: hoje)")
    args = p.parse_args(argv)
    try:
        codigo = SERIES_BCB[args.indice]
        di = date.fromisoformat(args.data_inicial)
        df = date.fromisoformat(args.data_final)
        registros = buscar_serie(codigo, di, df)
        adicionados = atualizar_csv(args.indice, args.csv, registros)
        print(json.dumps({
            "status": "ok", "indice": args.indice, "serie_bcb": codigo,
            "registros_consultados": len(registros), "linhas_adicionadas": adicionados,
        }, ensure_ascii=False))
        return 0
    except AtualizacaoError as exc:
        print(json.dumps({"status": "erro", "codigo": exc.code, "mensagem": exc.message}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
