# 🎯 RDAA Orchestrator — Referência Rápida

**Status:** ✅ Pronto para Produção  
**Data:** 2026-09-02  
**Commits:** 12 adicionados (linear history)  
**Testes:** 129 passaram, 3 skipped  

---

## 📚 Documentação

| Arquivo | Propósito |
|---------|-----------|
| **ENTREGA-FINAL.md** | Sumário técnico completo, checklist, próximos passos |
| **HERMES.md** | Contrato: Hermes como gerente, não redator |
| **AGENTS.md** | Papéis de Claude/Codex/Agy/Hermes, segregação |
| **roteamento-ia.md** | Fluxo visual C/B/A com vault_context_ready |
| **skills/orquestrar-rdaa/SKILL.md** | 10-step procedure, CLI, troubleshooting |
| **skills/orchestrate-rdaa-hermes/SKILL.md** | API Python, exemplos, constraints |

---

## 🚀 Como Usar

### Via CLI (Terminal)
```bash
# Inicializar matéria (C/B/A, risco determinado)
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py init .rdaa-run/matter-id \
  --matter-id matter-id --piece-level B --risk-level medio

# Ver status atual (read-only)
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py status .rdaa-run/matter-id

# Avançar fase
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py advance .rdaa-run/matter-id intake_ready

# Consultar Ementário (B/A apenas)
py -3.14 skills/redigir-peca/scripts/integracao_obsidian.py consultar-ementario \
  --domain dano-moral --output .rdaa-run/matter-id/EMENTARIO.json

# Registrar consulta no manifesto
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py register-vault-lookup .rdaa-run/matter-id \
  --vault ementario-resolutivo --artifact .rdaa-run/matter-id/EMENTARIO.json

# Registrar aprovação humana
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py approve .rdaa-run/matter-id \
  --gate skeleton_approval --artifact ./ESQUELETO.md --approved-by Ricardo

# Executar worker isolado
py -3.14 skills/redigir-peca/scripts/executar_motor.py codex \
  --prompt .rdaa-run/matter-id/PROMPT.md --output .rdaa-run/matter-id/DRAFT.md \
  --state-dir .rdaa-run/matter-id --role writer --timeout 600

# Gerar painel (dashboard HTML)
py -3.14 skills/orquestrar-rdaa/scripts/painel_status.py .rdaa-run/matter-id \
  --output .rdaa-run/matter-id/PAINEL.html
```

### Via Python (Hermes Skill)
```python
from skills.orchestrate_rdaa_hermes.scripts.hermes_orchestrator import *

# Inicializar
manifest = initialize_matter(".rdaa-run/matter-id", "matter-id", "B", "medio")

# Avançar
advance_phase(".rdaa-run/matter-id", "intake_ready")

# Consultar Ementário
ementario = query_ementario("dano-moral", output_path=".rdaa-run/matter-id/EMENTARIO.json")

# Registrar consulta
if ementario["exit_code"] == 0:
    register_vault_lookup(".rdaa-run/matter-id", "ementario-resolutivo", 
                         ".rdaa-run/matter-id/EMENTARIO.json")

# Registrar aprovação
register_approval(".rdaa-run/matter-id", "skeleton_approval", "./ESQUELETO.md", "Ricardo")

# Gerar dashboard
dashboard = generate_dashboard(".rdaa-run/matter-id")
```

---

## 📂 Arquivos Principais

| Arquivo | Linhas | Propósito |
|---------|--------|----------|
| `orquestracao/roteamento.json` | 59 | Política C/B/A com vault config |
| `skills/redigir-peca/scripts/orquestrador_rdaa.py` | 527 | Máquina de estados determinística |
| `skills/redigir-peca/scripts/integracao_obsidian.py` | 183 | Consulta Ementário read-only |
| `skills/redigir-peca/scripts/executar_motor.py` | 157 | Executor isolado (Codex/Agy/Claude) |
| `skills/orquestrar-rdaa/scripts/painel_status.py` | 114 | Painel HTML operacional |
| `skills/orchestrate-rdaa-hermes/scripts/hermes_orchestrator.py` | 241 | Wrapper Python para Hermes |

---

## 🧪 Testes

```bash
# Rodar todos (129 testes, 3 skipped)
py -3.14 -m pytest -q

# Rodar suite específica
py -3.14 -m pytest tests/test_e2e_abc.py -v          # E2E (C/B/A)
py -3.14 -m pytest tests/test_orquestrador_rdaa.py -v  # Máquina de estados
py -3.14 -m pytest tests/test_integracao_obsidian.py -v  # Obsidian read-only
py -3.14 -m pytest tests/test_hermes_orchestrator.py -v # Wrapper Python
```

---

## 🔒 Segurança

✅ **Nenhuma credencial preservada**  
✅ **Hash íntegro (SHA256) em todos os artefatos**  
✅ **Redação obrigatória de dados sensíveis**  
✅ **Path traversal bloqueado**  
✅ **Independência de workers verificável** (provider + model + role)  
✅ **Lock por matéria** (mutex .rdaa-orchestrator.lock)  
✅ **Gates humanos exigem confirmação explícita**  
✅ **Nenhuma decisão automática** sobre mérito jurídico  

---

## 🎯 Fluxo por Nível

### **C (Simples)**
```
intake_ready → drafting → draft_ready → validating → candidate_ready 
→ qa_passed → release_ready → published → vault_registered
```
- ❌ Sem Obsidian
- ✅ Sem gates humanos
- ✅ Rápido (overhead mínimo)

### **B (Médio)**
```
intake_ready → vault_context_ready → sources_ready → skeleton_ready 
→ awaiting_skeleton_approval → skeleton_approved → drafting → draft_ready 
→ criticizing → critique_ready → validating → candidate_ready 
→ qa_passed → release_ready → published → vault_registered
```
- ✅ Ementário consulta obrigatória
- ✅ Gate: skeleton_approval
- ✅ Redação + Crítica + Validação

### **A (Complexo)**
```
intake_ready → vault_context_ready → sources_ready → council_ready 
→ skeleton_ready → … → release_approval gate → … → vault_registered
```
- ✅ Ementário + Jusbrasil + Conselho
- ✅ Gates: skeleton_approval, release_approval (strategy_exception condicional)
- ✅ Máximo rigor + auditoriae

---

## 🛠️ Troubleshooting

| Problema | Solução |
|----------|---------|
| **Lock error** | Outro processo está escrevendo. Verifique `.rdaa-orchestrator.lock` |
| **Phase mismatch** | Use `status` para ver fase atual antes de `advance` |
| **Gate open** | Use `clarify()` para obter aprovação, depois `approve` para registrar |
| **Vault not found** | Verifique WSL mount ou usar fallback path |
| **Worker timeout** | Aumente `--timeout` ou diagnose CLI (Claude/Codex/Agy) |
| **Budget exceeded** | Redija prompt menor ou aumente `--max-budget-usd` |

---

## 📊 Commits Adicionados

```
9877587 refactor: atualizar referencias cruzadas às skills relacionadas
da53303 test: atualizar testes de executor motor e QA
47bfda9 docs(skill): redigir-peca — workflow atualizado com vault_context_ready
1d1fd58 docs: contrato Hermes, arquitetura RDAA, entrega final
f7c6554 test: testes E2E e de integração para orquestrador + Obsidian + wrapper
ea8838a feat(skill): orchestrate-rdaa-hermes — wrapper Python para Hermes
e04ada0 feat(skill): orquestrar-rdaa com procedimentos E2E e painel
2267bb6 feat(painel): dashboard HTML estático com vault lookups
9edbf2c feat(executar-motor): executor isolado com sandbox, timeout, orçamento
435875e feat(integracao-obsidian): consulta read-only do Ementário com redação segura
496cfa8 feat(orquestrador): máquina de estados determinística com suporte a vault
2a2c54c feat(orquestracao): adiciona politica de roteamento C/B/A com vault_context_ready
```

---

## 🔜 Próximos Passos (Opcionais)

- [ ] Auto-resumption: cron job que retoma matérias bloqueadas
- [ ] Monitoramento: alertas sobre atrasos
- [ ] Versioning manifesto: git-backed para histórico
- [ ] Ementário escrita: integrar `claude-obsidian` pós-publicação
- [ ] Métricas: dashboard de duração/custo
- [ ] Multi-worker paralelo: draft-A, draft-B em paralelo

---

**Pronto para produção. 🎯**
