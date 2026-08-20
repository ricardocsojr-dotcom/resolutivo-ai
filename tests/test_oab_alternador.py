"""Regressões do alternador explícito de OAB e dos hyperlinks de e-mail."""

from __future__ import annotations

import importlib.util
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "formatar-peca" / "scripts" / "construir_peca.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("rdaa_construir_peca_oab_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_MISSING = object()


def _context(uf=_MISSING):
    context = {
        "blocos": [],
        "publicacoes": False,
        "fecho": "Nestes termos, aguarda deferimento.",
        "assinatura_automatica_final": True,
    }
    if uf is not _MISSING:
        context["uf_processo_originario"] = uf
    return context


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


def _texts_from_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    return " ".join(
        node.text or ""
        for node in root.iter(f"{{{W}}}t")
    )


def _hyperlink_records(path: Path) -> list[dict[str, str | None]]:
    with zipfile.ZipFile(path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        rels = ET.fromstring(archive.read("word/_rels/document.xml.rels"))

    targets = {
        item.attrib["Id"]: item.attrib.get("Target")
        for item in rels.findall(f"{{{PKG_REL}}}Relationship")
    }
    records = []
    for hyperlink in document.iter(f"{{{W}}}hyperlink"):
        rid = hyperlink.attrib.get(f"{{{R}}}id")
        run = hyperlink.find(f"{{{W}}}r")
        assert run is not None
        text = "".join(node.text or "" for node in run.iter(f"{{{W}}}t"))
        color = run.find(f"{{{W}}}rPr/{{{W}}}color")
        underline = run.find(f"{{{W}}}rPr/{{{W}}}u")
        records.append(
            {
                "text": text,
                "target": targets.get(rid),
                "color": color.attrib.get(f"{{{W}}}val") if color is not None else None,
                "underline": underline.attrib.get(f"{{{W}}}val") if underline is not None else None,
            }
        )
    return records


def test_oab_by_valid_uf_and_state_name() -> None:
    builder = _load_builder()
    go = builder._signatarios_para_contexto(_context("GO"))
    assert go[0][1] == "OAB/GO 18.703-A"

    go_name = builder._signatarios_para_contexto(_context("Goiás"))
    assert go_name[0][1] == "OAB/GO 18.703-A"

    sp = builder._signatarios_para_contexto(_context("SP"))
    assert sp[0][1] == "OAB/SP 422.887-A"
    assert sp[1][1] == "OAB/SP 548.105"


def test_default_mg_is_preserved_without_declared_uf() -> None:
    builder = _load_builder()
    selected = builder._signatarios_para_contexto(_context())
    assert selected[0][1] == "OAB/MG 78.870"
    assert selected[1][1] == "OAB/MG 96.919"


def test_unknown_uf_blocks_validation_and_generation() -> None:
    builder = _load_builder()
    context = _context("XX")
    try:
        builder.validar_contexto(context)
    except ValueError as exc:
        assert "sem cadastro de OAB" in str(exc)
    else:
        raise AssertionError("UF não cadastrada deveria bloquear a validação")

    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp) / "nao-deve-gerar.docx"
        try:
            builder.construir_peca(context, str(output))
        except ValueError:
            assert not output.exists()
        else:
            raise AssertionError("UF não cadastrada não poderia gerar DOCX")


def test_docx_contains_mailto_hyperlinks_with_blue_underline() -> None:
    builder = _load_builder()
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp) / "peca-oab-sp.docx"
        builder.construir_peca(_context("SP"), str(output))
        text = _texts_from_docx(output)
        records = _hyperlink_records(output)

    assert "OAB/SP 422.887-A" in text
    assert "OAB/SP 548.105" in text
    emails = {record["text"]: record for record in records if record["target"]}
    assert emails["wanderley@romanodonadel.com.br"]["target"] == "mailto:wanderley@romanodonadel.com.br"
    assert emails["wanderley@romanodonadel.com.br"]["color"] == "0563C1"
    assert emails["wanderley@romanodonadel.com.br"]["underline"] == "single"
    assert len(emails) == 4


def main() -> None:
    test_oab_by_valid_uf_and_state_name()
    test_default_mg_is_preserved_without_declared_uf()
    test_unknown_uf_blocks_validation_and_generation()
    test_docx_contains_mailto_hyperlinks_with_blue_underline()
    print("PASS test_oab_alternador")


if __name__ == "__main__":
    main()
