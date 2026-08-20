#!/usr/bin/env python3
"""Revisão semântica objetiva, coordenação e métricas locais do RDAA.

Este módulo compara registros explicitamente identificados. Ele não usa LLM,
não acessa serviços externos e não classifica mérito, validade ou risco por
inferência textual.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from .estado_rdaa import SCHEMA_VERSION, initialize_state
except ImportError:  # execução direta pelo caminho do script
    from estado_rdaa import SCHEMA_VERSION, initialize_state


MAX_AUTO_CORRECTION_ROUNDS = 1
OPTIONAL_ROUTE_AGENTS = ("critico-rdaa", "conselho-rdaa")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return dict(default)
    return payload if isinstance(payload, dict) else dict(default)


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


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return list(value) if isinstance(value, list) else [value]


def _item_text(item: Any) -> str:
    if not isinstance(item, dict):
        return str(item).strip()
    for key in ("texto", "descricao", "valor", "veredito", "pedido", "risco"):
        if item.get(key) is not None:
            return str(item[key]).strip()
    return ""


def _items_by_id(items: Iterable[Any]) -> tuple[dict[str, Any], list[str]]:
    indexed: dict[str, Any] = {}
    duplicates: list[str] = []
    for item in items:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        item_id = str(item["id"])
        if item_id in indexed:
            duplicates.append(item_id)
        else:
            indexed[item_id] = item
    return indexed, duplicates


def _finding(
    *,
    kind: str,
    severity: str,
    message: str,
    entity_ids: list[str] | None = None,
    location: str | None = None,
    requires_human_review: bool = False,
) -> dict[str, Any]:
    marker = json.dumps(
        {
            "kind": kind,
            "message": message,
            "entity_ids": entity_ids or [],
            "location": location,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    finding_id = "SEM-" + hashlib.sha1(marker.encode("utf-8")).hexdigest()[:12]
    return {
        "id": finding_id,
        "kind": kind,
        "severity": severity,
        "message": message,
        "entity_ids": entity_ids or [],
        "localizacao": location,
        "requires_human_review": requires_human_review,
        "status": "aberto",
    }


def _all_entity_ids(state: dict[str, Any]) -> tuple[set[str], list[dict[str, Any]]]:
    keys = (
        "facts",
        "theses_structured",
        "theses",
        "hypotheses_structured",
        "hypotheses",
        "requests",
        "risks",
        "decisions",
        "citations",
        "semantic_blocks",
    )
    all_ids: set[str] = set()
    findings: list[dict[str, Any]] = []
    for key in keys:
        items = _as_list(state.get(key))
        indexed, duplicates = _items_by_id(items)
        all_ids.update(indexed)
        if key == "semantic_blocks":
            for block in items:
                if isinstance(block, dict):
                    all_ids.update(str(item) for item in block.get("semantic_ids", []) if item)
        for item_id in duplicates:
            findings.append(
                _finding(
                    kind="duplicate_id",
                    severity="erro",
                    message=f"ID duplicado no campo {key}: {item_id}",
                    entity_ids=[item_id],
                    location=key,
                )
            )
    return all_ids, findings


def review_state(state_dir: Path | str) -> dict[str, Any]:
    """Verificar apenas consistência objetiva dos registros estruturados."""
    state_path = Path(state_dir)
    paths = initialize_state(state_path, matter_id=state_path.name)
    state = _read_json(paths["state"], {"matter_id": state_path.name})
    all_ids, findings = _all_entity_ids(state)
    if paths["provenance"].exists():
        for line in paths["provenance"].read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict) and record.get("id"):
                all_ids.add(str(record["id"]))

    references = {
        "source_ids": "fonte",
        "fact_ids": "fato",
        "thesis_ids": "tese",
        "request_ids": "pedido",
        "evidence_pivot_ids": "evidência-pivot",
    }
    for field in (
        "facts",
        "theses_structured",
        "hypotheses_structured",
        "requests",
        "risks",
        "decisions",
    ):
        for item in _as_list(state.get(field)):
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id")) if item.get("id") else None
            for ref_field, label in references.items():
                refs = item.get(ref_field)
                if not isinstance(refs, list):
                    continue
                for ref in refs:
                    ref_id = str(ref)
                    if ref_id not in all_ids:
                        findings.append(
                            _finding(
                                kind="reference_missing",
                                severity="erro",
                                message=f"{label} referenciada não existe: {ref_id}",
                                entity_ids=[item_id, ref_id] if item_id else [ref_id],
                                location=f"{field}.{item_id or 'sem-id'}.{ref_field}",
                            )
                        )
            if field == "risks" and item.get("nivel") and not item.get("origem"):
                findings.append(
                    _finding(
                        kind="risk_without_origin",
                        severity="alerta",
                        message="Risco com nível declarado sem origem explícita.",
                        entity_ids=[item_id] if item_id else [],
                        location=f"{field}.{item_id or 'sem-id'}",
                        requires_human_review=True,
                    )
                )

    process_values = {
        str(item.get("valor")).strip()
        for item in _as_list(state.get("facts"))
        if isinstance(item, dict) and item.get("campo") == "numero_processo" and item.get("valor")
    }
    if len(process_values) > 1:
        findings.append(
            _finding(
                kind="process_identity_conflict",
                severity="erro",
                message="Há mais de um número de processo explícito nos fatos da matéria.",
                entity_ids=[],
                location="facts.numero_processo",
            )
        )

    request_texts: dict[str, list[str]] = {}
    for item in _as_list(state.get("requests")):
        if not isinstance(item, dict):
            continue
        text = _item_text(item).casefold()
        if text:
            request_texts.setdefault(text, []).append(str(item.get("id", "")))
    for text, ids in request_texts.items():
        if len(ids) > 1:
            findings.append(
                _finding(
                    kind="possible_duplicate_request",
                    severity="alerta",
                    message=f"Pedidos com texto equivalente: {text}",
                    entity_ids=[item_id for item_id in ids if item_id],
                    location="requests",
                    requires_human_review=True,
                )
            )

    blocking = [item for item in findings if item["severity"] == "erro"]
    report = {
        "schema_version": SCHEMA_VERSION,
        "matter_id": str(state.get("matter_id") or state_path.name),
        "checked_at": _now(),
        "status": "BLOCK" if blocking else "PASS",
        "findings": findings,
        "counts": {
            "total": len(findings),
            "blocking": len(blocking),
            "alerts": sum(1 for item in findings if item["severity"] == "alerta"),
        },
    }
    return report


def persist_semantic_review(state_dir: Path | str, report: dict[str, Any]) -> Path:
    state_path = Path(state_dir)
    paths = initialize_state(state_path, matter_id=report.get("matter_id") or state_path.name)
    state = _read_json(paths["state"], {"matter_id": state_path.name})
    reviews = _as_list(state.get("semantic_reviews"))
    existing = {str(item.get("id")) for item in reviews if isinstance(item, dict) and item.get("id")}
    review_id = "REVIEW-" + hashlib.sha1(
        json.dumps(report.get("findings", []), ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:12]
    record = {
        "id": review_id,
        "status": report.get("status"),
        "counts": report.get("counts", {}),
        "finding_ids": [item.get("id") for item in report.get("findings", []) if item.get("id")],
        "checked_at": report.get("checked_at") or _now(),
        "origem": "semantica_rdaa",
    }
    if review_id not in existing:
        reviews.append(record)
    state["semantic_reviews"] = reviews
    state["updated_at"] = _now()
    _write_json(paths["state"], state)
    return paths["state"]


def route_for_matter(
    state_dir: Path | str,
    explicit_level: str | None = None,
    explicit_agents: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Retornar rota conservadora baseada apenas em nível explicitamente declarado."""
    state_path = Path(state_dir)
    paths = initialize_state(state_path, matter_id=state_path.name)
    state = _read_json(paths["state"], {"matter_id": state_path.name})
    requested_agents = []
    for agent in explicit_agents or []:
        normalized = str(agent).strip()
        if normalized in OPTIONAL_ROUTE_AGENTS and normalized not in requested_agents:
            requested_agents.append(normalized)
    declared = explicit_level
    source = "argumento_explicito" if explicit_level else None
    if declared is None and state.get("declared_risk_level"):
        declared = str(state["declared_risk_level"])
        source = "contexto_explicitamente_declarado"
    if declared is None:
        for item in _as_list(state.get("risks")):
            if isinstance(item, dict) and item.get("nivel"):
                declared = str(item["nivel"]).lower()
                source = "risco_declarado"
                break
    declared = str(declared).lower() if declared else None

    route = {
        "matter_id": str(state.get("matter_id") or state_path.name),
        "risk_level": declared,
        "risk_source": source,
        "required": ["semantic_review", "revisor-rdaa"],
        "recommended": [],
        "explicit": requested_agents,
        "selected": ["semantic_review", "revisor-rdaa"],
        "omitted": list(OPTIONAL_ROUTE_AGENTS),
        "optional": list(OPTIONAL_ROUTE_AGENTS),
        "selection_source": "conservadora",
        "max_auto_correction_rounds": MAX_AUTO_CORRECTION_ROUNDS,
        "reason": "rota conservadora; nenhum nível foi inferido",
    }
    if declared in {"a", "alto", "high"}:
        route["recommended"] = ["critico-rdaa", "conselho-rdaa"]
        route["reason"] = "nível alto explicitamente declarado"
    elif declared in {"b", "medio", "médio", "medium"}:
        route["recommended"] = ["critico-rdaa"]
        route["reason"] = "nível intermediário explicitamente declarado"
    elif declared in {"c", "baixo", "low"}:
        route["reason"] = "nível baixo explicitamente declarado; QA e revisão permanecem"
    route["selected"] = list(dict.fromkeys(route["required"] + route["recommended"] + route["explicit"]))
    route["omitted"] = [agent for agent in OPTIONAL_ROUTE_AGENTS if agent not in route["selected"]]
    if route["explicit"]:
        route["selection_source"] = "risco_declarado+override_explicito" if declared else "override_explicito"
        route["reason"] += "; agente adicional solicitado explicitamente"
    elif declared:
        route["selection_source"] = "risco_declarado"
    return route


def persist_route(
    state_dir: Path | str,
    explicit_level: str | None = None,
    explicit_agents: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Persistir no manifesto a rota, sem inferir o nível da matéria."""
    state_path = Path(state_dir)
    paths = initialize_state(state_path, matter_id=state_path.name)
    manifest = _read_json(paths["manifest"], {"matter_id": state_path.name})
    if explicit_agents is None:
        previous_route = manifest.get("route") if isinstance(manifest.get("route"), dict) else {}
        explicit_agents = previous_route.get("explicit", [])
    route = route_for_matter(state_path, explicit_level, explicit_agents)
    manifest["route"] = route
    manifest["route_updated_at"] = _now()
    manifest["updated_at"] = _now()
    _write_json(paths["manifest"], manifest)
    return route


def record_agent_event(
    state_dir: Path | str,
    agent: str,
    *,
    event: str = "context_pack",
    rerun: bool = False,
    measure: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Registrar somente contagens agregadas de eventos do fluxo."""
    state_path = Path(state_dir)
    paths = initialize_state(state_path, matter_id=state_path.name)
    manifest = _read_json(paths["manifest"], {"matter_id": state_path.name})
    events = manifest.get("agent_events") if isinstance(manifest.get("agent_events"), dict) else {}
    events["count"] = int(events.get("count", 0)) + 1
    events["reruns"] = int(events.get("reruns", 0)) + (1 if rerun else 0)
    by_agent = events.get("by_agent") if isinstance(events.get("by_agent"), dict) else {}
    item = by_agent.get(agent) if isinstance(by_agent.get(agent), dict) else {}
    item["count"] = int(item.get("count", 0)) + 1
    item["reruns"] = int(item.get("reruns", 0)) + (1 if rerun else 0)
    item["events"] = int(item.get("events", 0)) + 1
    if measure:
        item["bytes"] = int(item.get("bytes", 0)) + int(measure.get("bytes", 0))
        item["items"] = int(item.get("items", 0)) + int(measure.get("items", 0))
    by_agent[agent] = item
    events["by_agent"] = by_agent
    events["last_event"] = event
    events["updated_at"] = _now()
    manifest["agent_events"] = events
    manifest["updated_at"] = _now()
    _write_json(paths["manifest"], manifest)
    return events


def record_publish_event(state_dir: Path | str, *, blocked: bool) -> dict[str, Any]:
    """Contar tentativas de publicação sem registrar conteúdo do DOCX."""
    state_path = Path(state_dir)
    paths = initialize_state(state_path, matter_id=state_path.name)
    manifest = _read_json(paths["manifest"], {"matter_id": state_path.name})
    manifest["publish_attempts"] = int(manifest.get("publish_attempts", 0)) + 1
    manifest["blocked_attempts"] = int(manifest.get("blocked_attempts", 0)) + (1 if blocked else 0)
    manifest["updated_at"] = _now()
    _write_json(paths["manifest"], manifest)
    return manifest


def record_review_round(
    state_dir: Path | str,
    finding_ids: Iterable[str],
    *,
    changed: bool,
) -> dict[str, Any]:
    state_path = Path(state_dir)
    paths = initialize_state(state_path, matter_id=state_path.name)
    state = _read_json(paths["state"], {"matter_id": state_path.name})
    manifest = _read_json(paths["manifest"], {"matter_id": state_path.name})
    rounds = manifest.get("semantic_rounds", {})
    if not isinstance(rounds, dict):
        rounds = {}
    ids = sorted({str(item) for item in finding_ids if item})
    for finding_id in ids:
        item = rounds.get(finding_id, {})
        if not isinstance(item, dict):
            item = {}
        item["count"] = int(item.get("count", 0)) + 1
        item["last_changed"] = bool(changed)
        item["updated_at"] = _now()
        rounds[finding_id] = item
    manifest["semantic_rounds"] = rounds
    manifest["updated_at"] = _now()
    _write_json(paths["manifest"], manifest)
    return {"finding_ids": ids, "rounds": rounds, "changed": bool(changed)}


def should_retry(state_dir: Path | str, finding_ids: Iterable[str]) -> bool:
    paths = initialize_state(Path(state_dir), matter_id=Path(state_dir).name)
    manifest = _read_json(paths["manifest"], {})
    rounds = manifest.get("semantic_rounds", {})
    ids = [str(item) for item in finding_ids if item]
    if not ids:
        return False
    return any(int(rounds.get(item, {}).get("count", 0)) < MAX_AUTO_CORRECTION_ROUNDS for item in ids)


def measure_context_pack(pack: dict[str, Any]) -> dict[str, int]:
    serialized = json.dumps(pack, ensure_ascii=False, sort_keys=True)
    return {
        "bytes": len(serialized.encode("utf-8")),
        "characters": len(serialized),
        "fields": len(pack),
        "items": sum(len(value) for value in pack.values() if isinstance(value, list)),
    }


def record_context_metric(state_dir: Path | str, pack: dict[str, Any]) -> dict[str, Any]:
    state_path = Path(state_dir)
    paths = initialize_state(state_path, matter_id=state_path.name)
    state = _read_json(paths["state"], {"matter_id": state_path.name})
    metrics = state.get("metrics") if isinstance(state.get("metrics"), dict) else {}
    context_metrics = metrics.get("context_packs") if isinstance(metrics.get("context_packs"), dict) else {}
    measure = measure_context_pack(pack)
    task_type = str(pack.get("task_type", "desconhecido"))
    by_task = context_metrics.get("by_task") if isinstance(context_metrics.get("by_task"), dict) else {}
    task = by_task.get(task_type) if isinstance(by_task.get(task_type), dict) else {}
    for key, value in measure.items():
        task[key] = int(task.get(key, 0)) + int(value)
    task["count"] = int(task.get("count", 0)) + 1
    by_task[task_type] = task
    context_metrics["count"] = int(context_metrics.get("count", 0)) + 1
    context_metrics["bytes"] = int(context_metrics.get("bytes", 0)) + measure["bytes"]
    context_metrics["characters"] = int(context_metrics.get("characters", 0)) + measure["characters"]
    context_metrics["by_task"] = by_task
    metrics["context_packs"] = context_metrics
    state["metrics"] = metrics
    state["updated_at"] = _now()
    _write_json(paths["state"], state)
    return measure


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Revisão semântica e coordenação RDAA")
    parser.add_argument("state_dir", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("review", help="revisar consistência objetiva")
    route = commands.add_parser("route", help="montar rota conservadora")
    route.add_argument("--level", default=None)
    route.add_argument("--agent", action="append", choices=list(OPTIONAL_ROUTE_AGENTS), default=[])
    retry = commands.add_parser("retry", help="verificar se ainda cabe rodada automática")
    retry.add_argument("finding_ids", nargs="*")
    args = parser.parse_args()
    if args.command == "review":
        report = review_state(args.state_dir)
        persist_semantic_review(args.state_dir, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if report["status"] == "BLOCK" else 0
    if args.command == "route":
        route = persist_route(args.state_dir, args.level, args.agent)
        print(json.dumps(route, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"retry": should_retry(args.state_dir, args.finding_ids)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
