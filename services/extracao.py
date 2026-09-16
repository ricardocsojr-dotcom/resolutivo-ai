"""Extração determinística de anexos para Markdown -- motor RDAA V4.

Converte qualquer anexo de entrada (PDF nativo, PDF escaneado, imagem)
em um único ``packages/intake.md`` normalizado, ANTES de qualquer worker
de IA tocar no caso. Nenhuma etapa aqui decide conteúdo jurídico -- só
extrai texto de forma determinística e delega interpretação ao writer.

Estratégia (nesta ordem, por página):
1. PDF com camada de texto nativa -> extração direta via PyMuPDF (fitz).
   Não envolve OCR nem LLM.
2. PDF sem texto (escaneado) ou imagem solta -> renderiza em alta
   resolução e roda OCR local via Tesseract (pytesseract). Uma única
   passagem por página -- nunca fatiada em regiões, ao contrário do
   que era feito manualmente com vision_analyze.

Contrato de saída (packages/intake.md):

    # Intake -- <matter_id>

    ## Documento: <nome_arquivo>
    Páginas: N | Extração: texto_nativo | ocr | misto

    ### Página 1
    <texto>

    ...

Falha de extração de um anexo não derruba os demais -- registra erro
na seção do documento e segue. Falha total (nenhum anexo processável)
levanta ContractError para bloquear a fase seguinte (fail-safe).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import pymupdf as fitz  # PyMuPDF -- nome moderno, evita warning de depreciação em stdout
except ImportError:  # pragma: no cover
    fitz = None

try:
    import pytesseract
    from PIL import Image
except ImportError:  # pragma: no cover
    pytesseract = None
    Image = None


class ExtractionError(RuntimeError):
    """Falha ao extrair todos os anexos de uma matéria."""


# Resolução de renderização para OCR (DPI). 300 é o piso recomendado
# para OCR de documentos jurídicos escaneados sem perda de qualidade.
OCR_RENDER_DPI = 300

# Limiar mínimo de caracteres por página para considerar que o PDF tem
# camada de texto nativa aproveitável (abaixo disso, cai para OCR).
MIN_NATIVE_CHARS_PER_PAGE = 20


@dataclass
class PageResult:
    numero: int
    texto: str
    metodo: str  # "texto_nativo" | "ocr" | "erro"


@dataclass
class DocumentResult:
    nome_arquivo: str
    paginas: list[PageResult] = field(default_factory=list)
    erro: str | None = None

    @property
    def metodo_predominante(self) -> str:
        metodos = {p.metodo for p in self.paginas}
        if not metodos:
            return "erro"
        if metodos == {"texto_nativo"}:
            return "texto_nativo"
        if metodos == {"ocr"}:
            return "ocr"
        return "misto"


def _extrair_pdf(caminho: Path, use_ocr: bool = True) -> DocumentResult:
    if fitz is None:
        raise ExtractionError(
            "PyMuPDF (fitz) não está instalado -- extração de PDF indisponível"
        )

    doc = DocumentResult(nome_arquivo=caminho.name)
    try:
        pdf = fitz.open(str(caminho))
    except Exception as exc:  # noqa: BLE001
        doc.erro = f"falha ao abrir PDF: {exc}"
        return doc

    try:
        for i, page in enumerate(pdf, start=1):
            texto_nativo = page.get_text("text").strip()
            if len(texto_nativo) >= MIN_NATIVE_CHARS_PER_PAGE:
                doc.paginas.append(PageResult(i, texto_nativo, "texto_nativo"))
                continue

            # Sem texto nativo suficiente -> renderiza e faz OCR
            if not use_ocr:
                doc.paginas.append(PageResult(i, "[documento requer OCR, mas foi suprimido via opção]", "ocr_off"))
                continue

            texto_ocr = _ocr_pagina_pdf(page)
            doc.paginas.append(PageResult(i, texto_ocr, "ocr"))
    finally:
        pdf.close()

    return doc


def _ocr_pagina_pdf(page: Any) -> str:
    if pytesseract is None or Image is None:
        return "[OCR indisponível -- pytesseract/Pillow não instalados]"

    zoom = OCR_RENDER_DPI / 72  # fitz renderiza a 72 DPI por padrão
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    try:
        return pytesseract.image_to_string(img, lang="por").strip()
    except Exception as exc:  # noqa: BLE001
        return f"[erro OCR: {exc}]"


def _extrair_imagem(caminho: Path, use_ocr: bool = True) -> DocumentResult:
    doc = DocumentResult(nome_arquivo=caminho.name)
    if not use_ocr:
        doc.erro = "OCR suprimido (--no-ocr)"
        return doc
    if pytesseract is None or Image is None:
        doc.erro = "pytesseract/Pillow não instalados -- OCR de imagem indisponível"
        return doc

    try:
        img = Image.open(caminho)
        texto = pytesseract.image_to_string(img, lang="por").strip()
        doc.paginas.append(PageResult(1, texto, "ocr"))
    except Exception as exc:  # noqa: BLE001
        doc.erro = f"falha ao processar imagem: {exc}"

    return doc


EXTENSOES_PDF = {".pdf"}
EXTENSOES_IMAGEM = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def extrair_anexo(caminho: Path, use_ocr: bool = True) -> DocumentResult:
    """Extrai um único anexo (PDF ou imagem) para texto por página."""
    ext = caminho.suffix.lower()
    if ext in EXTENSOES_PDF:
        return _extrair_pdf(caminho, use_ocr=use_ocr)
    if ext in EXTENSOES_IMAGEM:
        return _extrair_imagem(caminho, use_ocr=use_ocr)
    doc = DocumentResult(nome_arquivo=caminho.name)
    doc.erro = f"extensão não suportada: {ext}"
    return doc


def _render_documento_md(doc: DocumentResult) -> str:
    linhas = [f"## Documento: {doc.nome_arquivo}"]
    if doc.erro:
        linhas.append(f"**Erro de extração:** {doc.erro}")
        linhas.append("")
        return "\n".join(linhas)

    linhas.append(
        f"Páginas: {len(doc.paginas)} | Extração: {doc.metodo_predominante}"
    )
    linhas.append("")
    for pagina in doc.paginas:
        linhas.append(f"### Página {pagina.numero}")
        linhas.append(pagina.texto if pagina.texto else "[página sem texto extraído]")
        linhas.append("")
    return "\n".join(linhas)


def gerar_intake_md(
    matter_id: str,
    anexos: list[Path],
    *,
    output_path: Path,
    use_ocr: bool = True,
) -> dict[str, Any]:
    """Extrai todos os anexos e grava packages/intake.md.

    Levanta ExtractionError se NENHUM anexo foi extraído com sucesso
    (fail-safe: bloqueia a fase seguinte em vez de deixar o writer
    trabalhar sem fatos).  Falhas parciais (alguns anexos falham, outros
    não) são registradas no próprio Markdown e não bloqueiam.
    """
    if not anexos:
        # Sem anexos é um caso válido (ex.: manifestação sem documento
        # novo) -- grava intake vazio e explícito, não é erro.
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            f"# Intake -- {matter_id}\n\n(Nenhum anexo fornecido nesta matéria.)\n",
            encoding="utf-8",
        )
        return {"status": "SKIPPED", "documentos": [], "output_path": str(output_path)}

    documentos = [extrair_anexo(Path(a), use_ocr=use_ocr) for a in anexos]
    sucesso = [d for d in documentos if not d.erro]

    if not sucesso:
        detalhes = "; ".join(f"{d.nome_arquivo}: {d.erro}" for d in documentos)
        raise ExtractionError(f"nenhum anexo pôde ser extraído -- {detalhes}")

    partes = [f"# Intake -- {matter_id}", ""]
    partes.extend(_render_documento_md(d) for d in documentos)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(partes), encoding="utf-8")

    return {
        "status": "OK" if len(sucesso) == len(documentos) else "PARTIAL",
        "documentos": [
            {
                "nome": d.nome_arquivo,
                "paginas": len(d.paginas),
                "metodo": d.metodo_predominante,
                "erro": d.erro,
            }
            for d in documentos
        ],
        "output_path": str(output_path),
    }
