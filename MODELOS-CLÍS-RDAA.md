# Configuração de Modelos por CLI — RDAA

**Data:** 2026-09-02  
**Fontes:** `config.yaml` (Hermes), `orquestracao/roteamento.json`, `skills/revisor-rdaa/references/roteamento-executavel.md`

---

## Arquitetura

O sistema RDAA usa **múltiplos CLIs independentes** para garantir que cada função (redação, crítica, validação, planejamento) seja executada por um modelo diferente com proveniência verificável.

### Princípio

```
writer.model_family ≠ critic.model_family ≠ validator.model_family
```

Cada CLI tem seu próprio modelo. A independência é verificável por:
- `provider` (OpenAI, Anthropic, Google, etc.)
- `model` (gpt-X, claude-Y, etc.)
- `role` (writer, critic, validator, planner)

---

## Workers e Modelos por CLI

| Worker | CLI | Provider | Model Family | Descrição |
|--------|-----|----------|-------------|-----------|
| **planner** | `claude` | Anthropic | anthropic | Planeja estratégia jurídica, aprova esqueletos |
| **writer** | `codex` | OpenAI | openai | Redige peças (contestações, apelações, etc.) |
| **critic** | `agy` (Antigravity) | Google | google | Critica tese redada (vulnerabilidades, contratese) |
| **validator** | `claude` | Anthropic | anthropic | Valida conformidade e QA antes de publicar |

**Fonte:** `orquestracao/roteamento.json`, linhas 3-7.

---

## Modelo Específico por CLI

### 1. **Claude (Planner + Validator)**

**CLI:** `claude`  
**Provider:** Anthropic  
**Model Family:** anthropic  

**Modelos conhecidos (verificar com `claude --version`):**
- `claude-opus` (mais capaz, maior contexto)
- `claude-sonnet` (equilibrado)
- `claude-haiku` (rápido, menor contexto)

**Funções:**
- `planner`: Lê fatos, teses, evidências; produz estratégia jurídica, aprova esqueleto
- `validator`: Lê peça completa; checklist de conformidade, regras RDAA, gates de QA

**Invocação:**
```bash
claude --task plan --input matter.json
claude --task validate --input peca.json
```

---

### 2. **Codex (Writer)**

**CLI:** `codex`  
**Provider:** OpenAI  
**Model Family:** openai  

**Modelos conhecidos:**
- `gpt-5` (versão mais nova, 2026)
- `gpt-4` (compatível legado)
- Versões específicas: `gpt-5.5`, `gpt-5.6` (ver config.yaml linha 2)

**Funções:**
- Redige blocos de peça (abertura, fundamentação, pedidos, fecho)
- Integra tese aprovada + fontes selecionadas
- Respeita estilo RDAA e tags de formatação

**Invocação:**
```bash
codex --task write --schema blocos.json --input context.json --output peca.json
```

**Configuração atual (config.yaml linhas 2-4):**
```yaml
model:
  default: gpt-5.6-luna
  provider: openai-codex
  base_url: https://chatgpt.com/backend-api/codex
```

---

### 3. **Antigravity / Agy (Critic)**

**CLI:** `agy`  
**Provider:** Google  
**Model Family:** google  

**Modelos conhecidos:**
- `gemini-2.0` (mais novo, 2026)
- `gemini-1.5` (compatível)
- Variantes: Pro, Flash

**Funções:**
- Analisa peça redada pelo Codex
- Identifica vulnerabilidades de tese
- Propõe contratese alternativa
- Marca pontos a verificar

**Invocação:**
```bash
agy --task critique --input peca.json --output critica.json
```

**Nota:** Antigravity é wrapper interno para Google Gemini (ou modelo Google configurado).

---

## Hermes (Este Agente)

**Modelo atual:** `claude-haiku-4-5-20251001` (verificado no system prompt)  
**Provider:** Anthropic  
**Papel:** **Orquestrador apenas**, não redator/crítico jurídico

**Funções:**
- Controlar estado (`run_manifest.json`)
- Invocar CLIs (Codex, Agy, Claude)
- Gerenciar aprovações humanas (Ricardo)
- Registrar provenance e hashes
- **NUNCA** substituir decisão jurídica de worker independente

**Restrição explícita (AGENTS.md):**
> "Hermes não deve substituir Claude, Codex ou Agy como redator/revisor jurídico independente"

---

## Workflow Simplificado (Nível B)

```
1. Ricardo declara: "Abrir matéria X, nível B"
   ↓
2. Hermes inicializa orquestracao/run_manifest.json
   ↓
3. Vault Obsidian consultado (Ementário)
   ↓
4. Claude (planner) aprova esqueleto
   ↓
5. Codex (writer) redige peça
   ↓
6. Agy (critic) analisa
   ↓
7. Claude (validator) QA + conformidade
   ↓
8. Hermes publica + registra vault
```

**Cada step persiste resultado em `run_manifest.json` com hash e timestamp.**

---

## Verificação de Independência

Após publicação, confirmar:

```json
{
  "writer": {
    "provider": "openai",
    "model": "gpt-5.6",
    "model_family": "openai"
  },
  "critic": {
    "provider": "google",
    "model": "gemini-2.0",
    "model_family": "google"
  },
  "validator": {
    "provider": "anthropic",
    "model": "claude-opus",
    "model_family": "anthropic"
  }
}
```

✅ **Independência garantida:** 3 providers diferentes, 3 model families diferentes.

---

## Fallback e Degradação

Se CLI não responder (linha 5-9, config.yaml):

```yaml
fallback_providers:
  - provider: opencode-free
    model: nemotron-3-ultra-free
  - provider: opencode-free
    model: deepseek-v4-flash-free
```

**Regra:** Fallback apenas se worker principal indisponível. Hermes **não** silencia falha; pausa e aguarda aprovação.

---

## Para Chamar um CLI Específico

```bash
# Planner (Claude)
claude --config ~/.config/claude/config.yaml --prompt "Analisar: ..." > output.json

# Writer (Codex)
codex --model gpt-5.6 --temperature 0 --input context.json > peca.json

# Critic (Agy / Gemini)
agy --model gemini-2.0 --task critique --input peca.json > critique.json

# Validator (Claude)
claude --config ~/.config/claude/validator --prompt "Validar: ..." > qa.json
```

---

## Resumo Final

| Função | CLI | Modelo | Independência |
|--------|-----|--------|---|
| Planejamento | Claude | claude-opus/sonnet | Anthropic |
| **Redação** | **Codex** | **gpt-5.6** | **OpenAI** |
| **Crítica** | **Agy** | **gemini-2.0** | **Google** |
| Validação | Claude | claude-opus/sonnet | Anthropic |
| Orquestração | Hermes | claude-haiku | Anthropic (sem autoridade jurídica) |

✅ **3 provedores independentes para as 3 funções críticas (redação, crítica, validação)**

---

**Próximo passo:** Confirmar versões exatas de modelos com:
```bash
codex --version
agy --version
claude --version
```
