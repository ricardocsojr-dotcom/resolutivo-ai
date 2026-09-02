# Tempo de produção por nível — B/C não passam de crítica e validação plena

**Fonte de verdade única:** `orquestracao/roteamento.json`. Não existe script
paralelo de "fluxo rápido" — o orquestrador oficial (`orquestrador_rdaa.py`)
lê a política e decide sozinho quais estágios cada nível percorre.

## Estágios por nível (após correção de 2026-09-02)

| Nível | Estágios de produção após `drafting`/`draft_ready` |
|-------|------------------------------------------------------|
| **A** | `draft_ready` → `criticizing` → `critique_ready` → `validating` → `candidate_ready` |
| **B** | `draft_ready` → `validating` → `candidate_ready` |
| **C** | `draft_ready` → `candidate_ready` (direto) |

- **Nível A**: crítica independente (Antigravity) + validação (Claude). É o
  único nível com o estágio `criticizing`.
- **Nível B**: sem crítica. Uma validação Claude ao final do texto, antes de
  publicar.
- **Nível C**: sem crítica, sem validação. Peça de modelo fixo e uso
  cotidiano (juntada, ciência, oposição a julgamento virtual, concordância,
  pedido de prazo) — o checklist de estilo e o QA gate do `publicar_docx.py`
  continuam rodando (controle mecânico, não julgamento jurídico), mas não há
  chamada a `executar_motor.py --role validator`.

## Por que existia o problema

Antes da correção, `roteamento.json` exigia `criticizing`/`critique_ready`
também no nível B e `validating` também no nível C — nenhum nível abaixo de A
podia pular etapa nenhuma. Isso fazia toda peça B/C atravessar o mesmo
fluxo pesado de uma peça A (crítica Antigravity + validação Claude), e uma
manifestação simples levava a mesma ~1h de uma peça premium.

A correção mexeu em um único lugar: `orquestracao/roteamento.json`
(`levels.B.stages` e `levels.C.stages`) e a checagem de papel obrigatório em
`orquestrador_rdaa.py::avancar_fase` (um papel só é exigido se o próprio
estágio existir na rota do nível). Não há segunda diretriz, script ou flag
concorrente — quem decide é a política.

## Comando (igual para todos os níveis — a rota decide o resto)

```bash
# Redação (sempre roda, qualquer nível)
py -3.14 skills/redigir-peca/scripts/executar_motor.py codex \
  --prompt .rdaa-run/<matter>/PROMPT-REDACAO.md \
  --output .rdaa-run/<matter>/RASCUNHO-CODEX.md \
  --state-dir .rdaa-run/<matter> --role writer

py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py advance .rdaa-run/<matter> draft_ready

# A partir daqui, a rota decide sozinha:
# - Nível A: avance para "criticizing" (crítica obrigatória) antes de "validating"
# - Nível B: avance direto para "validating" ("criticizing" não existe na rota)
# - Nível C: avance direto para "candidate_ready" ("validating" não existe na rota)
```

Tentar registrar uma execução de crítico/validador fora do estágio certo
falha com `WorkflowStateError` — não é uma opção silenciosa, é a política
recusando a chamada.

## Quando declarar cada nível

- **A**: tese nova, jurisprudência conflituosa, estratégia processual
  relevante, recurso em tribunal, peça de risco alto.
- **B**: manifestação sobre diligência/execução, memorial desenvolvido,
  impugnação baseada em fatos do processo, réplica, petição de
  prosseguimento rotineiro.
- **C**: juntada, ciência, oposição a julgamento virtual, concordância,
  pedido de prazo — texto que não diverge do modelo padrão do escritório.

`risk_escalation` em `roteamento.json` pode reclassificar a rota para cima
(risco alto força pelo menos B; risco crítico força A) — nunca para baixo.

## Testes

`tests/test_orquestrador_rdaa.py` cobre:
- `test_rota_b_exige_validacao_mas_dispensa_critica_independente`
- `test_rota_c_nao_tem_criticizing_nem_validating`
- `test_fluxo_c_avanca_de_draft_ready_direto_para_candidate_ready`
- `test_risco_alto_nunca_rebaixa_fluxo_c`
