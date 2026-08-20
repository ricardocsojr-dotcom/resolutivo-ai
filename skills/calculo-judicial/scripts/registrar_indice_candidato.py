#!/usr/bin/env python3
"""Prepara um índice local candidato sem modificar o manifesto aprovado.

O script não baixa arquivos, não consulta APIs, não altera a tabela oficial e não
promove o índice para aprovado. Ele apenas valida a estrutura mínima do CSV,
calcula o SHA-256 e grava um pacote JSON de proveniência para revisão humana.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


SERIES_TYPES = {
    "taxa_mensal_percentual",
    "taxa_diaria_decimal",
    "fator_acumulado",
    "taxa_aniversario_percentual",
    "numero_indice",
    "outro",
}
FREQUENCIES = {"mensal", "diaria", "por_aniversario", "outra"}


class CandidateError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def error(code: str, message: str) -> CandidateError:
    return CandidateError(code, message)


def read_csv(path: Path) -> tuple[bytes, list[tuple[date, Decimal]]]:
    if not path.is_file():
        raise error("arquivo_inexistente", f"Arquivo CSV não encontrado: {path}.")
    raw = path.read_bytes()
    digest_text = raw.decode("utf-8-sig")
    reader = csv.DictReader(digest_text.splitlines())
    if reader.fieldnames != ["data", "valor"]:
        raise error("cabecalho_invalido", "O CSV deve conter exatamente o cabeçalho data,valor.")
    rows: list[tuple[date, Decimal]] = []
    previous: date | None = None
    seen: set[date] = set()
    for line_number, record in enumerate(reader, start=2):
        if set(record) != {"data", "valor"}:
            raise error("colunas_invalidadas", f"Linha {line_number} contém colunas inesperadas.")
        raw_date = record.get("data")
        raw_value = record.get("valor")
        if not isinstance(raw_date, str) or not raw_date.strip():
            raise error("data_ausente", f"Data ausente na linha {line_number}.")
        try:
            record_date = date.fromisoformat(raw_date.strip())
        except ValueError as exc:
            raise error("data_invalida", f"Data inválida na linha {line_number}: {raw_date!r}.") from exc
        if record_date in seen:
            raise error("data_duplicada", f"Data duplicada na linha {line_number}: {record_date.isoformat()}.")
        if previous is not None and record_date <= previous:
            raise error("datas_fora_de_ordem", f"Datas fora de ordem na linha {line_number}.")
        try:
            value = Decimal(str(raw_value).strip())
        except (InvalidOperation, ValueError) as exc:
            raise error("valor_invalido", f"Valor inválido na linha {line_number}.") from exc
        if not value.is_finite():
            raise error("valor_nao_finito", f"Valor não finito na linha {line_number}.")
        rows.append((record_date, value))
        seen.add(record_date)
        previous = record_date
    if not rows:
        raise error("csv_vazio", "O CSV não possui registros.")
    return raw, rows


def build_candidate(args: argparse.Namespace) -> dict[str, Any]:
    if args.tipo_serie not in SERIES_TYPES:
        raise error("tipo_serie_invalido", f"Tipo de série não suportado no cadastro: {args.tipo_serie}.")
    if args.frequencia not in FREQUENCIES:
        raise error("frequencia_invalida", f"Frequência não suportada no cadastro: {args.frequencia}.")
    raw, rows = read_csv(args.csv)
    digest = hashlib.sha256(raw).hexdigest()
    first_date, last_date = rows[0][0], rows[-1][0]
    values = [value for _, value in rows]
    return {
        "schema_version": "1",
        "status": "candidato",
        "indice": args.indice,
        "definicao_proposta": {
            "arquivo": args.csv.name,
            "tipo_serie": args.tipo_serie,
            "unidade": args.unidade,
            "frequencia": args.frequencia,
            "convencoes": args.convencao,
        },
        "proveniencia": {
            "autoridade_primaria": args.autoridade,
            "url": args.url,
            "codigo_serie": args.codigo_serie,
            "arquivo_bruto": args.arquivo_bruto,
            "data_coleta": args.data_coleta,
            "observacoes": args.observacao,
        },
        "integridade": {
            "sha256_csv": digest,
            "registros": len(rows),
            "cobertura_inicio": first_date.isoformat(),
            "cobertura_fim": last_date.isoformat(),
            "valor_minimo": format(min(values), "f"),
            "valor_maximo": format(max(values), "f"),
        },
        "bloqueio": "Não altera o manifesto. Exige caso dourado e aprovação explícita.",
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Preparar índice local candidato para revisão")
    p.add_argument("--csv", required=True, type=Path)
    p.add_argument("--indice", required=True)
    p.add_argument("--tipo-serie", required=True, choices=sorted(SERIES_TYPES))
    p.add_argument("--unidade", required=True)
    p.add_argument("--frequencia", required=True, choices=sorted(FREQUENCIES))
    p.add_argument("--convencao", action="append", required=True)
    p.add_argument("--autoridade", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--codigo-serie", default="")
    p.add_argument("--arquivo-bruto", default="")
    p.add_argument("--data-coleta", default="")
    p.add_argument("--observacao", default="")
    p.add_argument("--output", required=True, type=Path)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        candidate = build_candidate(args)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "ok", "saida": str(args.output), "sha256_csv": candidate["integridade"]["sha256_csv"]}, ensure_ascii=False))
        return 0
    except CandidateError as exc:
        print(json.dumps({"status": "erro", "codigo": exc.code, "mensagem": exc.message}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
