# ⚔️ Peças com Revisão Adversarial

> Redação de peças processuais com o "advogado do diabo" embutido: antes do protocolo, a skill simula o juiz (admissibilidade e clareza) e a parte contrária (contra-argumentos) e entrega o relatório de fragilidades com severidade.

**No dia a dia:** *A contestação está pronta às 22h e parece ótima — para você, que a escreveu. Você roda a simulação: o "juiz" aponta que o pedido subsidiário ficou indeterminado, e o "adversário" acha o flanco — você impugnou o fato errado e deixou incontroverso justamente o que doía. Vinte minutos de ajuste hoje valem mais que dois anos de recurso depois.*

## Por que usar

- ✍️ **Redação estruturada** — síntese → preliminares → mérito → pedidos, com fundamentação integrada à skill `jurisprudencia-verificada`
- 👨‍⚖️ **Simulação do juiz** — requisitos formais, pedidos determinados, coerência, o que um julgador sobrecarregado entende em 10 minutos
- 🥊 **Simulação do adversário** — os 5 melhores ataques que a parte contrária faria contra a sua peça
- 🚦 **Relatório de fragilidades** — bloqueante / relevante / cosmético, para decidir o que corrigir antes do fatal
- ✅ **Checklist pré-protocolo** — universal, roda em qualquer peça

## Instalação por modelo de IA

| Plataforma | Como instalar |
|---|---|
| **Claude Code** (recomendado) | `git clone https://github.com/neimaciel/redator-adversarial ~/.claude/skills/redator-adversarial` → invocar com `/redator-adversarial` |
| **Claude.ai / Claude Desktop** | Criar Projeto "Peças com Revisão Adversarial" → colar `SKILL.md` nas instruções → subir `workflows/`, `templates/` e `lib/` como conhecimento |
| **ChatGPT (GPT personalizado)** | Criar GPT → `SKILL.md` em *Instructions* → `workflows/`, `templates/`, `lib/` em *Knowledge* → ativar *Code Interpreter* para cálculos |
| **Gemini (Gem)** | Criar Gem "Peças com Revisão Adversarial" com `SKILL.md` nas instruções + arquivos anexados |
| **Gemini CLI** | Clonar o repo e referenciar o caminho no `GEMINI.md` do projeto |
| **Cursor / Windsurf / Codex CLI** | Clonar no repo do escritório e apontar `.cursor/rules` / `AGENTS.md` para `SKILL.md` |

> Regra de ouro: `SKILL.md` é sempre a **instrução de sistema**; `workflows/`, `templates/` e `lib/`
> são a **base de conhecimento**; `scripts/` (quando houver) só executa em plataformas com runtime.


## Comandos

```
/redator-adversarial redigir <peça>      # redação estruturada
/redator-adversarial juiz                # simulação do julgador na peça atual
/redator-adversarial adversario          # simulação da parte contrária
/redator-adversarial fragilidades        # relatório completo (juiz + adversário)
/redator-adversarial pre-protocolo       # checklist final
```

## Aviso — ferramenta de apoio, não substituto

Esta skill instrumenta o advogado; **não** substitui julgamento profissional.
Estratégia processual, decisão de acordo e casos sensíveis são decisão humana —
artefatos que exigem essa decisão saem marcados `STATUS: AGUARDANDO DECISÃO DO ADVOGADO`.
Toda citação legal deve ser conferida na fonte antes do protocolo.

---
**Mantenedor:** [@neimaciel](https://github.com/neimaciel) · Suíte skills-advocacia · MIT
