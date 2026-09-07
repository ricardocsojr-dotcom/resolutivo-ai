"""
Testa se o gerador nativo RDAA (construir_peca.py) configura w:lang em pt-BR
no nível de documento base (docDefaults), no estilo Normal e em settings.xml.
"""

import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "formatar-peca" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from construir_peca import construir_peca  # noqa: E402

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def test_construir_peca_configura_idioma_pt_br():
    context = {
        "peca": "Manifestação",
        "tribunal": "TJSP",
        "comarca": "São Paulo",
        "vara": "1ª Vara Cível",
        "numero_processo": "1000000-00.2026.8.26.0100",
        "partes": "Autora: Empresa Alfa\nRéu: Banco Beta",
        "blocos": [
            {"tipo": "titulo", "texto": "I. DOS FATOS"},
            {"tipo": "paragrafo", "texto": "Manifestação regular com termos em língua portuguesa."},
        ],
    }

    with tempfile.TemporaryDirectory(prefix="rdaa-test-lang-") as tmpdir:
        out_path = Path(tmpdir) / "peca_teste_idioma.docx"
        construir_peca(context, str(out_path))

        assert out_path.is_file()

        with zipfile.ZipFile(out_path) as z:
            # 1. Verifica styles.xml -> docDefaults -> rPrDefault -> rPr -> lang
            styles_xml = z.read("word/styles.xml")
            root_styles = ET.fromstring(styles_xml)

            doc_defaults = root_styles.find("w:docDefaults", NS)
            assert doc_defaults is not None, "w:docDefaults não encontrado em styles.xml"

            rpr_default = doc_defaults.find("w:rPrDefault/w:rPr", NS)
            assert rpr_default is not None, "w:rPrDefault/w:rPr não encontrado em styles.xml"

            lang_default = rpr_default.find("w:lang", NS)
            assert lang_default is not None, "w:lang não encontrado em docDefaults"
            assert lang_default.attrib.get(f"{{{NS['w']}}}val") == "pt-BR", (
                f"Idioma padrão em docDefaults esperado 'pt-BR', obteve: {lang_default.attrib}"
            )

            # 2. Verifica styles.xml -> style[styleId='Normal'] -> rPr -> lang
            normal_style = root_styles.find("w:style[@w:styleId='Normal']", NS)
            assert normal_style is not None, "Estilo Normal não encontrado em styles.xml"

            normal_lang = normal_style.find("w:rPr/w:lang", NS)
            assert normal_lang is not None, "w:lang não encontrado no estilo Normal"
            assert normal_lang.attrib.get(f"{{{NS['w']}}}val") == "pt-BR", (
                f"Idioma no estilo Normal esperado 'pt-BR', obteve: {normal_lang.attrib}"
            )

            # 3. Verifica settings.xml -> themeFontLang
            settings_xml = z.read("word/settings.xml")
            root_settings = ET.fromstring(settings_xml)

            theme_font_lang = root_settings.find("w:themeFontLang", NS)
            if theme_font_lang is not None:
                assert theme_font_lang.attrib.get(f"{{{NS['w']}}}val") == "pt-BR", (
                    f"themeFontLang esperado 'pt-BR', obteve: {theme_font_lang.attrib}"
                )
