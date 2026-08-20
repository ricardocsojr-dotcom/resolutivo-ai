#!/usr/bin/env python3
"""Regressões das extensões integradas a partir das skills anexadas."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def texto(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def main():
    flavia = texto("skills/estilo-flavia-rdaa/SKILL.md")
    converter = texto("skills/converter-arquivo-grande/SKILL.md")
    previsao = texto("skills/previsao-condenacao-rdaa/SKILL.md")
    catalogo = texto("skills/revisor-rdaa/references/catalogo-skills-externas.md")
    storytelling = texto("skills/legal-design-rdaa/references/data-storytelling-rdaa.md")

    assert "estilo_alvo: flavia" in flavia
    assert "não publica" in flavia
    assert "não consulta nem grava o vault automaticamente" in flavia
    assert "sem travessão ou meio-travessão em títulos" in flavia

    assert "Não instale pacotes" in converter
    assert "pip install" not in converter
    assert "não instalar automaticamente" in converter
    assert "aguarde autorização explícita" in converter

    assert "modo: previsao_condenacao" in previsao
    assert "não infere risco" in previsao.casefold()
    assert "Nenhuma consulta ou gravação no vault ocorre automaticamente" in previsao
    assert "não publica DOCX" in previsao

    assert "estilo-flavia-rdaa" in catalogo
    assert "converter-arquivo-grande" in catalogo
    assert "previsao-condenacao-rdaa" in catalogo
    assert "Data Storytelling RDAA" in storytelling
    assert "tipo C" in storytelling

    script = ROOT / "skills/previsao-condenacao-rdaa/scripts/liquidar_pedidos.py"
    result = subprocess.run(
        [sys.executable, str(script), "--demo"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "demo() ok" in result.stdout
    print("PASS test_extensoes_anexadas")


if __name__ == "__main__":
    main()
