---
name: previsao-condenacao-rdaa
description: >-
  Executa uma análise estruturada de provisão pré-sentença somente quando Ricardo
  pedir explicitamente previsão ou estimativa e o contexto declarar
  `modo: previsao_condenacao`. Separa entradas jurídicas, cálculo determinístico,
  fontes opcionais e limitações. Não infere risco, não consulta vault, CNJ,
  DataJud ou Jusbrasil automaticamente e não substitui a análise jurídica do
  advogado. Se já houver sentença ou acórdão, use `analise-provisao-rdaa`.
---

# Previsão de Condenação — RDAA

## Contrato de integração com o RDAA

Esta skill é um módulo de análise sob demanda e não uma etapa automática da
redação de peças. Ela só pode ser ativada por pedido explícito e por um contexto
operacional que declare `modo: previsao_condenacao`. O resultado deve ser tratado
como estimativa de trabalho, com limitações visíveis, e não como previsão certa,
probabilidade estatística ou decisão jurídica.

A classificação de risco de cada pedido é uma entrada estruturada que deve estar
justificada por prova ou fato identificado. O script `liquidar_pedidos.py` apenas
normaliza a entrada, calcula meses, soma valores e aplica o percentual fornecido.
Ele não escolhe `provavel`, `possivel` ou `remoto`, não lê texto livre e não
avalia pertinência jurídica.

Vault, Jusbrasil e qualquer outra fonte externa são opcionais e só podem ser
usados quando Ricardo autorizar a fonte na execução. Se houver consulta externa,
registre origem, localização, trecho, data, finalidade e limitações em provenance.
Nenhuma consulta ou gravação no vault ocorre automaticamente.

O relatório não publica DOCX nem altera o estado confirmado da matéria. Se um
resultado for usado em uma peça, ele volta ao esqueleto, à revisão semântica e à
publicação protegida do RDAA.

## Por que esta skill existe

Ricardo já tentou isso antes com quatro prompts diferentes (`Modelo 1` a `Modelo 4`, na
pasta "Previsão de Condenação"). Todos tinham a mesma estrutura de 4 etapas (qualificação
de risco → liquidação → provisão pré-sentença → provisão recursal) e essa estrutura era
boa. O problema não era a estrutura — era que duas partes do processo foram delegadas a
texto livre do modelo, que é não-determinístico por natureza:

1. **Cálculo de juros/correção "de cabeça"** — cada rodada arredondava/estimava diferente.
2. **Jurisprudência citada de memória** — sem fonte real, o modelo ora lembrava, ora
   inventava, ora esquecia um precedente que tinha citado na rodada anterior.

Esta skill resolve isso não escrevendo um prompt "melhor", mas tirando essas duas partes
da prosa: cálculo vai para um script Python determinístico, e jurisprudência/histórico do
réu vem de busca real no Jusbrasil em vez de memória do modelo. A única coisa que continua
sendo julgamento jurídico — como deve ser — é a leitura da prova e a qualificação do risco
de cada pedido.

**Nota de versão**: a primeira versão desta skill usava o DataJud (CNJ) para calibrar a
probabilidade pelo histórico do réu. Foi removido depois do primeiro teste real — o DataJud
público é um índice *por tribunal* (não existe busca nacional num único request), a busca
por nome de parte exige correspondência bem exata, e um réu litigante nacional (ex.: uma
empresa com clientes em vários estados) fica sub-amostrado se a busca ficar presa ao
tribunal do caso em análise. Testado com um réu real, retornou zero em 4 tentativas
(nome variando, 3 tribunais diferentes) — não é um caso isolado de "não achou", é a
ferramenta errada para isso. O Jusbrasil (que já cobre múltiplos tribunais numa busca só e
provou funcionar bem nos testes) assumiu o papel de fonte de histórico do réu, não só de
jurisprudência de valor — ver Etapa 2 abaixo.

**Limitação atual, seja transparente sobre ela**: o escritório ainda não tem um histórico
próprio de condenações. Enquanto isso não existir, o valor de pedidos ilíquidos (dano
moral, por exemplo) se apoia em jurisprudência pública — que é mais rasa que um histórico
interno de casos já decididos pela própria carteira. Quando esse histórico existir, ele
deve ser consultado *antes* da jurisprudência pública para qualquer pedido semelhante já
visto pelo escritório.

## Fluxo obrigatório

### Etapa 1 — Leitura e qualificação dos pedidos

Leia a petição inicial (e a contestação, se houver). Para cada pedido, explícito ou
implícito, registre: tipo (dano material, dano moral, lucros cessantes, repetição de
indébito, outro), valor pleiteado, período de incidência se houver, e as provas
apresentadas de cada lado.

Classifique o risco de cada pedido usando a matriz objetiva em
`references/metodologia-previsao-condenacao.md` (seção "Matriz de risco por prova") — ela
existe para que a mesma prova sempre gere a mesma classificação, rodada após rodada. Nunca
classifique como "possível" ou "provável" sem apontar o documento/fato específico que
sustenta a classificação — é a mesma exigência de rastreabilidade que o resto do padrão
RDAA já cobra.

### Etapa 1.5 — Histórico interno do escritório, somente se autorizado

A consulta ao vault não é automática. Só use o histórico interno se Ricardo
autorizar a fonte na execução e se o contexto fornecer o caminho válido. Quando
usado, registre que se trata de informação interna, sua localização e a diferença
entre dado informado, conferência operacional e conclusão jurídica.

Se não houver autorização ou registro interno aplicável, declare a ausência e
continue apenas com as entradas e fontes explicitamente aprovadas. Não crie
registro no vault ao final e não trate um caso como candidato a gravação futura
sem solicitação separada.

### Etapa 2 — Jusbrasil, somente se autorizado

Esta etapa só pode ser executada quando Ricardo autorizar explicitamente o
Jusbrasil na execução e houver sessão disponível. A busca não é presumida pela
existência de um processo ou de um nome de réu. Registre a autorização, a URL,
a data, a consulta usada, o resultado observado e as limitações antes de usar
qualquer item no relatório.

Uma busca só, duas perguntas. O Jusbrasil cobre múltiplos tribunais de uma vez (ao
contrário do DataJud, que é um índice por tribunal) — por isso ele serve tanto para
calibrar a PROBABILIDADE (histórico do réu) quanto para fundamentar o VALOR (jurisprudência
do tipo de pedido).

**a) Histórico do réu.** Use `mcp__Claude_in_Chrome__navigate` para
`https://www.jusbrasil.com.br/acompanhamentos/processos` (com a extensão do Chrome
conectada e o usuário logado no Jusbrasil) e pesquise o **nome ou CNPJ do réu** na caixa de
busca ("Digite um CPF, CNPJ, nome ou número") — não o nome combinado com o autor deste caso
especificamente, e não restrito ao tribunal da comarca do processo em análise. Essa página
lista os processos reais daquele réu **agregados de vários tribunais numa busca só**
(testado: um réu apareceu com processos em TJMG, TJSP e TJPR ao mesmo tempo), com status
(Encerrado/Em andamento/Arquivado), tribunal e matéria — é um nível de cobertura que nem o
DataJud (preso a um tribunal por consulta) nem a busca de jurisprudência (só ementas de
2ª instância) davam sozinhos.

Cuidado com desambiguação: réus com nome de marca conhecida costumam ter várias pessoas
jurídicas distintas (franquias/regionais) com CNPJs diferentes sob o mesmo nome — confirme
que o CNPJ encontrado é o mesmo réu do processo em análise (ou, se for do mesmo grupo
econômico mas CNPJ diferente, registre isso explicitamente em vez de tratar como o mesmo
réu). Para cada processo relevante (mesmo assunto do caso em análise), clique em "Ver
processo" e leia o histórico de andamentos — ele traz **datas reais** de cada evento
(inclusive, quando disponível, arquivamento/decisão final), o que também alimenta a idade
processual empírica da Etapa 4 (correção monetária), não só a taxa de procedência.

Registre quantos processos foram localizados, o desfecho de cada um (procedente,
improcedente, acordo, arquivado) e calcule uma **taxa empírica de procedência** sobre essa
amostra. Trate isso como evidência de peso na Camada B (qualitativa) da matriz de risco,
não como substituto da análise das provas do caso concreto. **Sempre declare o tamanho da
amostra** (não é a mesma coisa dizer "6 de 8" e "6 de 200") e nunca apresente a taxa como
probabilidade estatisticamente robusta — é um indício real, não uma certeza. Se a busca não
retornar nada relevante para
aquele réu, diga isso explicitamente e siga só com a Etapa 1 — não invente uma taxa.

**b) Jurisprudência de valor.** Antes da busca ao vivo, veja a tabela "Valores de
referência externos (Jus IA)" em `references/metodologia-previsao-condenacao.md` — ela dá
uma faixa de sanidade rápida para os tipos de pedido que já são matéria do escritório
(negativação indevida, protesto indevido, repetição de indébito). Ela é um piso de
qualidade quando não há nada melhor, não um substituto da busca ao vivo. Para pedidos
ilíquidos (dano moral, principalmente), use `buscar-jurisprudencia` para trazer ementas
literais de casos com fatos análogos, preferencialmente do mesmo tribunal/comarca. Use o
valor de condenação citado nessas ementas como referência — nunca "lembre" um valor médio
de jurisprudência sem essa busca. Se as ementas trouxerem valores divergentes, apresente o
intervalo (não uma média forçada) e justifique qual ponto do intervalo é mais aplicável ao
caso concreto, com base na gravidade/prova.

**Antes de comparar, traga cada valor citado para o valor presente.** Uma ementa de 2023
e uma de 2025 não são comparáveis em R$ nominal — rode cada valor de referência pela skill
`calculo-judicial` (data-base = data da decisão citada na ementa, data final = hoje) antes
de colocá-los lado a lado ou de usá-los como âncora do valor a provisionar. Sem isso, o
intervalo de referência fica artificialmente distorcido a favor do precedente mais antigo.

### Etapa 3 — Liquidação determinística

Pedidos com período e valor definidos (repetição de indébito, lucros cessantes) NUNCA
devem ser somados em prosa. Preencha um JSON estruturado e rode:

```
python scripts/liquidar_pedidos.py pedidos.json
```

Veja o cabeçalho do script para o formato exato do JSON. O script devolve o valor
liquidado por pedido e a provisão ponderada (valor × percentual de risco definido na
Etapa 1) — sem arredondamento livre do modelo.

### Etapa 4 — Provisão financeira (atualização monetária)

Para atualizar qualquer valor no tempo (correção monetária, juros), use a skill
`calculo-judicial` — não estime SELIC, IPCA ou qualquer índice de cabeça, mesmo que pareça
"só uma aproximação rápida". É exatamente esse tipo de atalho que gerava respostas
diferentes a cada rodada nos modelos antigos. Informe a `calculo-judicial` a data de início
(ajuizamento ou data do evento danoso, conforme o pedido) e a data final (hoje, ou a data
estimada de desembolso — ver `references/metodologia-previsao-condenacao.md` para prazos
médios de tramitação por rito).

Se já houver sentença (situação de borda — normalmente isso já seria caso de
`analise-provisao-rdaa`), acrescente honorários de sucumbência e a multa do art. 523 do
CPC conforme as regras em `references/metodologia-previsao-condenacao.md`.

### Etapa 5 — Relatório final

Use este formato:

```
## 1. Resumo do caso
Comarca/Vara | Réu | Valor da causa | Fase atual

## 2. Tabela de pedidos
Pedido | Período | Valor liquidado | Risco (%) | Fundamento da classificação

## 3. Histórico interno do escritório (vault)
[casos do mesmo réu/tipo de pedido já registrados em wiki/processos/, ou "réu/pedido
ainda não visto no vault — este caso é candidato a registro futuro"]

## 4. Histórico do réu e jurisprudência de referência (Jusbrasil)
Histórico do réu: amostra de N processos localizados | desfecho observado | taxa empírica
de procedência [ou: "réu não localizado nas buscas — sem taxa"]
Jurisprudência de valor: [ementas citadas, com valor e link — ver formato de
buscar-jurisprudencia]

## 5. Provisão financeira sugerida
Valor liquidado total | Atualização monetária (índice e período usados) | Provisão
ponderada | TOTAL

## 6. Limitações desta análise
[o que não pôde ser confirmado, amostra pequena, ausência de histórico interno, etc.]
```

A seção 6 não é opcional — se alguma informação foi assumida por falta de dado melhor,
diga isso explicitamente em vez de apresentar o número final como se fosse mais preciso do
que realmente é.

## Quando esta skill não é a certa

- Processo já tem sentença ou acórdão → `analise-provisao-rdaa` (double-check de
  classificação já em andamento).
- Só precisa da ementa/precedente, sem montar provisão → `buscar-jurisprudencia`.
- Só precisa atualizar um valor entre duas datas → `calculo-judicial`.
- Cadastro da base (Resolutivo/CPJ-3C) com problema estrutural → `correcao-base-rdaa`
  primeiro, depois volte para cá se for o caso.
