from __future__ import annotations
from typing import Any

def exigir_liberado(manifest: dict[str, Any]) -> None:
    status = manifest.get("status")
    if status in ("paused", "aborted", "paralisado"):
        raise ValueError(f"execução bloqueada pelo disjuntor (status: {status})")

def falhar(manifest: dict[str, Any], diagnostic: str, timestamp: str) -> dict[str, Any]:
    phase = manifest.get("phase", "unknown")
    failures = manifest.setdefault("failures", {})
    entry = failures.setdefault(phase, {"count": 0, "last_failure_at": None, "error": None})
    entry["count"] += 1
    entry["last_failure_at"] = timestamp
    entry["error"] = str(diagnostic)
    if entry["count"] >= 2:
        manifest["status"] = "paused"
    return entry

def decidir(manifest: dict[str, Any], action: str, authority: str, reason: str, timestamp: str) -> None:
    if str(authority).strip().casefold() != "ricardo":
        raise ValueError("somente autoridade ricardo pode decidir disjuntor")
    if not str(reason).strip():
        raise ValueError("justificativa obrigatória")
    if action == "resume":
        manifest["status"] = "ready"
        phase = manifest.get("phase")
        if phase and phase in manifest.get("failures", {}):
            manifest["failures"][phase]["count"] = 0
    elif action == "abort":
        manifest["status"] = "aborted"
    else:
        raise ValueError(f"ação de disjuntor inválida: {action}")
    manifest.setdefault("disjuntor_decisions", []).append({
        "action": action,
        "authority": authority,
        "reason": reason,
        "at": timestamp,
    })
