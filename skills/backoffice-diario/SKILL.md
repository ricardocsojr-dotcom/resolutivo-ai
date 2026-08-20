---
name: backoffice-diario
description: >
  Abre o dia operacional do escritório RDAA: consulta processos com prazo
  próximo no DataJud, verifica publicações no DJEN, organiza as providências
  do dia e gera o briefing diário. Use todas as manhãs ou quando Ricardo
  pedir "o que tem pra hoje", "organiza o dia", "tem alguma publicação",
  "quais os prazos de hoje", "abre o escritório", ou qualquer variação que
  indique início de jornada operacional ou revisão de agenda do dia.
---

# Backoffice Diário — RDAA

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
