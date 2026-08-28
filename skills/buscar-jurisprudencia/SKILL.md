---
name: buscar-jurisprudencia
description: >
  Busca jurisprudência brasileira para fundamentar peças processuais do RDAA.
  Combina duas fontes: Jusbrasil (ementas literais via extensão do Chrome) e
  DataJud/CNJ (metadados processuais). Use sempre que Ricardo pedir
  jurisprudência, precedente, ementa, entendimento dos tribunais, ou quando
  estiver redigindo uma peça e precisar de fundamento jurisprudencial. Ative
  com termos como "busca jurisprudência sobre", "me dá precedentes de",
  "qual o entendimento do STJ sobre", "acha ementa de", "preciso de
  jurisprudência para esta peça", ou qualquer variação que indique pesquisa
  jurisprudencial para fundamentação de peça processual.
---

# Busca de Jurisprudência — RDAA

Fluxo integrado: Jusbrasil (ementa literal) + DataJud (volume/contexto).

## Etapa 1 — Jusbrasil (fonte primária)

Use a skill `jusbrasil-jurisprudencia` para buscar e retornar as ementas
literais. Essa é a fonte principal — o usuário precisa do texto exato para
citar na peça.

Parâmetros padrão:
- **Quantidade**: 3 ementas (salvo pedido diferente)
- **Tribunal preferencial**: STJ primeiro; se não houver, TJSP
- **Saída**: ementa literal + tribunal + processo + relator + data + URL

## Etapa 2 — DataJud (contexto quantitativo, opcional)

**Desativada desde 2026-08-23** — o MCP `CNJ` (DataJud/DJEN) foi
desconectado (ver `CLAUDE.md`). Não tente `buscar_processos_por_assunto`
nem qualquer outra consulta ao DataJud automaticamente. Se Ricardo quiser
volume/dados estatísticos de processos sobre o tema, informe que a consulta
automática está desligada e a verificação deve ser manual.

## Formato de entrega

Para cada ementa, entregue também um identificador estável, a origem, a
localização, o uso pretendido e o estado de conferência.

---
**[TRIBUNAL] — [Número do processo]**
*Relator: [Nome] | Julgado em: [Data]*

> [EMENTA LITERAL]

Disponível em: [URL Jusbrasil]

`source_id` — [identificador estável]
`origem` — `buscar-jurisprudencia`
`uso` — [tese ou bloco provável]
`status` — `verificada_externamente`
`literalidade_confirmada` — `true`
`conferencia` — `fonte acessada no navegador, data se disponível e método usado

---

Ao final, se usou DataJud: *"Volume no [tribunal]: [N] processos encontrados
sobre o tema — demonstra reiteração do entendimento."*

## Regra de ouro

Nunca parafraseie a ementa. O usuário usa o texto para citar na peça —
qualquer alteração pode comprometer a citação formal.

## Registro no estado compartilhado

Depois de conferir cada resultado na fonte indicada, registre a ementa literal
no estado local da matéria usando `skills/revisor-rdaa/scripts/contexto_rdaa.py`.
O registro deve conservar tribunal, número do processo, relator, data, URL,
texto literal, origem, uso e os dados de conferência quando disponíveis. Use o
tipo `jurisprudencia` e o status automático da função `register_research`, que é
`verificada_externamente` somente porque esta etapa já declarou a conferência
externa.

Não registre como verificada uma ementa apenas copiada do histórico, do vault
ou de texto livre. Nesses casos, mantenha o registro como `informada` ou
`pendente` pelo fluxo de contexto. O ledger é auxiliar à resposta e não muda a
regra de nunca inventar ou parafrasear citação. Antes da redação, selecione os
`source_id` no esqueleto e vincule cada fonte ao bloco e ao uso pretendido.

Antes de redigir ou revisar, o orquestrador monta um pacote `redator`, `critico`
ou `revisor` para a mesma matéria. O pacote contém somente as fontes e fatos
necessários à tarefa; não é necessário repassar o provenance inteiro.
