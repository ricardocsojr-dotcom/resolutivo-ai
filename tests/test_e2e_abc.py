#!/usr/bin/env python3
"""Teste E2E: fluxo C → B com Obsidian, validação de independência de workers."""

import importlib.util
import json
from pathlib import Path
from datetime import datetime, timezone

import pytest

SPEC = importlib.util.spec_from_file_location(
    "orquestrador_rdaa",
    Path(__file__).resolve().parents[1] / "skills" / "redigir-peca" / "scripts" / "orquestrador_rdaa.py",
)
assert SPEC and SPEC.loader
ORCHESTRATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORCHESTRATOR)


class TestE2EIntegracaoObsidian:
    """E2E: C pula Obsidian; B exige vault_context_ready com consulta registrada."""

    def test_nivel_c_sem_vault_requirements(self, tmp_path):
        """Nível C: intake_ready → drafting, sem vault_context_ready."""
        state_dir = tmp_path / "matter-c"
        
        # Inicializar C
        manifest = ORCHESTRATOR.inicializar_execucao(
            state_dir, "matter-c", piece_level="C", risk_level="baixo"
        )
        
        assert manifest["route"]["declared_piece_level"] == "C"
        assert "vault_context_ready" not in manifest["route"]["stages"]
        
        # Avançar
        ORCHESTRATOR.avancar_fase(state_dir, "intake_ready")
        manifest = json.loads((state_dir / "run_manifest.json").read_text(encoding="utf-8"))
        assert manifest["phase"] == "intake_ready"
        
        # Próxima é drafting (sem vault)
        ORCHESTRATOR.avancar_fase(state_dir, "drafting")
        manifest = json.loads((state_dir / "run_manifest.json").read_text(encoding="utf-8"))
        assert manifest["phase"] == "drafting"

    def test_nivel_b_exige_consulta_obsidian_antes_de_vault_context_ready(self, tmp_path):
        """Nível B: vault_context_ready exige consulta do Ementário registrada primeiro."""
        state_dir = tmp_path / "matter-b"
        
        # Inicializar B
        manifest = ORCHESTRATOR.inicializar_execucao(
            state_dir, "matter-b", piece_level="B", risk_level="medio"
        )
        
        assert manifest["route"]["declared_piece_level"] == "B"
        assert "vault_context_ready" in manifest["route"]["stages"]
        assert manifest["route"]["vault"]["lookup"]["enabled"]
        
        # Avançar a intake_ready
        ORCHESTRATOR.avancar_fase(state_dir, "intake_ready")
        manifest = json.loads((state_dir / "run_manifest.json").read_text(encoding="utf-8"))
        assert manifest["phase"] == "intake_ready"
        
        # Tentar ir direto para vault_context_ready deve falhar (sem consulta)
        with pytest.raises(ORCHESTRATOR.WorkflowStateError, match="consulta do Ementário válida"):
            ORCHESTRATOR.avancar_fase(state_dir, "vault_context_ready")
        
        # Registrar consulta do Ementário
        vault_context_file = state_dir / "EMENTARIO-CONTEXTO.json"
        vault_context_file.write_text(json.dumps({
            "origin": "cerebro-ricar",
            "mode": "read_only",
            "status": "informada",
            "domain": "dano-moral",
            "domain_found": True,
            "documents": [
                {"relative_path": "wiki/sources/PREC-001.md", "title": "Precedente 001"},
                {"relative_path": "wiki/sources/PREC-002.md", "title": "Precedente 002"},
            ],
        }))
        
        # Registrar consulta no manifesto
        ORCHESTRATOR.registrar_consulta_vault(
            state_dir,
            vault="cerebro-ricar",
            artifact_path=vault_context_file,
            metadata={"domain": "dano-moral"},
        )
        
        # Agora pode avançar para vault_context_ready
        ORCHESTRATOR.avancar_fase(state_dir, "vault_context_ready")
        manifest = json.loads((state_dir / "run_manifest.json").read_text(encoding="utf-8"))
        assert manifest["phase"] == "vault_context_ready"
        
        # Verificar que consulta foi registrada
        assert len(manifest.get("vault", {}).get("lookups", [])) == 1
        lookup = manifest["vault"]["lookups"][0]
        assert lookup["vault"] == "cerebro-ricar"
        assert lookup["status"] == "informada"
        assert lookup["documents_count"] == 2

    def test_workers_independentes_writer_critic_validator(self, tmp_path):
        """Verificar que writer, critic e validator são independentes (provider/model diferentes)."""
        state_dir = tmp_path / "matter-audit"
        
        manifest = ORCHESTRATOR.inicializar_execucao(
            state_dir, "matter-audit", piece_level="B", risk_level="medio"
        )
        
        route = manifest["route"]
        workers = route["workers"]
        identities = route["worker_identity"]
        
        # Papéis distribuídos
        assert workers["writer"] == "codex"
        assert workers["critic"] == "antigravity"
        assert workers["validator"] == "claude"
        
        # Sem repetição de provider
        writer_id = identities["writer"]
        critic_id = identities["critic"]
        validator_id = identities["validator"]
        
        providers = [writer_id["provider"], critic_id["provider"], validator_id["provider"]]
        families = [writer_id["model_family"], critic_id["model_family"], validator_id["model_family"]]
        
        # Cada dupla tem providers diferentes
        assert writer_id["provider"] != critic_id["provider"]
        assert writer_id["provider"] != validator_id["provider"]
        assert critic_id["provider"] != validator_id["provider"]
        
        # Audit trail: rastreável por provider + cli + role
        assert writer_id["cli"] == "codex"
        assert critic_id["cli"] == "agy"
        assert validator_id["cli"] == "claude"

    def test_painel_exibe_vault_lookup_status_e_independencia(self, tmp_path):
        """Painel deve exibir: vault lookups, worker identity, fases."""
        state_dir = tmp_path / "matter-painel"
        
        manifest = ORCHESTRATOR.inicializar_execucao(
            state_dir, "matter-painel", piece_level="B", risk_level="baixo"
        )
        
        # Simular fluxo B: intake → vault lookup → vault_context_ready
        ORCHESTRATOR.avancar_fase(state_dir, "intake_ready")
        
        vault_file = state_dir / "EMENTARIO-CONTEXTO.json"
        vault_file.write_text(json.dumps({
            "origin": "cerebro-ricar",
            "mode": "read_only",
            "status": "informada",
            "domain": "dano-moral",
            "domain_found": True,
            "documents": [{"title": "Precedente A"}],
        }))
        
        ORCHESTRATOR.registrar_consulta_vault(
            state_dir,
            vault="cerebro-ricar",
            artifact_path=vault_file,
        )
        
        ORCHESTRATOR.avancar_fase(state_dir, "vault_context_ready")
        
        # Gerar painel
        PAINEL = importlib.util.spec_from_file_location(
            "painel_status",
            Path(__file__).resolve().parents[1] / "skills" / "orquestrar-rdaa" / "scripts" / "painel_status.py",
        )
        assert PAINEL and PAINEL.loader
        painel_mod = importlib.util.module_from_spec(PAINEL)
        PAINEL.loader.exec_module(painel_mod)
        
        html_path = state_dir / "PAINEL.html"
        manifest = json.loads((state_dir / "run_manifest.json").read_text(encoding="utf-8"))
        html_path.write_text(painel_mod.render_panel(manifest), encoding="utf-8")
        
        assert html_path.exists()
        
        html_content = html_path.read_text(encoding="utf-8")
        
        # Verificar conteúdo
        assert "vault_context_ready" in html_content  # Fase
        assert "cerebro-ricar" in html_content  # Vault mostrado
        assert "dano-moral" in html_content  # Domínio
        assert "informada" in html_content  # Status read-only


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
