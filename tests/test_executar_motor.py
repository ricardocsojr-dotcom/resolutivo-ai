import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "redigir-peca" / "scripts" / "executar_motor.py"
SPEC = importlib.util.spec_from_file_location("executar_motor", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

ORCHESTRATOR_PATH = ROOT / "skills" / "redigir-peca" / "scripts" / "orquestrador_rdaa.py"
ORCHESTRATOR_SPEC = importlib.util.spec_from_file_location("orquestrador_rdaa_for_executor", ORCHESTRATOR_PATH)
ORCHESTRATOR = importlib.util.module_from_spec(ORCHESTRATOR_SPEC)
assert ORCHESTRATOR_SPEC and ORCHESTRATOR_SPEC.loader
ORCHESTRATOR_SPEC.loader.exec_module(ORCHESTRATOR)


def test_motores_usam_entrada_direta_e_so_gravam_no_sucesso(tmp_path):
    prompt = tmp_path / "prompt.md"
    prompt.write_text("analise isto", encoding="utf-8")

    with patch.object(MODULE.subprocess, "run") as run:
        run.return_value.returncode = 0
        run.return_value.stdout = "rascunho\n"
        run.return_value.stderr = ""
        codex_out = tmp_path / "codex.md"
        MODULE.executar("codex", prompt, codex_out, None, 30)
        command = run.call_args.args[0]
        assert Path(command[0]).stem.lower() == "codex"
        assert command[1] == "exec"
        assert run.call_args.kwargs["input"] == "analise isto"
        assert codex_out.read_text(encoding="utf-8") == "rascunho\n"

        run.return_value.stdout = json.dumps(
            {"event": "result", "result": {"status": "SUCCESS", "response": "crítica"}},
            ensure_ascii=False,
        )
        agy_out = tmp_path / "agy.md"
        MODULE.executar("antigravity", prompt, agy_out, None, 30)
        command = run.call_args.args[0]
        assert Path(command[0]).stem.lower() == "agy" and "stream-json" in command
        assert "--sandbox" in command
        assert "dangerously-skip-permissions" not in " ".join(command)
        assert json.loads(run.call_args.kwargs["input"])["message"]["content"] == "analise isto"
        assert agy_out.read_text(encoding="utf-8") == "crítica\n"


def test_claude_recebe_pacote_por_stdin_e_devolve_resultado_estruturado(tmp_path):
    prompt = tmp_path / "prompt.md"
    prompt.write_text("valide esta peça", encoding="utf-8")
    output = tmp_path / "claude.md"

    with patch.object(MODULE.subprocess, "run") as run:
        run.return_value.returncode = 0
        run.return_value.stderr = ""
        run.return_value.stdout = json.dumps(
            {"type": "result", "subtype": "success", "result": "validação", "session_id": "sessao-1", "modelUsage": {"claude-sonnet-4-6": {"costUSD": 0.01}}},
            ensure_ascii=False,
        )
        result = MODULE.executar("claude", prompt, output, None, 30)

    command = run.call_args.args[0]
    assert Path(command[0]).stem.lower() == "claude"
    assert command[1] == "-p"
    assert "--no-session-persistence" in command
    assert "--tools" in command
    assert "--max-budget-usd" in command
    assert command[command.index("--max-budget-usd") + 1] == "1.0"
    assert run.call_args.kwargs["input"] == "valide esta peça"
    assert output.read_text(encoding="utf-8") == "validação\n"
    assert result["session_id"] == "sessao-1"
    assert result["model_ids"] == ["claude-sonnet-4-6"]


def test_executor_registra_saida_no_manifesto_quando_recebe_papel(tmp_path):
    ORCHESTRATOR.inicializar_execucao(tmp_path, "caso-123", "B", "baixo")
    ORCHESTRATOR.avancar_fase(tmp_path, "intake_ready")
    vault_context = tmp_path / "EMENTARIO-CONTEXTO.json"
    vault_context.write_text(
        '{"origin": "ementario-resolutivo", "status": "informada", "mode": "read_only"}',
        encoding="utf-8",
    )
    ORCHESTRATOR.registrar_consulta_vault(tmp_path, vault="ementario-resolutivo", artifact_path=vault_context)
    for phase in ("vault_context_ready", "sources_ready", "skeleton_ready", "awaiting_skeleton_approval"):
        ORCHESTRATOR.avancar_fase(tmp_path, phase)
    skeleton = tmp_path / "ESQUELETO.md"
    skeleton.write_text("aprovado", encoding="utf-8")
    ORCHESTRATOR.registrar_aprovacao(tmp_path, "skeleton_approval", skeleton, "Ricardo")
    ORCHESTRATOR.avancar_fase(tmp_path, "skeleton_approved")
    ORCHESTRATOR.avancar_fase(tmp_path, "drafting")
    prompt = tmp_path / "PROMPT-REDACAO.md"
    prompt.write_text("redija", encoding="utf-8")
    output = tmp_path / "RASCUNHO.md"

    with patch.object(MODULE.subprocess, "run") as run:
        run.return_value.returncode = 0
        run.return_value.stderr = ""
        run.return_value.stdout = "rascunho"
        MODULE.executar("codex", prompt, output, None, 30, state_dir=tmp_path, role="writer")

    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["executions"][0]["role"] == "writer"
    assert manifest["executions"][0]["motor"] == "codex"


def test_executor_bloqueia_worker_antes_da_chamada_externa_fora_da_fase(tmp_path):
    ORCHESTRATOR.inicializar_execucao(tmp_path, "caso-123", "B", "baixo")
    prompt = tmp_path / "PROMPT-REDACAO.md"
    prompt.write_text("redija", encoding="utf-8")

    with patch.object(MODULE.subprocess, "run") as run:
        with pytest.raises(ValueError, match="fase incompatível"):
            MODULE.executar("codex", prompt, tmp_path / "RASCUNHO.md", None, 30, state_dir=tmp_path, role="writer")
        run.assert_not_called()


def test_antigravity_ignora_linhas_de_log_fora_do_stream_json(tmp_path):
    prompt = tmp_path / "prompt.md"
    prompt.write_text("critique", encoding="utf-8")
    output = tmp_path / "critica.md"

    with patch.object(MODULE.subprocess, "run") as run:
        run.return_value.returncode = 0
        run.return_value.stderr = ""
        run.return_value.stdout = "aviso local\n" + json.dumps(
            {"event": "result", "result": {"status": "SUCCESS", "response": "crítica"}},
            ensure_ascii=False,
        )
        MODULE.executar("antigravity", prompt, output, None, 30)

    assert output.read_text(encoding="utf-8") == "crítica\n"


def test_saida_estruturada_ausente_e_erro_em_vez_de_gravar_null():
    stdout = json.dumps({"event": "result", "result": {"status": "SUCCESS"}}, ensure_ascii=False)

    with pytest.raises(RuntimeError, match="resultado válido"):
        MODULE._resultado_antigravity(stdout, structured=True)


def test_resolve_executavel_para_caminho_nativo_do_windows():
    with patch.object(MODULE.shutil, "which", return_value=r"C:\\Ferramentas\\codex.EXE"):
        assert MODULE._executavel("codex") == r"C:\\Ferramentas\\codex.EXE"


def test_falha_do_motor_preserva_diagnostico_emitido_no_stdout(tmp_path):
    prompt = tmp_path / "prompt.md"
    prompt.write_text("redija", encoding="utf-8")

    with patch.object(MODULE.subprocess, "run") as run:
        run.return_value.returncode = 1
        run.return_value.stderr = ""
        run.return_value.stdout = "quota excedida"
        with pytest.raises(RuntimeError, match="quota excedida"):
            MODULE.executar("codex", prompt, tmp_path / "saida.md", None, 30)
