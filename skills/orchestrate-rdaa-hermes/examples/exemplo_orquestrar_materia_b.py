#!/usr/bin/env python3
"""Example Hermes skill: Use orchestrate-rdaa-hermes to manage a full B-level matter."""

from pathlib import Path
from hermes_tools import terminal, clarify

# Import the orchestrator wrapper
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "orchestrate-rdaa-hermes" / "scripts"))
from hermes_orchestrator import (
    initialize_matter, get_state, advance_phase, register_approval,
    query_ementario, register_vault_lookup, generate_dashboard,
)


def orchestrate_b_matter(matter_id: str, domain: str, risk: str = "medio"):
    """
    Example: Orchestrate a B-level matter end-to-end.
    
    This demonstrates calling the orchestrator from a Hermes skill without
    letting Hermes make juridical decisions.
    """
    state_dir = Path(f".rdaa-run/{matter_id}")
    state_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔄 Orchestrating matter {matter_id} (B/{risk})...")
    
    # 1. Initialize
    print("\n1️⃣  Initializing manifest...")
    manifest = initialize_matter(state_dir, matter_id, "B", risk)
    print(f"   ✓ Phase: {manifest['phase']}")
    print(f"   ✓ Route: B (Codex → Agy → Claude)")
    
    # 2. Advance to intake_ready (no human gate needed)
    print("\n2️⃣  Advancing to intake_ready...")
    advance_phase(state_dir, "intake_ready")
    print(f"   ✓ Ready for Ementário consultation")
    
    # 3. Query Ementário (automatic, but show what we're doing)
    print(f"\n3️⃣  Consulting Ementário (domain: {domain})...")
    ementario_file = state_dir / "EMENTARIO-CONTEXTO.json"
    vault_result = query_ementario(domain, output_path=ementario_file)
    
    if vault_result["exit_code"] == 0:
        payload = vault_result["payload"]
        print(f"   ✓ Found {payload['documents_count']} documents")
        print(f"   ✓ Mode: read-only ({payload['mode']})")
        print(f"   ✓ Status: {payload['status']}")
        
        # Register lookup
        print(f"\n4️⃣  Registering vault lookup...")
        register_vault_lookup(state_dir, "ementario-resolutivo", ementario_file)
        print(f"   ✓ Lookup registered with hash")
    else:
        print(f"   ⚠️  Vault query failed: {vault_result['stderr'][:200]}")
        print(f"   ⚠️  Skipping vault-dependent phases")
        return
    
    # 5. Advance to vault_context_ready
    print(f"\n5️⃣  Advancing to vault_context_ready...")
    advance_phase(state_dir, "vault_context_ready")
    print(f"   ✓ Vault context loaded")
    
    # 6. Advance to sources_ready (no worker needed for skeleton phase)
    print(f"\n6️⃣  Advancing to sources_ready...")
    advance_phase(state_dir, "sources_ready")
    print(f"   ✓ Sources ready for skeleton planning")
    
    # 7. Advance to skeleton_ready (planner/Claude should have done this)
    print(f"\n7️⃣  Advancing to skeleton_ready...")
    advance_phase(state_dir, "skeleton_ready")
    print(f"   ✓ Skeleton phase complete")
    
    # 8. Open gate for human approval
    print(f"\n8️⃣  Awaiting skeleton approval...")
    advance_phase(state_dir, "awaiting_skeleton_approval")
    
    # Get human decision (EXAMPLE: simulating approval)
    decision = clarify(questions=[{
        "question": f"Approve skeleton for {matter_id}?",
        "choices": ["Approve", "Reject", "Revise"]
    }])
    
    if decision["responses"][0] == "Approve":
        # Create a minimal artifact for approval record
        skeleton_file = state_dir / "SKELETON-APPROVED.md"
        skeleton_file.write_text("# Approved Skeleton\n\n(placeholder for human-approved structure)")
        
        # Register approval
        print(f"\n9️⃣  Registering approval...")
        register_approval(state_dir, "skeleton_approval", skeleton_file, "Ricardo")
        print(f"   ✓ Approval recorded")
        
        # Advance to skeleton_approved
        print(f"\n🔟 Advancing to skeleton_approved...")
        advance_phase(state_dir, "skeleton_approved")
        print(f"   ✓ Skeleton approved, ready for drafting")
    else:
        print(f"\n❌ Skeleton rejected. Matter halted.")
        return
    
    # 11. Generate dashboard for visual inspection
    print(f"\n📊 Generating dashboard...")
    dashboard_path = generate_dashboard(state_dir)
    print(f"   ✓ Dashboard: {dashboard_path}")
    print(f"   ✓ Open in Hermes preview to monitor progress")
    
    # Summary
    state = get_state(state_dir)
    print(f"\n✅ Orchestration progress:")
    print(f"   Matter: {matter_id}")
    print(f"   Phase: {state['phase']}")
    print(f"   Next: Codex will draft → Agy will critique → Claude will validate")
    print(f"   Workers: {state['route']['workers']}")


if __name__ == "__main__":
    # Example invocation
    orchestrate_b_matter(
        matter_id="contrato-2026-0042",
        domain="contratos-bancarios",
        risk="medio"
    )
