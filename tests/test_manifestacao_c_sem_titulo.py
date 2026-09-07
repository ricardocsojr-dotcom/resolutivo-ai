"""Regressão do gate estrutural para manifestação C sem títulos."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "formatar-peca" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from construir_peca import construir_peca  # noqa: E402
from verificar_formatacao import checar  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "context_happy.json"


def test_structural_verifier_accepts_simple_manifestation_without_titles() -> None:
    context = json.loads(FIXTURE.read_text(encoding="utf-8"))
    context["blocos"] = [
        {
            "tipo": "abertura",
            "nome_parte": "COOPERATIVA AGROPECUÁRIA LTDA. DE UBERLÂNDIA – CALU",
            "resto": ", já qualificada nos autos, vem apresentar ",
            "nome_peca": "DESISTÊNCIA",
            "resto_depois": ".",
        },
        {"tipo": "numerado", "texto": "A embargante requer a homologação da desistência."},
    ]

    with tempfile.TemporaryDirectory(prefix="rdaa-manifestacao-c-") as temp:
        document = Path(temp) / "manifestacao.docx"
        construir_peca(context, document)
        findings = checar(document)

    assert not any("nenhum título encontrado" in finding for finding in findings)
