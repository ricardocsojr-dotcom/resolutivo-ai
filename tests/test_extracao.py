"""Testes de services/extracao.py -- extração determinística de anexos.

Gera fixtures PDF/imagem em runtime via PyMuPDF/Pillow (sem depender de
arquivos versionados) para cobrir os três caminhos: texto nativo, OCR de
PDF escaneado e OCR de imagem solta.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf
import pytest
from PIL import Image, ImageDraw

from services.extracao import (
    ExtractionError,
    extrair_anexo,
    gerar_intake_md,
)


def _pdf_texto_nativo(caminho: Path, texto: str) -> None:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), texto)
    doc.save(str(caminho))
    doc.close()


def _imagem_com_texto(caminho: Path, texto: str) -> None:
    img = Image.new("RGB", (600, 200), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 80), texto, fill="black")
    img.save(caminho)


def test_extrai_pdf_com_texto_nativo(tmp_path):
    pdf_path = tmp_path / "peticao.pdf"
    _pdf_texto_nativo(pdf_path, "Texto de teste nativo do PDF.")

    resultado = extrair_anexo(pdf_path)

    assert resultado.erro is None
    assert len(resultado.paginas) == 1
    assert resultado.paginas[0].metodo == "texto_nativo"
    assert "Texto de teste nativo" in resultado.paginas[0].texto


def test_extrai_imagem_via_ocr(tmp_path):
    img_path = tmp_path / "ar_scan.png"
    _imagem_com_texto(img_path, "RECEBIDO")

    resultado = extrair_anexo(img_path)

    assert resultado.erro is None
    assert len(resultado.paginas) == 1
    assert resultado.paginas[0].metodo == "ocr"


def test_extensao_nao_suportada_registra_erro(tmp_path):
    arquivo = tmp_path / "planilha.xlsx"
    arquivo.write_text("nao e um anexo valido", encoding="utf-8")

    resultado = extrair_anexo(arquivo)

    assert resultado.erro is not None
    assert "não suportada" in resultado.erro


def test_gerar_intake_md_sem_anexos_produz_arquivo_explicito(tmp_path):
    output = tmp_path / "packages" / "intake.md"

    result = gerar_intake_md("MAT-01", [], output_path=output)

    assert result["status"] == "SKIPPED"
    assert output.is_file()
    assert "Nenhum anexo fornecido" in output.read_text(encoding="utf-8")


def test_gerar_intake_md_com_anexo_valido(tmp_path):
    pdf_path = tmp_path / "citacao.pdf"
    _pdf_texto_nativo(pdf_path, "Certidão de citação.")
    output = tmp_path / "packages" / "intake.md"

    result = gerar_intake_md("MAT-01", [pdf_path], output_path=output)

    assert result["status"] == "OK"
    conteudo = output.read_text(encoding="utf-8")
    assert "# Intake -- MAT-01" in conteudo
    assert "Certidão de citação" in conteudo
    assert result["documentos"][0]["metodo"] == "texto_nativo"


def test_gerar_intake_md_todos_anexos_falham_levanta_erro(tmp_path):
    arquivo_invalido = tmp_path / "arquivo.docx"
    arquivo_invalido.write_text("nao suportado", encoding="utf-8")
    output = tmp_path / "packages" / "intake.md"

    with pytest.raises(ExtractionError):
        gerar_intake_md("MAT-01", [arquivo_invalido], output_path=output)

    # Fail-safe: não deve deixar um intake.md parcial/corrompido no lugar
    assert not output.is_file()


def test_gerar_intake_md_falha_parcial_nao_bloqueia(tmp_path):
    pdf_ok = tmp_path / "ok.pdf"
    _pdf_texto_nativo(pdf_ok, "Documento válido.")
    arquivo_ruim = tmp_path / "ruim.docx"
    arquivo_ruim.write_text("invalido", encoding="utf-8")
    output = tmp_path / "packages" / "intake.md"

    result = gerar_intake_md("MAT-01", [pdf_ok, arquivo_ruim], output_path=output)

    assert result["status"] == "PARTIAL"
    assert output.is_file()
