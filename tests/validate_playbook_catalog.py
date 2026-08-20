"""Validação determinística do catálogo local de modelos do playbook RDAA."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "skills" / "esqueleto-peca" / "references" / "catalogo-modelos.json"
EXPECTED_TYPES = {
    "contestacao",
    "agravo_instrumento",
    "agravo_recurso_especial",
    "agravo_interno",
    "apelação",
    "cumprimento_sentenca",
    "impugnacao_cumprimento",
    "impugnacao_contestacao",
    "impugnacao_embargos",
    "impugnacao_penhora",
    "manifestacao",
    "memoriais",
    "execucao",
    "contrarrazoes_resp",
    "contrarrazoes",
    "embargos_declaracao",
    "oposicao",
}
REQUIRED_MODEL_KEYS = {
    "modelo_id",
    "nome",
    "versao",
    "tipo_peca",
    "niveis_recomendados",
    "modo",
    "blocos",
    "variaveis",
    "dependencias",
    "recursos_visuais",
    "provenance",
    "checklist_minimo",
    "documentos_esperados",
}
VALID_LEVELS = {"A", "B", "C"}
VALID_MODES = {"referencia", "estrutura_orientadora", "molde_controlado"}


def fail(message: str) -> None:
    raise AssertionError(message)


def validate_model(model: dict[str, Any]) -> None:
    missing = REQUIRED_MODEL_KEYS - set(model)
    if missing:
        fail(f"modelo {model.get('modelo_id', '<sem id>')} sem campos {sorted(missing)}")
    if not isinstance(model["modelo_id"], str) or not model["modelo_id"].endswith("-v1"):
        fail(f"modelo_id inválido {model.get('modelo_id')}")
    if model["versao"] != 1:
        fail(f"versão inesperada em {model['modelo_id']}")
    if model["tipo_peca"] not in EXPECTED_TYPES:
        fail(f"tipo de peça não coberto {model['tipo_peca']}")
    if not set(model["niveis_recomendados"]).issubset(VALID_LEVELS):
        fail(f"nível inválido em {model['modelo_id']}")
    if model["modo"] not in VALID_MODES:
        fail(f"modo inválido em {model['modelo_id']}")
    if not isinstance(model["blocos"], list):
        fail(f"blocos não é lista em {model['modelo_id']}")
    if "C" in model["niveis_recomendados"] and model["blocos"]:
        fail(f"tipo C recebeu redação por blocos em {model['modelo_id']}")
    if not model["checklist_minimo"]:
        fail(f"checklist vazio em {model['modelo_id']}")
    if not model["documentos_esperados"]:
        fail(f"documentos esperados ausentes em {model['modelo_id']}")
    block_ids: set[str] = set()
    for block in model["blocos"]:
        if set(block) != {"id", "funcao", "obrigatorio"}:
            fail(f"bloco fora do contrato em {model['modelo_id']}: {block}")
        if block["id"] in block_ids:
            fail(f"bloco duplicado em {model['modelo_id']}: {block['id']}")
        block_ids.add(block["id"])
        if not isinstance(block["obrigatorio"], bool):
            fail(f"obrigatorio não booleano em {model['modelo_id']}")
    var_ids: set[str] = set()
    for variable in model["variaveis"]:
        if not {"id", "obrigatoria", "origem"}.issubset(variable):
            fail(f"variável fora do contrato em {model['modelo_id']}: {variable}")
        if variable["id"] in var_ids:
            fail(f"variável duplicada em {model['modelo_id']}: {variable['id']}")
        var_ids.add(variable["id"])
    provenance = model["provenance"]
    if provenance.get("origem") != "modelo_local" or provenance.get("versao") != 1:
        fail(f"provenance inválida em {model['modelo_id']}")


def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    if catalog.get("schema_version") != "1":
        fail("schema_version inesperado")
    models = catalog.get("modelos")
    if not isinstance(models, list) or len(models) != len(EXPECTED_TYPES):
        fail(f"quantidade de modelos inesperada {len(models) if isinstance(models, list) else models}")
    ids: set[str] = set()
    types: set[str] = set()
    for model in models:
        validate_model(model)
        if model["modelo_id"] in ids:
            fail(f"modelo_id duplicado {model['modelo_id']}")
        ids.add(model["modelo_id"])
        types.add(model["tipo_peca"])
    if types != EXPECTED_TYPES:
        fail(f"famílias divergentes. Esperadas {sorted(EXPECTED_TYPES)}. Obtidas {sorted(types)}")
    print(f"[OK] catálogo do playbook validado com {len(models)} famílias")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
