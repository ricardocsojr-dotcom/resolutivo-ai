"""Serviço de pesquisa — wrapper para fontes autorizadas.

Jusbrasil é a única fonte jurisprudencial externa autorizada (§2, §20).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def pesquisar_jusbrasil(
    query: str,
    *,
    tribunais: list[str] | None = None,
    max_results: int = 10,
) -> dict[str, Any]:
    """Pesquisa jurisprudencial via Jusbrasil (placeholder).

    NOTA: A implementação real chama a skill jusbrasil-jurisprudencia.
    Aqui serve como contrato para o motor V4.
    """
    if not query.strip():
        return {"status": "error", "reason": "query vazia"}

    return {
        "status": "placeholder",
        "query": query,
        "tribunais": tribunais or ["STJ", "TJSP", "TJMG"],
        "max_results": max_results,
        "results": [],
        "note": "implementação real via skill jusbrasil-jurisprudencia",
    }
