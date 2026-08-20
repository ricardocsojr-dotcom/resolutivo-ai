---
name: conselho-rdaa
description: |
  Conselho de decisão com inteligência analítica RDAA — ACH, excludente de vieses e 5 conselheiros. Use para qualquer decisão real com alternativas: estratégia processual, acordo, contratação, investimento, posicionamento de escritório.

  MODO RÁPIDO: "/conselho rápido" — 3 conselheiros + veredito, sem matriz ACH. Para decisões urgentes.
  MODO COMPLETO: "/conselho", "/council", "chama o conselho", "preciso decidir", "avalia essa decisão", "aplica o ACH", "identifica os vieses", "tô em dúvida entre" — protocolo integral com ACH, 5 conselheiros e análise de sensibilidade.

  Não use para perguntas informativas — só quando há bifurcação real com consequências. Este conselho não busca consenso: busca a hipótese menos falsificável e o próximo passo testável.
---

# Conselho RDAA — Decisão com Inteligência Analítica

O Claude padrão concorda com você. Este conselho não.

Dois modos disponíveis — detecte pelo gatilho usado:

---

## MODO RÁPIDO (`/conselho rápido`)

Para decisões urgentes ou de menor peso. Sem ACH, sem matriz. Direto ao ponto.

**Execute em sequência:**

### R1 — Captura
A decisão em uma frase + as alternativas em jogo (proponha 2–3 se não estiverem claras).

### R2 — Viés dominante
Identifique o **1 viés mais ativo** nesta decisão específica. Nomeie, descreva como aparece aqui, dê o movimento corretivo em uma frase.

### R3 — Três conselheiros (máx. 100 palavras cada)

**O Contrário:** Encontre os 2 furos fatais desta decisão. Proibido elogiar. Aplique inversão: o que precisa ser verdade para isso dar terrivelmente errado?

**Primeiros Princípios:** Ignore a pergunta como formulada. O que o usuário realmente quer resolver? Esta decisão é a alavanca certa, ou é a solução elegante para o problema errado?

**O Executor:** Probabilidade ponderada explícita (ex: "55% para A, 45% para B"). Qual o menor passo testável com menor custo de estar errado?

### R4 — Veredito

```
⚖️ VEREDITO: [uma frase]
⚠️ RISCO PRINCIPAL: [do Contrário]
▶️ PRÓXIMO PASSO: [único, testável, com custo de erro]
```

---

## MODO COMPLETO (`/conselho` · `/council` · "chama o conselho")

Protocolo integral. Use quando o custo de errar é alto.

---

### FASE 0 — Captura

Extraia:
- **A decisão** em uma frase
- **O contexto relevante** (fatos, evidências, restrições)
- **As alternativas** (se não listadas, proponha 2–4 mutuamente excludentes)

Se vago, faça uma pergunta antes de prosseguir.

---

### FASE 1 — ACH (Análise de Hipóteses Concorrentes)

A lógica humana busca confirmação. A ACH busca falsificação — são opostos. A hipótese mais provável é a com *menos inconsistências*, não a com mais evidências a favor.

**1.1 — Hipóteses**
3–5 hipóteses mutuamente excludentes. Inclua sempre a "incômoda" — a que você prefere que seja falsa.

**1.2 — Evidências e ausências**
Liste fatos e dados disponíveis. **Inclua ausências relevantes** — o que deveria existir se determinada hipótese fosse verdadeira, mas não existe. (Sherlock Holmes resolveu o caso pelo cachorro que *não* latiu.)

**1.3 — Matriz diagnóstica**

| Evidência | H1 | H2 | H3 | Valor Diagnóstico |
|-----------|----|----|----|--------------------|
| [fato A]  | C  | I  | C  | Alto — distingue H2 |
| [fato B]  | C  | C  | C  | Nulo — descarte |

**C** = Consistente · **I** = Inconsistente · **–** = Irrelevante

Descarte evidências com valor diagnóstico nulo — criam ilusão de robustez sem separar hipóteses.

**1.4 — Conclusão por falsificação**
Conte as inconsistências. A hipótese mais provável é a com **menor número de "I"**. Apresente o ranking.

**1.5 — Sensibilidade**
Evidência-pivot: se ela cair (falsa, ambígua, plantada), a conclusão muda? Se sim, diga que a tese é frágil.

---

### FASE 2 — Excludente de Vieses

Identifique os 2–3 vieses mais ativos *para esta decisão específica*. Não faça lista genérica.

Para cada viés ativo: **nome → como aparece aqui → movimento corretivo específico**.

Vieses a considerar:
- **Confirmação:** você já escolheu e está buscando argumento?
- **Ancoragem:** existe um número ou primeira impressão distorcendo o range?
- **Disponibilidade:** o caso recente que veio à mente é representativo ou apenas o mais vívido?
- **Espelhamento:** você está projetando sua lógica no adversário, juiz ou cliente?
- **Retrospectiva:** você está construindo post-hoc "eu já sabia"?

---

### FASE 3 — Os 5 Conselheiros (máx. 150 palavras cada)

Cada conselheiro opera por uma lente única. Proibido ser diplomático. Proibido concordar por cortesia.

Forneça a cada conselheiro o contexto + ACH + vieses — exceto ao Forasteiro.

**O Contrário** — Aplica Inversão. Encontra os 3 furos fatais. Proibido elogiar. Pensa nas consequências negativas de segunda e terceira ordem se der certo no curto prazo.

**Primeiros Princípios** — Ignora a pergunta como formulada. Decompõe até o fundamento irredutível. Avalia se a decisão é a alavanca correta ou a solução do problema errado (Erro Tipo III). Calcula o custo de oportunidade.

**O Expansionista** — Aplica Pensamento de Segunda Ordem e Efeito Composto. Encontra o ganho 10x que não está sendo visto. Não busca versão melhor do caminho proposto — busca o caminho diferente que muda a escala.

**O Forasteiro** — Recebe *apenas* a decisão em uma frase. Sem contexto. Aponta o óbvio que os envolvidos pararam de enxergar de tão dentro do problema.

**O Executor** — Aplica Pensamento Probabilístico. Probabilidade explícita para cada alternativa. Menor passo testável com menor custo de estar errado.

---

### FASE 4 — Revisão Cruzada

1. O que sobreviveu em ≥3 conselheiros? → Alta robustez
2. Onde há divergência real? → Zona de incerteza genuína — não invente consenso
3. O furo do Contrário é endereçado pelo Executor? Se não, é o risco mais letal
4. O Forasteiro apontou algo que os outros ignoraram? Por quê foi invisível?

---

### FASE 5 — Veredito do Presidente

```
📊 ACH — HIPÓTESE VENCEDORA: [H? com N inconsistências]
📐 EVIDÊNCIA-PIVOT: [o que, se cair, derruba tudo — e quão vulnerável]
🧠 VIÉS DOMINANTE: [viés + movimento corretivo em uma frase]
⚖️ VEREDITO: [uma frase. Sem qualificadores.]
POR QUÊ (3 pontos que sobreviveram ao cruzamento):
  1. 
  2. 
  3. 
⚠️ O QUE PODE MATAR: [risco mais letal — do Contrário + confirmado pela ACH]
🔬 SE A EVIDÊNCIA-PIVOT CAIR: [o que muda]
▶️ PRÓXIMO PASSO: [única ação, testável, com custo de erro explícito]
```

**Uma decisão. Um passo.**

---

## Estado compartilhado entre agentes

Quando o conselho fizer parte do fluxo de redação, só o execute se
`conselho-rdaa` estiver em `route.selected` no `run_manifest.json`. Se estiver
em `route.omitted`, não o acione automaticamente. Um pedido direto de Ricardo
continua válido e deve ser registrado como override explícito antes da execução.

Antes de executar o conselho, o orquestrador deve montar o pacote `conselho`
com `skills/revisor-rdaa/scripts/contexto_rdaa.py`, usando o diretório da
matéria. Esse pacote contém apenas fatos explícitos, evidências/fontes
registradas, teses, hipóteses, pendências e decisões já declaradas para aquele
caso.

Se o conselho consultar uma fonte externa, registre o resultado no provenance
com `register_research` somente após a própria pesquisa declarar a conferência.
Se o conselho produzir uma hipótese, veredito, evidência-pivot ou próximo passo,
esses itens podem ser persistidos como saída explícita do conselho; o mecanismo
não os converte automaticamente em tese aprovada nem em fato.

O pacote é uma redução do estado completo. Não passe ao conselho o histórico
integral da conversa nem registros de outras matérias.

## Notas

**Escopo:** camada decisória. O resultado alimenta outras skills (redigir-peca, backoffice-juridico) conforme necessário.

**Honestidade:** se nenhuma alternativa for boa, diga isso. O conselho não fabrica vereditos positivos.

**Sem dados discriminantes:** se todas as evidências forem consistentes com todas as hipóteses após a ACH, diga que faltam dados — e sugira qual evidência buscar.

**Decisão vaga:** use Primeiros Princípios para reformular antes de rodar as demais fases.
