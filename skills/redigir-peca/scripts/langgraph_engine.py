#!/usr/bin/env python3
"""
RDAA Workflow Engine (LangGraph Canonical)
CLI universal para clientes (Hermes, Codex, Claude Code, bash, N8N, etc).
"""

import os
import sys
import json
import sqlite3
import argparse
import hashlib
from typing import TypedDict, Any, Literal
from pathlib import Path
from copy import deepcopy

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

ROOT_DIR = Path(__file__).resolve().parents[3]
ROTEAMENTO_PATH = ROOT_DIR / "orquestracao" / "roteamento.json"

class RDAAState(TypedDict):
    matter_id: str
    nivel: str
    phase_idx: int
    phase_name: str
    status: str
    failures: int
    data: dict[str, Any]
    hashes: dict[str, str]
    identity: dict[str, dict[str, str]]

def _load_route() -> dict:
    if not ROTEAMENTO_PATH.exists():
        raise FileNotFoundError(f"Missing {ROTEAMENTO_PATH}")
    return json.loads(ROTEAMENTO_PATH.read_text(encoding="utf-8"))

def _write_manifest(state_dir: Path, state: dict):
    """Gera projeções imutáveis para legados/audit trails e protege de adulterações."""
    mf = state_dir / "run_manifest.json"
    ms = state_dir / "matter_state.json"

    route = _load_route()["levels"].get(state["nivel"], {})

    manifest_doc = {
        "matter_id": state["matter_id"],
        "version": "langgraph-canonical",
        "route": route,
        "identity": state.get("identity", {}),
        "stage": {
            "current_stage": state["phase_name"],
            "status": state["status"]
        },
        "gates": state["data"].get("gates", {}),
        "circuit_breaker": {
            "status": state["status"],
            "failures": state["failures"],
            "manual_intervention": state["data"].get("intervention")
        },
        "artifacts_hash": state.get("hashes", {})
    }

    mf.write_text(json.dumps(manifest_doc, indent=2, ensure_ascii=False), encoding="utf-8")

    # State minimal retrocompatível
    ms.write_text(json.dumps({"matter_id": state["matter_id"], "locked": state["status"] == "paused"}, indent=2), encoding="utf-8")

def execute_stage(state: RDAAState) -> RDAAState:
    # Apenas rehidrata a state para não violar mutabilidade de python no graph.
    new_state = deepcopy(state)
    return new_state

def router(state: RDAAState) -> str:
    # End node?
    route = _load_route()["levels"].get(state["nivel"])
    stages = route["stages"]

    if state["status"] == "paused":
        return "paused"
    if state["phase_idx"] >= len(stages):
        return END
    return stages[state["phase_idx"]]

def build_graph(nivel: str) -> StateGraph:
    cfg = _load_route()["levels"].get(nivel)
    if not cfg:
        raise ValueError(f"Nível de peça não encontrado: {nivel}")

    stages = cfg["stages"]

    # Grafo principal
    graph = StateGraph(RDAAState)

    # Todos os stages do mapeamento atuam como nós. As tréguas de autorização/locks
    # são resolvidas pela interface com `update_state` antes de transicionar.
    for stg in stages:
        graph.add_node(stg, execute_stage)

    graph.add_node("paused", execute_stage)

    # Transição inicial (a start invoca a progressão que parará apenas na exigência de client action)
    graph.add_edge(START, stages[0])

    return graph

class EngineCLI:
    def __init__(self, state_dir: str):
        self.state_dir = Path(state_dir).resolve()
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.state_dir / "langgraph.sqlite"

    def _execute(self, action: str, p_next: str | None = None, payload: dict | None = None) -> dict:
        payload = payload or {}
        config = {"configurable": {"thread_id": "rdaa-thread"}}

        with sqlite3.connect(str(self.db_path), check_same_thread=False) as conn:
            saver = SqliteSaver(conn)
            curr = saver.get_tuple(config)

            if not curr and action != "start":
                return {"error": "Máquina não inicializada.", "status": "blocked"}

            if action == "start":
                if curr: return {"error": "Máquina já rodando", "state": curr.checkpoint["channel_values"]}
                nivel = payload.get("nivel_peca", "B")
                initial_state: RDAAState = {
                    "matter_id": payload.get("matter_id", "matter-unset"),
                    "nivel": nivel,
                    "phase_idx": 0,
                    "phase_name": _load_route()["levels"][nivel]["stages"][0],
                    "status": "executing",
                    "failures": 0,
                    "data": {},
                    "hashes": {},
                    "identity": {}
                }

                graph = build_graph(nivel)
                app = graph.compile(checkpointer=saver)

                # Ativa initial state
                app.update_state(config, initial_state)
                # Proteção E2E Cérebro e lock auditável
                _write_manifest(self.state_dir, initial_state)

                return {"message": "Started", "current_stage": initial_state["phase_name"]}

            """ --- COMANDOS PARA ENGINE YA ATIVA --- """
            state: RDAAState = curr.checkpoint["channel_values"]
            app = build_graph(state["nivel"]).compile(checkpointer=saver)
            cfg_route = _load_route()["levels"][state["nivel"]]
            stg_list = cfg_route["stages"]
            current_stage_name = state["phase_name"]

            if action == "status":
                return {"stage": current_stage_name, "status": state["status"], "failures": state["failures"]}

            # Verifica disjuntor em TODOS OS RESTANTES
            if state["status"] == "paused" and action != "resume":
                return {"error": "O circuito está aberto (status: paused). Somente 'resume' por supervisor levanta a matéria.", "status": "blocked"}

            if action == "next":
                # Responde qual o papel que deve conduzir essa fase, o pacote minimo a entregar e a politica.
                # Se for fase de gate humano, responde com bloqueio pendente.
                if "awaiting_" in current_stage_name:
                    return {"instruction": f"Aguardando humano (gate) no estágio {current_stage_name}."}

                # Resgate do worker (quem opera este nó segundo a politica do orquestrador_rdaa?)
                w = cfg_route["workers"].get(current_stage_name, {"cli": "unknown", "role": "unknown"})
                return {
                    "action": "GO",
                    "phase": current_stage_name,
                    "worker_expected": w,
                    "artifacts_expected": ["hash_da_saida_para_lock"],
                }

            if action == "submit":
                if "awaiting_" in current_stage_name:
                    return {"error": "Não use submit em gate humano, use 'approve' ou 'fail'."}

                nstate = deepcopy(state)
                nstate["failures"] = 0 # reset upon success
                nstate["phase_idx"] += 1

                # Registro da Identidade do Worker que submeteu o pacote
                worker_cli = payload.get("worker_cli", "unknown")
                nstate["identity"][current_stage_name] = {"cli": worker_cli}

                if "hash" in payload:
                    nstate["hashes"][current_stage_name] = payload["hash"]

                if nstate["phase_idx"] < len(stg_list):
                    nstate["phase_name"] = stg_list[nstate["phase_idx"]]
                else:
                    nstate["phase_name"] = "DONE"
                    nstate["status"] = "completed"

                app.update_state(config, nstate)
                _write_manifest(self.state_dir, nstate)
                return {"action": "ACCEPTED", "next_stage": nstate["phase_name"]}

            if action == "fail":
                # Lógica fundamental do circuito (disjuntor de limite de falhas = 2)
                f = state["failures"] + 1
                nstate = deepcopy(state)
                nstate["failures"] = f

                if f >= 2:
                    nstate["status"] = "paused"
                    nstate["data"]["intervention"] = payload.get("reason", "Violou max_failures == 2")
                    resp = {"action": "CIRCUIT_TRIPPED", "status": "paused"}
                else:
                    # Falha não paralisa, ainda tentável na current_stage (pode route para revision na redação, que faz o fallback manual se programado no futuro).
                    resp = {"action": "FAIL_REGISTERED", "failures": f}

                app.update_state(config, nstate)
                _write_manifest(self.state_dir, nstate)
                return resp

            if action == "approve":
                if "awaiting_" not in current_stage_name:
                    return {"error": "Fase atual não suporta approve() ou gate humano."}

                if payload.get("authority") != "ricardo":
                    return {"error": "Somente authority: ricardo pode emitir approve em gates."}

                nstate = deepcopy(state)
                nstate["data"].setdefault("gates", {})[current_stage_name] = "approved_by_ricardo"
                nstate["phase_idx"] += 1
                if nstate["phase_idx"] < len(stg_list):
                    nstate["phase_name"] = stg_list[nstate["phase_idx"]]
                else:
                    nstate["phase_name"] = "DONE"

                app.update_state(config, nstate)
                _write_manifest(self.state_dir, nstate)
                return {"action": "APPROVED", "next_stage": nstate["phase_name"]}

            if action == "resume":
                if payload.get("authority") != "ricardo":
                    return {"error": "Somente authority: ricardo pode efetuar o bypass (resume) do disjuntor pausado."}

                if state["status"] != "paused":
                    return {"error": "Disjuntor não operou, matéria não está pausada."}

                nstate = deepcopy(state)
                nstate["status"] = "executing"
                nstate["failures"] = 0  # retry concedido
                nstate["data"]["intervention"] = "Resumed by Ricardo: " + payload.get("reason", "")

                app.update_state(config, nstate)
                _write_manifest(self.state_dir, nstate)
                return {"action": "RESUMED", "status": "executing", "stage": nstate["phase_name"]}

            return {"error": f"Unknown command {action}"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["start", "status", "next", "submit", "approve", "fail", "resume"])
    parser.add_argument("state_dir")
    parser.add_argument("--payload", default="{}")
    args = parser.parse_args()

    try:
        cli = EngineCLI(args.state_dir)
        payload = json.loads(args.payload)
        res = cli._execute(args.command, payload=payload)
    except Exception as e:
        res = {"error": str(e), "status": "exception"}

    print(json.dumps(res, indent=2, ensure_ascii=False))
    # Falha dura se erro (protecao CLI de falhas silenciosas ignoradas como ocorriam no motor velho):
    if "error" in res:
        sys.exit(1)

if __name__ == "__main__":
    main()
