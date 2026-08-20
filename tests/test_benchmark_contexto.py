#!/usr/bin/env python3
"""Regressões do benchmark local de contexto e roteamento."""

from __future__ import annotations

from pathlib import Path

from benchmark_contexto import run_benchmark

ROOT = Path(__file__).resolve().parents[1]


def test_benchmark_routes_and_measurements_are_deterministic() -> None:
    result = run_benchmark(ROOT / "tests" / "fixtures" / "context_happy.json")
    by_case = {case["case"]: case for case in result["cases"]}
    assert by_case["sem-nivel"]["risk_level"] is None
    assert by_case["sem-nivel"]["recommended"] == []
    assert by_case["medio"]["recommended"] == ["critico-rdaa"]
    assert by_case["alto"]["recommended"] == ["critico-rdaa", "conselho-rdaa"]
    for case in result["cases"]:
        assert case["rows"]
        assert all(row["full_state_bytes"] > row["bytes"] for row in case["rows"])
        assert all(0 < row["pack_to_state_ratio"] < 1 for row in case["rows"])


if __name__ == "__main__":
    test_benchmark_routes_and_measurements_are_deterministic()
    print("[OK] benchmark local de contexto e roteamento passou")
