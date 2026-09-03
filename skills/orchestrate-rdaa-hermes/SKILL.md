---
name: orchestrate-rdaa-hermes
description: Execute RDAA workflow commands via Hermes CLI integration. Direct use of orquestrador_rdaa as subprocess.
---

# RDAA Orchestrator — Hermes CLI Bridge

Exposes `orquestracao_rdaa` as a callable interface from Hermes skills and agents. All commands run deterministic state machine (`orquestrador_rdaa.py`) and never substitute model reasoning for human gate decisions.

## Quick Start

```bash
# Initialize a matter (C/B/A level, risk assessed)
python3 skills/redigir-peca/scripts/orquestrador_rdaa.py init .rdaa-run/matter-id \
  --matter-id matter-id --piece-level B --risk-level baixo

# Check current phase + route
python3 skills/redigir-peca/scripts/orquestrador_rdaa.py state .rdaa-run/matter-id

# (B/A only) Query Ementário and register lookup
python3 skills/redigir-peca/scripts/integracao_obsidian.py consultar-ementario \
  --domain dano-moral --output .rdaa-run/matter-id/EMENTARIO-CONTEXTO.json

python3 skills/redigir-peca/scripts/orquestrador_rdaa.py register-vault-lookup .rdaa-run/matter-id \
  --vault ementario-resolutivo --artifact .rdaa-run/matter-id/EMENTARIO-CONTEXTO.json

# Advance phase (one step at a time, gated)
python3 skills/redigir-peca/scripts/orquestrador_rdaa.py advance .rdaa-run/matter-id vault_context_ready

# Register human approval (skeleton, release, etc.)
python3 skills/redigir-peca/scripts/orquestrador_rdaa.py approve .rdaa-run/matter-id \
  --gate skeleton_approval --artifact ./ESQUELETO.md --approved-by Ricardo

# Execute isolated worker (Codex/Antigravity/Claude)
python3 skills/redigir-peca/scripts/executar_motor.py codex \
  --prompt .rdaa-run/matter-id/PROMPT.md --output .rdaa-run/matter-id/DRAFT.md \
  --state-dir .rdaa-run/matter-id --role writer --timeout 600

# Register executed output (via executar_motor already does this)
python3 skills/redigir-peca/scripts/orquestrador_rdaa.py register-execution .rdaa-run/matter-id \
  --role writer --motor codex --prompt ./PROMPT.md --output ./DRAFT.md

# Generate dashboard
python3 skills/orquestrar-rdaa/scripts/painel_status.py .rdaa-run/matter-id \
  --output .rdaa-run/matter-id/PAINEL.html
```

## Architecture

- **Deterministic state machine:** `orquestrador_rdaa.py` — all transitions logged, no LLM reasoning.
- **Worker executor:** `executar_motor.py` — isolated subprocess, worker-specific validation.
- **Obsidian read-only client:** `integracao_obsidian.py` — vault queries, redaction, provenance.
- **Dashboard:** `painel_status.py` — renders HTML from manifest.

All commands are **side-effect-free reads** or **locked writes** (mutex per matter). No automatic fallback, no silent retry.

## When to Use This Skill

- Hermes skill code needs to call the orchestrator directly (e.g., advancing phases, registering approvals).
- You need to wrap worker execution in subprocess calls with timeout/sandbox.
- You're building a higher-level automation layer (e.g., monitoring, auto-resumption).

## When NOT to Use This Skill

- For human-interactive matter management: use `orquestrar-rdaa` skill instead (higher-level, Hermes-idiomatic).
- For worker coding itself: workers don't call the orchestrator; use `executar_motor.py --state-dir` as the entry point.
- For Cérebro-Ricar writes: use `registrar_cerebro.py` (local, sem WSL). Read queries usam C:\Users\ricar\cerebro-ricar\ direto.

## Key Constraints

1. **One phase advance per call.** Don't call `advance` twice in sequence without checking state.
2. **Human gates are blocking.** If `open_gate` is set in the manifest, `advance` will fail. Use `clarify` to get approval, then `approve` to register it.
3. **Worker execution is isolated.** Codex, Agy, Claude run as subprocess. Hermes doesn't see stdout unless captured.
4. **Manifests are versioned.** Every `advance`, `approve`, or execution registers a transition + timestamp. Rollback is not supported; use backups if you need to restart.
5. **Vault is read-only in B/A.** `integracao_obsidian.py` blocks path traversal and redacts sensitive data before handing off to workers.

## Example: Full Matter Lifecycle (Python Wrapper)

Import and call directly from a Hermes skill:

```python
from pathlib import Path
from skills.orchestrate_rdaa_hermes.scripts.hermes_orchestrator import (
    initialize_matter, advance_phase, query_ementario, register_vault_lookup,
    register_approval, generate_dashboard,
)

matter_id = "contrato-2026-0042"
state_dir = Path(f".rdaa-run/{matter_id}")

# 1. Initialize
manifest = initialize_matter(state_dir, matter_id, "B", "medio")
print(f"Matter initialized, phase: {manifest['phase']}")

# 2. Advance to intake_ready
advance_phase(state_dir, "intake_ready")

# 3. Query Ementário (B only)
ementario = query_ementario(
    "contratos-bancarios",
    output_path=state_dir / "EMENTARIO.json"
)

if ementario["exit_code"] == 0:
    register_vault_lookup(state_dir, "ementario-resolutivo", 
                         state_dir / "EMENTARIO.json")
    
    # 4. Advance to vault_context_ready
    advance_phase(state_dir, "vault_context_ready")

# 5. Continue through skeleton phases...
advance_phase(state_dir, "sources_ready")
advance_phase(state_dir, "skeleton_ready")
advance_phase(state_dir, "awaiting_skeleton_approval")

# 6. Get human approval (use clarify for user decision)
decision = clarify(questions=[{
    "question": f"Approve skeleton for {matter_id}?",
    "choices": ["Approve", "Reject"]
}])

if decision["responses"][0] == "Approve":
    skeleton_file = state_dir / "SKELETON-APPROVED.md"
    skeleton_file.write_text("# Approved Structure")
    
    register_approval(state_dir, "skeleton_approval", 
                     skeleton_file, "Ricardo")
    advance_phase(state_dir, "skeleton_approved")

# 7. Workers handle their phases (drafting, criticizing, validating)
# Executor calls (executar_motor.py) run subprocess, register outputs auto

# 8. Generate dashboard for monitoring
dashboard = generate_dashboard(state_dir)
print(f"Dashboard: {dashboard}")
```

## CLI Reference

### `orquestrador_rdaa.py`

- `route --piece-level <C|B|A> --risk-level <baixo|medio|alto|critico>` — Display route without initialization.
- `init <state_dir> --matter-id <id> --piece-level <C|B|A> --risk-level <baixo|medio|alto|critico>` — Initialize manifest.
- `state <state_dir>` — Read and print current phase + route (no changes).
- `advance <state_dir> <phase>` — Transition to next phase (validates gate, sequence).
- `approve <state_dir> --gate <gate> --artifact <file> --approved-by <name>` — Register human approval.
- `register-vault-lookup <state_dir> --vault <vault> --artifact <file>` — Register read-only Ementário query.
- `register-execution <state_dir> --role <planner|writer|critic|validator> --motor <codex|agy|claude> --prompt <file> --output <file>` — Register completed worker output.

### `integracao_obsidian.py`

- `consultar-ementario --domain <domain> --vault-root <path> --output <file>` — Query Ementário, write JSON package with `origin`, `mode`, `status`, `documents`.

### `executar_motor.py`

- `codex|agy|claude --prompt <file> --output <file> --state-dir <dir> --role <role> [--timeout N] [--budget N]` — Run worker, register output, exit.

### `painel_status.py`

- `<state_dir> --output <file>` — Generate HTML dashboard.

## Troubleshooting

**Lock error:** Another process is writing to the matter. Wait or check `.rdaa-run/<matter_id>/.rdaa-orchestrator.lock`.

**Phase mismatch:** `advance` failed because next phase isn't what was expected. Print state with `state <state_dir>` and retry with correct phase.

**Gate open:** `advance` blocked because a human gate is pending. Use `clarify` to get approval, then `approve` to register.

**Vault not found:** `register-vault-lookup` failed. Ensure Ementário query succeeded and artifact has `origin: ementario-resolutivo`.

**Worker timeout:** `executar_motor.py` exceeded timeout. Increase `--timeout` or diagnose the worker CLI (Claude, Codex, Agy).
