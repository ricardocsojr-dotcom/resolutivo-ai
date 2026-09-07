---
name: buscar-jurisprudencia
description: >
  Busca jurisprudência brasileira no Jusbrasil (ementas literais via extensão do Chrome). Use sempre que Ricardo pedir
  jurisprudência, precedente, ementa, entendimento dos tribunais, ou quando
  estiver redigindo uma peça e precisar de fundamento jurisprudencial. Ative
  com termos como "busca jurisprudência sobre", "me dá precedentes de",
  "qual o entendimento do STJ sobre", "acha ementa de", "preciso de
  jurisprudência para esta peça", ou qualquer variação que indique pesquisa
  jurisprudencial para fundamentação de peça processual.
---

# Busca de Jurisprudência — RDAA

Fluxo: consulta ao índice temático do cérebro primeiro, Jusbrasil (fonte
primária) só para o que faltar.

## Etapa 0 — Índice temático do cérebro (sempre primeiro)

Antes de qualquer busca externa, consulte o índice de fontes já verificadas:

```text
py -3.14 skills/buscar-jurisprudencia/scripts/indexador_fontes.py buscar "<tema/tese>" --limit 5
```

É busca por tema (FTS5/BM25), não por domínio — não depende de acertar qual
`wiki/domains/*.md` a tese pertence, e cobre teses ainda não catalogadas em
nenhum domínio. Se retornar ementa aderente à tese atual, reaproveite-a
(mesmo `source_id`, ementa já literal e verificada) em vez de buscar de novo
no Jusbrasil — evita repetir a etapa mais lenta do processo (conferência de
literalidade). Se o índice não existir ou estiver desatualizado, reconstrua
com `reindex` antes de assumir que não há resultado:

```text
py -3.14 skills/buscar-jurisprudencia/scripts/indexador_fontes.py reindex
```

Avalie a aderência real do resultado à tese atual antes de reaproveitar —
ementa parecida por palavra-chave não é o mesmo que ementa aderente ao fato
concreto. **Além disso, respeite o objeto `revisao` retornado pelo índice:**

- `vigente` + `automatic_reuse: true`: pode ser reaproveitada, desde que
  aderente ao caso;
- `revisao_vencida`, `sem_prazo` ou `data_invalida`: é apenas candidata;
  confirme se ainda representa o entendimento atual antes de citá-la;
- toda fonte nova recebe revisão em **365 dias**. O precedente não "expira";
  após esse prazo, vence apenas a autorização para reutilização automática.

Na dúvida, trate como candidata e confirme como faria com um resultado novo do Jusbrasil.

## Etapa 1 — Jusbrasil (fonte primária, para o que não foi encontrado)

Use a skill `jusbrasil-jurisprudencia` para buscar e retornar as ementas
literais. Essa é a fonte principal — o usuário precisa do texto exato para
citar na peça.

Parâmetros padrão:
- **Quantidade**: 3 ementas (salvo pedido diferente)
- **Tribunal preferencial**: STJ primeiro; se não houver, TJSP
- **Saída**: ementa literal + tribunal + processo + relator + data + URL

## Etapa 2 — DataJud (contexto quantitativo, opcional)

**Removida.** Não há consulta ao DataJud/DJEN — não tente
`buscar_processos_por_assunto` nem qualquer consulta processual automática.
Se Ricardo quiser volume/dados estatísticos de processos sobre o tema,
informe que essa capacidade não existe e a verificação deve ser manual.

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

## Registro imediato no cérebro (não espera publicação)

Além do registro acima (estado local, por matéria), toda ementa nova
confirmada na Etapa 1 — não encontrada na Etapa 0 — deve ir para o cérebro
imediatamente, sem esperar a matéria publicar:

```text
py -3.14 skills/buscar-jurisprudencia/scripts/registrar_fonte_verificada.py \
  --tribunal "..." --numero-processo "..." --relator "..." --data-julgamento "..." \
  --url "..." --tema "<tese/tema, usado na busca futura>" --matter-id "<matter_id>" \
  --review-days 365 --ementa-literal "<ementa literal completa>"
```

`--review-days` é 365 por padrão e só deve ser alterado por decisão consciente

Isso existe porque a matéria pode travar, pausar ou nunca publicar — mas a
ementa já verificada é conhecimento válido independente do destino da peça, e
não deveria evaporar junto. O script indexa a fonte automaticamente para a
Etapa 0 encontrá-la em buscas futuras. Vinculação a domínio/conceito continua
sendo feita depois, se e quando a matéria virar estudo publicado (fluxo de
`estudo-juridico-rdaa`); este passo cobre só a fonte, o mais urgente. Não
repita aqui uma ementa que a Etapa 0 já trouxe do índice.

Antes de redigir ou revisar, o orquestrador monta um pacote `redator`, `critico`
ou `revisor` para a mesma matéria. O pacote contém somente as fontes e fatos
necessários à tarefa; não é necessário repassar o provenance inteiro.
