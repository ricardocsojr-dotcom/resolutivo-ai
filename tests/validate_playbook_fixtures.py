"""Valida a seleção dos modelos do playbook contra fixtures locais C, B e A."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "skills" / "esqueleto-peca" / "references" / "catalogo-modelos.json"
FIXTURES = ROOT / "tests" / "fixtures"
SCRIPT_DIR = ROOT / "skills" / "revisor-rdaa" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from classificacao_peca import validate_piece_contract  # noqa: E402

CASES = {
    "C": ("context_validacao_C.json", "manifestacao-v1", "direta", False),
    "B": ("context_validacao_B.json", "contestacao-v1", "blocos", True),
    "A": ("context_validacao_A.json", "apelacao-v1", "blocos", True),
}


def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    models = {model["modelo_id"]: model for model in catalog["modelos"]}
    for level, (filename, model_id, mode, blocks) in CASES.items():
        context: dict[str, Any] = json.loads((FIXTURES / filename).read_text(encoding="utf-8"))
        model = models[model_id]
        context["modelo_estrutura"] = {
            "modelo_id": model["modelo_id"],
            "versao": model["versao"],
            "niveis_recomendados": model["niveis_recomendados"],
        }
        context["modo_redacao"] = mode
        context["redacao_por_blocos"] = blocks
        report = validate_piece_contract(context)
        if report["status"] != "PASS":
            raise AssertionError(f"fixture {level} rejeitada: {report}")
        if report["nivel_peca"] != level:
            raise AssertionError(f"fixture {level} retornou nível {report['nivel_peca']}")
    print("[OK] fixtures C, B e A selecionam modelos compatíveis com o playbook")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
