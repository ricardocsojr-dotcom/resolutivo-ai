#!/usr/bin/env python3
"""Tests for hermes_orchestrator.py integration."""

import importlib.util
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

SPEC = importlib.util.spec_from_file_location(
    "hermes_orchestrator",
    Path(__file__).resolve().parents[1] / "skills" / "orchestrate-rdaa-hermes" / "scripts" / "hermes_orchestrator.py",
)
assert SPEC and SPEC.loader
ORCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORCH)


class TestHermesOrchestratorIntegration:
    """Test Python callable interface to orquestrador_rdaa."""

    def test_get_route_returns_valid_routing_decision(self):
        """get_route() returns proper route for piece level + risk."""
        route_c = ORCH.get_route("C", "baixo")
        assert route_c["declared_piece_level"] == "C"
        assert "vault" in route_c
        assert not route_c["vault"]["lookup"]["enabled"]
        
        route_b = ORCH.get_route("B", "medio")
        assert route_b["declared_piece_level"] == "B"
        assert route_b["vault"]["lookup"]["enabled"]
        assert route_b["vault"]["lookup"]["vault"] == "cerebro-ricar"

    def test_initialize_matter_creates_idempotent_manifest(self):
        """initialize_matter() creates run_manifest.json with route."""
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "matter-init-test"
            
            manifest = ORCH.initialize_matter(
                state_dir, "init-test", "B", "baixo"
            )
            
            assert manifest["phase"] == "initialized"
            assert manifest["matter_id"] == "init-test"
            assert manifest["route"]["declared_piece_level"] == "B"
            
            # Manifest file should exist
            assert (state_dir / "run_manifest.json").exists()
            
            # Idempotent: calling again should return same manifest
            manifest2 = ORCH.initialize_matter(
                state_dir, "init-test", "B", "baixo"
            )
            assert manifest["phase"] == manifest2["phase"]

    def test_get_state_reads_without_modifying(self):
        """get_state() reads manifest without side effects."""
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "matter-state-test"
            
            ORCH.initialize_matter(state_dir, "state-test", "B", "baixo")
            
            state1 = ORCH.get_state(state_dir)
            assert state1["phase"] == "initialized"
            
            # Call again: should be identical
            state2 = ORCH.get_state(state_dir)
            assert state1 == state2

    def test_advance_phase_transitions_correctly(self):
        """advance_phase() moves through phases in order."""
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "matter-advance-test"
            
            ORCH.initialize_matter(state_dir, "advance-test", "C", "baixo")
            
            # C should go intake_ready → drafting (no vault)
            m1 = ORCH.advance_phase(state_dir, "intake_ready")
            assert m1["phase"] == "intake_ready"
            
            m2 = ORCH.advance_phase(state_dir, "drafting")
            assert m2["phase"] == "drafting"

    def test_query_ementario_returns_read_only_payload(self):
        """query_ementario() generates a read-only Ementário package (if vault accessible)."""
        # Skip if vault not accessible
        vault_path = Path("\\wsl.localhost\\Ubuntu\\home\\ricar\\vaults\\cerebro-ricar\\CLAUDE.md")
        if not vault_path.exists():
            pytest.skip("Ementário vault not accessible (expected on Windows without WSL mount)")
        
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "EMENTARIO.json"
            
            result = ORCH.query_ementario(
                "dano-moral",
                vault_root="\\wsl.localhost\\Ubuntu\\home\\ricar\\vaults\\cerebro-ricar",
                output_path=output,
            )
            
            assert result["exit_code"] == 0
            assert output.exists()
            
            payload = result["payload"]
            assert payload["origin"] == "cerebro-ricar"
            assert payload["mode"] == "read_only"
            assert payload["status"] == "informada"
            assert payload["domain"] == "dano-moral"
            assert "documents" in payload

    def test_register_vault_lookup_records_consulta_in_manifest(self):
        """register_vault_lookup() links Ementário query to manifest (if vault accessible)."""
        vault_path = Path("\\wsl.localhost\\Ubuntu\\home\\ricar\\vaults\\cerebro-ricar\\CLAUDE.md")
        if not vault_path.exists():
            pytest.skip("Ementário vault not accessible")
        
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "matter-vault-test"
            
            ORCH.initialize_matter(state_dir, "vault-test", "B", "baixo")
            ORCH.advance_phase(state_dir, "intake_ready")
            
            # Query vault
            ementario_file = state_dir / "EMENTARIO.json"
            query_result = ORCH.query_ementario(
                "dano-moral",
                vault_root="\\wsl.localhost\\Ubuntu\\home\\ricar\\vaults\\cerebro-ricar",
                output_path=ementario_file,
            )
            
            # Register lookup
            record = ORCH.register_vault_lookup(
                state_dir,
                vault="cerebro-ricar",
                artifact_path=ementario_file,
            )
            
            assert record["vault"] == "cerebro-ricar"
            assert record["status"] == "informada"
            assert record["mode"] == "read_only"
            assert record["domain"] == "dano-moral"
            
            # Verify it's in manifest
            state = ORCH.get_state(state_dir)
            assert len(state.get("vault", {}).get("lookups", [])) == 1

    def test_generate_dashboard_creates_html(self):
        """generate_dashboard() renders HTML with phase + vault status (if vault accessible)."""
        vault_path = Path("\\wsl.localhost\\Ubuntu\\home\\ricar\\vaults\\cerebro-ricar\\CLAUDE.md")
        if not vault_path.exists():
            pytest.skip("Ementário vault not accessible")
        
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "matter-painel-test"
            
            ORCH.initialize_matter(state_dir, "painel-test", "B", "baixo")
            ORCH.advance_phase(state_dir, "intake_ready")
            
            # Query vault
            ementario_file = state_dir / "EMENTARIO.json"
            ORCH.query_ementario(
                "dano-moral",
                vault_root="\\wsl.localhost\\Ubuntu\\home\\ricar\\vaults\\cerebro-ricar",
                output_path=ementario_file,
            )
            ORCH.register_vault_lookup(
                state_dir,
                vault="cerebro-ricar",
                artifact_path=ementario_file,
            )
            
            # Generate dashboard
            html_path = ORCH.generate_dashboard(state_dir)
            
            assert html_path.exists()
            html_content = html_path.read_text(encoding="utf-8")
            
            # Verify key content is present
            assert "painel-test" in html_content  # Matter ID
            assert "intake_ready" in html_content  # Phase
            assert "cerebro-ricar" in html_content  # Vault
            assert "dano-moral" in html_content  # Domain

    def test_execute_worker_allows_cli_timeout_plus_grace_period(self, tmp_path):
        """O wrapper não pode matar o executor antes do timeout do worker."""
        with patch.object(ORCH, "_run_cmd", return_value={"exit_code": 0, "stdout": "", "stderr": ""}) as run_cmd:
            ORCH.execute_worker(
                "codex",
                tmp_path / "PROMPT.md",
                tmp_path / "RASCUNHO.md",
                tmp_path / "matter",
                "writer",
                timeout_seconds=600,
            )

        assert run_cmd.call_args.kwargs["timeout_seconds"] == 630

    def test_wrapper_handles_errors_gracefully(self):
        """OrchestratorError raised on invalid operations."""
        with tempfile.TemporaryDirectory() as tmp:
            nonexistent = Path(tmp) / "nonexistent"
            
            # Reading nonexistent state should raise
            with pytest.raises(ORCH.OrchestratorError, match="execução não inicializada"):
                ORCH.get_state(nonexistent)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
