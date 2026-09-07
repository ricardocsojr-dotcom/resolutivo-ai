#!/usr/bin/env python3
"""Audita o gap entre tempo de relogio por fase e tempo efetivo de worker
nos run_manifest.json existentes em .rdaa-run/**.

Nao altera nada. So le e reporta.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Projetos\resolutivo-ai\.rdaa-run")
EXTRA_ROOTS = [
    Path(r"C:\Users\ricar\OneDrive - RD\Resolutivo"),
]
SKIP_DIRS = {"e2e-abc", "engineering-review", "candidate"}


def parse_dt(s: str | None):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def find_manifests():
    seen = set()
    for base in [ROOT, *EXTRA_ROOTS]:
        if not base.exists():
            continue
        for p in base.rglob("run_manifest.json"):
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            rp = p.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            yield rp


def audit_one(path: Path) -> dict:
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"path": str(path), "error": str(e)}

    matter_id = d.get("matter_id") or path.parent.name
    transitions = d.get("transitions", [])
    executions = d.get("executions", [])
    nivel = d.get("nivel_peca") or (d.get("route") or {}).get("effective_piece_level")

    # tempo total (primeira -> ultima transicao)
    times = [parse_dt(t.get("at")) for t in transitions]
    times = [t for t in times if t]
    total_wall_s = (max(times) - min(times)).total_seconds() if len(times) >= 2 else None

    # tempo total de worker ativo (soma duration_ms das execucoes)
    worker_active_ms = sum(e.get("duration_ms") or 0 for e in executions)
    worker_active_s = worker_active_ms / 1000 if executions else 0

    # tempo por fase: usa "to" de cada transicao como marco, calcula delta
    # em relacao a transicao anterior
    phase_durations = []
    for i in range(1, len(transitions)):
        prev = parse_dt(transitions[i - 1].get("at"))
        cur = parse_dt(transitions[i].get("at"))
        if prev and cur:
            phase_durations.append(
                {
                    "phase": transitions[i].get("to"),
                    "from_phase": transitions[i - 1].get("to"),
                    "seconds": (cur - prev).total_seconds(),
                }
            )

    gap_s = None
    if total_wall_s is not None:
        gap_s = total_wall_s - worker_active_s

    return {
        "path": str(path),
        "matter_id": matter_id,
        "nivel_peca": nivel,
        "phase_final": d.get("phase"),
        "total_wall_s": total_wall_s,
        "worker_active_s": worker_active_s,
        "gap_s": gap_s,
        "n_executions": len(executions),
        "n_transitions": len(transitions),
        "phase_durations": sorted(phase_durations, key=lambda x: -x["seconds"])[:5],
    }


def fmt_min(seconds):
    if seconds is None:
        return "n/d"
    return f"{seconds/60:.1f}min"


def main():
    results = []
    for path in find_manifests():
        r = audit_one(path)
        if r.get("total_wall_s") and r["total_wall_s"] > 0:
            results.append(r)

    results.sort(key=lambda r: -(r.get("gap_s") or 0))

    print(f"\n{'='*100}")
    print(f"AUDITORIA DE GAP — {len(results)} matérias com timeline analisável")
    print(f"{'='*100}\n")

    header = f"{'matter_id':<45} {'nivel':<6} {'total':<10} {'worker':<10} {'gap':<10} {'gap%':<6} {'execs':<6}"
    print(header)
    print("-" * len(header))
    for r in results:
        total = r["total_wall_s"]
        gap = r["gap_s"]
        gap_pct = (gap / total * 100) if total else 0
        print(
            f"{r['matter_id'][:44]:<45} {str(r['nivel_peca'] or '?'):<6} "
            f"{fmt_min(total):<10} {fmt_min(r['worker_active_s']):<10} "
            f"{fmt_min(gap):<10} {gap_pct:>5.0f}% {r['n_executions']:<6}"
        )

    print(f"\n{'='*100}")
    print("TOP 3 MAIORES GAPS — detalhe de fases mais lentas")
    print(f"{'='*100}")
    for r in results[:3]:
        print(f"\n--- {r['matter_id']} (nível {r['nivel_peca']}) ---")
        print(f"  Caminho: {r['path']}")
        print(f"  Tempo total: {fmt_min(r['total_wall_s'])} | Worker ativo: {fmt_min(r['worker_active_s'])} | Gap: {fmt_min(r['gap_s'])}")
        print("  Fases mais lentas (wall time entre transições):")
        for pd in r["phase_durations"]:
            print(f"    {pd['from_phase']} -> {pd['phase']}: {fmt_min(pd['seconds'])}")

    # agregados
    total_gap = sum(r["gap_s"] or 0 for r in results)
    total_worker = sum(r["worker_active_s"] or 0 for r in results)
    total_wall = sum(r["total_wall_s"] or 0 for r in results)
    print(f"\n{'='*100}")
    print("AGREGADO GERAL")
    print(f"{'='*100}")
    print(f"  Tempo total de relógio somado: {fmt_min(total_wall)}")
    print(f"  Tempo de worker ativo somado:  {fmt_min(total_worker)}")
    print(f"  Gap total (tempo morto):       {fmt_min(total_gap)}  ({total_gap/total_wall*100:.0f}% do tempo total)" if total_wall else "")


if __name__ == "__main__":
    main()
