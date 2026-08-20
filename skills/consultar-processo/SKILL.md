---
name: consultar-processo
description: >
  Consulta andamento processual completo via DataJud (CNJ) e interpreta os
  movimentos para o advogado. Use sempre que Ricardo informar um número de
  processo e pedir andamento, movimentação, situação atual, o que aconteceu,
  prazo, ou quando quiser saber se houve despacho, decisão ou publicação
  recente. Ative com termos como "consulta o processo", "o que aconteceu nesse
  processo", "andamento do processo", "tem alguma movimentação", "qual a última
  decisão", "houve publicação", ou qualquer variação que indique consulta
  processual.
---

# Consulta Processual — RDAA

Esta skill é **sob demanda**. Ela só deve ser executada quando Ricardo pedir
andamento, movimentação, decisão, prazo, publicação ou situação atual, ou quando
uma rotina operacional específica declarar a consulta. A existência de número
de processo durante a redação de uma peça não aciona esta skill.

## Fluxo de execução

### 1. Identificar o tribunal

Se o usuário não informou o tribunal, extraia-o do número do processo (posição
14-17 do NPU) ou pergunte.

Referência rápida:
- `8.26` → TJSP
- `8.13` → TJMG
- `8.19` → TJRJ
- `4.03` → TRF3
- `3.00` → STJ

### 2. Consultar o DataJud

Use o MCP `CNJ`:
```
consultar_processo(numero_processo="...", tribunal="TJSP")
```

### 3. Interpretar e apresentar

Nunca devolva o JSON bruto. Traduza para o advogado:

**Formato de resposta:**

---
**Processo:** [número]
**Tribunal:** [nome] | **Órgão:** [câmara/vara]
**Classe:** [classe processual] | **Grau:** [1º/2º]
**Ajuizado em:** [data]

**Partes:**
- Autor: [nome]
- Réu: [nome]

**Último movimento:** [data] — [descrição interpretada]

**Movimentações recentes (últimas 5):**
| Data | Movimento |
|------|-----------|
| [data] | [descrição] |
...

**Análise rápida:**
[2-3 linhas: o que está pendente, qual o próximo passo provável, algum alerta de prazo se identificável]

---

### 4. Verificar DJEN (se relevante)

Se o usuário perguntar sobre publicações/intimações recentes, use:
```
buscar_publicacoes_dje_cnj(numero_processo="...")
```
E informe o que foi publicado e em que data.

## Alertas automáticos

Se identificar nas movimentações:
- **"Julgado"** ou **"Acórdão"** → avise que há decisão de mérito, sugira buscar o inteiro teor
- **"Prazo"** → destaque em negrito com a data
- **"Bloqueio"** ou **"Penhora"** → alerta vermelho
- **"Arquivado"** → informe que o processo está encerrado

## Registro no estado compartilhado

Quando a consulta retornar dados explícitos, registre no estado da matéria os
metadados e as movimentações relevantes com `register_research` e o tipo
`processo`. Preserve o número, tribunal, classe, partes, data da consulta,
identificador da movimentação e localização oficial quando fornecidos.

O registro conserva o que veio do CNJ/DataJud; ele não transforma a análise do
agente em fato, nem atribui urgência, risco ou validade a uma movimentação.
Alertas e interpretações continuam sendo saída explícita do agente e, quando
necessários ao caso, entram em `pending` ou `decisions` apenas por registro
declarado.
