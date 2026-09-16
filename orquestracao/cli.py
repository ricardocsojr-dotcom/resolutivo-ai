#!/usr/bin/env python3
"""CLI do motor RDAA V4 — interface local do Codex.

Comandos:
    rdaa start   <state_dir> --matter-id X --level B
    rdaa status  <state_dir>
    rdaa approve <state_dir> --gate skeleton_approval --authority ricardo
    rdaa resume  <state_dir> --authority ricardo --reason "motivo"
    rdaa abort   <state_dir> --authority ricardo --reason "motivo"
    rdaa audit   <state_dir>

O motor controla as transições.  O Codex apresenta gates e transmite
a decisão de Ricardo.  Não escreve diretamente em SQLite ou JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from orquestracao.contracts import ContractError, GateError, CircuitBreakerError
from orquestracao.contracts import HUMAN_GATES
from orquestracao.engine import RDAAEngine, ROUTE_PATH
from orquestracao.production_worker import production_worker
from orquestracao.system_handlers import DEFAULT_SYSTEM_HANDLERS


def _json_out(data: dict, exit_code: int = 0) -> int:
    """Imprime JSON e retorna exit code."""
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return exit_code


def _make_engine(state_dir, level: str, *, route_path: Path | None = None) -> RDAAEngine:
    """Constrói o motor conectado ao fluxo produtivo real.

    Injeta o worker de produção (CLI direta isolada para papéis externos,
    artefato manual do Codex para papéis ``engine: chat``) e os
    handlers de sistema padrão (QA, publicação, registro no vault) —
    é o único ponto da CLI que instancia ``RDAAEngine`` para uso
    operacional, garantindo que toda invocação real passe pelas mesmas
    regras corporativas.
    """
    return RDAAEngine(
        state_dir,
        level,
        worker=production_worker,
        system_handlers=DEFAULT_SYSTEM_HANDLERS,
        route_path=route_path or ROUTE_PATH,
    )


def _format_action_result(action: str, result: dict, **kwargs) -> int:
    """Modela o retorno JSON e o código de saída consoante o state do Grafo."""
    status = result.get("status", "")
    is_success = status not in ("failed", "paused", "aborted")

    # Monta payload mantendo state
    payload = {
        "action": action if is_success else f"{action}_FAILED",
        "current_phase": result.get("phase", ""),
        "status": status,
        "phases_completed": len(result.get("history", [])),
        **kwargs
    }
    stages = result.get("route", {}).get("stages", [])
    phase = result.get("phase", "")
    if phase in stages and stages.index(phase) + 1 < len(stages):
        next_phase = stages[stages.index(phase) + 1]
        gate = HUMAN_GATES.get(next_phase)
        if gate:
            payload["required_gate"] = gate

    state_dir = result.get("state_dir")
    if state_dir:
        detail_path = Path(str(state_dir)) / "last_cli_result.json"
        detail_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n",
            encoding="utf-8",
        )
        payload["details"] = str(detail_path.resolve())

    # Extrai o ultimo erro registrado nas exeucções que falharam, se existir
    if status == "failed":
        executions = result.get("executions", [])
        if executions and executions[-1].get("outcome") == "error":
            error = str(executions[-1].get("error", ""))
            payload["error"] = error.splitlines()[0][:300]

    return _json_out(payload, 0 if is_success else 1)


def cmd_start(args) -> int:
    """Inicializa uma matéria."""
    engine = _make_engine(
        args.state_dir, args.level,
        route_path=Path(args.route) if args.route else None,
    )
    try:
        result = engine.initialize(args.matter_id)

        if args.no_ocr:
            engine._build_graph().update_state(engine._config, {"options": {"use_ocr": False}})

        return _format_action_result(
            "STARTED", result,
            matter_id=args.matter_id,
            level=args.level
        )
    except Exception as exc:
        return _json_out({"error": str(exc), "action": "START_FAILED"}, 1)
    finally:
        engine.close()


def cmd_status(args) -> int:
    """Consulta o estado corrente."""
    engine = RDAAEngine(args.state_dir, "C")  # level é lido do estado; sem invocação de grafo
    try:
        state = engine.state()
        if not state:
            return _json_out({"error": "matéria não inicializada"}, 1)
        return _json_out({
            "matter_id": state.get("matter_id", ""),
            "level": state.get("nivel_peca", ""),
            "current_phase": state.get("phase", ""),
            "status": state.get("status", ""),
            "phases_completed": len(state.get("history", [])),
            "consecutive_failures": state.get("consecutive_failures", 0),
            "approvals": list(state.get("approvals", {}).keys()),
            "executions_count": len(state.get("executions", [])),
        })
    except Exception as exc:
        return _json_out({"error": str(exc)}, 1)
    finally:
        engine.close()


def cmd_approve(args) -> int:
    """Aprova um gate humano."""
    # Precisamos saber o nível — ler do estado existente (probe: não invoca o grafo)
    engine_probe = RDAAEngine(args.state_dir, "C")
    state = engine_probe.state()
    level = state.get("nivel_peca", "C")
    engine_probe.close()

    engine = _make_engine(args.state_dir, level)
    try:
        result = engine.approve_gate(args.gate, authority=args.authority)
        return _format_action_result(
            "APPROVED", result,
            gate=args.gate,
            authority=args.authority
        )
    except GateError as exc:
        return _json_out({"error": str(exc), "action": "APPROVE_REJECTED"}, 1)
    except Exception as exc:
        return _json_out({"error": str(exc), "action": "APPROVE_FAILED"}, 1)
    finally:
        engine.close()


def cmd_resume(args) -> int:
    """Retoma após disjuntor."""
    engine_probe = RDAAEngine(args.state_dir, "C")
    state = engine_probe.state()
    level = state.get("nivel_peca", "C")
    engine_probe.close()

    engine = _make_engine(args.state_dir, level)
    try:
        result = engine.resume(authority=args.authority, reason=args.reason)
        return _format_action_result(
            "RESUMED", result,
            authority=args.authority,
            reason=args.reason
        )
    except (GateError, ContractError) as exc:
        return _json_out({"error": str(exc), "action": "RESUME_REJECTED"}, 1)
    except Exception as exc:
        return _json_out({"error": str(exc), "action": "RESUME_FAILED"}, 1)
    finally:
        engine.close()

def cmd_step(args) -> int:
    """Avança a execução (pós-pausa)."""
    engine_probe = RDAAEngine(args.state_dir, "C")
    state = engine_probe.state()
    level = state.get("nivel_peca", "C")
    engine_probe.close()

    engine = _make_engine(args.state_dir, level)
    try:
        result = engine.step(authority=args.authority)
        return _format_action_result(
            "STEPPED", result,
            authority=args.authority
        )
    except Exception as exc:
        return _json_out({"error": str(exc), "action": "STEP_FAILED"}, 1)
    finally:
        engine.close()

def cmd_jump(args) -> int:
    """Pula para uma fase específica."""
    engine_probe = RDAAEngine(args.state_dir, "C")
    state = engine_probe.state()
    level = state.get("nivel_peca", "C")
    engine_probe.close()

    engine = _make_engine(args.state_dir, level)
    try:
        result = engine.jump(args.phase, authority=args.authority, reason=args.reason)
        return _format_action_result(
            "JUMPED", result,
            target_phase=args.phase,
            reason=args.reason
        )
    except Exception as exc:
        return _json_out({"error": str(exc), "action": "JUMP_FAILED"}, 1)
    finally:
        engine.close()

def cmd_abort(args) -> int:
    """Aborta a matéria."""
    if args.authority.strip().casefold() != "ricardo":
        return _json_out({"error": "somente authority: ricardo pode abortar"}, 1)

    engine_probe = RDAAEngine(args.state_dir, "C")
    state = engine_probe.state()
    level = state.get("nivel_peca", "C")
    engine_probe.close()

    engine = _make_engine(args.state_dir, level)
    try:
        from orquestracao.engine import build_rdaa_graph
        graph = engine._build_graph()
        graph.update_state(engine._config, {"status": "aborted"})
        return _json_out({
            "action": "ABORTED",
            "authority": args.authority,
            "reason": args.reason,
        })
    except Exception as exc:
        return _json_out({"error": str(exc), "action": "ABORT_FAILED"}, 1)
    finally:
        engine.close()


def cmd_audit(args) -> int:
    """Auditoria: mostra execuções, approvals e estado do disjuntor."""
    engine = RDAAEngine(args.state_dir, "C")
    try:
        state = engine.state()
        if not state:
            return _json_out({"error": "matéria não inicializada"}, 1)
        return _json_out({
            "matter_id": state.get("matter_id", ""),
            "level": state.get("nivel_peca", ""),
            "phase": state.get("phase", ""),
            "status": state.get("status", ""),
            "history": state.get("history", []),
            "executions": state.get("executions", []),
            "approvals": state.get("approvals", {}),
            "failures": state.get("failures", {}),
            "consecutive_failures": state.get("consecutive_failures", 0),
            "vault": state.get("vault", {}),
        })
    except Exception as exc:
        return _json_out({"error": str(exc)}, 1)
    finally:
        engine.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="rdaa",
        description="CLI do Motor RDAA V4",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # start
    p_start = sub.add_parser("start", help="Inicializa uma matéria")
    p_start.add_argument("state_dir")
    p_start.add_argument("--matter-id", required=True)
    p_start.add_argument("--level", required=True, choices=["A", "B", "C"])
    p_start.add_argument("--route", default=None)
    p_start.add_argument("--no-ocr", action="store_true", help="Ignora a extração massiva via OCR de imagens/PDFs")
    p_start.set_defaults(func=cmd_start)

    # status
    p_status = sub.add_parser("status", help="Consulta estado corrente")
    p_status.add_argument("state_dir")
    p_status.set_defaults(func=cmd_status)

    # approve
    p_approve = sub.add_parser("approve", help="Aprova gate humano")
    p_approve.add_argument("state_dir")
    p_approve.add_argument("--gate", required=True)
    p_approve.add_argument("--authority", default="ricardo")
    p_approve.set_defaults(func=cmd_approve)

    # resume
    p_resume = sub.add_parser("resume", help="Retoma após disjuntor")
    p_resume.add_argument("state_dir")
    p_resume.add_argument("--authority", default="ricardo")
    p_resume.add_argument("--reason", required=True)
    p_resume.set_defaults(func=cmd_resume)

    # step
    p_step = sub.add_parser("step", help="Avança a execução pausada num worker")
    p_step.add_argument("state_dir")
    p_step.add_argument("--authority", default="ricardo")
    p_step.set_defaults(func=cmd_step)

    # jump
    p_jump = sub.add_parser("jump", help="Pula direto para uma fase específica")
    p_jump.add_argument("state_dir")
    p_jump.add_argument("--phase", required=True)
    p_jump.add_argument("--reason", required=True)
    p_jump.add_argument("--authority", default="ricardo")
    p_jump.set_defaults(func=cmd_jump)

    # abort
    p_abort = sub.add_parser("abort", help="Aborta a matéria")
    p_abort.add_argument("state_dir")
    p_abort.add_argument("--authority", default="ricardo")
    p_abort.add_argument("--reason", required=True)
    p_abort.set_defaults(func=cmd_abort)

    # audit
    p_audit = sub.add_parser("audit", help="Auditoria completa")
    p_audit.add_argument("state_dir")
    p_audit.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
