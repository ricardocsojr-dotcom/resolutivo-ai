---
name: briefing-andamentos
description: >
  Executa o Radar Estratégico (script Python de análise de andamentos processuais) e
  gera um briefing estruturado com os resultados. Use sempre que Ricardo pedir para
  "rodar o radar", "atualizar os andamentos", "analisar a planilha do dia", "gerar
  o briefing de andamentos", "executar o script", "o que tem de crítico hoje",
  "rodar a análise dos processos", ou qualquer variação que indique execução do
  pipeline de andamentos e leitura do relatório estratégico gerado.
  Ative também quando Ricardo disser "roda o Python", "executa o radar",
  "atualiza a análise", "tem algum crítico?", "o que o script achou?".
---

# Briefing de Andamentos — Radar Estratégico RDAA

Executa o pipeline Python de análise de andamentos e entrega um briefing
operacional estruturado, no mesmo padrão do `/legal:brief`.

## Pasta de trabalho

Todos os arquivos estão em:
```

```

Arquivos relevantes:
- (_disparo automatizado via motor_) — pipeline principal (classifica, filtra histórico, chama IA)
- (_disparo automatizado via motor_) — gera planilha de exemplo quando não há planilha real
- `Andamentos do Dia - Resolutivo.xlsx` (ou similar) — entrada do dia
- `Relatorio_Estrategico_Final.xlsx` — saída gerada pelo pipeline
- `historico_andamentos.xlsx` — controle de deduplicação
- `base_monitoramento_estrategico.md` — clientes e processos VIP
- `processos_monitorados.md` — lista de processos monitorados

## Fluxo de execução

### 1. Verificar se há planilha do dia

Execute via bash na pasta de trabalho:


Se não houver planilha real (apenas os arquivos de controle), informe Ricardo
que não há planilha nova para processar e pergunte se deseja rodar com dados
de teste ((_disparo automatizado via motor_)).

### 2. Executar o pipeline de análise


Observe o output do script:
- "Nada novo para processar" → informe Ricardo e encerre
- Erros de API → informe o erro e sugira verificar a chave
- "Sucesso! Relatório gerado" → prossiga para leitura

### 3. Ler o relatório gerado

Após execução bem-sucedida, leia `Relatorio_Estrategico_Final.xlsx` usando Python:


### 4. Gerar o briefing

Com os dados lidos, estruture o briefing no formato abaixo.

**Regras de montagem:**
- Ordene sempre por classificação: Crítico → Alto → Médio → Baixo → Ruído
- Dentro de cada nível, ordene por `Dias Paralisado` (decrescente)
- Para Ruído: exiba apenas o resumo de contagem, não liste individualmente
- Destaque com ⚡ os andamentos com `Alerta_Paralisacao == "Sim"`
- Destaque com ★ processos com `Cliente VIP? == "Sim"` ou `Processo VIP? == "Sim"`
- Se `Providencia` estiver preenchida, inclua como linha de ação
- Use o número do processo truncado para legibilidade: primeiros 20 chars + "..."

## Formato do briefing

```
# Radar Estratégico RDAA — [DATA]

## 🚨 CRÍTICO — Ação Imediata
> [N processo(s)]

| Processo | Cliente | Andamento | Providência |
|----------|---------|-----------|-------------|
| [número] ★⚡ | [cliente] | [Leitura_Estrategica] | [Providencia] |

---

## ⚠️ ALTO — Atenção Prioritária
> [N processo(s)]

| Processo | Cliente | Andamento | Providência |
|----------|---------|-----------|-------------|
| [número] | [cliente] | [Leitura_Estrategica] | [Providencia] |

---

## 📋 MÉDIO — Providência Necessária
> [N processo(s)]

| Processo | Cliente | Andamento | Providência |
|----------|---------|-----------|-------------|

---

## 📌 BAIXO — Monitoramento VIP
> [N processo(s)]

| Processo | Cliente | Andamento |
|----------|---------|-----------|

---

## 📊 Resumo Executivo

- **Total de andamentos novos analisados:** [N]
- **Críticos:** [N] | **Altos:** [N] | **Médios:** [N] | **Baixos:** [N] | **Ruídos:** [N]
- **Com alerta de paralisação:** [N]
- **Processos VIP na amostra:** [N]
- **Andamentos já vistos (removidos como duplicata):** [informa se o script reportou]

### ⚡ Alertas de Paralisação
[Lista apenas os processos com Alerta_Paralisacao == "Sim", com dias paralisados]

### Fontes não disponíveis
[Qualquer fonte que não foi possível consultar — ex: API offline, planilha ausente]
```

## Notas operacionais

- Se o script reportar que "todos os andamentos já foram analisados", informe
  Ricardo e não gere o briefing — não há dados novos para exibir.
- Se houver erro de autenticação na API Gemini, exiba o erro exato e sugira
  verificar a chave `API_KEY` em (_disparo automatizado via motor_).
- O histórico de deduplicação (`historico_andamentos.xlsx`) é atualizado
  automaticamente pelo script — não mexa manualmente.
- Após gerar o briefing, ofereça: "Quer que eu acione a skill `backoffice-juridico`
  para calcular prazos e redigir mensagens para os críticos e altos?"
