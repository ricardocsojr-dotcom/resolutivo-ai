"""Integração do recorte de decisão anotado com estado e DOCX."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "skills" / "formatar-peca" / "scripts"
REVIEW_DIR = ROOT / "skills" / "revisor-rdaa" / "scripts"
sys.path.insert(0, str(BUILD_DIR))
sys.path.insert(0, str(REVIEW_DIR))

from anotar_decisao import annotate_decision  # noqa: E402
from construir_peca import construir_peca  # noqa: E402
from estado_rdaa import persist_context  # noqa: E402
from verificar_visual_law import verify_visual_law  # noqa: E402
PUBLISH = ROOT / "skills" / "revisor-rdaa" / "scripts" / "publicar_docx.py"


def test_decision_annotation_round_trip() -> None:
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        source = folder / "decision.png"
        annotated = folder / "decision-annotated.png"
        manifest_path = folder / "decision-annotated.json"
        Image.new("RGB", (400, 300), "white").save(source)
        manifest = annotate_decision({
            "source_path": str(source),
            "source_kind": "image",
            "rectangles": [{"id": "DEC-1", "x": 50, "y": 60, "width": 200, "height": 80}],
            "output_path": str(annotated),
            "manifest_path": str(manifest_path),
            "texto_pesquisavel": "Trecho literal da decisão fornecido.",
            "legenda": "Trecho destacado, página 1.",
            "source_ids": ["SRC-DEC-1"],
            "semantic_ids": ["DEC-1"],
        })
        context = json.loads((ROOT / "tests" / "fixtures" / "context_happy.json").read_text(encoding="utf-8"))
        context["numero_processo"] = "8888888-88.8888.8.88.8888"
        context["blocos"].append({
            "tipo": "decisao_anotada",
            "image_path": str(annotated),
            "annotation_manifest": str(manifest_path),
            "source_path": str(source),
            "source_sha256": manifest["source_sha256"],
            "pagina": 1,
            "legenda": "Trecho destacado, página 1.",
            "texto_pesquisavel": "Trecho literal da decisão fornecido.",
            "source_ids": ["SRC-DEC-1"],
            "semantic_ids": ["DEC-1"],
        })
        output = folder / "piece.docx"
        construir_peca(context, output)
        report = verify_visual_law(output, context)
        assert report["status"] == "PASS", report
        state_dir = folder / "state"
        persisted = persist_context(state_dir, context, output=output)
        state = json.loads(persisted["paths"]["state"].read_text(encoding="utf-8"))
        block = [item for item in state["semantic_blocks"] if item.get("tipo") == "decisao_anotada"]
        assert block and block[0]["page"] == 1
        provenance = (state_dir / "provenance.jsonl").read_text(encoding="utf-8")
        assert "decisao_anotada" in provenance

        context_path = folder / "context.json"
        context_path.write_text(json.dumps(context, ensure_ascii=False), encoding="utf-8")
        candidate = folder / "candidate.docx"
        final = folder / "final.docx"
        construir_peca(context, candidate)
        published = subprocess.run(
            [sys.executable, str(PUBLISH), "--input", str(candidate), "--output", str(final), "--context", str(context_path)],
            text=True, capture_output=True,
        )
        assert published.returncode == 0, published.stdout + published.stderr
        previous = final.read_bytes()
        Image.open(annotated).save(annotated, format="PNG", compress_level=0)
        construir_peca(context, candidate)
        blocked = subprocess.run(
            [sys.executable, str(PUBLISH), "--input", str(candidate), "--output", str(final), "--context", str(context_path)],
            text=True, capture_output=True,
        )
        assert blocked.returncode == 1, blocked.stdout + blocked.stderr
        assert final.read_bytes() == previous


if __name__ == "__main__":
    test_decision_annotation_round_trip()
    print("[OK] decisão anotada, provenance e DOCX passaram")
