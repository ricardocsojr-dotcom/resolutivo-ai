#!/usr/bin/env python3
"""Regressão 2026-09-11: publicar_docx.py nunca pode criar .rdaa-run aninhado.

Bug real: quando --state-dir não é passado e --output já vive dentro de um
.rdaa-run/<matter_id>/ existente, a derivação padrão
(output.parent / ".rdaa-run" / matter_id) criava um SEGUNDO .rdaa-run dentro
do primeiro. O manifesto real (fase published) ficava só no aninhado; o
canônico (.rdaa-run/<matter_id>/run_manifest.json), que orquestrador_rdaa.py
status, os hooks de sessão e o registro no Cérebro leem, nunca era
atualizado. Aconteceu de verdade em duas matérias publicadas em produção
(0747080-19.2014.8.13.0024 e 1045435-63.2026.8.13.0702), e o script imprimia
[OK] normalmente -- sem qualquer sinal do problema.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from test_qa_engineering import FIXTURE, GENERATOR

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = PLUGIN_ROOT / "skills" / "revisor-rdaa" / "scripts" / "publicar_docx.py"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PLUGIN_ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def test_recusa_state_dir_derivado_dentro_de_rdaa_run_existente() -> None:
    """--output dentro de um .rdaa-run/<matter_id>/ já existente, sem
    --state-dir explícito, deve falhar em vez de criar aninhamento."""
    with tempfile.TemporaryDirectory(prefix="rdaa-nested-") as tmp:
        folder = Path(tmp)
        context = folder / "context.json"
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        data["matter_id"] = "0747080-19.2014.8.13.0024"
        context.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        candidate = folder / "candidate.docx"
        generated = run([sys.executable, str(GENERATOR), "--context", str(context), "--output", str(candidate)])
        assert generated.returncode == 0, generated.stdout + generated.stderr

        # Simula o cenário real: matter_id já tem um .rdaa-run/<matter_id>/
        # de trabalho, e agora publicamos DENTRO dele sem --state-dir.
        matter_workdir = folder / ".rdaa-run" / "0747080-19.2014.8.13.0024"
        matter_workdir.mkdir(parents=True)
        output = matter_workdir / "peca_final.docx"

        result = run([
            sys.executable, str(PUBLISHER),
            "--input", str(candidate),
            "--output", str(output),
            "--context", str(context),
        ])
        assert result.returncode != 0, result.stdout + result.stderr
        assert "aninhado" in (result.stdout + result.stderr).lower()
        # Nunca deve ter criado o .rdaa-run duplicado dentro do de trabalho.
        assert not (matter_workdir / ".rdaa-run").exists()


def test_recusa_aninhamento_com_variacao_de_caixa_e_nao_escreve() -> None:
    """Windows trata paths sem diferenciar caixa; a proteção também deve."""
    with tempfile.TemporaryDirectory(prefix="rdaa-nested-case-") as tmp:
        folder = Path(tmp)
        context = folder / "context.json"
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        data["matter_id"] = "0747080-19.2014.8.13.0024"
        context.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        candidate = folder / "candidate.docx"
        generated = run([sys.executable, str(GENERATOR), "--context", str(context), "--output", str(candidate)])
        assert generated.returncode == 0, generated.stdout + generated.stderr

        # O diretório existente pode ter sido criado com outra capitalização.
        # A derivação do publicador ainda acrescenta o literal '.rdaa-run'.
        matter_workdir = folder / ".RDAA-RUN" / "0747080-19.2014.8.13.0024"
        matter_workdir.mkdir(parents=True)
        sentinel = matter_workdir / "preservar.txt"
        sentinel.write_text("estado anterior", encoding="utf-8")
        output = matter_workdir / "peca_final.docx"

        result = run([
            sys.executable, str(PUBLISHER),
            "--input", str(candidate),
            "--output", str(output),
            "--context", str(context),
        ])

        assert result.returncode != 0, result.stdout + result.stderr
        assert "aninhado" in (result.stdout + result.stderr).lower()
        assert sentinel.read_text(encoding="utf-8") == "estado anterior"
        assert not output.exists()
        assert not (matter_workdir / ".rdaa-run").exists()


def test_state_dir_explicito_fora_da_arvore_publica_normalmente() -> None:
    """--state-dir explícito e canônico (sem duplo .rdaa-run) continua ok."""
    with tempfile.TemporaryDirectory(prefix="rdaa-nested-ok-") as tmp:
        folder = Path(tmp)
        context = folder / "context.json"
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        data["matter_id"] = "caso-normal"
        context.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        candidate = folder / "candidate.docx"
        generated = run([sys.executable, str(GENERATOR), "--context", str(context), "--output", str(candidate)])
        assert generated.returncode == 0, generated.stdout + generated.stderr

        output = folder / "peca_final.docx"
        state_dir = folder / ".rdaa-run" / "caso-normal"
        result = run([
            sys.executable, str(PUBLISHER),
            "--input", str(candidate),
            "--output", str(output),
            "--state-dir", str(state_dir),
            "--context", str(context),
        ])
        assert result.returncode == 0, result.stdout + result.stderr
        assert (state_dir / "run_manifest.json").is_file()


def main() -> int:
    import pytest

    return pytest.main([str(Path(__file__).resolve()), "-q"])


if __name__ == "__main__":
    raise SystemExit(main())
