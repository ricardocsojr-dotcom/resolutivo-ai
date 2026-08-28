#!/usr/bin/env python3
"""Converte um relatório de mapeamento de acervo (formato do relatório de
importação de peças) numa planilha CSV editável, pra Ricardo aprovar/corrigir
cliente, tipo e ID de cada matéria antes de qualquer criação em massa de
pasta em Resolutivo-Dados.

Não cria nenhuma pasta, não copia nenhum arquivo — só lê o relatório e
escreve o CSV. A importação de fato é um passo posterior, separado, que lê
a planilha já revisada por Ricardo.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any

CABECALHO = re.compile(r"^#{3,5} (?:[\d.]+ )?(?:Workspace|Matéria): `(.*)`\s*$")
CONFIANCA = re.compile(r"Grau de Confiança\*\*:\s*(Alto|Médio|Baixo)")
CLASSIFICACAO = re.compile(r"Classifica(?:ção Resolutivo-Dados|ção Sugerida)\*\*:\s*`(.*)`")
TIPO_MATERIA = re.compile(r"Tipo de Matéria\*\*:\s*([^|\n]+)")
PECA_PRINCIPAL = re.compile(r"Peça Principal(?: Escolhida)?\*\*:\s*`(.*)`")
TOTAL_ARQUIVOS = re.compile(r"Total de Arquivos\*\*:\s*(\d+)")
ALERTA = re.compile(r"\*?\[PONTO A CONFERIR\]\*?\s*(.*)")
TAMANHO = re.compile(r"\(([\d.]+)\s*(KB|MB)\)")

CONFIANCA_MAP = {"Alto": "alta", "Médio": "media", "Baixo": "baixa"}

CAMPOS = [
    "origem",
    "cliente_sugerido",
    "confianca",
    "tipo_sugerido",
    "id_sugerido",
    "tipo_de_peca",
    "peca_principal",
    "total_arquivos",
    "maior_anexo_mb",
    "alertas_do_relatorio",
    "importar",
    "cliente_final",
    "tipo_final",
    "id_final",
    "observacoes",
]


def maior_tamanho_mb(bloco: str) -> str:
    tamanhos_mb = []
    for valor, unidade in TAMANHO.findall(bloco):
        mb = float(valor) / 1024 if unidade == "KB" else float(valor)
        tamanhos_mb.append(mb)
    return f"{max(tamanhos_mb):.2f}" if tamanhos_mb else ""


def dividir_blocos(texto: str) -> list[str]:
    linhas = texto.splitlines()
    indices = [i for i, linha in enumerate(linhas) if CABECALHO.match(linha)]
    blocos = []
    for pos, inicio in enumerate(indices):
        fim = indices[pos + 1] if pos + 1 < len(indices) else len(linhas)
        blocos.append("\n".join(linhas[inicio:fim]))
    return blocos


def parse_classificacao(valor: str | None) -> tuple[str, str, str]:
    if not valor:
        return "", "", ""
    partes = [p.strip() for p in valor.split(" > ")]
    if len(partes) == 3:
        return partes[0], partes[1], partes[2]
    return valor, "", ""


def parse_bloco(bloco: str) -> dict[str, Any]:
    origem = CABECALHO.match(bloco.splitlines()[0]).group(1)
    classificacao = CLASSIFICACAO.search(bloco)
    cliente, tipo, id_ = parse_classificacao(classificacao.group(1) if classificacao else None)
    confianca = CONFIANCA.search(bloco)
    tipo_materia = TIPO_MATERIA.search(bloco)
    peca = PECA_PRINCIPAL.search(bloco)
    total = TOTAL_ARQUIVOS.search(bloco)
    alertas = "; ".join(m.group(1).strip() for m in ALERTA.finditer(bloco))

    return {
        "origem": origem,
        "cliente_sugerido": cliente,
        "confianca": CONFIANCA_MAP.get(confianca.group(1), "") if confianca else "",
        "tipo_sugerido": tipo,
        "id_sugerido": id_,
        "tipo_de_peca": tipo_materia.group(1).strip() if tipo_materia else "",
        "peca_principal": peca.group(1) if peca else "",
        "total_arquivos": total.group(1) if total else "",
        "maior_anexo_mb": maior_tamanho_mb(bloco),
        "alertas_do_relatorio": alertas,
        "importar": "",
        "cliente_final": cliente,
        "tipo_final": tipo,
        "id_final": id_,
        "observacoes": "",
    }


def gerar_planilha(relatorio: Path, saida: Path) -> int:
    texto = relatorio.read_text(encoding="utf-8")
    blocos = dividir_blocos(texto)
    linhas = [parse_bloco(b) for b in blocos]
    with saida.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS)
        writer.writeheader()
        writer.writerows(linhas)
    return len(linhas)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--relatorio", required=True, type=Path)
    p.add_argument("--saida", required=True, type=Path)
    args = p.parse_args(argv)

    if not args.relatorio.is_file():
        print(f"Relatório não encontrado: {args.relatorio}", file=sys.stderr)
        return 1

    total = gerar_planilha(args.relatorio, args.saida)
    print(f"{total} linhas escritas em {args.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
