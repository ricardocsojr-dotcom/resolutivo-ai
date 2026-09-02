#!/usr/bin/env python3
"""Recorta e anota páginas de decisões sem alterar o original."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

try:
    from pdf2image import convert_from_path
except ImportError:  # pragma: no cover
    convert_from_path = None

try:
    import pypdfium2 as pdfium
except ImportError:  # pragma: no cover
    pdfium = None

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None


HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        Path(temp_name).replace(path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def _atomic_image(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower() or ".png"
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.stem}.", suffix=suffix, dir=path.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        image.save(temp_path, format="JPEG" if suffix in {".jpg", ".jpeg"} else "PNG")
        temp_path.replace(path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def _as_number(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} deve ser número inteiro")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} deve ser número inteiro") from exc
    if number != float(value):
        raise ValueError(f"{label} deve ser número inteiro")
    return number


def _rect(values: list[Any] | tuple[Any, ...], label: str) -> tuple[int, int, int, int]:
    if len(values) != 4:
        raise ValueError(f"{label} deve ter [x, y, largura, altura]")
    return tuple(_as_number(value, f"{label}[{index}]") for index, value in enumerate(values))  # type: ignore[return-value]


def _load_page(source: Path, source_kind: str, page: int, dpi: int) -> Image.Image:
    if not source.is_file():
        raise FileNotFoundError(f"Fonte não encontrada: {source}")
    kind = source_kind.lower()
    if kind == "pdf" or source.suffix.lower() == ".pdf":
        if page < 1:
            raise ValueError("page deve ser maior ou igual a 1")
        if convert_from_path is not None:
            pages = convert_from_path(str(source), dpi=dpi, first_page=page, last_page=page)
            if not pages:
                raise ValueError(f"Página inválida ou não renderizada: {page}")
            return pages[0].convert("RGB")
        elif pdfium is not None:
            doc = pdfium.PdfDocument(str(source))
            try:
                if page > len(doc):
                    raise ValueError(f"Página inválida: {page} excede {len(doc)}")
                pdf_page = doc[page - 1]
                return pdf_page.render(scale=dpi / 72).to_pil().convert("RGB")
            finally:
                doc.close()
        elif fitz is not None:
            doc = fitz.open(str(source))
            try:
                if page > len(doc):
                    raise ValueError(f"Página inválida: {page} excede {len(doc)}")
                pdf_page = doc[page - 1]
                pix = pdf_page.get_pixmap(dpi=dpi)
                return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            finally:
                doc.close()
        else:
            raise RuntimeError("Nenhum renderizador de PDF disponível (pdf2image, pypdfium2 ou PyMuPDF).")
    if page != 1:
        raise ValueError("imagem não-PDF aceita somente page=1")
    return Image.open(source).convert("RGB")


def _calculate_auto_crop_from_rectangles(rectangles: list[dict[str, Any]], source_width: int, source_height: int, margin_px: int = 20) -> tuple[int, int, int, int]:
    """Calcula a bounding box dos retângulos com margem, retornando crop [x, y, largura, altura].
    
    Estratégia: encontrar o mínimo e máximo x/y dos retângulos, expandir by `margin_px`
    em todas as direções (clampado aos limites da página), e retornar [x, y, w, h].
    
    Args:
        rectangles: lista de dicts com 'x', 'y', 'width', 'height'
        source_width, source_height: dimensões da página original
        margin_px: margem (pixels) ao redor da bbox (default 20)
    
    Returns:
        (crop_x, crop_y, crop_w, crop_h)
    """
    if not rectangles:
        return (0, 0, source_width, source_height)
    
    # Encontrar bounding box de todos os retângulos
    min_x = min(r["x"] for r in rectangles)
    min_y = min(r["y"] for r in rectangles)
    max_x = max(r["x"] + r["width"] for r in rectangles)
    max_y = max(r["y"] + r["height"] for r in rectangles)
    
    # Expandir com margem
    crop_x = max(0, min_x - margin_px)
    crop_y = max(0, min_y - margin_px)
    crop_right = min(source_width, max_x + margin_px)
    crop_bottom = min(source_height, max_y + margin_px)
    
    crop_w = crop_right - crop_x
    crop_h = crop_bottom - crop_y
    
    return (crop_x, crop_y, crop_w, crop_h)


def annotate_decision(spec: dict[str, Any]) -> dict[str, Any]:
    raw_source = str(spec.get("source_path") or "").strip()
    raw_output = str(spec.get("output_path") or "").strip()
    if not raw_source:
        raise ValueError("source_path é obrigatório")
    if not raw_output:
        raise ValueError("output_path é obrigatório")
    source = Path(raw_source).expanduser()
    output = Path(raw_output).expanduser()
    if source.resolve() == output.resolve():
        raise ValueError("a saída deve ser diferente da fonte original")
    source_kind = str(spec.get("source_kind") or "").lower()
    page = _as_number(spec.get("page", 1), "page")
    dpi = _as_number(spec.get("render_dpi", 180), "render_dpi")
    if dpi <= 0:
        raise ValueError("render_dpi deve ser positivo")

    image = _load_page(source, source_kind, page, dpi)
    source_width, source_height = image.size
    crop_value = spec.get("crop")
    
    # Processar retângulos ANTES de calcular o crop (para auto-crop funcionar)
    rectangles = spec.get("rectangles")
    if not isinstance(rectangles, list) or not rectangles:
        raise ValueError("rectangles deve ser uma lista não vazia")
    seen_ids: set[str] = set()
    normalized = []
    for index, item in enumerate(rectangles, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"rectangles[{index}] deve ser objeto")
        rect_id = str(item.get("id") or "").strip()
        if not rect_id or rect_id in seen_ids:
            raise ValueError(f"rectangles[{index}] deve ter ID único")
        seen_ids.add(rect_id)
        x, y, width, height = _rect([item.get("x"), item.get("y"), item.get("width"), item.get("height")], f"rectangles[{index}]")
        if width <= 0 or height <= 0 or x < 0 or y < 0 or x + width > source_width or y + height > source_height:
            raise ValueError(f"retângulo fora dos limites da página: {rect_id}")
        color = str(item.get("stroke_color") or "#FF0000")
        if not HEX_COLOR.fullmatch(color):
            raise ValueError(f"cor inválida no retângulo {rect_id}: use #RRGGBB")
        stroke = _as_number(item.get("stroke_px", 3), f"rectangles[{index}].stroke_px")
        if stroke <= 0 or stroke > 20:
            raise ValueError(f"espessura inválida no retângulo {rect_id}")
        normalized.append({
            "id": rect_id,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "stroke_color": color.upper(),
            "stroke_px": stroke,
            "label": item.get("label"),
        })
    
    # Determinar crop (pode ser manual ou auto a partir dos retângulos)
    if crop_value == "auto":
        crop = _calculate_auto_crop_from_rectangles(normalized, source_width, source_height, margin_px=20)
    elif crop_value is not None:
        crop = _rect(crop_value, "crop")
    else:
        crop = (0, 0, source_width, source_height)
    
    crop_x, crop_y, crop_w, crop_h = crop
    if crop_w <= 0 or crop_h <= 0 or crop_x < 0 or crop_y < 0 or crop_x + crop_w > source_width or crop_y + crop_h > source_height:
        raise ValueError("crop fora dos limites da página ou com dimensões inválidas")

    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    for item in normalized:
        draw.rectangle(
            (item["x"], item["y"], item["x"] + item["width"], item["y"] + item["height"]),
            outline=item["stroke_color"],
            width=item["stroke_px"],
        )
    final_image = annotated.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
    output.parent.mkdir(parents=True, exist_ok=True)
    _atomic_image(final_image, output)
    manifest_path = Path(str(spec.get("manifest_path") or output.with_suffix(".json")))
    final_rectangles = []
    for item in normalized:
        final_rectangles.append({
            **item,
            "x": item["x"] - crop_x,
            "y": item["y"] - crop_y,
        })
    manifest = {
        "schema_version": "1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_path": str(source),
        "source_sha256": _sha256(source),
        "source_kind": source_kind or ("pdf" if source.suffix.lower() == ".pdf" else "image"),
        "page": page,
        "render_dpi": dpi,
        "source_dimensions": {"width": source_width, "height": source_height},
        "crop": {"x": crop_x, "y": crop_y, "width": crop_w, "height": crop_h},
        "rectangles_original": normalized,
        "rectangles_output": final_rectangles,
        "output_path": str(output),
        "output_sha256": _sha256(output),
        "legenda": spec.get("legenda"),
        "texto_pesquisavel": spec.get("texto_pesquisavel"),
        "source_ids": spec.get("source_ids", []),
        "semantic_ids": spec.get("semantic_ids", []),
    }
    _atomic_json(manifest_path, manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Recortar e anotar decisão com retângulos vermelhos transparentes")
    parser.add_argument("--spec", type=Path, required=True, help="JSON do contrato de recorte")
    args = parser.parse_args()
    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        result = annotate_decision(spec)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERRO] {exc}", file=os.sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
