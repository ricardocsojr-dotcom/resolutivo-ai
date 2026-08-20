"""Regressões da proibição de travessão e dois pontos nos títulos."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import zipfile
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "formatar-peca" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from construir_peca import construir_peca, validar_contexto  # noqa: E402
from verificar_formatacao import checar  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "context_happy.json"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def _context() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_generator_rejects_all_title_fields() -> None:
    cases = [
        ({"tipo": "titulo", "texto": "DOS FATOS: SÍNTESE"}, "titulo"),
        ({"tipo": "titulo2", "texto": "Da questão — central"}, "titulo2"),
        ({"tipo": "titulo3", "texto": "PROVA – DOCUMENTAL"}, "titulo3"),
        ({"tipo": "inicio_razoes", "titulo_razoes": "RAZÕES: DO RECURSO"}, "titulo_razoes"),
    ]
    for block, label in cases:
        context = _context()
        context["blocos"] = [block]
        try:
            validar_contexto(context)
        except ValueError as exc:
            assert label in str(exc)
            assert "caractere proibido" in str(exc)
        else:
            raise AssertionError(f"{label} inválido passou pela validação")


def _mutate_title(source: Path, destination: Path, target: str, suffix: str) -> None:
    with zipfile.ZipFile(source) as zin, zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "word/document.xml":
                root = etree.fromstring(data)
                changed = False
                for paragraph in root.findall(".//w:body/w:p", NS):
                    text = "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))
                    if target in text:
                        text_node = paragraph.findall(".//w:t", NS)[-1]
                        text_node.text = (text_node.text or "") + suffix
                        changed = True
                        break
                assert changed, f"título não encontrado no DOCX: {target}"
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            zout.writestr(info, data)


def test_structural_verifier_rejects_adultered_titles() -> None:
    with tempfile.TemporaryDirectory(prefix="rdaa-title-guard-") as temp:
        folder = Path(temp)
        context = _context()
        context["blocos"] = [
            {"tipo": "abertura", "nome_parte": "JOÃO DA SILVA", "resto": ", vem manifestar-se."},
            {"tipo": "titulo", "texto": "DA SÍNTESE NECESSÁRIA"},
            {"tipo": "titulo2", "texto": "Da questão central"},
            {"tipo": "titulo3", "texto": "PROVA DOCUMENTAL"},
            {"tipo": "paragrafo", "texto": "A parte apresenta os fundamentos."},
            {"tipo": "assinaturas"},
        ]
        valid = folder / "valid.docx"
        construir_peca(context, valid)

        colon = folder / "colon.docx"
        _mutate_title(valid, colon, "DA SÍNTESE NECESSÁRIA", ":")
        colon_findings = checar(colon)
        assert any("dois-pontos proibido" in finding for finding in colon_findings)

        dash = folder / "dash.docx"
        _mutate_title(valid, dash, "Da questão central", " — complemento")
        dash_findings = checar(dash)
        assert any("travessão proibido" in finding for finding in dash_findings)


def test_valid_titles_remain_accepted() -> None:
    context = _context()
    validar_contexto(context)


if __name__ == "__main__":
    test_generator_rejects_all_title_fields()
    test_structural_verifier_rejects_adultered_titles()
    test_valid_titles_remain_accepted()
    print("[OK] títulos sem travessão e dois pontos passaram")
