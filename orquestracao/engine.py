"""Motor RDAA V4 — grafo LangGraph único e canônico.

O grafo, e não um worker, controla todas as transições.  Workers são
callbacks injetáveis: produção injeta chamadas HTTP ao OmniRoute; testes
injetam funções determinísticas.

Invariantes V4 (§2):
- Uma única implementação do motor.
- Nenhuma resposta de modelo ou cliente escolhe a próxima fase.
- Cada etapa recebe somente o contexto necessário.
- Skills contêm inteligência; Python controla execução e estado.
- Falha de persistência bloqueia o fluxo.
- Ricardo é a única autoridade para gates, retomada e aborto.

Estrutura:
- ``build_rdaa_graph``: constrói o StateGraph para um nível (A/B/C).
- ``RDAAEngine``: facade persistente com SQLite por matéria.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from orquestracao.contracts import (
    CircuitBreakerError,
    ContractError,
    GateError,
    HUMAN_GATES,
    RDAAState,
    ROLE_OUTPUT_PHASE,
    load_route,
    sha256_file,
    sha256_text,
    validate_level,
)

# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------

Worker = Callable[[str, RDAAState], dict[str, Any] | None]
"""Callback de worker: (role, state) → saída ou None."""

SystemHandler = Callable[[RDAAState], dict[str, Any] | None]
"""Callback de handler de sistema (não-IA): (state) → saída ou None.

Usado para fases determinísticas que não envolvem chamada a um Combo —
QA, publicação, registro no Cérebro-Ricar.  Segue exatamente o
mesmo tratamento de falha e disjuntor que os workers de IA."""

ROOT = Path(__file__).resolve().parents[1]
ROUTE_PATH = ROOT / "orquestracao" / "roteamento.json"

MAX_CONSECUTIVE_FAILURES = 2


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Construtor do grafo
# ---------------------------------------------------------------------------

def build_rdaa_graph(
    level: str,
    *,
    worker: Worker | None = None,
    system_handlers: dict[str, SystemHandler] | None = None,
    checkpointer: Any = None,
    route_path: Path = ROUTE_PATH,
) -> Any:
    """Constrói um StateGraph linear com nós de execução e gates humanos.

    Cada fase da rota vira um nó.  Se a fase tem um papel associado
    (planner → sources_ready, writer → draft_ready, etc.) e um worker
    foi injetado, o worker é chamado dentro do nó.

    Fases de sistema (não-IA) — QA, publicação, registro no vault — podem
    ter um ``SystemHandler`` associado via ``system_handlers``.  Handlers
    de sistema seguem o mesmo tratamento de falha e disjuntor que
    workers de IA, mas não usam papel/Combo.

    Gates humanos (awaiting_skeleton_approval, release_ready) são
    configurados como ``interrupt_before`` para que o LangGraph pause
    a execução e aguarde aprovação explícita.
    """
    level = validate_level(level)
    spec = load_route(level, route_path)
    stages: list[str] = list(spec["stages"])
    system_handlers = system_handlers or {}

    # Mapeamento fase → papel (invertido de ROLE_OUTPUT_PHASE)
    roles_by_phase: dict[str, str] = {}
    workers_in_route = spec.get("workers", {})
    for role, output_phase in ROLE_OUTPUT_PHASE.items():
        if role in workers_in_route and output_phase in stages:
            roles_by_phase[output_phase] = role

    graph = StateGraph(RDAAState)

    def _make_node(phase: str, role: str | None):
        """Fábrica de nós — captura phase e role por closure."""

        def node(state: RDAAState) -> dict[str, Any]:
            # 1. Verificar gate humano
            gate = HUMAN_GATES.get(phase)
            if gate and gate in spec.get("required_human_gates", []):
                if not state.get("approvals", {}).get(gate):
                    raise GateError(
                        f"aprovação humana exigida para {gate}"
                    )

            # 2. Verificar disjuntor
            if state.get("consecutive_failures", 0) >= MAX_CONSECUTIVE_FAILURES:
                raise CircuitBreakerError(
                    f"disjuntor aberto: {state['consecutive_failures']} "
                    f"falhas consecutivas na fase {phase}"
                )

            # 3. Preparar atualizações
            updates: dict[str, Any] = {"phase": phase}
            history = list(state.get("history", [])) + [phase]
            updates["history"] = history

            # 4. Executar worker (papel de IA) ou handler de sistema (não-IA)
            handler = system_handlers.get(phase)
            label = role if role else (f"system:{phase}" if handler else f"system:{phase}")
            executor: Any = None
            if role and worker:
                executor = lambda: worker(role, state)
            elif handler:
                executor = lambda: handler(state)
            elif not role and phase in ("qa_passed", "published", "vault_registered"):
                def fail_on_missing_handler():
                    raise ContractError(f"handler de sistema obrigatorio ausente para fase critica '{phase}'")
                executor = fail_on_missing_handler

            if executor is not None:
                try:
                    result = executor() or {}
                    outputs = dict(state.get("outputs", {}))
                    outputs[label] = result
                    updates["outputs"] = outputs
                    updates["consecutive_failures"] = 0
                    # Registrar execução
                    executions = list(state.get("executions", []))
                    executions.append({
                        "role": label,
                        "phase": phase,
                        "at": _now(),
                        "outcome": "ok",
                    })
                    updates["executions"] = executions
                except Exception as exc:
                    # Registrar falha e incrementar disjuntor.
                    # IMPORTANTE: retornamos as atualizações de falha em vez de
                    # propagar a exceção, para que o LangGraph persista o estado
                    # com o disjuntor atualizado.
                    cf = state.get("consecutive_failures", 0) + 1
                    failures = dict(state.get("failures", {}))
                    failures[phase] = failures.get(phase, 0) + 1
                    updates["consecutive_failures"] = cf
                    updates["failures"] = failures
                    executions = list(state.get("executions", []))
                    executions.append({
                        "role": label,
                        "phase": phase,
                        "at": _now(),
                        "outcome": "error",
                        "error": str(exc),
                    })
                    updates["executions"] = executions
                    if cf >= MAX_CONSECUTIVE_FAILURES:
                        updates["status"] = "paused"
                    else:
                        # Falha isolada (abaixo do limiar do disjuntor): a fase
                        # NÃO é considerada concluída — o grafo interrompe a
                        # travessia aqui.  QA reprovado, publicação ou registro
                        # no vault com falha NUNCA seguem para a próxima aresta.
                        updates["status"] = "failed"
                    # Retorna com status de falha em vez de propagar — o grafo
                    # persiste o checkpoint e quem invocou pode ler o status.
                    updates["_worker_error"] = str(exc)
                    _project_manifest(state, phase, history, label, updates)
                    return updates

            # 5. Atualizar status
            if phase in HUMAN_GATES and HUMAN_GATES[phase] in spec.get("required_human_gates", []):
                updates["status"] = "awaiting_approval"
            elif phase == stages[-1]:
                updates["status"] = "vault_registered"
            else:
                updates["status"] = "executing"

            # 6. Projetar manifesto
            _project_manifest(state, phase, history, label, updates)

            return updates

        return node

    # Criar nós
    for phase in stages:
        role = roles_by_phase.get(phase)
        graph.add_node(phase, _make_node(phase, role))

    # Criar arestas lineares, condicionadas ao sucesso da fase anterior.
    # Se a fase que acabou de rodar terminou em "failed" ou "paused"
    # (erro de worker/handler, QA reprovado, publicação ou vault com
    # falha), o grafo INTERROMPE a travessia em vez de seguir para a
    # próxima etapa — falha nunca é silenciosamente ultrapassada.
    def _make_router(next_phase: str):
        def router(state: RDAAState) -> str:
            if state.get("status") in ("failed", "paused", "aborted"):
                return END
            return next_phase
        return router

    graph.add_edge(START, stages[0])
    for prev_phase, next_phase in zip(stages, stages[1:]):
        graph.add_conditional_edges(
            prev_phase,
            _make_router(next_phase),
            {next_phase: next_phase, END: END},
        )
    graph.add_edge(stages[-1], END)

    # Gates humanos como interrupt_before
    interrupt_phases = [
        p for p in stages
        if HUMAN_GATES.get(p) in spec.get("required_human_gates", []) or p in roles_by_phase
    ]

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=interrupt_phases,
    )


# ---------------------------------------------------------------------------
# Projeção de manifesto (não decide transições)
# ---------------------------------------------------------------------------

def _project_manifest(
    state: RDAAState,
    phase: str,
    history: list[str],
    role: str | None,
    updates: dict[str, Any],
) -> None:
    """Atualiza run_manifest.json e matter_state.json como projeção auditável.

    A projeção nunca decide o próximo nó — isso é do grafo.
    """
    state_dir = state.get("state_dir")
    if not state_dir:
        return

    root = Path(str(state_dir))
    manifest_path = root / "run_manifest.json"
    matter_state_path = root / "matter_state.json"

    try:
        # Ler manifesto existente ou criar novo
        manifest: dict[str, Any] = {}
        if manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        # Atualizar campos
        manifest["matter_id"] = state.get("matter_id", "")
        manifest["nivel_peca"] = state.get("nivel_peca", "")
        manifest["phase"] = phase
        manifest["status"] = updates.get("status", "executing")
        manifest["updated_at"] = _now()
        manifest["graph_history"] = history

        if role:
            manifest.setdefault("graph_executions", []).append({
                "role": role,
                "phase": phase,
                "at": _now(),
            })

        # Escrever manifesto
        serialized = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        manifest_path.write_text(serialized, encoding="utf-8")

        # Escrever matter_state
        matter_state = {
            "matter_id": state.get("matter_id", ""),
            "nivel_peca": state.get("nivel_peca", ""),
            "phase": phase,
            "status": manifest["status"],
            "history": history,
        }
        matter_state_path.write_text(
            json.dumps(matter_state, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, json.JSONDecodeError):
        # Projeção não pode bloquear a execução do grafo
        return


# ---------------------------------------------------------------------------
# Facade persistente
# ---------------------------------------------------------------------------

def _fases_mecanicas_puladas(
    stages: list[str], current_idx: int, target_idx: int, system_handlers: dict[str, Any]
) -> list[str]:
    """Fases com system_handler determinístico que um jump para frente pularia sem rodar."""
    if target_idx <= current_idx:
        return []
    return [p for p in stages[current_idx + 1 : target_idx] if p in system_handlers]


class RDAAEngine:
    """Facade que gerencia uma matéria com SQLite de checkpoints.

    Comandos:
    - ``initialize``: cria estado inicial e roda até o primeiro gate
    - ``approve_gate``: aprova um gate humano e continua
    - ``state``: retorna o estado corrente
    - ``resume``: retoma após disjuntor (requer authority: ricardo)
    - ``close``: fecha a conexão SQLite
    """

    def __init__(
        self,
        state_dir: str | Path,
        nivel_peca: str,
        *,
        worker: Worker | None = None,
        system_handlers: dict[str, SystemHandler] | None = None,
        route_path: Path = ROUTE_PATH,
    ):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.nivel_peca = validate_level(nivel_peca)
        self.worker = worker
        self.system_handlers = system_handlers or {}
        self.route_path = route_path
        self._conn = sqlite3.connect(
            str(self.state_dir / "langgraph.sqlite"),
            check_same_thread=False,
        )
        self._saver = SqliteSaver(self._conn)
        self._config = {"configurable": {"thread_id": "rdaa-main"}}
        self._spec = load_route(self.nivel_peca, self.route_path)

    def _build_graph(self):
        return build_rdaa_graph(
            self.nivel_peca,
            worker=self.worker,
            system_handlers=self.system_handlers,
            checkpointer=self._saver,
            route_path=self.route_path,
        )

    def _check_duplicate_attempt(self, matter_id: str) -> None:
        """Bloqueia reinício com o mesmo input que já reprovou noutro state_dir.

        Contorno real observado: reexecutar em um ``state_dir`` novo
        (ex.: ``-v2``, ``-v3``) reseta ``consecutive_failures`` a 0, porque
        o disjuntor vive no estado daquele diretório -- então o disjuntor
        nunca vê a repetição como consecutiva. Esta checagem cobre esse
        contorno comparando o hash do input com o de tentativas irmãs
        (mesmo ``matter_id``, diretórios ao lado) que já reprovaram.
        """
        input_paths = [
            self.state_dir / "packages" / "writer-input.md",
            self.state_dir / "packages" / "planner-input.md",
        ]
        current_hash = None
        current_path = None
        for path in input_paths:
            if path.is_file():
                current_hash = sha256_file(path)
                current_path = path
                break
        if current_hash is None:
            return  # nada gravado ainda (fluxo omniroute, ou fase inicial) -- nada a comparar

        parent = self.state_dir.parent
        if not parent.is_dir():
            return

        for sibling in parent.iterdir():
            if not sibling.is_dir() or sibling.resolve() == self.state_dir.resolve():
                continue
            matter_state_path = sibling / "matter_state.json"
            if not matter_state_path.is_file():
                continue
            try:
                sibling_state = json.loads(matter_state_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if sibling_state.get("matter_id") != matter_id:
                continue
            # Só bloqueia se o irmão de fato pausou por exaustão de tentativas
            # (disjuntor estourado). Diretórios temporários de teste têm
            # matter_id igual mas NUNCA estouram o disjuntor -- não confundir.
            if sibling_state.get("consecutive_failures", 0) < MAX_CONSECUTIVE_FAILURES:
                continue
            sibling_input = sibling / "packages" / current_path.name
            if not sibling_input.is_file():
                continue
            if sha256_file(sibling_input) == current_hash:
                raise ContractError(
                    f"tentativa duplicada bloqueada: {current_path.name} tem o "
                    f"mesmo conteúdo (sha256) de uma tentativa que já reprovou em "
                    f"{sibling.name} (fase {sibling_state.get('phase')!r}, "
                    f"status {sibling_state.get('status')!r}). Corrija o conteúdo "
                    f"antes de tentar de novo, ou rode "
                    f"`cli resume {sibling} --authority ricardo --reason ...` "
                    f"no diretório original em vez de criar um novo state_dir."
                )

    def initialize(self, matter_id: str) -> dict[str, Any]:
        """Cria estado inicial e executa até o primeiro gate ou conclusão."""
        self._check_duplicate_attempt(matter_id)
        initial: RDAAState = {
            "matter_id": matter_id,
            "nivel_peca": self.nivel_peca,
            "phase": "",
            "status": "executing",
            "history": [],
            "outputs": {},
            "approvals": {},
            "failures": {},
            "consecutive_failures": 0,
            "options": {},
            "hashes": {},
            "state_dir": str(self.state_dir),
            "route": self._spec,
            "executions": [],
            "vault": {"lookups": [], "syncs": []},
            "transitions": [],
        }

        graph = self._build_graph()
        result = graph.invoke(initial, config=self._config)
        return result

    def approve_gate(self, gate: str, *, authority: str = "ricardo") -> dict[str, Any]:
        """Aprova um gate humano e continua a execução."""
        if authority.strip().casefold() != "ricardo":
            raise GateError("somente authority: ricardo pode aprovar gates")

        # Obter estado corrente
        current = self.state()
        if not current:
            raise ContractError("nenhum estado encontrado")

        # Registrar aprovação
        approvals = dict(current.get("approvals", {}))
        planner = current.get("outputs", {}).get("planner", {})
        planner_text = planner.get("content", "") if isinstance(planner, dict) else str(planner)
        approvals[gate] = {
            "approved": True,
            "approved_by": authority,
            "approved_at": _now(),
            "artifact_sha256": sha256_text(planner_text) if gate == "skeleton_approval" and planner_text else "",
        }

        # Atualizar estado e continuar
        graph = self._build_graph()
        graph.update_state(self._config, {"approvals": approvals})
        result = graph.invoke(None, config=self._config)
        return result

    def step(self, *, authority: str = "ricardo") -> dict[str, Any]:
        """Avança a execução quando pausada antes de um Worker."""
        if authority.strip().casefold() != "ricardo":
            raise GateError("somente authority: ricardo pode comandar step")
        current = self.state()
        if not current:
            raise ContractError("nenhum estado encontrado")
        graph = self._build_graph()
        return graph.invoke(None, config=self._config)

    def jump(self, target_phase: str, *, reason: str = "", authority: str = "ricardo") -> dict[str, Any]:
        """Pula etapas intermediárias saltando imediatamente para a target_phase fornecida.

        Nunca pula por cima de uma fase mecânica (system_handlers determinístico,
        ex. qa_passed/published/vault_registered): essas só podem ser alcançadas
        rodando o grafo de verdade, para o motor oficial (construir_peca.py etc.)
        realmente executar em vez de ser contornado.
        """
        if authority.strip().casefold() != "ricardo":
            raise GateError("somente authority: ricardo pode comandar jump")
        if not reason.strip():
            raise ContractError("justificativa obrigatória para jump")

        current = self.state()
        if not current:
            raise ContractError("nenhum estado encontrado")

        stages = current.get("route", {}).get("stages", [])
        if not stages:
            raise ContractError("estado sem rota/stages definidos")
        if target_phase not in stages:
            raise ValueError(f"Fase {target_phase} inválida")

        current_phase = current.get("phase", "")
        current_idx = stages.index(current_phase) if current_phase in stages else -1
        target_idx = stages.index(target_phase)
        pulados_mecanicos = _fases_mecanicas_puladas(stages, current_idx, target_idx, self.system_handlers)
        if pulados_mecanicos:
            raise GateError(
                f"jump de {current_phase!r} para {target_phase!r} pularia a(s) fase(s) "
                f"mecânica(s) {pulados_mecanicos} sem executá-las. Rode `step` até "
                f"alcançar cada uma (elas rodam o motor oficial de verdade) em vez de saltar por cima."
            )

        # Se target for a primeira fase (idx=0), as_node = START, senão a fase anterior.
        as_node = START if target_idx == 0 else stages[target_idx - 1]

        graph = self._build_graph()
        graph.update_state(self._config, {"phase": target_phase, "status": "executing", "failures": {}, "consecutive_failures": 0}, as_node=as_node)
        return graph.invoke(None, config=self._config)

    def state(self) -> dict[str, Any]:
        """Retorna o estado corrente da matéria."""
        snapshot = self._saver.get_tuple(self._config)
        if snapshot is None:
            return {}
        return dict(snapshot.checkpoint.get("channel_values", {}))

    def resume(self, *, authority: str = "ricardo", reason: str = "") -> dict[str, Any]:
        """Retoma a fase que falhou (requer authority: ricardo).

        Aceita dois estados de bloqueio:
        - ``paused``: disjuntor aberto (2 falhas consecutivas) — reseta o
          contador ao retomar, dando um novo orçamento de tentativas.
        - ``failed``: falha isolada abaixo do limiar do disjuntor — a fase
          continua bloqueada até Ricardo decidir retomar; o contador NÃO é
          resetado, para que o disjuntor efetivamente abra na 2ª falha.

        Em ambos os casos a fase que falhou é REEXECUTADA (não pulada) —
        o motor rebobina o checkpoint para o nó anterior à fase falha e
        invoca o grafo novamente a partir dali.
        """
        if authority.strip().casefold() != "ricardo":
            raise GateError("somente authority: ricardo pode retomar")
        if not reason.strip():
            raise ContractError("justificativa obrigatória para retomada")

        current = self.state()
        status = current.get("status")
        if status not in ("paused", "failed"):
            raise ContractError("matéria não está pausada nem em falha")

        failed_phase = current.get("phase", "")
        stages: list[str] = list(self._spec["stages"])
        if failed_phase not in stages:
            raise ContractError(f"fase corrente desconhecida na rota: {failed_phase!r}")
        idx = stages.index(failed_phase)
        predecessor = stages[idx - 1] if idx > 0 else START

        updates: dict[str, Any] = {"status": "executing"}
        if status == "paused":
            updates["consecutive_failures"] = 0

        graph = self._build_graph()
        graph.update_state(self._config, updates, as_node=predecessor)
        result = graph.invoke(None, config=self._config)
        return result

    def close(self) -> None:
        """Fecha a conexão SQLite."""
        try:
            self._conn.close()
        except Exception:
            pass
