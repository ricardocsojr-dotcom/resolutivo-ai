# Contrato semântico e de risco do RDAA

## Finalidade

Esta camada organiza fatos, evidências, teses, pedidos, riscos e decisões para
permitir comparação objetiva entre contexto, peça e saídas dos agentes. Ela não
reescreve a peça, não escolhe estratégia e não diagnostica mérito jurídico.

> O sistema pode comparar registros explicitamente identificados; não pode
> inferir validade jurídica, força probatória, risco processual ou correção de
> tese a partir de texto livre.

## Compatibilidade

O contrato é aditivo ao `matter_state.json` atual. Os campos legados `facts`,
`theses`, `citations`, `decisions` e `pending` continuam válidos, inclusive
quando contêm strings. Registros estruturados podem ser acrescentados sem
exigir migração imediata.

| Entidade | Campo sugerido | Uso |
|---|---|---|
| Fato | `facts` | Dado explicitamente fornecido ou conferido |
| Evidência | `provenance.jsonl`/`citations` | Fonte ou documento identificado |
| Tese | `theses` | Linha argumentativa declarada |
| Pedido | `requests` | Objetivo da peça declarado |
| Risco | `risks` | Risco declarado pelo usuário ou agente |
| Decisão | `decisions` | Veredito, alternativa ou próximo passo declarado |
| Revisão | `semantic_reviews` | Achados objetivos e pendências |

## IDs e referências

Toda entidade estruturada deve ter um `id` estável dentro da matéria. Referências
entre entidades usam IDs (`fact_ids`, `source_ids`, `thesis_ids`, `request_ids` e
`evidence_pivot_ids`). O código pode verificar se um ID existe, mas não deve
completar referência ausente por semelhança textual. ID inexistente gera
pendência objetiva.

## Registro mínimo

```json
{
  "id": "T-1",
  "tipo": "tese",
  "texto": "Texto explicitamente fornecido",
  "status": "proposta",
  "fact_ids": ["F-1"],
  "source_ids": ["SRC-1"],
  "origem": "redator"
}
```

Os status são declarações do fluxo, não classificações automáticas. Exemplos:
`informado`, `conferido`, `proposta`, `aprovada`, `pendente`, `contestada`,
`registrada` e `rejeitada`.

## Fatos, evidências e teses

Um fato deve conservar texto, origem e localização. Uma evidência deve apontar
para fonte ou documento identificado. O mecanismo não atribui autenticidade,
força probatória, pertinência ou valor diagnóstico.

Uma tese pode ser proposta, aprovada, refinada ou rejeitada apenas quando o
usuário ou agente responsável declarar o status. Hipótese do conselho ou do
crítico não vira tese automaticamente.

## Pedidos

Pedidos podem ser registrados como objetos com `id`, `tipo`, `texto`, `status`,
`source_ids`, `localizacao` e `origem`. O comparador pode verificar presença,
ordem, duplicidade e vínculo com bloco identificado, mas não decide se o pedido
é cabível ou suficiente.

## Riscos

Risco é saída declarada, nunca classificação inferida por palavras ou tipo de
processo. Se houver nível (`alto`, `medio`, `baixo`), ele deve ter sido
fornecido explicitamente. Caso contrário, o registro conserva `nivel: null` e
pode ficar `pendente`.

```json
{
  "id": "RISK-1",
  "descricao": "Risco explicitamente apontado",
  "nivel": null,
  "status": "pendente",
  "thesis_ids": ["T-1"],
  "origem": "critico-rdaa"
}
```

## Decisões

Uma decisão pode conter `alternativa`, `texto`, `evidence_pivot_ids`, `next_step`,
`status` e `origem`. O sistema pode conferir identidade e isolamento da matéria,
mas não escolhe alternativa nem calcula probabilidade sem saída explícita do
conselho.

## Revisão semântica objetiva

A revisão pode produzir registros com `id`, `kind`, `severity`, `message`,
`localizacao`, `entity_ids`, `requires_human_review` e `status`. Exemplos de
achados comparáveis sem julgamento jurídico:

| Achado | Resultado |
|---|---|
| Fonte citada com ID inexistente | erro objetivo de referência |
| Número de processo divergente | erro objetivo de identidade |
| Tese/pedido declarado sem vínculo identificado | pendência de rastreabilidade |
| Pedido repetido | alerta de possível duplicidade |
| Risco ou tese sem origem explícita | violação de contrato |
| Informação dependente dos autos | `[PONTO A CONFERIR]` |

Erros objetivos de identidade ou referência impossível podem bloquear publicação.
Achados que dependem de juízo jurídico são alertas ou pendências e nunca podem
bloquear por decisão automática.

## Ciclos e reversibilidade

Cada achado tem ID estável. O mesmo achado reaparecendo sem mudança relevante não
deve disparar rodada infinita; o coordenador registra a repetição e aplica o
limite definido para a matéria.

A ausência dos novos campos não invalida contextos antigos. A implementação é
local, reversível e compatível com o gate, backup e substituição atômica do DOCX.
