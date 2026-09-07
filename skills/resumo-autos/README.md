# 📚 Resumo de Autos Volumosos

> Transforma processos de milhares de páginas em: linha do tempo processual, mapa de provas, quadro de teses e "estado da arte" em 1 página — com cada afirmação citando a folha dos autos.

**No dia a dia:** *O caso tem 4.800 páginas e caiu no seu colo porque o colega saiu do escritório. Em vez de uma semana lendo PDF, você pede o resumo: sai a linha do tempo com os 40 atos que importam, o mapa do que cada parte provou (e do que ninguém provou), e o alerta — há uma decisão de fls. 3.212 determinando emenda que ninguém cumpriu. Você assume o caso sabendo mais do que quem o tocava.*

## Por que usar

- 🕐 **Linha do tempo processual** — só os atos relevantes, cada um com folha/ID citado
- 🗺️ **Mapa de provas por fato controvertido** — o que cada parte juntou, o que foi deferido, o que falta
- ⚖️ **Quadro de teses** — argumentos de cada parte × como o juízo tratou cada um até aqui
- 📄 **Estado da arte em 1 página** — onde o processo está, pendências, próximos prazos, riscos imediatos
- 🔍 **Auditável** — afirmação sem lastro nos autos sai marcada `[NÃO LOCALIZADO NOS AUTOS]`, nunca inventada

## Instalação por modelo de IA

| Plataforma | Como instalar |
|---|---|
| **Claude Code** (recomendado) | `git clone https://github.com/neimaciel/resumo-autos ~/.claude/skills/resumo-autos` → invocar com `/resumo-autos` |
| **Claude.ai / Claude Desktop** | Criar Projeto "Resumo de Autos Volumosos" → colar `SKILL.md` nas instruções → subir `workflows/`, `templates/` e `lib/` como conhecimento |
| **ChatGPT (GPT personalizado)** | Criar GPT → `SKILL.md` em *Instructions* → `workflows/`, `templates/`, `lib/` em *Knowledge* → ativar *Code Interpreter* para cálculos |
| **Gemini (Gem)** | Criar Gem "Resumo de Autos Volumosos" com `SKILL.md` nas instruções + arquivos anexados |
| **Gemini CLI** | Clonar o repo e referenciar o caminho no `GEMINI.md` do projeto |
| **Cursor / Windsurf / Codex CLI** | Clonar no repo do escritório e apontar `.cursor/rules` / `AGENTS.md` para `SKILL.md` |

> Regra de ouro: `SKILL.md` é sempre a **instrução de sistema**; `workflows/`, `templates/` e `lib/`
> são a **base de conhecimento**; `scripts/` (quando houver) só executa em plataformas com runtime.


## Comandos

```
/resumo-autos timeline        # linha do tempo dos atos relevantes
/resumo-autos provas          # mapa de provas por fato controvertido
/resumo-autos teses           # quadro de teses das partes × juízo
/resumo-autos estado          # estado da arte em 1 página
/resumo-autos transicao       # memorando de troca de responsável pelo caso
```

## Aviso — ferramenta de apoio, não substituto

Esta skill instrumenta o advogado; **não** substitui julgamento profissional.
Estratégia processual, decisão de acordo e casos sensíveis são decisão humana —
artefatos que exigem essa decisão saem marcados `STATUS: AGUARDANDO DECISÃO DO ADVOGADO`.
Toda citação legal deve ser conferida na fonte antes do protocolo.

---
**Mantenedor:** [@neimaciel](https://github.com/neimaciel) · Suíte skills-advocacia · MIT
