#!/usr/bin/env python3
"""
Converte linhas extraídas de uma tabela (parcelas/custas/principal/deduções/honorários)
para o formato CSV "perfil":

    data,valor,tipo,histórico,mostraTipo,t,correção,juros,dtJuros

Uso:
    Passe um JSON (lista de objetos) via stdin, um objeto por linha da tabela original.
    Cada objeto deve ter as chaves (todas como string, exatamente como veio da tabela):
        - data       (ex: "14/06/2014" ou já "2014-06-14")
        - valor      (ex: "1.804,00" ou já "1804.00")
        - tipo       (ex: "Principal", "Custas", "Deduções", "Honorários" — copiado literal)
        - historico  (copiado literal, com acentos/maiúsculas/hífen)
        - correcao   ("S" ou "N", qualquer caixa)
        - juros      ("S" ou "N", qualquer caixa)
        - dtJuros    (data igual a `data`, ou "" se não houver)

    Imprime em stdout as linhas CSV já prontas (sem cabeçalho), uma por linha.
    Se alguma linha tiver dado inconsistente, o script para e reporta o problema em
    stderr com o índice da linha, para que o erro seja mostrado ao usuário em vez de
    ser silenciosamente "adivinhado".
"""
import sys
import json
import re
import csv
import io

DATE_BR = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")
DATE_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


def normalize_date(raw: str, field_name: str, row_idx: int) -> str:
    raw = (raw or "").strip()
    if not raw:
        return ""
    m = DATE_BR.match(raw)
    if m:
        d, mo, y = m.groups()
        return f"{y}-{mo}-{d}"
    if DATE_ISO.match(raw):
        return raw
    raise ValueError(
        f"linha {row_idx}: campo '{field_name}' com data em formato não reconhecido: {raw!r} "
        "(esperado DD/MM/YYYY ou YYYY-MM-DD)"
    )


def normalize_valor(raw: str, row_idx: int) -> str:
    original = raw
    s = (raw or "").strip()
    s = s.replace("R$", "").strip()
    if not s:
        raise ValueError(f"linha {row_idx}: campo 'valor' vazio")
    if "," in s:
        # formato brasileiro: ponto = milhar, vírgula = decimal
        s = s.replace(".", "").replace(",", ".")
    try:
        val = float(s)
    except ValueError:
        raise ValueError(f"linha {row_idx}: valor não numérico: {original!r}")
    return f"{val:.2f}"


def normalize_flag(raw: str, field_name: str, row_idx: int) -> str:
    v = (raw or "").strip().upper()
    if v not in ("S", "N"):
        raise ValueError(
            f"linha {row_idx}: campo '{field_name}' deve ser 'S' ou 'N', veio {raw!r}"
        )
    return v


def convert_row(row: dict, row_idx: int) -> list:
    data = normalize_date(row.get("data", ""), "data", row_idx)
    valor = normalize_valor(row.get("valor", ""), row_idx)
    tipo = (row.get("tipo") or "").strip()
    historico = row.get("historico", "")
    correcao = normalize_flag(row.get("correcao", ""), "correcao", row_idx)
    juros = normalize_flag(row.get("juros", ""), "juros", row_idx)
    dt_juros = normalize_date(row.get("dtJuros", ""), "dtJuros", row_idx)

    if not tipo:
        raise ValueError(f"linha {row_idx}: campo 'tipo' vazio")

    # mostraTipo e t ficam sempre vazios
    return [data, valor, tipo, historico, "", "", correcao, juros, dt_juros]


def main():
    raw_input = sys.stdin.read()
    try:
        rows = json.loads(raw_input)
    except json.JSONDecodeError as e:
        print(f"ERRO: entrada não é um JSON válido: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(rows, list):
        print("ERRO: o JSON de entrada deve ser uma lista de objetos (uma por linha).", file=sys.stderr)
        sys.exit(1)

    out_lines = []
    errors = []
    for i, row in enumerate(rows, start=1):
        try:
            out_lines.append(convert_row(row, i))
        except ValueError as e:
            errors.append(str(e))

    if errors:
        print("Inconsistências encontradas:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    for line in out_lines:
        writer.writerow(line)

    sys.stdout.write(buf.getvalue())


if __name__ == "__main__":
    main()
