import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "redigir-peca" / "scripts" / "orquestrador_rdaa.py"
SPEC = importlib.util.spec_from_file_location("orquestrador_rdaa", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _avancar_fluxo_b_ate_fontes(state_dir: Path) -> None:
    MODULE.avancar_fase(state_dir, "intake_ready")
    context = state_dir / "EMENTARIO-CONTEXTO.json"
    context.write_text(
        '{"origin": "ementario-resolutivo", "status": "informada", "mode": "read_only"}',
        encoding="utf-8",
    )
    MODULE.registrar_consulta_vault(state_dir, vault="ementario-resolutivo", artifact_path=context)
    MODULE.avancar_fase(state_dir, "vault_context_ready")
    MODULE.avancar_fase(state_dir, "sources_ready")


def test_rota_b_exige_critica_independente_e_validacao_independente():
    route = MODULE.selecionar_rota("B", "baixo")

    assert route["effective_piece_level"] == "B"
    assert route["worker_allowed_phases"]["writer"] == ["drafting"]
    assert route["workers"] == {
        "planner": "claude",
        "writer": "codex",
        "critic": "antigravity",
        "validator": "claude",
    }
    assert "criticizing" in route["stages"]
    assert route["required_human_gates"] == ["skeleton_approval"]


def test_rota_b_exige_contexto_do_ementario_antes_das_fontes():
    route = MODULE.selecionar_rota("B", "baixo")

    assert route["vault"]["lookup"]["enabled"] is True
    assert route["vault"]["lookup"]["vault"] == "ementario-resolutivo"
    assert route["stages"].index("vault_context_ready") < route["stages"].index("sources_ready")


def test_risco_alto_nunca_rebaixa_fluxo_c():
    route = MODULE.selecionar_rota("C", "alto")

    assert route["effective_piece_level"] == "B"
    assert route["escalated_by_risk"] is True
    assert "criticizing" in route["stages"]


def test_rota_rejeita_critico_da_mesma_familia_do_redator():
    with pytest.raises(MODULE.RoutePolicyError, match="independente"):
        MODULE.validar_segregacao(
            {
                "writer": {"engine": "codex", "model_family": "openai"},
                "critic": {"engine": "outro-codex", "model_family": "openai"},
                "validator": {"engine": "claude", "model_family": "anthropic"},
            }
        )


def test_rota_rejeita_critico_e_validador_da_mesma_familia():
    with pytest.raises(MODULE.RoutePolicyError, match="independente"):
        MODULE.validar_segregacao(
            {
                "writer": {"engine": "codex", "model_family": "openai"},
                "critic": {"engine": "agy", "model_family": "google"},
                "validator": {"engine": "outro-agy", "model_family": "google"},
            }
        )


def test_aprovacao_do_esqueleto_e_invalida_quando_artefato_muda(tmp_path):
    MODULE.inicializar_execucao(tmp_path, "caso-123", "B", "baixo")
    _avancar_fluxo_b_ate_fontes(tmp_path)
    for phase in ("skeleton_ready", "awaiting_skeleton_approval"):
        MODULE.avancar_fase(tmp_path, phase)

    skeleton = tmp_path / "ESQUELETO.md"
    skeleton.write_text("versão aprovada", encoding="utf-8")
    MODULE.registrar_aprovacao(tmp_path, "skeleton_approval", skeleton, "Ricardo")

    assert MODULE.aprovacao_valida(tmp_path, "skeleton_approval", skeleton)
    MODULE.avancar_fase(tmp_path, "skeleton_approved")

    skeleton.write_text("versão alterada", encoding="utf-8")
    assert not MODULE.aprovacao_valida(tmp_path, "skeleton_approval", skeleton)


def test_aprovacao_persiste_caminho_absoluto_para_retornar_em_outro_cwd(tmp_path, monkeypatch):
    state_dir = tmp_path / "state"
    MODULE.inicializar_execucao(state_dir, "caso-123", "B", "baixo")
    _avancar_fluxo_b_ate_fontes(state_dir)
    for phase in ("skeleton_ready", "awaiting_skeleton_approval"):
        MODULE.avancar_fase(state_dir, phase)
    artifact = tmp_path / "ESQUELETO.md"
    artifact.write_text("versão aprovada", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    MODULE.registrar_aprovacao(state_dir, "skeleton_approval", Path("ESQUELETO.md"), "Ricardo")
    monkeypatch.chdir(tmp_path.parent)

    assert MODULE.aprovacao_valida(state_dir, "skeleton_approval")


def test_nao_permite_pular_fase_do_fluxo(tmp_path):
    MODULE.inicializar_execucao(tmp_path, "caso-123", "C", "baixo")

    with pytest.raises(MODULE.WorkflowStateError, match="próxima fase"):
        MODULE.avancar_fase(tmp_path, "skeleton_ready")


def test_nao_permite_finalizar_rascunho_sem_execucao_do_redator(tmp_path):
    MODULE.inicializar_execucao(tmp_path, "caso-123", "C", "baixo")
    MODULE.avancar_fase(tmp_path, "intake_ready")
    MODULE.avancar_fase(tmp_path, "drafting")

    with pytest.raises(MODULE.WorkflowStateError, match="execução do papel writer"):
        MODULE.avancar_fase(tmp_path, "draft_ready")


def test_contexto_do_ementario_e_exigido_antes_de_avancar_fluxo_b(tmp_path):
    MODULE.inicializar_execucao(tmp_path, "caso-123", "B", "baixo")
    MODULE.avancar_fase(tmp_path, "intake_ready")

    with pytest.raises(MODULE.WorkflowStateError, match="consulta do Ementário"):
        MODULE.avancar_fase(tmp_path, "vault_context_ready")

    context = tmp_path / "EMENTARIO-CONTEXTO.json"
    context.write_text(
        '{"origin": "ementario-resolutivo", "status": "informada", "mode": "read_only"}',
        encoding="utf-8",
    )
    record = MODULE.registrar_consulta_vault(
        tmp_path,
        vault="ementario-resolutivo",
        artifact_path=context,
        metadata={"status": "informada", "mode": "read_only"},
    )

    assert record["artifact_sha256"]
    MODULE.avancar_fase(tmp_path, "vault_context_ready")


def test_registro_operacional_e_exigido_antes_de_vault_registered(tmp_path):
    MODULE.inicializar_execucao(tmp_path, "caso-123", "C", "baixo")
    manifest = MODULE._read_manifest(tmp_path)
    manifest["phase"] = "published"
    MODULE._write_json(tmp_path / "run_manifest.json", manifest)

    with pytest.raises(MODULE.WorkflowStateError, match="registro no vault operacional"):
        MODULE.avancar_fase(tmp_path, "vault_registered")

    receipt = tmp_path / "RECIBO-VAULT-OPERACIONAL.json"
    receipt.write_text('{"vault": "procedimentos-informacoes", "status": "registered"}', encoding="utf-8")
    record = MODULE.registrar_sincronizacao_vault(
        tmp_path,
        vault="procedimentos-informacoes",
        artifact_path=receipt,
        metadata={"status": "registered"},
    )

    assert record["artifact_sha256"]
    MODULE.avancar_fase(tmp_path, "vault_registered")


def test_nao_permite_finalizar_rascunho_com_saida_alterada(tmp_path):
    MODULE.inicializar_execucao(tmp_path, "caso-123", "C", "baixo")
    MODULE.avancar_fase(tmp_path, "intake_ready")
    MODULE.avancar_fase(tmp_path, "drafting")
    prompt = tmp_path / "PROMPT.md"
    output = tmp_path / "RASCUNHO.md"
    prompt.write_text("pacote", encoding="utf-8")
    output.write_text("original", encoding="utf-8")
    MODULE.registrar_execucao(tmp_path, role="writer", motor="codex", prompt_path=prompt, output_path=output)
    output.write_text("alterado", encoding="utf-8")

    with pytest.raises(MODULE.WorkflowStateError, match="hash da saída"):
        MODULE.avancar_fase(tmp_path, "draft_ready")


def test_gate_estrategico_condicional_pausa_e_exige_aprovacao_explicita(tmp_path):
    MODULE.inicializar_execucao(tmp_path, "caso-123", "A", "baixo")
    gate = MODULE.abrir_gate_humano(tmp_path, "strategy_exception", "tese central vulnerável")
    artifact = tmp_path / "DECISAO-ESTRATEGICA.md"
    artifact.write_text("seguir com a tese", encoding="utf-8")

    assert gate["gate"] == "strategy_exception"
    with pytest.raises(MODULE.WorkflowStateError, match="aprovação pendente"):
        MODULE.avancar_fase(tmp_path, "intake_ready")
    assert MODULE.registrar_aprovacao(tmp_path, "strategy_exception", artifact, "Ricardo")["gate"] == "strategy_exception"
    assert MODULE._read_manifest(tmp_path)["status"] == "ready"


def test_lock_da_materia_exclui_segunda_operacao_simultanea(tmp_path):
    with MODULE.bloqueio_materia(tmp_path):
        assert (tmp_path / ".rdaa-orchestrator.lock").is_file()
        with pytest.raises(MODULE.WorkflowLockError, match="em uso"):
            with MODULE.bloqueio_materia(tmp_path):
                pass
    assert not (tmp_path / ".rdaa-orchestrator.lock").exists()


def test_inicializacao_respeita_lock_da_materia(tmp_path):
    with MODULE.bloqueio_materia(tmp_path):
        with pytest.raises(MODULE.WorkflowLockError):
            MODULE.inicializar_execucao(tmp_path, "caso-bloqueado", "C", "baixo")

def test_redator_nao_pode_registrar_execucao_antes_do_estagio_de_redacao(tmp_path):
    MODULE.inicializar_execucao(tmp_path, "caso-123", "B", "baixo")
    prompt = tmp_path / "PROMPT-REDACAO.md"
    output = tmp_path / "RASCUNHO.md"
    prompt.write_text("pacote", encoding="utf-8")
    output.write_text("rascunho", encoding="utf-8")

    with pytest.raises(MODULE.WorkflowStateError, match="fase incompatível"):
        MODULE.registrar_execucao(tmp_path, role="writer", motor="codex", prompt_path=prompt, output_path=output)


def test_registra_execucao_com_hashes_e_identidade_do_worker(tmp_path):
    MODULE.inicializar_execucao(tmp_path, "caso-123", "B", "baixo")
    _avancar_fluxo_b_ate_fontes(tmp_path)
    for phase in ("skeleton_ready", "awaiting_skeleton_approval"):
        MODULE.avancar_fase(tmp_path, phase)
    skeleton = tmp_path / "ESQUELETO.md"
    skeleton.write_text("esqueleto aprovado", encoding="utf-8")
    MODULE.registrar_aprovacao(tmp_path, "skeleton_approval", skeleton, "Ricardo")
    MODULE.avancar_fase(tmp_path, "skeleton_approved")
    MODULE.avancar_fase(tmp_path, "drafting")
    prompt = tmp_path / "PROMPT-REDACAO.md"
    output = tmp_path / "RASCUNHO.md"
    prompt.write_text("pacote mínimo", encoding="utf-8")
    output.write_text("rascunho", encoding="utf-8")

    record = MODULE.registrar_execucao(
        tmp_path,
        role="writer",
        motor="codex",
        prompt_path=prompt,
        output_path=output,
        metadata={
            "session_id": "codex-1",
            "duration_ms": 42,
            "model_ids": ["gpt-5.6-codex"],
            "usage": {"input_tokens": 120, "output_tokens": 80},
        },
    )

    assert record["role"] == "writer"
    assert record["worker"]["model_family"] == "openai"
    assert record["model_ids"] == ["gpt-5.6-codex"]
    assert record["usage"]["output_tokens"] == 80
    assert record["input_sha256"] != record["output_sha256"]
    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["executions"] == [record]


def test_cli_inicializa_e_mostra_status(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["orquestrador_rdaa.py", "init", str(tmp_path), "--matter-id", "caso-123", "--piece-level", "B", "--risk-level", "baixo"],
    )
    assert MODULE.main() == 0
    assert json.loads(capsys.readouterr().out)["phase"] == "initialized"

    monkeypatch.setattr(sys, "argv", ["orquestrador_rdaa.py", "status", str(tmp_path)])
    assert MODULE.main() == 0
    assert json.loads(capsys.readouterr().out)["matter_id"] == "caso-123"
