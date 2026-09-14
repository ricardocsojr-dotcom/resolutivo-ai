"""E2E do motor LangGraph: A, B e C sem transições implícitas."""
import json
from pathlib import Path

import pytest

from orquestracao.langgraph_engine import RDAALangGraph


def fake_worker(role, state):
    return {"role": role, "phase_seen": state.get("phase")}


def route(level):
    return json.loads((Path(__file__).parents[1] / "orquestracao" / "roteamento.json").read_text(encoding="utf-8"))["levels"][level]["stages"]


@pytest.mark.parametrize("level", ["A", "B", "C"])
def test_rotas_e2e_langgraph_sem_pular_fases(tmp_path, level):
    state_dir = tmp_path / f"matter-{level}"
    engine = RDAALangGraph(state_dir, level, worker=fake_worker)
    try:
        result = engine.initialize(f"matter-{level}")
        if level in {"A", "B"}:
            result = engine.approve_gate("skeleton_approval")
        if level == "A":
            result = engine.approve_gate("release_approval")
        assert result["phase"] == "vault_registered"
        assert result["history"] == route(level)
        assert (state_dir / "langgraph.sqlite").is_file()
        assert (state_dir / "run_manifest.json").is_file()
        assert (state_dir / "matter_state.json").is_file()
    finally:
        engine.close()


def test_rota_a_obrigatoriamente_executa_critic(tmp_path):
    calls = []

    def worker(role, state):
        calls.append(role)
        return {"ok": True}

    engine = RDAALangGraph(tmp_path / "a", "A", worker=worker)
    try:
        engine.initialize("premium")
        engine.approve_gate("skeleton_approval")
        engine.approve_gate("release_approval")
        assert calls == ["planner", "writer", "critic", "validator"]
        history = engine.state()["history"]
        assert history[history.index("draft_ready") + 1 : history.index("validating")] == ["criticizing", "critique_ready"]
        assert "criticizing" in history
        assert "critique_ready" in history
    finally:
        engine.close()


def test_checkpoint_sobrevive_reabertura(tmp_path):
    state_dir = tmp_path / "persisted"
    first = RDAALangGraph(state_dir, "A", worker=fake_worker)
    first.initialize("persisted-matter")
    first.close()

    second = RDAALangGraph(state_dir, "A", worker=fake_worker)
    try:
        assert second.state()["phase"] == "skeleton_ready"
        assert second.state()["history"][-1] == "skeleton_ready"
    finally:
        second.close()
