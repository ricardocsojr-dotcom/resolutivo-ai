#!/usr/bin/env python3
"""Executa validação integrada de contextos anonimizados C, B e A."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "skills" / "formatar-peca" / "scripts" / "construir_peca.py"
PUBLISH = ROOT / "skills" / "revisor-rdaa" / "scripts" / "publicar_docx.py"
FIXTURES = ROOT / "tests" / "fixtures"
SCRIPT_DIR = ROOT / "skills" / "revisor-rdaa" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from contexto_rdaa import TASK_TYPES, build_context_pack  # noqa: E402
from semantica_rdaa import measure_context_pack  # noqa: E402
from verificar_semantica_docx import verify_docx_semantics  # noqa: E402



def _load_context(case: str) -> dict[str, Any]:
    path = FIXTURES / f"context_validacao_{case}.json"
    context = json.loads(path.read_text(encoding="utf-8"))
    if case == "A":
        for block in context.get("blocos", []):
            if block.get("tipo") == "figura":
                block["image_path"] = str(FIXTURES / "visual-law-fixture.png")
    return context



def _run(command: list[str], log_path: Path) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    log_path.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"comando falhou ({result.returncode}): {' '.join(command)}")



def validate_case(case: str, output_root: Path) -> dict[str, Any]:
    case_dir = output_root / case
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True)
    context = _load_context(case)
    context_path = case_dir / "context.json"
    context_path.write_text(json.dumps(context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    candidate = case_dir / "candidate.docx"
    final = case_dir / "final.docx"
    state_dir = case_dir / ".rdaa-run"
    backup_dir = case_dir / ".rdaa-backups"
    qa_json = case_dir / "qa.json"

    _run([sys.executable, str(BUILD), "--context", str(context_path), "--output", str(candidate)], case_dir / "build.log")
    _run(
        [
            sys.executable,
            str(PUBLISH),
            "--input",
            str(candidate),
            "--output",
            str(final),
            "--state-dir",
            str(state_dir),
            "--backup-dir",
            str(backup_dir),
            "--qa-json",
            str(qa_json),
            "--context",
            str(context_path),
        ],
        case_dir / "publish.log",
    )
    assert final.is_file(), f"final não gerado para {case}"
    semantic = verify_docx_semantics(final, context)
    assert semantic["status"] == "PASS", semantic
    state_case_dir = state_dir
    manifest = json.loads((state_case_dir / "run_manifest.json").read_text(encoding="utf-8"))
    state = json.loads((state_case_dir / "matter_state.json").read_text(encoding="utf-8"))
    assert manifest["route"]["risk_level"] == context["nivel_risco"].lower()
    assert manifest["nivel_peca"] == context["nivel_peca"]
    assert manifest["piece_contract_status"] == "PASS"
    assert manifest["publish_attempts"] == 1
    assert manifest["blocked_attempts"] == 0
    assert state["matter_id"] == context["matter_id"]
    assert state["nivel_peca"] == context["nivel_peca"]
    pack_metrics = {}
    for task_type in sorted(TASK_TYPES):
        pack = build_context_pack(state_case_dir, task_type)
        if task_type in {"redator", "revisor", "formatador"}:
            assert pack["nivel_peca"] == context["nivel_peca"]
            assert pack["redacao_por_blocos"] is (case in {"A", "B"})
        pack_metrics[task_type] = measure_context_pack(pack)
    manifest = json.loads((state_case_dir / "run_manifest.json").read_text(encoding="utf-8"))
    state = json.loads((state_case_dir / "matter_state.json").read_text(encoding="utf-8"))
    return {
        "case": case,
        "matter_id": context["matter_id"],
        "risk_level": context["nivel_risco"],
        "piece_level": context["nivel_peca"],
        "route": manifest["route"],
        "publish_attempts": manifest["publish_attempts"],
        "blocked_attempts": manifest["blocked_attempts"],
        "semantic_status": semantic["status"],
        "final_bytes": final.stat().st_size,
        "state_keys": sorted(state.keys()),
        "agent_events": manifest.get("agent_events", {}),
        "context_metrics": state.get("metrics", {}).get("context_packs", {}),
        "pack_metrics": pack_metrics,
    }



def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validar peças anonimizadas RDAA")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    if args.output_root.exists():
        shutil.rmtree(args.output_root)
    args.output_root.mkdir(parents=True)
    results = [validate_case(case, args.output_root) for case in ("C", "B", "A")]
    report = {"cases": results, "status": "PASS"}
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
