"""Testes unitários do compilador Markdown -> RDAA e do iterador rápido."""

import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
MD2RDAA = ROOT / "skills" / "formatar-peca" / "scripts" / "md2rdaa.py"
ITERAR = ROOT / "scripts" / "iterar_peca.py"
CONSTRUIR = ROOT / "skills" / "formatar-peca" / "scripts" / "construir_peca.py"


def test_md2rdaa_compila_peticao_completa(tmp_path):
    md_text = """AO JUÍZO DA 14ª VARA CÍVEL E EMPRESARIAL DE BELÉM/PA

Processo: 0879903-83.2025.8.14.0301
Autora: TRIVALE ADMINISTRAÇÃO LTDA.
Ré: EQUATORIAL PARÁ DISTRIBUIDORA DE ENERGIA S.A.

TRIVALE ADMINISTRAÇÃO LTDA., já qualificada nos autos, por seus advogados que esta subscrevem, vem, respeitosamente, à presença de Vossa Excelência, com fundamento no CPC, art. 357, § 1º, formular PEDIDO DE ESCLARECIMENTOS, pelas razões a seguir expostas.

# I. OBJETO DA MANIFESTAÇÃO

1. A presente manifestação visa ao aperfeiçoamento da decisão saneadora.

## 1.1. Pontos Controvertidos

2. Os pontos controvertidos devem ser delimitados de forma objetiva.

# VIII. PEDIDOS

Diante do exposto, a Autora requer:

a) o acolhimento dos esclarecimentos;
b) a delimitação dos fatos controvertidos;
c) a exibição de documentos pela Ré.

Requer que as publicações referentes a este feito sejam realizadas exclusivamente em nome do advogado Wanderley Romano Donadel, OAB/MG 78.870.

Nestes termos, aguarda deferimento.

Belém/PA, 8 de setembro de 2026.
"""
    input_md = tmp_path / "minuta.md"
    output_json = tmp_path / "contexto.json"
    input_md.write_text(md_text, encoding="utf-8")

    res = subprocess.run(
        [sys.executable, str(MD2RDAA), str(input_md), "--output", str(output_json), "--nivel", "B"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stderr + res.stdout
    assert output_json.is_file()

    ctx = json.loads(output_json.read_text(encoding="utf-8"))
    
    # 1. Endereçamento normalizado para fórmula solene
    assert ctx["enderecamento"].startswith("EXCELENTÍSSIMO")
    assert "14ª VARA CÍVEL E EMPRESARIAL" in ctx["enderecamento"]
    assert "BELÉM/PA" in ctx["enderecamento"]

    # 2. Local e data padronizados em Uberlândia/MG
    assert ctx["data_local"].startswith("Uberlândia/MG")

    # 3. Número do processo e partes
    assert ctx["numero_processo"] == "0879903-83.2025.8.14.0301"
    assert "TRIVALE ADMINISTRAÇÃO LTDA." in ctx["partes"]

    # 4. Blocos compilados
    tipos = [b["tipo"] for b in ctx["blocos"]]
    assert "abertura" in tipos
    assert "titulo" in tipos
    assert "titulo2" in tipos
    assert "numerado" in tipos
    assert "alinea" in tipos
    assert "assinaturas" in tipos

    # 5. Constrói DOCX diretamente a partir do JSON compilado
    docx_out = tmp_path / "peca.docx"
    res_build = subprocess.run(
        [sys.executable, str(CONSTRUIR), "--context", str(output_json), "--output", str(docx_out)],
        capture_output=True,
        text=True,
    )
    assert res_build.returncode == 0, res_build.stderr + res_build.stdout
    assert docx_out.is_file()


def test_md2rdaa_nao_inventa_metadados_de_outro_caso(tmp_path):
    input_md = tmp_path / "minuta.md"
    output_json = tmp_path / "contexto.json"
    input_md.write_text("# MANIFESTAÇÃO\n\n1. Texto demonstrativo.", encoding="utf-8")

    res = subprocess.run(
        [sys.executable, str(MD2RDAA), str(input_md), "--output", str(output_json), "--nivel", "B"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stderr + res.stdout
    ctx = json.loads(output_json.read_text(encoding="utf-8"))
    assert ctx["numero_processo"] == ""
    assert ctx["partes"] == ""
    assert ctx["publicacoes_texto"] == ""
    assert ctx["enderecamento"] == "[ENDEREÇAMENTO A CONFERIR]"


def test_md2rdaa_preserva_paragrafos_numerados_e_separa_alineas_de_pedidos(tmp_path):
    input_md = tmp_path / "minuta_pedidos.md"
    output_json = tmp_path / "contexto_pedidos.json"
    texto = """EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA 1ª VARA CÍVEL

Processo: 1000000-00.2026.8.13.0000
Autora: EMPRESA TESTE LTDA.
Réu: PARTE CONTRÁRIA

EMPRESA TESTE LTDA., já qualificada nos autos, vem requerer a juntada de documentos, pelas razões a seguir expostas.

# I. PRELIMINAR

1. O primeiro parágrafo do corpo traz fundamentação fática com requerer no corpo.
2. O segundo parágrafo traz fundamentação jurídica com citação legal.

# II. PEDIDOS

3. Diante do exposto, a Autora requer:
a) o deferimento do pedido principal;
b) a juntada dos documentos anexos.

Requer que as publicações referentes a este feito sejam realizadas exclusivamente em nome do advogado WANDERLEY ROMANO DONADEL, OAB/MG 78.870, sob pena de nulidade.

Nestes termos, aguarda deferimento.

Uberlândia/MG, 14 de setembro de 2026.
"""
    input_md.write_text(texto, encoding="utf-8")

    res = subprocess.run(
        [sys.executable, str(MD2RDAA), str(input_md), "--output", str(output_json), "--nivel", "C"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stderr + res.stdout
    ctx = json.loads(output_json.read_text(encoding="utf-8"))

    blocos = ctx["blocos"]
    numerados = [b for b in blocos if b.get("tipo") == "numerado"]
    alineas = [b for b in blocos if b.get("tipo") == "alinea"]

    # Parágrafos 1 e 2 do corpo devem ser numerados, NÃO alíneas
    assert len(numerados) >= 3
    assert "primeiro parágrafo do corpo" in numerados[0]["texto"]
    assert "segundo parágrafo" in numerados[1]["texto"]
    assert numerados[2]["texto"].endswith("requer:")

    # Alíneas devem conter somente os itens a) e b)
    assert len(alineas) == 2
    assert "o deferimento" in alineas[0]["texto"]
    assert "a juntada" in alineas[1]["texto"]

    # Publicações devem ser capturadas no metadado e não nos blocos do corpo
    assert "WANDERLEY ROMANO DONADEL" in ctx["publicacoes_texto"]
    assert "sob pena de nulidade" in ctx["publicacoes_texto"]

