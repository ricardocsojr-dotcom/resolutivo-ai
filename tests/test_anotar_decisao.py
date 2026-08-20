"""Regressões do recorte e anotação de decisões."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
import sys

from PIL import Image
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "formatar-peca" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from anotar_decisao import annotate_decision  # noqa: E402


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_crop_rectangles_manifest_and_original_preservation() -> None:
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        source = folder / "decisao.png"
        output = folder / "decisao-anotada.png"
        image = Image.new("RGB", (800, 600), "white")
        image.save(source)
        original_hash = _hash(source)
        manifest = annotate_decision({
            "source_path": str(source),
            "source_kind": "image",
            "page": 1,
            "crop": [100, 50, 500, 400],
            "rectangles": [{"id": "R-1", "x": 150, "y": 100, "width": 200, "height": 80}],
            "output_path": str(output),
            "legenda": "Trecho destacado.",
            "texto_pesquisavel": "Trecho literal fornecido.",
            "source_ids": ["SRC-1"],
        })
        assert output.exists()
        assert _hash(source) == original_hash
        assert Image.open(output).size == (500, 400)
        assert manifest["rectangles_output"][0]["x"] == 50
        assert manifest["rectangles_output"][0]["y"] == 50
        annotated = Image.open(output).convert("RGB")
        assert annotated.getpixel((50, 50)) == (255, 0, 0)
        assert annotated.getpixel((150, 90)) == (255, 255, 255)
        assert manifest["output_sha256"] == _hash(output)


def test_pdf_page_selection_and_annotation() -> None:
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        source = folder / "decision.pdf"
        output = folder / "decision-page-2.png"
        pdf = canvas.Canvas(str(source), pagesize=(400, 300))
        pdf.drawString(40, 250, "Página 1")
        pdf.showPage()
        pdf.drawString(40, 250, "Página 2")
        pdf.save()
        manifest = annotate_decision({
            "source_path": str(source),
            "source_kind": "pdf",
            "page": 2,
            "render_dpi": 72,
            "rectangles": [{"id": "PDF-R-1", "x": 30, "y": 30, "width": 160, "height": 30}],
            "output_path": str(output),
            "texto_pesquisavel": "Página 2 — trecho fornecido.",
        })
        assert output.exists()
        assert manifest["page"] == 2
        assert manifest["source_kind"] == "pdf"
        assert Image.open(output).size[0] == 400


def test_invalid_geometry_and_missing_output_are_rejected() -> None:
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp) / "decisao.png"
        Image.new("RGB", (100, 100), "white").save(source)
        base = {
            "source_path": str(source),
            "source_kind": "image",
            "rectangles": [{"id": "R-1", "x": 90, "y": 90, "width": 20, "height": 20}],
            "output_path": str(Path(temp) / "out.png"),
        }
        try:
            annotate_decision(base)
        except ValueError as exc:
            assert "limites" in str(exc)
        else:
            raise AssertionError("retângulo fora da página deveria falhar")

        missing_output = dict(base)
        missing_output.pop("output_path")
        try:
            annotate_decision(missing_output)
        except ValueError as exc:
            assert "output_path" in str(exc)
        else:
            raise AssertionError("output ausente deveria falhar")


def main() -> int:
    test_crop_rectangles_manifest_and_original_preservation()
    test_pdf_page_selection_and_annotation()
    test_invalid_geometry_and_missing_output_are_rejected()
    print("[OK] recorte, retângulo transparente, manifesto e preservação passaram")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
