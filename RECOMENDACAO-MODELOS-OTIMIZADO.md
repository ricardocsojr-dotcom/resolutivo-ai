# Recomendação de Modelos Otimizados — RDAA 2026-09

**Data:** 2026-09-02  
**Base:** Tabelas de desempenho ChatGPT/Claude/Antigravity vs. casos de uso jurídicos  
**Objetivo:** Mapear modelo ideal por worker, balanceando capacidade × custo

---

## Análise por Worker

### 1️⃣ **Planner (Claude)**

**Função:** Ler fatos, teses, evidências → aprova esqueleto  
**Critério:** Compreensão estrutural, sem criatividade excessiva

| Candidato | Análise | Recomendação |
|-----------|---------|---|
| **Haiku 4.5** | ★★ (análise jurídica simples) — **insuficiente para estratégia** | ❌ |
| **Sonnet 5** | ★★★ (análise jurídica simples + redação) — **adequado** | ✅ **RECOMENDADO** |
| **Opus 5** | ★★★ (estratégia jurídica difícil) — **overcapacity** | ⚠️ Possível se orçamento permite |

**Recomendação:** `claude-sonnet-5`  
**Razão:** Análise estrutural + aprovação de esqueleto = ★★★ em Sonnet; Opus é overqualified.

---

### 2️⃣ **Writer (OpenAI)**

**Função:** Redige peça inteira com blocos, fontes selecionadas  
**Critério:** Criatividade + conformidade, contexto longo, estiloRDAA

| Candidato | Análise | Recomendação |
|-----------|---------|---|
| **Luna (gpt-5.6)** | ★★ (programação complexa) — **marginal para redação jurídica** | ⚠️ Usar se custo crítico |
| **Terra (gpt-5.5)** | ★★★ (análise jurídica + código) — **adequado** | ✅ **RECOMENDADO** |
| **Sol (gpt-5)** | ★★★ (estratégia jurídica) — **overcapacity** | ⚠️ Possível se qualidade crítica |

**Recomendação:** `gpt-5.5` (Terra)  
**Razão:** Redação de peça exige criatividade jurídica (★★★); Luna é marginal (★★); Sol é overcapacity.  
**Fallback:** Luna se custo for bloqueador; Sol se peça for crítica (nível A).

---

### 3️⃣ **Critic (Google/Antigravity)**

**Função:** Identifica vulnerabilidades, propõe contratese  
**Critério:** Raciocínio adversarial, profundidade, pensamento divergente

| Candidato | Análise | Recomendação |
|-----------|---------|---|
| **Gemini 3.7 Flash** | 🟩 baixo consumo, rápido — **rápido demais para crítica** | ❌ |
| **Gemini 3.6 Flash** | 🟩 baixo consumo, eficiente — **bom para triagem, fraco para crítica séria** | ⚠️ |
| **GPT-OSS-120B** | 🟨 reasoning moderado — **insuficiente para crítica séria** | ❌ |
| **Gemini 3.1 Pro High** | 🟧 reasoning High, tokens ↑ — **adequado** | ✅ **RECOMENDADO** |
| **Claude Sonnet 4.6 Thinking** | 🟧 thinking mode — **overcapacity se Sonnet já é critic** | ⚠️ |
| **Claude Opus 4.6 Thinking** | 🟥 muito alto consumo — **overcapacity** | ❌ |

**Recomendação:** `gemini-3.1-pro-high`  
**Razão:** Critic precisa de raciocínio profundo (adversarial); Gemini 3.1 Pro High tem reasoning High. Flash é rápido demais.  
**Nota:** Se Critic for Claude Sonnet Thinking em vez de Gemini, mantém independência (Google ≠ Anthropic).

---

### 4️⃣ **Validator (Claude)**

**Função:** QA conformidade, checklist RDAA, gates finais  
**Critério:** Regras estruturais, verificação de fatos, sem raciocínio criativo

| Candidato | Análise | Recomendação |
|-----------|---------|---|
| **Haiku 4.5** | ★★★ (extração + classificação) — **adequado para QA estrutural** | ✅ **RECOMENDADO** |
| **Sonnet 5** | ★★★ (desnecessário para QA simples) — **overcapacity, mais barato que Opus** | ⚠️ Alternativa |
| **Opus 5** | ★★★ (problem very hard) — **overcapacity** | ❌ |

**Recomendação:** `claude-haiku-4.5`  
**Razão:** Validation é checklist estrutural (★★★ em Haiku); Sonnet/Opus são overcapacity.  
**Benefício:** Haiku é o modelo mais barato da Anthropic.

---

## Configuração Recomendada

### Cenário 1: **Otimizado para Custo** (Nível C/B)

```json
{
  "planner": {
    "cli": "claude",
    "model": "claude-sonnet-5",
    "provider": "anthropic"
  },
  "writer": {
    "cli": "codex",
    "model": "gpt-5.5",
    "provider": "openai"
  },
  "critic": {
    "cli": "agy",
    "model": "gemini-3.1-pro-high",
    "provider": "google"
  },
  "validator": {
    "cli": "claude",
    "model": "claude-haiku-4.5",
    "provider": "anthropic"
  }
}
```

**Rationale:**
- Planner: Sonnet (análise), não Opus
- Writer: Terra/gpt-5.5 (redação), não Luna (marginal) ou Sol (caro)
- Critic: Gemini 3.1 Pro (reasoning), não Flash (rápido demais)
- Validator: Haiku (checklist), não Sonnet (overcapacity)

**Custo relativo:** 🟨 Médio-alto (Sonnet + Terra + Pro High + Haiku)

---

### Cenário 2: **Máxima Qualidade** (Nível A)

```json
{
  "planner": {
    "cli": "claude",
    "model": "claude-opus-5",
    "provider": "anthropic"
  },
  "writer": {
    "cli": "codex",
    "model": "gpt-5",
    "provider": "openai"
  },
  "critic": {
    "cli": "agy",
    "model": "claude-opus-4.6-thinking",
    "provider": "anthropic"
  },
  "validator": {
    "cli": "claude",
    "model": "claude-sonnet-5",
    "provider": "anthropic"
  }
}
```

**Rationale:**
- Planner: Opus (estratégia difícil)
- Writer: Sol/gpt-5 (melhor geração jurídica)
- Critic: Claude Opus Thinking (raciocínio aprofundado)
- Validator: Sonnet (qualidade extra)

**Custo relativo:** 🟥 Muito alto (Opus × 3 + Sol)  
**Problema:** Critic é Claude (não Google) → perde independência com Planner/Validator (ambos Anthropic)

---

### Cenário 3: **Balanceado + Independência Garantida** ⭐ **RECOMENDADO**

```json
{
  "planner": {
    "cli": "claude",
    "model": "claude-sonnet-5",
    "provider": "anthropic",
    "model_family": "anthropic"
  },
  "writer": {
    "cli": "codex",
    "model": "gpt-5.5",
    "provider": "openai",
    "model_family": "openai"
  },
  "critic": {
    "cli": "agy",
    "model": "gemini-3.1-pro-high",
    "provider": "google",
    "model_family": "google"
  },
  "validator": {
    "cli": "claude",
    "model": "claude-haiku-4.5",
    "provider": "anthropic",
    "model_family": "anthropic"
  }
}
```

**Garantias de Independência:**
```
✅ writer.model_family (openai) ≠ critic.model_family (google)
✅ critic.model_family (google) ≠ validator.model_family (anthropic)
✅ writer.model_family (openai) ≠ validator.model_family (anthropic)
```

**Custo relativo:** 🟨 Médio  
**Qualidade:** ★★★ para todos os casos de uso jurídico  

---

## Comparativo Direto (ChatGPT vs. Claude vs. Antigravity)

### Redação de Peça (Writer)

| Modelo | Rating | Custo | Independência |
|--------|--------|-------|---|
| Luna (gpt-5.6) | ★★ | 🟩 baixo | OpenAI ✅ |
| **Terra (gpt-5.5)** | **★★★** | **🟨 médio** | **OpenAI ✅** |
| Sol (gpt-5) | ★★★ | 🟧 alto | OpenAI ✅ |

**Vencedor:** Terra (gpt-5.5) — melhor custo/benefício

---

### Crítica de Tese (Critic)

| Modelo | Rating | Custo | Independência |
|--------|--------|-------|---|
| Gemini 3.6 Flash | ★★ | 🟩 baixo | Google ✅ |
| GPT-OSS-120B | ★★ | 🟨 médio | Open-source ❌ (não controla Anthropic) |
| **Gemini 3.1 Pro High** | **★★★** | **🟧 alto** | **Google ✅** |
| Claude Sonnet Thinking | ★★★ | 🟧 alto | Anthropic (conflita com Planner) |

**Vencedor:** Gemini 3.1 Pro High — reasoning aprofundado + independência

---

### Validação QA (Validator)

| Modelo | Rating | Custo | Independência |
|--------|--------|-------|---|
| **Haiku 4.5** | **★★★** | **🟩 muito baixo** | **Anthropic ✅** |
| Sonnet 5 | ★★★ | 🟨 médio | Anthropic ✅ |
| Opus 5 | ★★★ | 🟧 alto | Anthropic ✅ |

**Vencedor:** Haiku 4.5 — checklist estrutural + menor custo

---

## Implementação

### 1. Atualizar `orquestracao/roteamento.json`

```json
{
  "workers": {
    "planner": {"engine": "claude", "provider": "anthropic", "model": "claude-sonnet-5"},
    "writer": {"engine": "codex", "provider": "openai", "model": "gpt-5.5"},
    "critic": {"engine": "antigravity", "provider": "google", "model": "gemini-3.1-pro-high"},
    "validator": {"engine": "claude", "provider": "anthropic", "model": "claude-haiku-4.5"}
  }
}
```

### 2. Atualizar `config.yaml`

```yaml
model:
  default: gpt-5.5  # Mudar de gpt-5.6-luna para gpt-5.5 (Terra)
  provider: openai-codex
```

### 3. Registrar Fallback em `config.yaml`

```yaml
fallback_providers:
  - provider: openai-codex
    model: gpt-5.5  # Primary
  - provider: openai-codex
    model: gpt-5.6-luna  # Fallback 1 (custo)
  - provider: opencode-free
    model: nemotron-3-ultra-free  # Fallback 2 (gratuito)
```

---

## Resumo Final

| Worker | Modelo Recomendado | Razão | Custo |
|--------|-------------------|-------|-------|
| **Planner** | claude-sonnet-5 | ★★★ análise jurídica | 🟨 médio |
| **Writer** | gpt-5.5 (Terra) | ★★★ redação criativa | 🟨 médio |
| **Critic** | gemini-3.1-pro-high | ★★★ reasoning + adversarial | 🟧 alto |
| **Validator** | claude-haiku-4.5 | ★★★ checklist estrutural | 🟩 baixo |
| **Hermes** | claude-haiku-4.5 | ★★★ orquestração (atual) | 🟩 baixo |

✅ **Custo total:** 🟨 Médio-alto (equilibrado)  
✅ **Independência:** Garantida (3 providers diferentes)  
✅ **Qualidade:** ★★★ para todos os casos (C/B/A)  
✅ **Fallback:** Configurado com Luna + gratuito

---

**Status:** Pronto para implementar no próximo cycle (2026-09-15)
