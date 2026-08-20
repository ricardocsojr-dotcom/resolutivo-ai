# Contrato de consulta processual opcional

## Regra principal

A presença de número de processo no contexto **não autoriza nem obriga**, por si
só, uma consulta ao CNJ/DataJud ou ao DJEN durante a redação de uma peça.

O fluxo padrão de `/redigir-peca` pode produzir a peça com os fatos fornecidos,
o ementário, a pesquisa jurisprudencial solicitada e a pesquisa legal necessária,
sem consultar andamento ou publicações externas.

> **CNJ/DataJud/DJEN são capacidades sob demanda, não etapas automáticas do
> fluxo de redação.**

## Gatilhos válidos

A consulta processual ou de publicações pode ser executada quando ocorrer pelo
menos uma destas situações explícitas:

| Situação | Consulta permitida |
|---|---|
| Ricardo pede andamento, movimentação, última decisão ou situação atual | `consultar-processo` com CNJ/DataJud |
| Ricardo pede publicação, intimação, prazo ou DJEN | DJEN/CNJ |
| Ricardo pede expressamente consulta externa no contexto da peça | Consulta indicada |
| Fluxo `/backoffice-diario` é invocado para abrir a agenda operacional | DJEN e DataJud, pois são a finalidade própria da skill |
| Ricardo pede volume estatístico ou reiteração quantitativa de processos | DataJud, pela etapa opcional de `buscar-jurisprudencia` |

A mera existência de número de processo, prazo mencionado, tipo de peça ou
nível A/B não é gatilho suficiente.

## O que permanece obrigatório no fluxo de redação

O orquestrador continua respeitando as regras já existentes para classificação
C/B/A, consulta ao vault, pesquisa jurisprudencial quando exigida pelo nível,
esqueleto com aprovação, redação, crítica, revisão e publicação protegida. A
consulta processual não é pré-requisito para executar essas etapas.

Se o documento depender de uma informação que somente o andamento externo pode
fornecer, o fluxo deve registrar uma pendência explícita, como `[PONTO A
CONFERIR]`, sem inventar o dado e sem consultar automaticamente.

## Preservação da capacidade

As skills `consultar-processo`, `backoffice-diario` e a etapa quantitativa de
`buscar-jurisprudencia` não são removidas. Quando forem chamadas pelo usuário ou
pelo fluxo operacional próprio, continuam podendo usar seus MCPs e registrar os
resultados no provenance local.

A consulta usada no backoffice diário permanece parte da rotina do próprio
backoffice porque essa skill existe justamente para verificar publicações e
prazos. Isso não torna a consulta obrigatória para redigir uma peça.

## Provenance

Quando uma consulta opcional for executada, seus metadados e resultados podem
ser registrados como `processo` ou `publicacao` com origem explícita. Quando a
consulta não for executada, o estado não deve criar registro fictício nem afirmar
que não houve movimentação; deve apenas permanecer sem esse resultado ou conter
pendência declarada.

## Custo e controle

A remoção da obrigatoriedade reduz chamadas externas e contexto repetido no
fluxo padrão. O usuário não precisa alterar sua forma de trabalho: basta pedir
a consulta quando quiser. Nenhum MCP, script ou skill é apagado, permitindo
rollback e uso futuro.
