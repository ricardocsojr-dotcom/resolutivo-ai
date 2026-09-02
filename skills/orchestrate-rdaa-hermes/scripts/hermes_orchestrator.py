#!/usr/bin/env python3
"""Hermes skill integration: callable Python interface to orquestrador_rdaa."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ORCHESTRATOR_SCRIPT = ROOT / "skills" / "redigir-peca" / "scripts" / "orquestrador_rdaa.py"
OBSIDIAN_SCRIPT = ROOT / "skills" / "redigir-peca" / "scripts" / "integracao_obsidian.py"
EXECUTOR_SCRIPT = ROOT / "skills" / "redigir-peca" / "scripts" / "executar_motor.py"
PAINEL_SCRIPT = ROOT / "skills" / "orquestrar-rdaa" / "scripts" / "painel_status.py"


class OrchestratorError(Exception):
    """Orchestrator command failed."""


def _run_cmd(cmd: list[str], check: bool = True) -> dict[str, Any]:
    """Run a command via subprocess, capture stdout/stderr."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if check and result.returncode != 0:
            raise OrchestratorError(
                f"Command failed (exit {result.returncode}):\n"
                f"Command: {' '.join(cmd)}\n"
                f"Stderr: {result.stderr}"
            )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        raise OrchestratorError("Command timed out (30s)")
    except Exception as exc:
        raise OrchestratorError(f"Subprocess error: {exc}")


def get_route(piece_level: str, risk_level: str) -> dict[str, Any]:
    """Get route for a piece level and risk level."""
    result = _run_cmd(
        [sys.executable, str(ORCHESTRATOR_SCRIPT), "route",
         "--piece-level", piece_level, "--risk-level", risk_level]
    )
    # Parse JSON from stdout
    return json.loads(result["stdout"])


def initialize_matter(
    state_dir: Path | str,
    matter_id: str,
    piece_level: str,
    risk_level: str,
) -> dict[str, Any]:
    """Initialize a new matter manifest."""
    state_dir = Path(state_dir)
    result = _run_cmd(
        [sys.executable, str(ORCHESTRATOR_SCRIPT), "init", str(state_dir),
         "--matter-id", matter_id,
         "--piece-level", piece_level,
         "--risk-level", risk_level]
    )
    # Parse JSON from stdout
    return json.loads(result["stdout"])


def get_state(state_dir: Path | str) -> dict[str, Any]:
    """Read current manifest state (no changes)."""
    state_dir = Path(state_dir)
    result = _run_cmd(
        [sys.executable, str(ORCHESTRATOR_SCRIPT), "status", str(state_dir)]
    )
    return json.loads(result["stdout"])


def advance_phase(state_dir: Path | str, target_phase: str) -> dict[str, Any]:
    """Advance to the next phase."""
    state_dir = Path(state_dir)
    result = _run_cmd(
        [sys.executable, str(ORCHESTRATOR_SCRIPT), "advance", str(state_dir), target_phase]
    )
    return json.loads(result["stdout"])


def register_approval(
    state_dir: Path | str,
    gate: str,
    artifact_path: Path | str,
    approved_by: str,
) -> dict[str, Any]:
    """Register a human approval."""
    state_dir = Path(state_dir)
    artifact_path = Path(artifact_path)
    result = _run_cmd(
        [sys.executable, str(ORCHESTRATOR_SCRIPT), "approve", str(state_dir),
         "--gate", gate,
         "--artifact", str(artifact_path),
         "--approved-by", approved_by]
    )
    return json.loads(result["stdout"])


def query_ementario(
    domain: str,
    vault_root: Path | str | None = None,
    output_path: Path | str | None = None,
) -> dict[str, Any]:
    """Query Ementário (Obsidian vault)."""
    if vault_root is None:
        vault_root = "\\wsl.localhost\\Ubuntu\\home\\ricar\\vaults\\ementario-resolutivo"
    if output_path is None:
        output_path = ROOT / ".rdaa-run" / f"EMENTARIO-{domain}.json"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    result = _run_cmd(
        [sys.executable, str(OBSIDIAN_SCRIPT), "consultar-ementario",
         "--domain", domain,
         "--vault-root", str(vault_root),
         "--output", str(output_path)]
    )
    
    # Read the generated JSON
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    return {
        "output_path": str(output_path),
        "exit_code": result["exit_code"],
        "payload": payload,
    }


def register_vault_lookup(
    state_dir: Path | str,
    vault: str,
    artifact_path: Path | str,
) -> dict[str, Any]:
    """Register a vault lookup in the manifest."""
    state_dir = Path(state_dir)
    artifact_path = Path(artifact_path)
    result = _run_cmd(
        [sys.executable, str(ORCHESTRATOR_SCRIPT), "register-vault-lookup", str(state_dir),
         "--vault", vault,
         "--artifact", str(artifact_path)]
    )
    return json.loads(result["stdout"])


def execute_worker(
    motor: str,
    prompt_path: Path | str,
    output_path: Path | str,
    state_dir: Path | str,
    role: str,
    timeout_seconds: int = 600,
    max_budget_usd: float | None = None,
) -> dict[str, Any]:
    """Execute an isolated worker (Codex, Agy, Claude)."""
    state_dir = Path(state_dir)
    prompt_path = Path(prompt_path)
    output_path = Path(output_path)
    
    cmd = [
        sys.executable, str(EXECUTOR_SCRIPT), motor,
        "--prompt", str(prompt_path),
        "--output", str(output_path),
        "--state-dir", str(state_dir),
        "--role", role,
        "--timeout", str(timeout_seconds),
    ]
    
    if max_budget_usd is not None:
        cmd.extend(["--max-budget-usd", str(max_budget_usd)])
    
    result = _run_cmd(cmd)
    
    return {
        "motor": motor,
        "role": role,
        "exit_code": result["exit_code"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "output_path": str(output_path),
    }


def generate_dashboard(state_dir: Path | str, output_path: Path | str | None = None) -> Path:
    """Generate HTML dashboard."""
    state_dir = Path(state_dir)
    if output_path is None:
        output_path = state_dir / "PAINEL.html"
    else:
        output_path = Path(output_path)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    _run_cmd(
        [sys.executable, str(PAINEL_SCRIPT), str(state_dir),
         "--output", str(output_path)]
    )
    
    return output_path


if __name__ == "__main__":
    # Example: initialize and check state
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp:
        state_dir = Path(tmp) / "test-matter"
        
        print("1. Initialize matter B/baixo...")
        manifest = initialize_matter(
            state_dir, "test-matter", "B", "baixo"
        )
        print(f"   Phase: {manifest['phase']}")
        print(f"   Route: {manifest['route']['declared_piece_level']}")
        
        print("\n2. Get current state...")
        state = get_state(state_dir)
        print(f"   Phase: {state['phase']}")
        print(f"   Vault required: {state['route']['vault']['lookup']['enabled']}")
        
        print("\n3. Advance to intake_ready...")
        manifest = advance_phase(state_dir, "intake_ready")
        print(f"   Phase: {manifest['phase']}")
        
        print("\n✓ All basic operations work!")
