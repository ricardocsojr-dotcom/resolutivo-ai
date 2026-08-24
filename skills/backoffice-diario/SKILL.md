---
name: backoffice-diario
description: >
  [DESATIVADA POR ENQUANTO — 2026-08-23] Não ativar. Dependia do MCP CNJ, que
  foi desconectado deliberadamente. Se o usuário pedir o briefing do dia,
  informe que a consulta automática de DataJud/DJEN está desligada por
  enquanto e pergunte se ele quer organizar a agenda com os dados que ele
  fornecer manualmente (via backoffice-juridico).
---

# Backoffice Diário — RDAA (DESATIVADA)

> **Desativada em 2026-08-23 a pedido do Ricardo**: o fluxo inteiro depende de
> DataJud + DJEN, que foram desligados por não estarem sendo úteis na
> prática. O servidor MCP `CNJ` foi removido de `.mcp.json`. Para reativar:
> adicionar de volta a entrada `"CNJ"` em `.mcp.json` e restaurar a
> `description` original abaixo no frontmatter.
>
> Descrição original (para reativação):
> "Abre o dia operacional do escritório RDAA: consulta processos com prazo
> próximo no DataJud, verifica publicações no DJEN, organiza as providências
> do dia e gera o briefing diário."

O restante deste arquivo documenta o fluxo original, preservado para quando a
skill for reativada. Enquanto estiver desativada, **não execute nada abaixo**.

Rotina matinal integrada: DataJud + DJEN + agenda operacional.

## O que este fluxo faz

1. Verifica publicações recentes no DJEN para os processos monitorados
2. Consulta andamentos no DataJud de processos com prazo iminente
3. Organiza as providências do dia com responsável e urgência
4. Gera o briefing diário pronto para uso

## Fluxo de execução

### 1. Obter lista de processos monitorados

Pergunte ao Ricardo ou leia do contexto quais processos estão ativos. Se ele
forneceu uma lista ou planilha, use esses números.

### 2. Consultar DJEN para cada processo

```
buscar_publicacoes_dje_cnj(numero_processo="...")
```

Para cada publicação encontrada nas últimas 48h, inclua no briefing como
**URGENTE** com data de publicação e conteúdo.

### 3. Consultar movimentos recentes no DataJud

```
consultar_processo(numero_processo="...", tribunal="...")
```

Filtre movimentos das últimas 48h. Se houver despacho, decisão ou julgamento,
inclua no briefing como **AÇÃO NECESSÁRIA**.

### 4. Integrar com backoffice-juridico

Passe as providências identificadas para a skill `backoffice-juridico` para:
- Calcular prazos (prazo a contar de publicação)
- Identificar responsável (quem deve agir)
- Redigir mensagem para o cliente se necessário

### 5. Gerar o briefing diário

**Formato:**

---
# Briefing RDAA — [DATA]

## ⚠️ URGENTE (publicações e decisões recentes)
[lista de processos com publicação nas últimas 48h]

## 📋 PROVIDÊNCIAS DO DIA
| Processo | Prazo | Providência | Responsável |
|----------|-------|-------------|-------------|
| [número] | [data] | [o que fazer] | [quem] |

## 📬 COMUNICAÇÕES PENDENTES (clientes)
[se houver]

## ℹ️ SEM NOVIDADES
[processos consultados sem movimentação recente]

---

## Nota

Para prazos, o cálculo padrão considera dias úteis conforme CPC (art. 219).
A skill `backoffice-juridico` faz esse cálculo — chame-a com o texto do
movimento identificado para obter a data exata do prazo.
