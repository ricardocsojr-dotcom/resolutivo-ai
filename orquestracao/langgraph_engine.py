"""Motor principal do fluxo RDAA baseado em LangGraph.

O grafo, e não um worker, controla todas as transições. O manifesto JSON é uma
projeção auditável; o checkpoint autoritativo do grafo fica em ``state_dir``.
Workers são callbacks injetáveis para que produção possa chamar as CLIs e E2E
possa usar funções determinísticas.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

ROOT = Path(__file__).resolve().parents[1]
ROUTE_PATH = ROOT / "orquestracao" / "roteamento.json"
ROLE_PHASE = {"planner": "sources_ready", "writer": "draft_ready", "critic": "critique_ready", "validator": "candidate_ready"}
HUMAN_GATES = {"awaiting_skeleton_approval": "skeleton_approval", "release_ready": "release_approval"}


class RDAAState(TypedDict, total=False):
    matter_id: str
    nivel_peca: str
    phase: str
    history: list[str]
    outputs: dict[str, Any]
    approvals: dict[str, bool]
    status: str
    state_dir: str


Worker = Callable[[str, RDAAState], dict[str, Any] | None]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _route(level: str, route_path: Path = ROUTE_PATH) -> dict[str, Any]:
    level = str(level).strip().upper()
    payload = json.loads(route_path.read_text(encoding="utf-8"))
    if level not in {"A", "B", "C"} or not isinstance(payload.get("levels", {}).get(level), dict):
        raise ValueError("nivel_peca deve ser A, B ou C")
    return payload["levels"][level]


def build_rdaa_graph(level: str, *, worker: Worker | None = None, checkpointer: Any = None, route_path: Path = ROUTE_PATH):
    """Constrói um StateGraph linear, com papéis reais como nós de execução."""
    spec = _route(level, route_path)
    stages = list(spec["stages"])
    roles_by_phase = {phase: role for role, phase in ROLE_PHASE.items() if role in spec.get("workers", {}) and phase in stages}
    # Fases governamentais sem worker continuam sendo nós, portanto não são puladas.
    graph = StateGraph(RDAAState)

    def make_node(phase: str, role: str | None):
        def node(state: RDAAState) -> dict[str, Any]:
            gate = HUMAN_GATES.get(phase)
            if gate and gate in spec.get("required_human_gates", []) and not state.get("approvals", {}).get(gate):
                raise PermissionError(f"aprovação humana exigida para {gate}")
            updates: dict[str, Any] = {"phase": phase}
            history = list(state.get("history", [])) + [phase]
            updates["history"] = history
            if role and worker:
                result = worker(role, state) or {}
                outputs = dict(state.get("outputs", {}))
                outputs[role] = result
                updates["outputs"] = outputs
            _project_checkpoint(state, phase, history, role, updates)
            return updates
        return node

    for phase in stages:
        graph.add_node(phase, make_node(phase, roles_by_phase.get(phase)))
    graph.add_edge(START, stages[0])
    for previous, current in zip(stages, stages[1:]):
        graph.add_edge(previous, current)
    graph.add_edge(stages[-1], END)
    return graph.compile(checkpointer=checkpointer, interrupt_before=[p for p in stages if HUMAN_GATES.get(p) in spec.get("required_human_gates", [])])


def _project_checkpoint(state: RDAAState, phase: str, history: list[str], role: str | None, updates: dict[str, Any]) -> None:
    """Atualiza manifest/matter_state como projeção; não decide o próximo nó."""
    state_dir = state.get("state_dir")
    if not state_dir:
        return
    root = Path(str(state_dir))
    path = root / "run_manifest.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        manifest["phase"] = phase
        manifest["status"] = "awaiting_approval" if phase in HUMAN_GATES else "ready"
        manifest["updated_at"] = _now()
        manifest["graph_history"] = history
        if role:
            manifest.setdefault("graph_executions", []).append({"role": role, "phase": phase, "at": _now()})
        serialized = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        path.write_text(serialized, encoding="utf-8")
        (root / "matter_state.json").write_text(json.dumps({"matter_id": state.get("matter_id"), "nivel_peca": state.get("nivel_peca"), "phase": phase, "status": manifest["status"], "history": history}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        # Uma projeção não pode alterar a execução do checkpoint.
        return


class RDAALangGraph:
    """Facade persistente: um SQLite de checkpoints por diretório de execução."""

    def __init__(self, state_dir: str | Path, nivel_peca: str, *, worker: Worker | None = None, route_path: Path = ROUTE_PATH):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.nivel_peca = str(nivel_peca).strip().upper()
        self.worker = worker
        self._conn = sqlite3.connect(self.state_dir / "langgraph.sqlite", check_same_thread=False)
        self._checkpointer = SqliteSaver(self._conn)
        self._checkpointer.setup()
        self.graph = build_rdaa_graph(self.nivel_peca, worker=worker, checkpointer=self._checkpointer, route_path=route_path)
        self.config = {"configurable": {"thread_id": self._thread_id()}}

    def _thread_id(self) -> str:
        return str(self.state_dir.resolve())

    def initialize(self, matter_id: str) -> RDAAState:
        existing = self.state()
        if existing.get("history"):
            return existing
        route = _route(self.nivel_peca)
        manifest_path = self.state_dir / "run_manifest.json"
        if not manifest_path.exists():
            manifest_path.write_text(json.dumps({"matter_id": matter_id, "phase": "initialized", "status": "ready", "route": route, "created_at": _now(), "updated_at": _now()}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        state: RDAAState = {"matter_id": matter_id, "nivel_peca": self.nivel_peca, "phase": "initialized", "history": [], "outputs": {}, "approvals": {}, "status": "ready", "state_dir": str(self.state_dir)}
        return self.graph.invoke(state, self.config)

    def run(self, *, input_state: dict[str, Any] | None = None) -> RDAAState:
        return self.graph.invoke(input_state, self.config)

    def state(self) -> RDAAState:
        snapshot = self.graph.get_state(self.config)
        return dict(snapshot.values)  # type: ignore[return-value]

    def approve_gate(self, gate: str, *, approved_by: str = "ricardo") -> RDAAState:
        if str(approved_by).strip().casefold() != "ricardo":
            raise PermissionError("authority ricardo exigida para aprovação humana")
        current = self.state()
        stages = list(_route(self.nivel_peca).get("stages", []))
        phase = current.get("phase", "")
        next_phase = stages[stages.index(phase) + 1] if phase in stages and stages.index(phase) + 1 < len(stages) else None
        expected = HUMAN_GATES.get(next_phase or phase)
        if expected != gate:
            raise ValueError(f"gate não está aberto: {gate}")
        approvals = dict(current.get("approvals", {})); approvals[gate] = True
        self.graph.update_state(self.config, {"approvals": approvals, "status": "ready"})
        return self.graph.invoke(None, self.config)

    def close(self) -> None:
        self._conn.close()


def run_workflow(state_dir: str | Path, matter_id: str, nivel_peca: str, *, worker: Worker | None = None) -> RDAAState:
    engine = RDAALangGraph(state_dir, nivel_peca, worker=worker)
    try:
        return engine.initialize(matter_id)
    finally:
        engine.close()
