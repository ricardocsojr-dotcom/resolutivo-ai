#!/usr/bin/env python3
"""Regressões do contrato de consulta CNJ/DataJud/DJEN sob demanda."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "formatar-peca" / "scripts"
CONTEXT_FIXTURE = ROOT / "tests" / "fixtures" / "context_happy.json"


def test_redigir_does_not_require_process_query() -> None:
    text = (ROOT / "skills" / "redigir-peca" / "SKILL.md").read_text(encoding="utf-8")
    assert "### 3. Consultar o processo — OPCIONAL" in text
    assert "A existência de número de processo **não** dispara consulta automática" in text
    assert "Se há número de processo, execute a skill `consultar-processo` primeiro" not in text
    assert "MCP `CNJ` → dados processuais somente quando" in text
    global_text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "A existência de número de processo não dispara consulta automática" in global_text
    assert "Sempre que receber um número de processo" not in global_text
    assert "Não o consulte automaticamente" in global_text


def test_process_and_publication_skills_remain_available_on_demand() -> None:
    process_text = (ROOT / "skills" / "consultar-processo" / "SKILL.md").read_text(encoding="utf-8")
    backoffice_text = (ROOT / "skills" / "backoffice-diario" / "SKILL.md").read_text(encoding="utf-8")
    assert "Esta skill é **sob demanda**" in process_text
    assert "consultar_processo(numero_processo=" in process_text
    assert "buscar_publicacoes_dje_cnj(numero_processo=" in backoffice_text
    assert "consultar_processo(numero_processo=" in backoffice_text


def test_context_with_process_publishes_without_query_step() -> None:
    build = SCRIPTS / "construir_peca.py"
    publish = ROOT / "skills" / "revisor-rdaa" / "scripts" / "publicar_docx.py"
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        context = json.loads(CONTEXT_FIXTURE.read_text(encoding="utf-8"))
        context["numero_processo"] = "9999999-99.9999.8.26.9999"
        context_path = folder / "context.json"
        context_path.write_text(json.dumps(context, ensure_ascii=False), encoding="utf-8")
        candidate = folder / "candidate.docx"
        output = folder / "final.docx"

        build_result = subprocess.run(
            [sys.executable, str(build), "--context", str(context_path), "--output", str(candidate)],
            text=True,
            capture_output=True,
        )
        assert build_result.returncode == 0, build_result.stdout + build_result.stderr
        publish_result = subprocess.run(
            [
                sys.executable,
                str(publish),
                "--input",
                str(candidate),
                "--output",
                str(output),
                "--context",
                str(context_path),
            ],
            text=True,
            capture_output=True,
        )
        assert publish_result.returncode == 0, publish_result.stdout + publish_result.stderr
        assert output.is_file()
        assert (folder / ".rdaa-run" / "9999999-99.9999.8.26.9999" / "matter_state.json").is_file()


if __name__ == "__main__":
    test_redigir_does_not_require_process_query()
    test_process_and_publication_skills_remain_available_on_demand()
    test_context_with_process_publishes_without_query_step()
    print("[OK] consulta CNJ/DataJud/DJEN opcional e capacidades sob demanda passaram")
