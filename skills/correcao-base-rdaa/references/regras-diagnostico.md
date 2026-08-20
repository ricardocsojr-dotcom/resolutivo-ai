# Regras de diagnóstico da base (Resolutivo / CPJ-3C)

Estas regras foram desenvolvidas e validadas com Ricardo em cima da base real
do escritório. Se uma nova exportação do CPJ-3C mudar nomes de coluna ou
padrões de preenchimento, ajuste aqui e no script — não decida sozinho que um
achado "não faz sentido" sem confirmar com o usuário primeiro.

## 1. Classificação jurídica de "recurso"

Uma "Ação" é tratada como **recurso** (no sentido técnico do CPC, art. 994) se
o texto contiver, normalizado (minúsculo, sem acento):

- agravo de instrumento, agravo interno, agravo regimental
- agravo em recurso especial, agravo (em) recurso extraordinário
- apelação, recurso de apelação
- embargos de declaração
- embargos infringentes
- recurso especial, recurso extraordinário, recurso inominado, recurso ordinário
- pedido de concessão de efeito suspensivo (REsp/RExt) — recurso-adjacente, mas tratado como recurso porque só existe em função de um recurso pendente

**Deliberadamente excluídos** (são ações ou incidentes autônomos, não recursos,
mesmo contendo palavras parecidas):

- Embargos à Execução — defesa autônoma em execução, gera novo mérito
- Embargos de Terceiro — ação autônoma
- Impugnação a crédito habilitado — incidente em falência/recuperação judicial
- Conflito de Competência — incidente processual próprio (CPC art. 951+)
- Incidente de Desconsideração de Personalidade Jurídica — incidente
- Ação Rescisória — ação autônoma para desconstituir coisa julgada, não recurso

Se aparecer uma "Ação" nova que pareça um recurso mas não está na lista, ou que
esteja na lista mas semanticamente não seja (revise caso a caso), atualize
`RECURSO_PATTERNS` no script e explique a mudança ao usuário.

## 2. "Recurso solto" (sem processo de origem rastreável)

Ideia: se um registro é um recurso, deveria existir em algum lugar da base o
registro do processo de origem (a ação/execução/cumprimento de sentença que
deu causa ao recurso). Se não existir, a hipótese mais provável é que o
processo de origem foi arquivado/baixado e não ficou rastreado na base, ou
que a vinculação nunca foi feita — em qualquer caso, é um sinal de alerta que
merece checagem manual, não uma correção automática.

Um recurso é considerado "solto" quando **nenhuma** das checagens abaixo
encontra um "parceiro" de origem:

- **Por número do processo**: existe outro registro com o MESMO "Número do
  processo" cuja Ação não é recurso (ação de origem), OU cuja Instância = "1"?
  (cobre o caso comum de Apelação/Embargos de Declaração, que mantêm o mesmo
  número da ação de origem no primeiro grau)
- **Por Ficha**: existe outro registro na MESMA "Ficha" cuja Ação não é
  recurso, OU cuja Instância = "1"? (cobre o padrão legado de sub-fichas
  `.00`/`.01`/`.02` descrito no SKILL.md)

Se **nenhuma** das duas encontra parceiro, o registro é "solto". Isso é
intencionalmente mais permissivo que checar só por Ficha ou só por número —
testar com apenas uma das duas chaves gerou falsos positivos (casos onde a
origem existia, só que vinculada pela outra chave).

**Não generalize demais**: essa heurística cobre os dois padrões observados
na base do Resolutivo. Se o usuário mencionar um terceiro padrão de
vinculação (por exemplo, um campo textual que referencia o processo de
origem), incorpore como uma terceira checagem em vez de substituir as
existentes.

## 3. Inconsistência Status × Fase Processual

O campo "Localizador" guarda o status operacional (ATIVO, ARQUIVADO,
ATI-EST, SUSPENSO, HONORÁRIOS, ACOMPANHAMENTO, WATCHDOG...). O campo "Fase
Processual" é mais granular (Instrução, Recurso, Cumprimento de Sentença,
Arquivado, Arquivado Provisoriamente...). Os dois deveriam ser coerentes: se
a Fase diz "Arquivado", o Status também deveria dizer isso. Quando não
batem, é sinal de que um dos dois campos não foi atualizado.

## 4. Ação / Cliente / Polo

- **Ação em branco**: o tipo de peça não foi preenchido — sem isso, não dá
  para classificar o registro como recurso ou não, nem entender o que é o
  processo.
- **Cliente em branco**: falta identificar quem é o cliente do escritório
  naquele processo.
- **Polo do cliente**: compara o nome do Cliente (normalizado: maiúsculo, sem
  acento/pontuação, sem sufixos societários como LTDA/S.A./ME) contra Autor e
  Réu, por substring nos dois sentidos. Resultados possíveis: AUTOR, RÉU,
  AMBÍGUO (bate com os dois — checar homônimo), NÃO IDENTIFICADO (não bate
  com nenhum). "Não identificado" não é necessariamente erro: pode ser um
  terceiro interessado, credor por endosso, ou o próprio escritório figurando
  como parte processual (ex.: disputa de honorários) — sinalize para revisão
  humana, não assuma erro de cadastro.

## 5. Qualidade do Resumo/Assunto

- **Branco**: sem conteúdo.
- **Muito curto / sem conteúdo útil**: menos de 20 caracteres — normalmente é
  sinal de que alguém preencheu um valor monetário solto, um código interno
  (GCPJ...), ou uma frase que não descreve o caso (ex.: "A Calu é credor",
  "Sem acesso.").
- **Placeholder**: o texto só repete "[Recurso] <número do processo>", sem
  agregar informação.

Note que o mesmo critério de "muito curto" **não** se aplica ao campo
"Situação atual" — ali frases curtas como "Aguardando sentença" ou "Aguarda
decisão" são normais e úteis; só o branco é tratado como problema nesse
campo.

## 6. Campos críticos em branco (mutirão)

Risco, Situação atual e Fase Processual em branco não geram um achado linha a
linha (o volume é grande — historicamente mais de 50% da base) — são
reportados como contagem total e por advogado responsável, para orientar um
mutirão de preenchimento, não uma lista de revisão individual.
