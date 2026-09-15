"""QA estrutural e estilístico -- chamado pelo motor V4.

Delega ao gate real em skills/revisor-rdaa/scripts/qa_gate.py, que por sua
vez invoca skills/formatar-peca/scripts/verificar_formatacao.py e
skills/revisor-rdaa/scripts/verificar_estilo.py.

Este modulo NAO reimplementa a logica de QA -- ele importa e chama o
qa_gate.py existente via importlib, preservando exatamente o mesmo
comportamento testado em tests/test_qa_engineering.py e nos testes de
publicacao protegida. Reimplementar aqui seria duplicar uma superficie de
risco (paths dos validadores, argumentos, contrato de saida) que ja esta
coberta por testes.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QA_GATE_SCRIPT = ROOT / "skills" / "revisor-rdaa" / "scripts" / "qa_gate.py"

_module_cache: Any = None


def _load_qa_gate():
    """Carrega qa_gate.py uma unica vez via importlib (evita sys.path pollution)."""
    global _module_cache
    if _module_cache is not None:
        return _module_cache

    if not QA_GATE_SCRIPT.is_file():
        raise FileNotFoundError(f"qa_gate.py nao encontrado: {QA_GATE_SCRIPT}")

    spec = importlib.util.spec_from_file_location("qa_gate", QA_GATE_SCRIPT)
    if not spec or not spec.loader:
        raise ImportError(f"falha ao carregar qa_gate.py: {QA_GATE_SCRIPT}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _module_cache = module
    return module


def run_qa_gate(docx: Path, context_path: Path | None = None) -> dict[str, Any]:
    """Executa o gate de QA real (formatacao + estilo).

    Delega inteiramente a qa_gate.run_gate(), que ja e testado e usado
    em producao por publicar_docx.py.  Retorna dict com schema_version,
    status (PASS/FAIL), checks[] e errors[].
    """
    module = _load_qa_gate()
    return module.run_gate(docx, context_path)
