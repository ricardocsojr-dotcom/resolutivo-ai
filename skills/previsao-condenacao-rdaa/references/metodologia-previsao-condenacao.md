# Metodologia de previsão de condenação (pré-sentença)

Este documento reúne o que aproveitar dos quatro prompts que Ricardo testou antes
(`Modelo 1` a `Modelo 4`), com uma diferença: aqui cada regra é para ser aplicada de forma
consistente todo caso, e não para o modelo "decidir na hora" com um número diferente a
cada leitura. Se uma regra abaixo não cobrir o caso concreto, sinalize
`[VERIFICAR: ...]` em vez de inventar uma exceção nova.

## Matriz de risco por prova

### Danos materiais
| Situação | Classificação | Provisão |
|---|---|---|
| Comprovante de pagamento/gasto + nexo causal documentado | Provável (100%) | Integral |
| Alegação plausível, sem prova robusta (ex.: relato + e-mail de cobrança, sem extrato) | Possível (50%) | Parcial, com nota explicativa |
| Ressarcimento já realizado pela ré, sem dano residual comprovado | Remoto (0%) | Sem provisão |

### Danos morais
| Situação | Classificação |
|---|---|
| Dano presumido por norma/súmula consolidada (ex.: negativação indevida) + prova do evento | Provável |
| Depende de prova de abalo efetivo, sem elemento objetivo nos autos | Possível |
| Mero aborrecimento sem repercussão, ou fato já sanado sem prova de abalo | Remoto |

### Lucros cessantes
| Situação | Classificação |
|---|---|
| Base de cálculo (faturamento/renda) documentada + nexo com a paralisação alegada | Provável |
| Base estimada sem documento comprobatório direto | Possível |
| Ausência de qualquer lastro documental | Remoto |

### Regra geral (herdada do padrão RDAA)
Toda classificação deve remeter a um documento, prova, laudo ou fato específico dos autos
— nunca "possível" ou "provável" sem justificativa objetiva rastreável. Quando a Etapa 2
(histórico do réu no Jusbrasil) trouxer uma taxa empírica que diverge da classificação pela
prova documental, registre as duas e explique por que uma pesa mais que a outra no caso
concreto — não troque uma pela outra silenciosamente.

## Valores de referência externos (Jus IA, levantamento 2026-07-29)

**Leia isto antes de usar os números abaixo.** Estes valores vieram de uma consulta ao
Jus IA (IA do Jusbrasil, base em jurisprudência pública — STJ/TJSP/TJRJ/TJMG, últimos 2-3
anos, 80 fontes) feita para calibrar a metodologia, não de um levantamento da carteira real
do escritório. Duas ressalvas obrigatórias:

1. **É mercado, não é o escritório.** São faixas que aparecem na jurisprudência pública em
   geral — não necessariamente refletem o perfil de réus, comarcas e varas com quem o RDAA
   realmente litiga. Se Ricardo autorizar o uso de histórico interno ou de pesquisa Jusbrasil
   e houver dado próprio registrado em provenance, esse dado pode ser comparado com a tabela
   abaixo. A tabela é referência auxiliar, não o teto nem uma conclusão automática.
2. **Nem todo tipo de pedido aqui listado é matéria do escritório hoje.** Peça abaixo por
   categoria, sinalizando o que é e o que não é aplicável à carteira atual.

### Aplicável à carteira atual (dano moral/consumidor, cobrança indevida)

| Tipo de pedido | STJ | TJSP | TJRJ | TJMG | Valor de referência típico |
|---|---|---|---|---|---|
| Dano moral — negativação/inscrição indevida (SPC/Serasa) | R$ 5.000–20.000 | R$ 5.000–20.000 | R$ 5.000–10.000 | R$ 8.000–12.000 | ~R$ 10.000 |
| Dano moral — protesto indevido de título | R$ 8.000–20.000 | R$ 10.000–20.000 | R$ 10.000–15.000 | R$ 10.000–20.000 | ~R$ 10.000–15.000 (mais alto se pessoa jurídica) |
| Repetição de indébito em dobro (cobrança indevida) | — não é faixa, é regra fixa: dobro do valor pago + correção + juros (art. 42, § único, CDC). Desde o EAREsp 676.608/RS (STJ, 2021), não depende mais de provar má-fé do fornecedor para pagamentos feitos após 30/03/2021. | | | | |

Fatores de variação (negativação e protesto seguem a mesma lógica — dano in re ipsa):
existência de negativações anteriores (Súmula 385/STJ pode afastar/reduzir a indenização);
tempo de permanência da inscrição/protesto indevido; porte econômico do ofensor; para
protesto de pessoa jurídica, impacto em crédito/licitações/reputação comercial pesa mais
que no caso de pessoa física.

### Fora da carteira atual do escritório — não aplicar sem confirmar antes

| Tipo de pedido | Por que está aqui mesmo assim |
|---|---|
| Dano moral por atraso/cancelamento de voo | O RDAA não atua em direito aeronáutico hoje. Mantido só como exemplo de como a mesma metodologia se aplicaria a outra matéria — **não usar como referência para os pedidos atuais da carteira**, e não reativar sem confirmar com Ricardo que o escritório passou a atuar nesse tipo de caso. |

Se aparecer um tipo de pedido que não está em nenhuma das duas tabelas acima, não
extrapole por analogia sem justificar — rode a Etapa 2 (Jusbrasil) normalmente para esse
caso específico.

## Idade processual (para estimar até quando corrigir)

**Estado atual — placeholder, ainda não calibrado com dado real**: usar como estimativa de
trabalho, nunca como fato, e sempre marcar como estimativa genérica no relatório:

- **Juizado Especial (JEC)**: cerca de 1 ano e 2 meses até a sentença + 3 meses de
  execução, salvo indício em contrário no processo (movimentação já mais adiantada, por
  exemplo).
- **Justiça Comum**: cerca de 3 anos e 7 meses até a sentença + 3 meses de execução.
- Se o processo já ultrapassou esses prazos nas movimentações reais, use a fase real
  observada, não a estimativa genérica.

**Roadmap (a desenhar com Ricardo)**: essa tabela é a parte mais fraca da metodologia hoje
— é uma média genérica nacional, não reflete o tribunal, a vara ou o tipo de ação
específicos do caso. A ideia original era usar a amostra do DataJud (data de ajuizamento +
data de desfecho de cada processo) para calcular uma **idade processual empírica** — mas o
DataJud foi removido da Etapa 2 (ver nota de versão no SKILL.md: índice por tribunal, sem
busca nacional, zero resultado em teste real). O Jusbrasil assumiu esse papel via
`jusbrasil.com.br/acompanhamentos/processos` (busca por nome/CNPJ do réu, agregando vários
tribunais) — testado e confirmado que o histórico de andamentos de cada processo individual
traz **datas reais** de cada evento (não só a ementa final), então a mesma amostra da Etapa
2a pode alimentar essa idade processual empírica. Pontos a decidir quando isso for
desenhado:
- Tamanho de amostra mínimo para uma média empírica substituir a genérica.
- Se a idade deve ser calculada por réu específico, por vara, ou por tribunal — cada corte
  tem trade-off entre relevância e tamanho de amostra.
- Como versionar/atualizar essa média ao longo do tempo (ela muda conforme o tribunal
  acelera ou represa julgamentos).
- Quando o escritório tiver histórico interno de casos encerrados (ver seção final deste
  documento), ele deve virar a fonte primária da idade processual — é o único lugar que já
  captura as duas datas de forma estruturada, sem depender de nenhuma fonte pública.

## Honorários e multa (só relevante se já houver sentença — caso de borda)

- Honorários de sucumbência: 10% a 20% sobre o valor da condenação, conforme complexidade
  e resistência da causa (art. 85, CPC).
- Multa do art. 523, CPC: 10% adicional se houver risco concreto de não pagamento
  voluntário no prazo de 15 dias após intimação para cumprimento.
- Custas de preparo recursal: incluir apenas se houver indício real de recurso
  (sucumbência relevante para a parte, valor expressivo).

Se o processo já tem sentença, isso normalmente é caso de `analise-provisao-rdaa`
(double-check de classificação de processo em andamento) — trate esta seção como exceção,
não como fluxo padrão desta skill.

## Por que não estimar SELIC "de cabeça"

Um dos modelos antigos tinha um atalho de "+22% para Justiça Comum, +11% para JEC" como
fallback quando não desse para calcular direito. Esse atalho é exatamente o tipo de coisa
que produz números diferentes cada vez que alguém pede a mesma análise — a "aproximação"
muda dependendo de como o modelo arredonda naquela rodada. A skill `calculo-judicial` já
resolve isso com tabela real (TJMG não expurgada por padrão, ou outro índice se indicado)
— use sempre ela, mesmo que pareça mais lento que uma conta rápida em prosa.

A mesma ferramenta serve para trazer valores de jurisprudência citados (Etapa 2 do
SKILL.md) a valor presente antes de comparar — um precedente de anos atrás em R$ nominal
não é comparável a um recente sem correção.

## Premissas locais conhecidas (exemplos — adicione as suas conforme forem confirmadas)

Estas são premissas que o escritório já usava informalmente nos modelos antigos. Trate-as
como ponto de partida, não como regra travada — cada uma deve ser reconfirmada/atualizada
por Ricardo com o tempo, e novas premissas devem ser adicionadas aqui à medida que forem
validadas em casos reais:

- **Trivale/Servnet/AGL**: jurisprudência da Comarca de Uberlândia/MG como fonte auxiliar
  de analogia fática (arranjos de pagamento, falha contratual, cobrança indevida) —
  aplicar só quando houver semelhança fática real com o caso concreto.
- **Encerramento unilateral de conta sem negativação (JEC)**: precedente de dano moral
  médio de R$ 1.500,00 em alguns tribunais (ex.: TJBA), salvo prova de abalo maior — mas
  sempre validar contra jurisprudência atual via `buscar-jurisprudencia`, porque
  entendimento de tribunal muda com o tempo e esse valor pode estar desatualizado.

## Histórico interno, somente quando autorizado

O histórico interno pode ser estruturado no futuro em um vault próprio, mas não é
consultado nem gravado automaticamente. Se Ricardo autorizar seu uso, registre cada
processo e pedido com origem, localização, desfecho, valor pleiteado e valor da
condenação, distinguindo dado informado de conclusão jurídica.

Enquanto não houver histórico autorizado e validado, declare a ausência no relatório.
Jurisprudência pública ou pesquisa Jusbrasil só pode complementar a análise quando a
fonte for autorizada na execução e registrada em provenance. Nenhum dado externo cria
por si só uma classificação de risco ou uma conclusão de provisão.
