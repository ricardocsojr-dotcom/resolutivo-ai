# Instruções: Adaptar Hermes para Modelos Otimizados

**Data:** 2026-09-02  
**Objetivo:** Implementar configuração equilibrada (Sonnet + Terra + Gemini 3.1 Pro + Haiku)

---

## Passo 1: Atualizar `~/.hermes/config.yaml`

Abra `C:\Users\ricar\AppData\Local\hermes\config.yaml` e mude:

### ❌ ANTES:
```yaml
model:
  default: gpt-5.6-luna
  provider: openai-codex
  base_url: https://chatgpt.com/backend-api/codex
fallback_providers:
  - provider: opencode-free
    model: nemotron-3-ultra-free
  - provider: opencode-free
    model: deepseek-v4-flash-free
```

### ✅ DEPOIS:
```yaml
model:
  default: gpt-5.5
  provider: openai-codex
  base_url: https://chatgpt.com/backend-api/codex
fallback_providers:
  - provider: openai-codex
    model: gpt-5.5
  - provider: openai-codex
    model: gpt-5.6-luna
  - provider: opencode-free
    model: nemotron-3-ultra-free
  - provider: opencode-free
    model: deepseek-v4-flash-free
```

**Mudanças:**
- `default: gpt-5.6-luna` → `default: gpt-5.5` (Luna = fallback, não default)
- Adicionado `gpt-5.5` como fallback primário (mesmo provider, modelo alternativo)

**Salvar e fechar.**

---

## Passo 2: Verificar Roteamento (Já Feito! ✅)

O arquivo `orquestracao/roteamento.json` já foi atualizado com:

```json
{
  "workers": {
    "planner": {"engine": "claude", "provider": "anthropic", "model": "claude-sonnet-5", ...},
    "writer": {"engine": "codex", "provider": "openai", "model": "gpt-5.5", ...},
    "critic": {"engine": "antigravity", "provider": "google", "model": "gemini-3.1-pro-high", ...},
    "validator": {"engine": "claude", "provider": "anthropic", "model": "claude-haiku-4.5", ...}
  }
}
```

✅ Verificar com:
```bash
cat orquestracao/roteamento.json | jq '.workers'
```

---

## Passo 3: Verificar Configuração de CLI (Manual)

Cada CLI precisa ter seu modelo configurado. Dependendo de como você invoca:

### Se usar via script Python:
Confirmar que `scripts/orquestrador_rdaa.py` lê `roteamento.json` corretamente.

```bash
cd C:/Projetos/resolutivo-ai
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py route --piece-level B --risk-level baixo
```

Saída esperada:
```
Rota efetiva: B
Planner: claude-sonnet-5 (anthropic)
Writer: gpt-5.5 (openai)
Critic: gemini-3.1-pro-high (google)
Validator: claude-haiku-4.5 (anthropic)
```

### Se usar via CLI direto:
Confirmar que cada CLI tem seu modelo configurado:

```bash
# Planner
claude --model claude-sonnet-5 --task plan --input context.json

# Writer
codex --model gpt-5.5 --task write --input context.json

# Critic
agy --model gemini-3.1-pro-high --task critique --input peca.json

# Validator
claude --model claude-haiku-4.5 --task validate --input peca.json
```

---

## Passo 4: Testar Fluxo Completo (Nível B)

```bash
cd C:/Projetos/resolutivo-ai

# 1. Inicializar nova matéria
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py init \
  .rdaa-run/TEST-2026-09-02 \
  --matter-id test-2026-09-02 \
  --piece-level B \
  --risk-level baixo

# 2. Verificar rota
cat .rdaa-run/TEST-2026-09-02/run_manifest.json | jq '.route'

# 3. Executar workflow
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py route \
  .rdaa-run/TEST-2026-09-02

# 4. Consultar vault (Obsidian)
py -3.14 skills/redigir-peca/scripts/integracao_obsidian.py consultar-ementario \
  --domain "direito-civil" \
  --output .rdaa-run/TEST-2026-09-02/EMENTARIO-CONTEXTO.json

# 5. Avançar para drafting (planner + approval)
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py advance \
  .rdaa-run/TEST-2026-09-02 \
  vault_context_ready

# 6. Invocar writer (Codex com gpt-5.5)
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py invoke-worker \
  .rdaa-run/TEST-2026-09-02 \
  writer

# 7. Invocar critic (Agy com gemini-3.1-pro-high)
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py invoke-worker \
  .rdaa-run/TEST-2026-09-02 \
  critic

# 8. Invocar validator (Claude Haiku)
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py invoke-worker \
  .rdaa-run/TEST-2026-09-02 \
  validator

# 9. Publicar
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py publish \
  .rdaa-run/TEST-2026-09-02
```

**Esperado:**
- ✅ run_manifest.json registra cada worker com seu modelo
- ✅ Nenhuma falha por modelo não disponível
- ✅ Arquivo DOCX publicado com sucesso

---

## Passo 5: Verificar Proveniência

Após publicação, confirmar independência:

```bash
cat .rdaa-run/TEST-2026-09-02/run_manifest.json | jq '.execution_log[] | {worker, model, provider}'
```

Esperado:
```json
{"worker": "planner", "model": "claude-sonnet-5", "provider": "anthropic"}
{"worker": "writer", "model": "gpt-5.5", "provider": "openai"}
{"worker": "critic", "model": "gemini-3.1-pro-high", "provider": "google"}
{"worker": "validator", "model": "claude-haiku-4.5", "provider": "anthropic"}
```

✅ **3 providers diferentes** → Independência garantida

---

## Passo 6: Monitorar Custo & Performance

Após 3–5 matérias B/A executadas:

```bash
# Agregador de custos (se implementado)
py -3.14 skills/redigir-peca/scripts/monitor_custos.py \
  --from 2026-09-02 \
  --to 2026-09-10 \
  --format csv > custo-modelos-09-02.csv
```

Esperado: Custo 🟨 médio, performance ★★★ estável.

---

## Fallback & Degradação

Se um modelo não estiver disponível:

### Writer (gpt-5.5) indisponível:
```yaml
# config.yaml já tem fallback:
- provider: openai-codex
  model: gpt-5.6-luna      # Fallback 1 (mesma familia, modelo inferior)
- provider: opencode-free
  model: nemotron-3-ultra  # Fallback 2 (gratuito)
```

Sistema tenta sequencialmente:
1. gpt-5.5 (principal)
2. gpt-5.5 (fallback 1, caso provider caia)
3. gpt-5.6-luna (fallback 2, custo)
4. nemotron (fallback 3, gratuito)

**Aviso:** Cada fallback é registrado em run_manifest.json para auditoria.

---

## Checklist de Implementação

- [ ] Editar `~/.hermes/config.yaml` (Passo 1)
- [ ] Verificar `orquestracao/roteamento.json` (Passo 2) — ✅ JÁ FEITO
- [ ] Testar fluxo completo com matéria B (Passo 4)
- [ ] Verificar proveniência (Passo 5)
- [ ] Monitorar performance (Passo 6)
- [ ] Documentar resultados

---

## Timeline

- **2026-09-02:** Config.yaml + roteamento.json atualizados ✅
- **2026-09-02 a 2026-09-10:** Teste com 3–5 matérias (você)
- **2026-09-15:** Aprovação / ajustes finais
- **2026-09-20:** Produção completa (Nível C/B/A)

---

## Suporte

Se houver erro:

1. **"Model not found: gpt-5.5"** → Verificar acesso OpenAI; confirmar chave
2. **"gemini-3.1-pro-high indisponível"** → Usar fallback Gemini 3.6 Flash ou Claude Sonnet Thinking
3. **"run_manifest.json não atualiza"** → Verificar permissões em `.rdaa-run/`

---

**Documento de referência:** `RECOMENDACAO-MODELOS-OTIMIZADO.md`  
**Configuração atual:** `MODELOS-CLÍS-RDAA.md`
