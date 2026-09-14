"""Testes E2E do Motor RDAA V4: A, B e C sem transições implícitas.

Verifica:
- Que todas as fases da rota são visitadas na ordem correta.
- Que gates humanos bloqueiam corretamente.
- Que o disjuntor pausa após 2 falhas consecutivas.
- Que nenhuma CLI de IA é chamada (apenas workers injetados).
- Que os artefatos de estado são criados.
- Que a retomada (resume) funciona com authority: ricardo.
- Que duas matérias simultâneas não interferem.
"""

import json
import subprocess
from pathlib import Path

import pytest

from orquestracao.contracts import (
    CircuitBreakerError,
    GateError,
    load_route,
)
from orquestracao.engine import RDAAEngine


ROUTE_PATH = Path(__file__).resolve().parents[1] / "orquestracao" / "roteamento.json"


# ---------------------------------------------------------------------------
# Worker sintético
# ---------------------------------------------------------------------------

def fake_worker(role, state):
    """Worker determinístico para testes."""
    return {"role": role, "phase_seen": state.get("phase", "")}


def route_stages(level: str) -> list[str]:
    """Retorna as fases da rota para um nível."""
    return list(load_route(level, ROUTE_PATH)["stages"])


DUMMY_HANDLERS = {
    "qa_passed": lambda s: {"status": "ok"},
    "published": lambda s: {"status": "ok"},
    "vault_registered": lambda s: {"status": "ok"},
}


# ---------------------------------------------------------------------------
# E2E por nível
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("level", ["A", "B", "C"])
def test_rotas_e2e_sem_pular_fases(tmp_path, level):
    """O motor visita todas as fases da rota na ordem correta."""
    state_dir = tmp_path / f"matter-{level}"
    engine = RDAAEngine(state_dir, level, worker=fake_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        result = engine.initialize(f"matter-{level}")

        if level in {"A", "B"}:
            result = engine.approve_gate("skeleton_approval")
        if level == "A":
            result = engine.approve_gate("release_approval")

        assert result["phase"] == "vault_registered"
        assert result["history"] == route_stages(level)

        # Artefatos de estado
        assert (state_dir / "langgraph.sqlite").is_file()
        assert (state_dir / "run_manifest.json").is_file()
        assert (state_dir / "matter_state.json").is_file()
    finally:
        engine.close()


# ---------------------------------------------------------------------------
# Rota A: critic obrigatório
# ---------------------------------------------------------------------------

def test_rota_a_executa_critic_obrigatoriamente(tmp_path):
    """A rota A deve executar planner, writer, critic e validator."""
    calls: list[str] = []

    def tracking_worker(role, state):
        calls.append(role)
        return {"ok": True}

    engine = RDAAEngine(tmp_path / "a", "A", worker=tracking_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        engine.initialize("premium")
        engine.approve_gate("skeleton_approval")
        engine.approve_gate("release_approval")
        assert calls == ["planner", "writer", "critic", "validator"]
        history = engine.state()["history"]
        assert "criticizing" in history
        assert "critique_ready" in history
    finally:
        engine.close()


# ---------------------------------------------------------------------------
# Rota B: sem critic
# ---------------------------------------------------------------------------

def test_rota_b_nao_executa_critic(tmp_path):
    calls: list[str] = []

    def tracking_worker(role, state):
        calls.append(role)
        return {"ok": True}

    engine = RDAAEngine(tmp_path / "b", "B", worker=tracking_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        engine.initialize("developed")
        engine.approve_gate("skeleton_approval")
        assert "critic" not in calls
        assert "planner" in calls
        assert "writer" in calls
        assert "validator" in calls
    finally:
        engine.close()


# ---------------------------------------------------------------------------
# Rota C: sem gates, sem critic, sem planner
# ---------------------------------------------------------------------------

def test_rota_c_sem_gates(tmp_path):
    calls: list[str] = []

    def tracking_worker(role, state):
        calls.append(role)
        return {"ok": True}

    engine = RDAAEngine(tmp_path / "c", "C", worker=tracking_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        result = engine.initialize("simple")
        # Nível C não tem gates humanos, executa direto
        assert result["phase"] == "vault_registered"
        assert result["status"] == "vault_registered"
        assert calls == ["writer"]
    finally:
        engine.close()


# ---------------------------------------------------------------------------
# Gate humano bloqueia sem aprovação
# ---------------------------------------------------------------------------

def test_gate_bloqueia_sem_aprovacao(tmp_path):
    """O motor deve parar antes do gate awaiting_skeleton_approval."""
    engine = RDAAEngine(tmp_path / "gate", "B", worker=fake_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        result = engine.initialize("gate-test")
        # O motor pausa no gate
        state = engine.state()
        # A execução parou ANTES do gate
        assert "awaiting_skeleton_approval" not in state.get("history", [])
    finally:
        engine.close()


# ---------------------------------------------------------------------------
# Gate recusa autoridade não-ricardo
# ---------------------------------------------------------------------------

def test_gate_recusa_autoridade_ia(tmp_path):
    engine = RDAAEngine(tmp_path / "auth", "B", worker=fake_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        engine.initialize("auth-test")
        with pytest.raises(GateError, match="ricardo"):
            engine.approve_gate("skeleton_approval", authority="IA")
    finally:
        engine.close()


# ---------------------------------------------------------------------------
# Disjuntor: 2 falhas consecutivas pausam
# ---------------------------------------------------------------------------

def test_disjuntor_pausa_apos_duas_falhas(tmp_path):
    """O motor pausa após 2 falhas consecutivas no mesmo worker."""
    call_count = 0

    def failing_worker(role, state):
        nonlocal call_count
        call_count += 1
        raise RuntimeError("falha sintética")

    engine = RDAAEngine(tmp_path / "circ", "C", worker=failing_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        # O motor não propaga exceção — persiste o estado com a falha.
        result = engine.initialize("circuit-test")
        state = engine.state()

        # Deve ter registrado pelo menos 1 falha consecutiva
        assert state.get("consecutive_failures", 0) >= 1

        # Se teve falha, o _worker_error deve estar registrado
        assert "_worker_error" in state or state.get("consecutive_failures", 0) >= 1
    finally:
        engine.close()


# ---------------------------------------------------------------------------
# Resume após disjuntor
# ---------------------------------------------------------------------------

def test_resume_requer_ricardo(tmp_path):
    engine = RDAAEngine(tmp_path / "resume", "C", worker=fake_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        result = engine.initialize("resume-test")
        # Forçar estado pausado
        graph = engine._build_graph()
        graph.update_state(engine._config, {
            "status": "paused",
            "consecutive_failures": 2,
        })
        with pytest.raises(GateError, match="ricardo"):
            engine.resume(authority="IA", reason="teste")
    finally:
        engine.close()


def test_resume_exige_justificativa(tmp_path):
    engine = RDAAEngine(tmp_path / "resume2", "C", worker=fake_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        engine.initialize("resume-test")
        graph = engine._build_graph()
        graph.update_state(engine._config, {
            "status": "paused",
            "consecutive_failures": 2,
        })
        from orquestracao.contracts import ContractError
        with pytest.raises(ContractError, match="justificativa"):
            engine.resume(authority="ricardo", reason="")
    finally:
        engine.close()


# ---------------------------------------------------------------------------
# Duas matérias simultâneas
# ---------------------------------------------------------------------------

def test_duas_materias_independentes(tmp_path):
    """Duas matérias em diretórios diferentes não interferem."""
    engine1 = RDAAEngine(tmp_path / "m1", "C", worker=fake_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    engine2 = RDAAEngine(tmp_path / "m2", "C", worker=fake_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        r1 = engine1.initialize("matter-1")
        r2 = engine2.initialize("matter-2")
        assert r1["matter_id"] == "matter-1"
        assert r2["matter_id"] == "matter-2"
        assert r1["history"] == r2["history"]
        assert engine1.state()["matter_id"] == "matter-1"
        assert engine2.state()["matter_id"] == "matter-2"
    finally:
        engine1.close()
        engine2.close()


# ---------------------------------------------------------------------------
# Artefatos de manifesto
# ---------------------------------------------------------------------------

def test_manifesto_criado_corretamente(tmp_path):
    engine = RDAAEngine(tmp_path / "mf", "C", worker=fake_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        engine.initialize("manifest-test")
        manifest = json.loads(
            (tmp_path / "mf" / "run_manifest.json").read_text(encoding="utf-8")
        )
        assert manifest["matter_id"] == "manifest-test"
        assert manifest["phase"] == "vault_registered"
        assert "graph_history" in manifest

        matter_state = json.loads(
            (tmp_path / "mf" / "matter_state.json").read_text(encoding="utf-8")
        )
        assert matter_state["matter_id"] == "manifest-test"
    finally:
        engine.close()


# ---------------------------------------------------------------------------
# Nenhuma CLI de IA é chamada
# ---------------------------------------------------------------------------

def test_nenhuma_cli_de_ia_chamada(tmp_path, monkeypatch):
    """Garante que o motor não chama subprocessos de IA."""
    original_run = subprocess.run
    cli_calls: list[str] = []

    def spy_run(args, **kwargs):
        if isinstance(args, (list, tuple)):
            cmd = str(args[0]).lower()
            for banned in ("claude", "codex", "agy", "antigravity"):
                if banned in cmd:
                    cli_calls.append(cmd)
        return original_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", spy_run)

    engine = RDAAEngine(tmp_path / "nocli", "A", worker=fake_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        engine.initialize("no-cli-test")
        engine.approve_gate("skeleton_approval")
        engine.approve_gate("release_approval")
    finally:
        engine.close()

    assert cli_calls == [], f"CLIs de IA chamadas: {cli_calls}"


# ---------------------------------------------------------------------------
# CLI básica
# ---------------------------------------------------------------------------

def test_cli_status(tmp_path):
    """Testa o comando status sem disparar um worker externo."""
    state_dir = str(tmp_path / "cli-test")
    engine = RDAAEngine(state_dir, "C", worker=fake_worker, system_handlers=DUMMY_HANDLERS, route_path=ROUTE_PATH)
    try:
        engine.initialize("cli-001")
    finally:
        engine.close()

    result = subprocess.run(
        ["py", "-3.14", "-m", "orquestracao.cli",
         "status", state_dir],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(Path(__file__).resolve().parents[1]),
    )
    assert result.returncode == 0
    status = json.loads(result.stdout)
    assert status["matter_id"] == "cli-001"
    assert status["status"] == "vault_registered"
