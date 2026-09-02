#!/usr/bin/env python3
"""Política determinística de roteamento do fluxo RDAA.

O Hermes apresenta o fluxo e aciona os executores; este módulo decide somente
transições e segregação de funções. Ele não avalia mérito jurídico.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from functools import wraps
import copy
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ROUTE_PATH = ROOT / "orquestracao" / "roteamento.json"
_LEVEL_ORDER = {"C": 1, "B": 2, "A": 3}
_COMPLETION_ROLES = {"draft_ready": "writer", "critique_ready": "critic", "candidate_ready": "validator"}


class WorkflowLockError(ValueError):
    """A matéria já está sendo alterada por outro processo."""


@contextmanager
def bloqueio_materia(state_dir: Path | str):
    """Lock de exclusão mútua por matéria, liberado mesmo após exceção."""
    root = Path(state_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    lock = root / ".rdaa-orchestrator.lock"
    try:
        with lock.open("x", encoding="utf-8") as handle:
            json.dump({"pid": os.getpid(), "created_at": _now()}, handle)
    except FileExistsError as exc:
        raise WorkflowLockError(f"matéria em uso: {lock}") from exc
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


def operacao_exclusiva(fn):
    """Serializa mutações de um manifesto por diretório de matéria."""
    @wraps(fn)
    def wrapped(state_dir: Path | str, *args: Any, **kwargs: Any):
        with bloqueio_materia(state_dir):
            return fn(state_dir, *args, **kwargs)
    return wrapped


class RoutePolicyError(ValueError):
    """Rota inválida ou que viola segregação de funções."""


def _normalizar_nivel(value: str) -> str:
    level = str(value).strip().upper()
    if level not in _LEVEL_ORDER:
        raise RoutePolicyError("nível da peça deve ser C, B ou A")
    return level


def _normalizar_risco(value: str) -> str:
    risk = str(value).strip().lower()
    aliases = {"médio": "medio", "crítico": "critico"}
    return aliases.get(risk, risk)


def carregar_politica(path: Path | str = ROUTE_PATH) -> dict[str, Any]:
    path = Path(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RoutePolicyError(f"política de roteamento ausente: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RoutePolicyError(f"política de roteamento inválida: {exc}") from exc
    if not isinstance(payload.get("levels"), dict) or not isinstance(payload.get("workers"), dict) or not isinstance(payload.get("worker_allowed_phases"), dict):
        raise RoutePolicyError("política sem levels, workers ou worker_allowed_phases")
    validar_segregacao(payload["workers"])
    return payload


def validar_segregacao(workers: dict[str, dict[str, Any]]) -> None:
    required = {"writer", "critic", "validator"}
    missing = required - set(workers)
    if missing:
        raise RoutePolicyError(f"papéis ausentes: {', '.join(sorted(missing))}")
    writer = str(workers["writer"].get("model_family", "")).strip()
    critic = str(workers["critic"].get("model_family", "")).strip()
    validator = str(workers["validator"].get("model_family", "")).strip()
    if not writer or not critic or not validator:
        raise RoutePolicyError("todo papel precisa declarar model_family")
    if writer == critic:
        raise RoutePolicyError("crítico deve ser independente da família do redator")
    if writer == validator:
        raise RoutePolicyError("validador deve ser independente da família do redator")
    if critic == validator:
        raise RoutePolicyError("validador deve ser independente da família do crítico")


def selecionar_rota(piece_level: str, risk_level: str, policy_path: Path | str = ROUTE_PATH) -> dict[str, Any]:
    policy = carregar_politica(policy_path)
    declared = _normalizar_nivel(piece_level)
    risk = _normalizar_risco(risk_level)
    required_by_risk = policy.get("risk_escalation", {}).get(risk)
    if required_by_risk is None:
        raise RoutePolicyError("nível de risco deve ser baixo, médio, alto ou crítico")
    required_by_risk = _normalizar_nivel(required_by_risk)
    effective = max((declared, required_by_risk), key=_LEVEL_ORDER.__getitem__)
    level_policy = policy["levels"].get(effective)
    if not isinstance(level_policy, dict):
        raise RoutePolicyError(f"sem rota configurada para nível {effective}")
    workers = {
        role: str(spec.get("engine", "")).strip()
        for role, spec in policy["workers"].items()
    }
    if not all(workers.values()):
        raise RoutePolicyError("todo papel precisa declarar engine")
    return {
        "schema_version": policy.get("schema_version"),
        "declared_piece_level": declared,
        "risk_level": risk,
        "effective_piece_level": effective,
        "escalated_by_risk": effective != declared,
        "workers": workers,
        "worker_identity": copy.deepcopy(policy["workers"]),
        "worker_allowed_phases": copy.deepcopy(policy["worker_allowed_phases"]),
        "stages": list(level_policy.get("stages", [])),
        "required_human_gates": list(level_policy.get("required_human_gates", [])),
        "conditional_human_gates": list(level_policy.get("conditional_human_gates", [])),
        "vault": copy.deepcopy(level_policy.get("vault", {})),
    }


class WorkflowStateError(ValueError):
    """Transição ou aprovação incompatível com o estado persistido."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        Path(temp_name).replace(path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def _manifest_path(state_dir: Path | str) -> Path:
    return Path(state_dir) / "run_manifest.json"


def _read_manifest(state_dir: Path | str) -> dict[str, Any]:
    path = _manifest_path(state_dir)
    if not path.is_file():
        raise WorkflowStateError("execução não inicializada")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorkflowStateError("manifesto de execução inválido") from exc


def _read_json_artifact(path: Path, description: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorkflowStateError(f"{description} inválido") from exc
    if not isinstance(payload, dict):
        raise WorkflowStateError(f"{description} inválido")
    return payload


@operacao_exclusiva
def inicializar_execucao(state_dir: Path | str, matter_id: str, piece_level: str, risk_level: str) -> dict[str, Any]:
    """Cria um manifesto idempotente, sem interpretar conteúdo jurídico."""
    state_dir = Path(state_dir)
    route = selecionar_rota(piece_level, risk_level)
    path = _manifest_path(state_dir)
    if path.exists():
        existing = _read_manifest(state_dir)
        if existing.get("matter_id") != matter_id:
            raise WorkflowStateError("matter_id não corresponde ao manifesto existente")
        return existing
    manifest = {
        "schema_version": route["schema_version"],
        "matter_id": matter_id,
        "created_at": _now(),
        "updated_at": _now(),
        "phase": "initialized",
        "status": "ready",
        "route": route,
        "approvals": [],
        "executions": [],
        "vault": {"lookups": [], "syncs": []},
        "transitions": [{"from": None, "to": "initialized", "at": _now()}],
    }
    _write_json(path, manifest)
    return manifest


def aprovacao_valida(state_dir: Path | str, gate: str, artifact_path: Path | str | None = None) -> bool:
    manifest = _read_manifest(state_dir)
    approvals = [item for item in manifest.get("approvals", []) if item.get("gate") == gate and item.get("approved")]
    if not approvals:
        return False
    approval = approvals[-1]
    artifact = Path(artifact_path) if artifact_path is not None else Path(str(approval.get("artifact_path", "")))
    return artifact.is_file() and approval.get("artifact_sha256") == _sha256(artifact)


@operacao_exclusiva
def abrir_gate_humano(state_dir: Path | str, gate: str, reason: str) -> dict[str, Any]:
    """Pausa uma matéria quando um worker identifica questão estratégica condicional."""
    manifest = _read_manifest(state_dir)
    allowed = set(manifest.get("route", {}).get("conditional_human_gates", []))
    if gate not in allowed:
        raise WorkflowStateError(f"gate condicional não configurado: {gate}")
    record = {"gate": gate, "reason": str(reason).strip(), "opened_at": _now()}
    manifest["open_gate"] = record
    manifest["status"] = "awaiting_approval"
    manifest["updated_at"] = _now()
    _write_json(_manifest_path(state_dir), manifest)
    return record


@operacao_exclusiva
def registrar_aprovacao(state_dir: Path | str, gate: str, artifact_path: Path | str, approved_by: str) -> dict[str, Any]:
    manifest = _read_manifest(state_dir)
    route = manifest.get("route", {})
    allowed_gates = set(route.get("required_human_gates", [])) | set(route.get("conditional_human_gates", []))
    if gate not in allowed_gates:
        raise WorkflowStateError(f"gate não exigido pela rota: {gate}")
    artifact = Path(artifact_path).resolve()
    if not artifact.is_file():
        raise WorkflowStateError(f"artefato de aprovação ausente: {artifact}")
    record = {
        "gate": gate,
        "approved": True,
        "approved_by": str(approved_by).strip() or "usuário",
        "approved_at": _now(),
        "artifact_path": str(artifact),
        "artifact_sha256": _sha256(artifact),
    }
    manifest.setdefault("approvals", []).append(record)
    if manifest.get("open_gate", {}).get("gate") == gate:
        manifest.pop("open_gate", None)
        manifest["status"] = "ready"
    manifest["updated_at"] = _now()
    _write_json(_manifest_path(state_dir), manifest)
    return record


@operacao_exclusiva
def registrar_consulta_vault(
    state_dir: Path | str,
    *,
    vault: str,
    artifact_path: Path | str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Registra somente uma consulta read-only do Ementário em B/A."""
    manifest = _read_manifest(state_dir)
    lookup_policy = manifest.get("route", {}).get("vault", {}).get("lookup", {})
    if not lookup_policy.get("enabled"):
        raise WorkflowStateError("consulta automática ao vault não é permitida nesta rota")
    if manifest.get("phase") != "intake_ready":
        raise WorkflowStateError("consulta ao vault só é permitida após intake_ready")
    if vault != lookup_policy.get("vault"):
        raise WorkflowStateError("vault consultado não corresponde à rota")
    artifact = Path(artifact_path).resolve()
    if not artifact.is_file():
        raise WorkflowStateError(f"artefato de consulta ausente: {artifact}")
    payload = _read_json_artifact(artifact, "artefato de consulta ao vault")
    expected_status = lookup_policy.get("context_status", "informada")
    if payload.get("origin") != vault or payload.get("mode") != "read_only" or payload.get("status") != expected_status:
        raise WorkflowStateError("consulta ao vault sem provenance read-only informada")
    record = {
        "vault": vault,
        "recorded_at": _now(),
        "artifact_path": str(artifact),
        "artifact_sha256": _sha256(artifact),
        "status": expected_status,
        "mode": "read_only",
        "domain": payload.get("domain"),
        "domain_found": payload.get("domain_found"),
        "documents_count": len(payload.get("documents", [])) if isinstance(payload.get("documents"), list) else 0,
        "metadata": dict(metadata or {}),
    }
    manifest.setdefault("vault", {}).setdefault("lookups", []).append(record)
    manifest["updated_at"] = _now()
    _write_json(_manifest_path(state_dir), manifest)
    return record


@operacao_exclusiva
def registrar_sincronizacao_vault(
    state_dir: Path | str,
    *,
    vault: str,
    artifact_path: Path | str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Registra recibo real de publicação no vault; não aceita pendência como sucesso."""
    manifest = _read_manifest(state_dir)
    if manifest.get("phase") != "published":
        raise WorkflowStateError("sincronização de vault só é permitida após publicação")
    sync_policy = manifest.get("route", {}).get("vault", {}).get("sync", {})
    allowed = set(sync_policy.get("required_after_publish", [])) | set(sync_policy.get("optional_after_publish", []))
    if vault not in allowed:
        raise WorkflowStateError("vault de sincronização não corresponde à rota")
    artifact = Path(artifact_path).resolve()
    if not artifact.is_file():
        raise WorkflowStateError(f"recibo de vault ausente: {artifact}")
    payload = _read_json_artifact(artifact, "recibo de vault")
    if payload.get("vault") != vault or payload.get("status") != "registered":
        raise WorkflowStateError("recibo de vault não confirma registro")
    record = {
        "vault": vault,
        "recorded_at": _now(),
        "artifact_path": str(artifact),
        "artifact_sha256": _sha256(artifact),
        "status": "registered",
        "metadata": dict(metadata or {}),
    }
    manifest.setdefault("vault", {}).setdefault("syncs", []).append(record)
    manifest["updated_at"] = _now()
    _write_json(_manifest_path(state_dir), manifest)
    return record


@operacao_exclusiva
def avancar_fase(state_dir: Path | str, target_phase: str) -> dict[str, Any]:
    manifest = _read_manifest(state_dir)
    if manifest.get("open_gate"):
        raise WorkflowStateError("aprovação pendente para gate humano aberto")
    route = manifest.get("route", {})
    stages = list(route.get("stages", []))
    current = str(manifest.get("phase", "initialized"))
    expected_index = 0 if current == "initialized" else stages.index(current) + 1 if current in stages else -1
    if expected_index < 0 or expected_index >= len(stages) or target_phase != stages[expected_index]:
        expected = stages[expected_index] if 0 <= expected_index < len(stages) else "nenhuma"
        raise WorkflowStateError(f"próxima fase esperada: {expected}")
    gate_by_phase = {"skeleton_approved": "skeleton_approval", "published": "release_approval"}
    gate = gate_by_phase.get(target_phase)
    if gate and gate in route.get("required_human_gates", []) and not aprovacao_valida(state_dir, gate):
        raise WorkflowStateError(f"aprovação válida exigida para {gate}")
    if target_phase == "vault_context_ready":
        lookups = manifest.get("vault", {}).get("lookups", [])
        required_vault = route.get("vault", {}).get("lookup", {}).get("vault")
        if not any(
            item.get("vault") == required_vault
            and Path(str(item.get("artifact_path", ""))).is_file()
            and _sha256(Path(str(item["artifact_path"]))) == item.get("artifact_sha256")
            for item in lookups
        ):
            raise WorkflowStateError("consulta do Ementário válida exigida antes de vault_context_ready")
    if target_phase == "vault_registered":
        required_syncs = set(route.get("vault", {}).get("sync", {}).get("required_after_publish", []))
        completed_syncs = {
            item.get("vault")
            for item in manifest.get("vault", {}).get("syncs", [])
            if Path(str(item.get("artifact_path", ""))).is_file()
            and _sha256(Path(str(item["artifact_path"]))) == item.get("artifact_sha256")
            and item.get("status") == "registered"
        }
        missing_syncs = required_syncs - completed_syncs
        if missing_syncs:
            names = ", ".join(sorted(missing_syncs))
            raise WorkflowStateError(f"registro no vault operacional exigido: {names}")
    required_role = _COMPLETION_ROLES.get(target_phase)
    # Papel só é exigido se o próprio estágio existir na rota do nível
    # (nível C não tem "validating"/"criticizing" nos stages — não bloqueia).
    if required_role == "validator" and "validating" not in stages:
        required_role = None
    if required_role == "critic" and "criticizing" not in stages:
        required_role = None
    if required_role:
        worker_executions = [execution for execution in manifest.get("executions", []) if execution.get("role") == required_role]
        if not worker_executions:
            raise WorkflowStateError(f"execução do papel {required_role} exigida antes de {target_phase}")
        if not any(
            Path(str(execution.get("output_path", ""))).is_file()
            and _sha256(Path(str(execution["output_path"]))) == execution.get("output_sha256")
            for execution in worker_executions
        ):
            raise WorkflowStateError(f"hash da saída do papel {required_role} não confere")
    manifest["phase"] = target_phase
    manifest["status"] = "awaiting_approval" if target_phase.startswith("awaiting_") else "ready"
    manifest["updated_at"] = _now()
    manifest.setdefault("transitions", []).append({"from": current, "to": target_phase, "at": _now()})
    _write_json(_manifest_path(state_dir), manifest)
    return manifest


def validar_inicio_worker(state_dir: Path | str, role: str, motor: str) -> dict[str, Any]:
    """Falha antes de chamar a CLI se papel/motor/fase não forem autorizados."""
    manifest = _read_manifest(state_dir)
    identities = manifest.get("route", {}).get("worker_identity", {})
    worker = identities.get(role)
    if not isinstance(worker, dict):
        raise WorkflowStateError(f"papel não configurado: {role}")
    if worker.get("engine") != motor:
        raise WorkflowStateError(f"motor {motor} não corresponde ao papel {role}")
    allowed_phases = set(manifest.get("route", {}).get("worker_allowed_phases", {}).get(role, []))
    if manifest.get("phase") not in allowed_phases:
        raise WorkflowStateError(f"fase incompatível com o papel {role}: {manifest.get('phase')}")
    return manifest


@operacao_exclusiva
def registrar_execucao(
    state_dir: Path | str,
    *,
    role: str,
    motor: str,
    prompt_path: Path | str,
    output_path: Path | str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Registra uma saída já produzida; workers nunca editam o manifesto."""
    manifest = validar_inicio_worker(state_dir, role, motor)
    worker = manifest["route"]["worker_identity"][role]
    prompt = Path(prompt_path).resolve()
    output = Path(output_path).resolve()
    if not prompt.is_file() or not output.is_file():
        raise WorkflowStateError("prompt e saída precisam existir antes do registro")
    metadata = dict(metadata or {})
    record = {
        "role": role,
        "motor": motor,
        "worker": copy.deepcopy(worker),
        "recorded_at": _now(),
        "prompt_path": str(prompt),
        "output_path": str(output),
        "input_sha256": _sha256(prompt),
        "output_sha256": _sha256(output),
        "session_id": metadata.get("session_id"),
        "duration_ms": metadata.get("duration_ms"),
        "model_ids": list(metadata.get("model_ids") or []),
        "usage": dict(metadata.get("usage") or {}),
    }
    manifest.setdefault("executions", []).append(record)
    manifest["updated_at"] = _now()
    _write_json(_manifest_path(state_dir), manifest)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Máquina de estados determinística do fluxo RDAA")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="inicializa uma execução")
    init.add_argument("state_dir", type=Path)
    init.add_argument("--matter-id", required=True)
    init.add_argument("--piece-level", required=True, choices=("A", "B", "C", "a", "b", "c"))
    init.add_argument("--risk-level", required=True)

    status = commands.add_parser("status", help="mostra o manifesto")
    status.add_argument("state_dir", type=Path)

    advance = commands.add_parser("advance", help="avança uma única fase")
    advance.add_argument("state_dir", type=Path)
    advance.add_argument("phase")

    approve = commands.add_parser("approve", help="registra aprovação humana vinculada a hash")
    approve.add_argument("state_dir", type=Path)
    approve.add_argument("--gate", required=True)
    approve.add_argument("--artifact", type=Path, required=True)
    approve.add_argument("--approved-by", required=True)

    open_gate = commands.add_parser("open-gate", help="pausa para decisão humana condicional")
    open_gate.add_argument("state_dir", type=Path)
    open_gate.add_argument("--gate", required=True)
    open_gate.add_argument("--reason", required=True)

    lookup = commands.add_parser("register-vault-lookup", help="registra pacote read-only do Ementário")
    lookup.add_argument("state_dir", type=Path)
    lookup.add_argument("--vault", required=True)
    lookup.add_argument("--artifact", type=Path, required=True)

    sync = commands.add_parser("register-vault-sync", help="registra recibo de sincronização de vault")
    sync.add_argument("state_dir", type=Path)
    sync.add_argument("--vault", required=True)
    sync.add_argument("--artifact", type=Path, required=True)

    route = commands.add_parser("route", help="mostra a rota sem gravar estado")
    route.add_argument("--piece-level", required=True, choices=("A", "B", "C", "a", "b", "c"))
    route.add_argument("--risk-level", required=True)

    args = parser.parse_args()
    if args.command == "init":
        result = inicializar_execucao(args.state_dir, args.matter_id, args.piece_level, args.risk_level)
    elif args.command == "status":
        result = _read_manifest(args.state_dir)
    elif args.command == "advance":
        result = avancar_fase(args.state_dir, args.phase)
    elif args.command == "approve":
        result = registrar_aprovacao(args.state_dir, args.gate, args.artifact, args.approved_by)
    elif args.command == "open-gate":
        result = abrir_gate_humano(args.state_dir, args.gate, args.reason)
    elif args.command == "register-vault-lookup":
        result = registrar_consulta_vault(args.state_dir, vault=args.vault, artifact_path=args.artifact)
    elif args.command == "register-vault-sync":
        result = registrar_sincronizacao_vault(args.state_dir, vault=args.vault, artifact_path=args.artifact)
    else:
        result = selecionar_rota(args.piece_level, args.risk_level)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
