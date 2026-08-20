"""Contrato determinístico dos tipos de peça do RDAA.

O módulo valida somente propriedades operacionais declaradas no contexto.
Não infere mérito, risco, pertinência, autenticidade ou validade jurídica.
"""

from __future__ import annotations

from typing import Any

NIVEIS_PECAS = ("A", "B", "C")
MODOS_REDACAO = {"direta", "blocos", "molde_controlado"}

NIVEL_CONFIG = {
    "A": {
        "nome": "premium",
        "descricao": "peça premium com todos os recursos aprovados para o caso",
        "redacao_por_blocos_permitida": True,
        "esqueleto_recomendado": True,
    },
    "B": {
        "nome": "desenvolvida",
        "descricao": "peça baseada no processo com desenvolvimento, explicação ou recurso visual melhor",
        "redacao_por_blocos_permitida": True,
        "esqueleto_recomendado": True,
    },
    "C": {
        "nome": "simples",
        "descricao": "peça muito simples, normalmente em parágrafos curtos",
        "redacao_por_blocos_permitida": False,
        "esqueleto_recomendado": False,
    },
}


def normalizar_nivel(value: Any) -> str | None:
    """Normalizar somente a declaração explícita do tipo da peça."""
    if value is None:
        return None
    normalized = str(value).strip().upper()
    return normalized or None


def _finding(code: str, message: str, *, severity: str = "erro") -> dict[str, str]:
    return {"id": code, "severity": severity, "message": message}


def validate_piece_contract(context: dict[str, Any]) -> dict[str, Any]:
    """Validar o contrato operacional declarado no contexto.

    Contextos legados sem ``nivel_peca`` são aceitos para preservar
    compatibilidade. O fluxo novo de ``redigir-peca`` deve declarar o campo.
    """
    if not isinstance(context, dict):
        return {
            "status": "BLOCK",
            "nivel_peca": None,
            "modo_redacao": None,
            "redacao_por_blocos": None,
            "findings": [_finding("nivel_peca_contexto_invalido", "O contexto da peça deve ser um objeto JSON.")],
        }

    nivel = normalizar_nivel(context.get("nivel_peca"))
    if nivel is None:
        return {
            "status": "SKIPPED",
            "nivel_peca": None,
            "modo_redacao": None,
            "redacao_por_blocos": None,
            "findings": [],
            "compatibilidade_legada": True,
        }

    findings: list[dict[str, str]] = []
    if nivel not in NIVEIS_PECAS:
        findings.append(_finding("nivel_peca_invalido", "nivel_peca deve ser A, B ou C."))
        return {
            "status": "BLOCK",
            "nivel_peca": nivel,
            "modo_redacao": None,
            "redacao_por_blocos": None,
            "findings": findings,
        }

    modo = str(context.get("modo_redacao") or ("blocos" if nivel in {"A", "B"} else "direta")).strip().lower()
    redacao_por_blocos = context.get("redacao_por_blocos")
    if redacao_por_blocos is None:
        redacao_por_blocos = nivel in {"A", "B"}
    else:
        redacao_por_blocos = bool(redacao_por_blocos)

    if modo not in MODOS_REDACAO:
        findings.append(_finding("modo_redacao_invalido", "modo_redacao deve ser direta, blocos ou molde_controlado."))

    if nivel == "C" and (modo in {"blocos", "molde_controlado"} or redacao_por_blocos):
        findings.append(
            _finding(
                "tipo_c_sem_blocos",
                "O tipo C não pode usar redação por blocos nem modo molde_controlado.",
            )
        )

    if nivel in {"A", "B"} and context.get("exigir_esqueleto") is not True:
        findings.append(
            _finding(
                "esqueleto_desabilitado",
                "Os tipos A e B exigem exigir_esqueleto: true no fluxo de redação.",
            )
        )

    if context.get("vault_automatico") is True or context.get("consulta_vault_automatica") is True:
        findings.append(
            _finding(
                "vault_automatico_proibido",
                "Nenhum tipo de peça pode disparar consulta automática ao vault neste momento.",
            )
        )

    model = context.get("modelo_estrutura")
    if model is not None:
        if not isinstance(model, dict):
            findings.append(_finding("modelo_estrutura_invalido", "modelo_estrutura deve ser um objeto."))
        else:
            if not str(model.get("modelo_id") or "").strip():
                findings.append(_finding("modelo_id_ausente", "Um modelo selecionado deve declarar modelo_id."))
            if model.get("versao") is None:
                findings.append(_finding("modelo_versao_ausente", "Um modelo selecionado deve declarar versao."))
            recommended = model.get("niveis_recomendados")
            if isinstance(recommended, list) and recommended and nivel not in {normalizar_nivel(item) for item in recommended}:
                findings.append(
                    _finding(
                        "modelo_nivel_incompativel",
                        "O modelo declarado não inclui o nivel_peca selecionado em niveis_recomendados.",
                    )
                )

    return {
        "status": "BLOCK" if findings else "PASS",
        "nivel_peca": nivel,
        "modo_redacao": modo,
        "redacao_por_blocos": redacao_por_blocos,
        "findings": findings,
        "compatibilidade_legada": False,
    }


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Validar contrato de tipo de peça RDAA")
    parser.add_argument("context", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.context.read_text(encoding="utf-8"))
    print(json.dumps(validate_piece_contract(payload), ensure_ascii=False, indent=2))
