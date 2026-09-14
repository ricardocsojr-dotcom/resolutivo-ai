# Plano de Extrema Produtividade para Peça Tipo B 

## Objetivo
Reduzir o tempo de execução e iteração do nível B para **50% do nível A**, garantindo qualidade técnica com menor profundidade exploratória e mais resiliência contra loops mecânicos (QA).

## Status de Implementação (2026-09-14)

| Eixo | Componente | Status | Commit |
|------|-----------|--------|--------|
| Auto-fix QA | `production_worker.py`: correção automática de erros mecânicos (formatação, estilo) antes do gate | ✅ **Implementado** | `882c254` |
| Orçamento B | `roteamento.json`: Planner B instruído com `budget: "fast"` (vs A: `"exhaustive"`) | ✅ **Configurado** | `0923252` |
| Bloqueio de duplicatas | Engine: rejeita novo state_dir com writer-input.md idêntico já reprovado | ✅ **Implementado** | `66e9e5b` |
| Extração determinística | `intake_ready`: PyMuPDF + Tesseract (produz packages/intake.md), elimina vision_analyze fatiado | ✅ **Implementado** | `2ed61fe` |
| Nível C engine | `roteamento.json`: C.writer.engine volta a `"chat"` (motor usa writer-input.md diretamente) | ✅ **Corrigido** | `2dfe5b0` |

## Eixos Estruturais

### 1. Orçamento Diferenciado e Foco (Planner)
- **Como é no A:** `budget: "exhaustive"` — Busca exaustiva, compilação de múltiplos precedentes, `critic` avaliza o draft.
- **Como é no B (AGORA):** `budget: "fast"` — Busca **direta e limitada** (max 2 precedentes fundamentais, sem devaneio doutrinário). Configurado em `orquestracao/roteamento.json`.
- **Estrutura da Rota:**
  - A: `[planner → writer → critic → validator → qa_passed]` (4 workers)
  - B: `[planner → writer → validator → qa_passed]` (3 workers, sem critic)
  - C: `[writer (chat) → qa_passed]` (1 worker)

### 2. Paralelização e Extração Inteligente (✅ PRONTO)
- **Extração OCR determinística:** `handle_intake_ready()` em `system_handlers.py` chama `services/extracao.py` uma única vez por matéria:
  - Entrada: `<state_dir>/anexos/*.pdf` (qualquer combinação)
  - Saída: `<state_dir>/packages/intake.md` (normalizado, texto nativo + OCR onde necessário)
  - Ganho: 8+ minutos de `vision_analyze` fatiado eliminados para PDFs longos (confirmado em sessão hoje)
- **Contexto do cofre leve:** `vault_context_ready` no B apenas traz metadados/citações essenciais; sem full-text pesado de jurisprudência que A usa.

### 3. Cache de Fases (Reaproveitamento)
- O comando `cli resume` **já persiste** todos os `outputs` no checkpoint SQLite da matéria.
- Se QA reprovar apenas em formatação (ex: alínea mal numerada), o próximo `resume` pode saltar diretamente a `validating` (não re-rodar `writer`), consumindo o output anterior.
- **Documentação:** Abrir em skill `redigir-peca` como seção "Retomada Rápida" — condições em que resume pula fases.

### 4. Revisão Automática Anti-Gargalo (Auto-Fix de QA) ✅ **IMPLEMENTADO**
- **Antes (problema):** Falha de QA em formatação (ex: alínea fora de padrão) reprovava → disjuntor → fila travada aguardando humano.
- **Agora (solução):** `production_worker.production_worker()`, linha 206+:
  1. Compila o candidato DOCX
  2. Roda `qa_gate` silenciosamente
  3. **Se falhar:** Monta um `Packet` especial ("_qa_fix") com os detalhes exatos do erro
  4. Envia **1 única vez** ao modelo para autocorreção
  5. Recompila e marca `result["qa_auto_fixed"] = True`
  6. **Se auto-fix também falhar:** devolve o original (não entra em loop)
- **Resultado:** Erros mecânicos corrigidos invisibilmente, sem tocar no disjuntor ou fila
- Métrica esperada: **30-40% redução** de tentativas em nível B causadas por formatação

## Ganhos de Tempo Esperados

| Operação | Antes | Depois | Redução |
|----------|-------|--------|---------|
| Extração de PDF (1-3 anexos, ~50 pág total) | 8-12 min (vision_analyze fatiado) | ~30 seg (PyMuPDF + Tesseract local) | **94%** |
| Planejamento (nível B) | ~12 min (exhaustive search) | ~6 min (fast, 2 precedentes) | **50%** |
| Revisão (B vs A) | +5 min (critic phase) | 0 min (crítica offline ou pulada) | **5 min** |
| QA loop (erros mecânicos) | +8 min (retry full) | 0 min (auto-fix in-worker) | **~40% das retentativas** |
| **Total Nível B** | ~38 min | ~19 min | **50%** |

## Próximos Passos

1. **Skill `redigir-peca`:** Adicionar seção "Retomada Rápida" documentando quando `cli resume` pula fases (exemplo: if QA falhou na formatação, resume pula writer).
2. **Métrica de Cache:** Adicionar field `outputs_reused_from` no `run_manifest.json` para rastrear qual fase foi saltada, para auditar economia real.
3. **Teste E2E de B:** Criar `test_e2e_peca_b.py` simulando fluxo B completo (planner fast → writer → validator → qa → auto-fix success scenario).
4. **Gate de Velocidade:** Configurar alerta se uma peça B ultrapassar 25 min (metade de A), investigar se orçamento de pesquisa foi respeitado.

