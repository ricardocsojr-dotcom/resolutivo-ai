#!/usr/bin/env python3
"""Regressões do módulo semântico, de risco e de métricas locais."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "revisor-rdaa" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from semantica_rdaa import (  # noqa: E402
    measure_context_pack,
    persist_semantic_review,
    persist_route,
    record_agent_event,
    record_context_metric,
    record_publish_event,
    record_review_round,
    review_state,
    route_for_matter,
    should_retry,
)
from estado_rdaa import initialize_state  # noqa: E402



def _write_state(state_dir: Path, payload: dict) -> None:
    paths = initialize_state(state_dir, matter_id=payload.get("matter_id", state_dir.name))
    paths["state"].write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")



def test_semantic_review_passes_valid_references_and_blocks_missing_reference() -> None:
    with tempfile.TemporaryDirectory() as temp:
        valid_dir = Path(temp) / "valid"
        _write_state(
            valid_dir,
            {
                "schema_version": "3",
                "matter_id": "valid",
                "facts": [{"id": "F-1", "campo": "numero_processo", "valor": "1"}],
                "theses_structured": [{"id": "T-1", "texto": "Tese", "source_ids": ["C-1"]}],
                "citations": [{"id": "C-1", "texto": "Fonte"}],
                "requests": [{"id": "REQ-1", "texto": "Pedido"}],
                "risks": [{"id": "R-1", "descricao": "Risco", "nivel": None, "origem": "critico"}],
                "decisions": [],
            },
        )
        valid_report = review_state(valid_dir)
        assert valid_report["status"] == "PASS"
        persist_semantic_review(valid_dir, valid_report)

        invalid_dir = Path(temp) / "invalid"
        _write_state(
            invalid_dir,
            {
                "schema_version": "3",
                "matter_id": "invalid",
                "facts": [],
                "theses_structured": [{"id": "T-1", "texto": "Tese", "source_ids": ["MISSING"]}],
                "citations": [],
            },
        )
        invalid_report = review_state(invalid_dir)
        assert invalid_report["status"] == "BLOCK"
        assert any(item["kind"] == "reference_missing" for item in invalid_report["findings"])


def test_route_requires_explicit_risk_and_keeps_critical_agents_optional_when_unknown() -> None:
    with tempfile.TemporaryDirectory() as temp:
        unknown_dir = Path(temp) / "unknown"
        _write_state(unknown_dir, {"matter_id": "unknown", "risks": []})
        unknown = route_for_matter(unknown_dir)
        assert unknown["risk_level"] is None
        assert unknown["recommended"] == []
        assert unknown["required"] == ["semantic_review", "revisor-rdaa"]
        assert unknown["selected"] == ["semantic_review", "revisor-rdaa"]
        assert unknown["omitted"] == ["critico-rdaa", "conselho-rdaa"]
        override = route_for_matter(unknown_dir, explicit_agents=["critico-rdaa"])
        assert "critico-rdaa" in override["selected"]
        assert "critico-rdaa" not in override["omitted"]
        assert override["selection_source"] == "override_explicito"

        high_dir = Path(temp) / "high"
        _write_state(
            high_dir,
            {
                "matter_id": "high",
                "risks": [{"id": "R-1", "descricao": "Alto", "nivel": "alto", "origem": "usuario"}],
            },
        )
        high = route_for_matter(high_dir)
        assert high["risk_level"] == "alto"
        assert "critico-rdaa" in high["recommended"]
        assert "conselho-rdaa" in high["recommended"]
        assert high["selected"] == ["semantic_review", "revisor-rdaa", "critico-rdaa", "conselho-rdaa"]
        assert high["omitted"] == []


def test_route_and_execution_events_are_persisted_without_inference() -> None:
    with tempfile.TemporaryDirectory() as temp:
        state_dir = Path(temp) / "manifest"
        _write_state(state_dir, {"matter_id": "manifest"})
        route = persist_route(state_dir)
        assert route["risk_level"] is None
        assert route["recommended"] == []
        explicit = persist_route(state_dir, explicit_agents=["critico-rdaa"])
        assert explicit["selection_source"] == "override_explicito"
        assert "critico-rdaa" in explicit["selected"]
        preserved = persist_route(state_dir)
        assert preserved["explicit"] == ["critico-rdaa"]
        route_high = persist_route(state_dir, "alto")
        assert route_high["risk_level"] == "alto"
        assert "critico-rdaa" in route_high["recommended"]
        assert route_high["selected"] == ["semantic_review", "revisor-rdaa", "critico-rdaa", "conselho-rdaa"]
        record_agent_event(state_dir, "redator", measure={"bytes": 10, "items": 2})
        record_publish_event(state_dir, blocked=True)
        manifest = json.loads((state_dir / "run_manifest.json").read_text(encoding="utf-8"))
        assert manifest["route"]["risk_level"] == "alto"
        assert manifest["agent_events"]["by_agent"]["redator"]["bytes"] == 10
        assert manifest["publish_attempts"] == 1
        assert manifest["blocked_attempts"] == 1


def test_semantic_round_limit_prevents_infinite_retry() -> None:
    with tempfile.TemporaryDirectory() as temp:
        state_dir = Path(temp) / "rounds"
        _write_state(state_dir, {"matter_id": "rounds"})
        assert should_retry(state_dir, ["SEM-1"]) is True
        first = record_review_round(state_dir, ["SEM-1"], changed=False)
        assert first["rounds"]["SEM-1"]["count"] == 1
        assert should_retry(state_dir, ["SEM-1"]) is False


def test_context_metrics_are_local_and_measure_serialized_pack() -> None:
    with tempfile.TemporaryDirectory() as temp:
        state_dir = Path(temp) / "metrics"
        _write_state(state_dir, {"matter_id": "metrics"})
        pack = {"matter_id": "metrics", "task_type": "redator", "facts": [{"id": "F-1"}]}
        measured = measure_context_pack(pack)
        recorded = record_context_metric(state_dir, pack)
        assert measured == recorded
        state = json.loads((state_dir / "matter_state.json").read_text(encoding="utf-8"))
        assert state["metrics"]["context_packs"]["count"] == 1
        assert state["metrics"]["context_packs"]["by_task"]["redator"]["count"] == 1


if __name__ == "__main__":
    test_semantic_review_passes_valid_references_and_blocks_missing_reference()
    test_route_requires_explicit_risk_and_keeps_critical_agents_optional_when_unknown()
    test_route_and_execution_events_are_persisted_without_inference()
    test_semantic_round_limit_prevents_infinite_retry()
    test_context_metrics_are_local_and_measure_serialized_pack()
    print("[OK] revisão semântica, roteamento, limite de rodada e métricas passaram")
