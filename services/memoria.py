"""Serviço de memória — Cérebro-Ricar, chamado pelo motor V4.

Delega a registrar_cerebro.py existente. Este módulo serve como
fronteira limpa para o motor, sem importar diretamente os scripts
de skill.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def registrar_cerebro(
    state_dir: Path,
    matter_id: str,
    level: str,
) -> dict[str, Any]:
    """Registra matéria no Cérebro-Ricar pós-publicação.

    Delega a skills/redigir-peca/scripts/registrar_cerebro.py.
    """
    import importlib.util

    script = Path(__file__).resolve().parents[1] / "skills" / "redigir-peca" / "scripts" / "registrar_cerebro.py"
    if not script.is_file():
        return {"status": "skipped", "reason": "registrar_cerebro.py não encontrado"}

    spec = importlib.util.spec_from_file_location("registrar_cerebro", script)
    if not spec or not spec.loader:
        return {"status": "error", "reason": "falha ao carregar registrar_cerebro.py"}

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.registrar(state_dir, matter_id, level)
