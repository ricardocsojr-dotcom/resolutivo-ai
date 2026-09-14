"""Servico de publicacao -- chamado pelo motor V4.

Invoca skills/revisor-rdaa/scripts/publicar_docx.py como subprocesso, que
e o pipeline real e testado de publicacao protegida:

    1. Valida contrato do state_dir (sem aninhamento de .rdaa-run).
    2. Roda QA (formatacao + estilo).
    3. Roda revisao semantica: docx semantics, visual law, esqueleto,
       contrato de peca.
    4. Cria backup atomico do arquivo anterior.
    5. Substitui por copia atomica com verificacao de hash pos-copia
       (reverte automaticamente se o hash divergir).
    6. Promove o estado candidato (candidate/) para o state_dir final.
    7. Registra no Cerebro-Ricar + OpenViking (a menos que --skip-cerebro).

Este modulo NAO reimplementa nada dessa logica -- reimplementar aqui
duplicaria uma superficie de seguranca critica (validacao semantica, lei
visual, esqueleto, contrato de peca) sem a cobertura de
tests/test_publicacao_protegida.py e tests/test_publicar_docx_state_dir_aninhado.py.
Ele so traduz o contrato services/* (Path in, dict out) para o CLI real.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLICAR_DOCX_SCRIPT = ROOT / "skills" / "revisor-rdaa" / "scripts" / "publicar_docx.py"


def publicar_docx(
    candidate: Path,
    output: Path,
    *,
    state_dir: Path | None = None,
    backup_dir: Path | None = None,
    context_path: Path | None = None,
    skip_cerebro: bool = False,
    timeout: int = 300,
) -> dict[str, Any]:
    """Publica um DOCX candidato via o pipeline real publicar_docx.py.

    Retorna dict com status, phase e o manifesto resultante quando
    disponivel.  Levanta RuntimeError em caso de rejeicao (exit_code != 0),
    com a saida stderr/stdout do processo para diagnostico.
    """
    if not candidate.is_file():
        raise FileNotFoundError(f"candidato ausente: {candidate}")
    if not PUBLICAR_DOCX_SCRIPT.is_file():
        raise FileNotFoundError(f"publicar_docx.py nao encontrado: {PUBLICAR_DOCX_SCRIPT}")

    command = [
        sys.executable, str(PUBLICAR_DOCX_SCRIPT),
        "--input", str(candidate),
        "--output", str(output),
    ]
    if state_dir:
        command += ["--state-dir", str(state_dir)]
    if backup_dir:
        command += ["--backup-dir", str(backup_dir)]
    if context_path:
        command += ["--context", str(context_path)]
    if skip_cerebro:
        command += ["--skip-cerebro"]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        cwd=ROOT,
    )

    manifest: dict[str, Any] = {}
    effective_state_dir = state_dir or (output.parent / ".rdaa-run")
    manifest_path = effective_state_dir / "run_manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}

    if result.returncode != 0:
        raise RuntimeError(
            f"publicacao rejeitada (exit_code={result.returncode}): "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )

    return {
        "status": manifest.get("status", "PUBLISHED"),
        "phase": manifest.get("phase", "published"),
        "output_path": str(output),
        "candidate_path": str(candidate),
        "manifest": manifest,
        "stdout": result.stdout.strip(),
    }
