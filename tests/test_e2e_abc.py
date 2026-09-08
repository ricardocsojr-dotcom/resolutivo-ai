"""Teste E2E de integração do ecossistema RDAA (A, B, C) com Cérebro-Ricar."""

import importlib.util
import json
from pathlib import Path
import pytest

# Carregar módulos dinamicamente
SPEC = importlib.util.spec_from_file_location(
    "orquestrador_rdaa",
    Path(__file__).resolve().parents[1] / "skills" / "redigir-peca" / "scripts" / "orquestrador_rdaa.py",
)
assert SPEC and SPEC.loader
ORCHESTRATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORCHESTRATOR)

SPEC_OBSIDIAN = importlib.util.spec_from_file_location(
    "integracao_obsidian",
    Path(__file__).resolve().parents[1] / "skills" / "redigir-peca" / "scripts" / "integracao_obsidian.py",
)
assert SPEC_OBSIDIAN and SPEC_OBSIDIAN.loader
OBSIDIAN = importlib.util.module_from_spec(SPEC_OBSIDIAN)
SPEC_OBSIDIAN.loader.exec_module(OBSIDIAN)


class TestE2EIntegracaoObsidian:
    """Valida o fluxo ponta a ponta com Ementário do Cérebro-Ricar."""

    def test_fluxo_c_nao_consulta_vault(self, tmp_path):
        """Peça nível C não deve ter etapa de vault lookup."""
        state_dir = tmp_path / "matter-c"
        
        manifest = ORCHESTRATOR.inicializar_execucao(
            state_dir, "matter-c", piece_level="C"
        )
        
        # Verificar que C não tem lookup no vault
        assert manifest["route"]["vault"]["lookup"]["enabled"] is False
        assert "vault_context_ready" not in manifest["route"]["stages"]
        
        # Avança direto: initialized → intake_ready → drafting → draft_ready → candidate_ready
        ORCHESTRATOR.avancar_fase(state_dir, "intake_ready")
        ORCHESTRATOR.avancar_fase(state_dir, "drafting")
        ORCHESTRATOR.avancar_fase(state_dir, "draft_ready")
        ORCHESTRATOR.avancar_fase(state_dir, "candidate_ready")
        
        manifest = json.loads((state_dir / "run_manifest.json").read_text(encoding="utf-8"))
        assert manifest["phase"] == "candidate_ready"

    def test_fluxo_b_exige_vault_context_antes_de_sources(self, tmp_path):
        """Peça nível B exige registrar consulta do Ementário antes de avançar para vault_context_ready."""
        state_dir = tmp_path / "matter-b"
        
        manifest = ORCHESTRATOR.inicializar_execucao(
            state_dir, "matter-b", piece_level="B"
        )
        
        assert manifest["route"]["vault"]["lookup"]["enabled"] is True
        assert "vault_context_ready" in manifest["route"]["stages"]
        
        ORCHESTRATOR.avancar_fase(state_dir, "intake_ready")
        
        # Tentar avançar para vault_context_ready SEM registrar consulta deve falhar
        with pytest.raises(ValueError, match="consulta do Ementário válida exigida"):
            ORCHESTRATOR.avancar_fase(state_dir, "vault_context_ready")
            
        # Simular artefato de consulta
        vault_context_file = state_dir / "EMENTARIO-CONTEXTO.json"
        vault_context_file.write_text(json.dumps({
            "origin": "cerebro-ricar",
            "mode": "read_only",
            "status": "informada",
            "domain": "dano-moral",
            "domain_found": True,
            "documents": [{"title": "Precedente 1"}, {"title": "Precedente 2"}],
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
        """Verificar que no nível A writer, critic e validator são independentes."""
        state_dir = tmp_path / "matter-audit"
        
        manifest = ORCHESTRATOR.inicializar_execucao(
            state_dir, "matter-audit", piece_level="A"
        )
        
        route = manifest["route"]
        workers = route["workers"]
        identities = route["worker_identity"]
        
        # Papéis distribuídos no nível A
        assert workers["planner"] == "claude"
        assert workers["writer"] == "codex"
        assert workers["critic"] == "antigravity"
        assert workers["validator"] == "chat"
        
        writer_id = identities["writer"]
        critic_id = identities["critic"]
        
        assert writer_id["provider"] != critic_id["provider"]
        assert writer_id["cli"] == "codex"
        assert critic_id["cli"] == "agy"

    def test_painel_exibe_vault_lookup_status_e_independencia(self, tmp_path):
        """Painel deve exibir: vault lookups, worker identity, fases."""
        state_dir = tmp_path / "matter-painel"
        
        manifest = ORCHESTRATOR.inicializar_execucao(
            state_dir, "matter-painel", piece_level="B"
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
        assert "vault_context_ready" in html_content
        assert "cerebro-ricar" in html_content
        assert "dano-moral" in html_content
        assert "informada" in html_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
