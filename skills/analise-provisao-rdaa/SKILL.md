---
name: analise-provisao-rdaa
description: >-
  Classifica risco processual (provável, possível, remoto) e estima contingência/provisão para processos do
  contencioso do escritório Romano Donadel, cruzando a árvore institucional por estágio processual com o
  critério de auditoria CPC 25/NBC TG 25 (rastreabilidade, separação entre fato e avaliação). Funciona como
  um double-check — recebe a classificação e a justificativa que o usuário já sugeriu e devolve uma segunda
  opinião fundamentada, sinalizando concordância ou divergência. Use SEMPRE que Ricardo pedir análise de
  provisão, quanto devemos provisionar, para classificar o risco de um processo, para fazer o double check
  de uma provisão, risco provável ou possível, passivo contingente, algo de CPC 25/NBC TG 25, ou revisar a
  classificação de risco de um cliente ou carteira de processos. Ative também quando enviar uma lista de
  processos com a classificação atual pedindo para conferir se está certa.
---

# Análise de Provisão — RDAA (double-check de risco processual)

## O que este skill faz

Aplica a metodologia de classificação de risco (provável/possível/remoto) e
estimativa de contingência definida por Ricardo para o setor Resolutivo, e
devolve uma segunda opinião fundamentada sobre a classificação que o próprio
usuário sugeriu — apontando concordância ou divergência com justificativa
objetiva. **Não decide a provisão contábil** — isso é do cliente/contabilidade
(CPC 25/NBC TG 25); este skill entrega o insumo jurídico.

Leia `references/metodologia-provisao.md` antes de classificar qualquer
processo — ele tem a árvore de decisão completa (b.1 a b.9, incluindo as
exceções b.3.1, b.7.1, b.8 e b.9), os critérios qualitativos de auditoria, os
quatro campos financeiros e os 17 campos mínimos que todo processo precisa
ter no relatório final.

## Antes de classificar: reunir os insumos mínimos

Para aplicar a metodologia com segurança, você precisa saber, por processo:

- Tipo de ação (para checar se cai em alguma exceção da árvore: b.7 —
  cumprimento de sentença, execução de título extrajudicial, execução
  fiscal — nasce como Provável; b.7.1 — ação monitória — nasce como
  Possível e escalona por revelia; b.9 — ação declaratória de inexistência
  de débito — cliente é autor mas pode ser economicamente passivo)
- Se o processo tramita em Juizado Especial (exceção b.3.1: sentença
  desfavorável eleva direto para Provável, sem aguardar acórdão)
- Se o caso foi resolvido por acordo com parcelamento (b.8): durante o
  cumprimento ativo a classificação é Remoto e o valor não entra na
  provisão jurídica; só há contingenciamento a partir da notícia de quebra
  do acordo, com base na multa específica do caso
- Fase processual atual e último andamento relevante
- Se já houve sentença/acórdão e qual foi o resultado (improcedente,
  procedente em parte, totalmente procedente)
- Se há recurso pendente ou já julgado, e o resultado
- Se houve trânsito em julgado
- Se há depósito judicial do valor ou garantia do débito sem pagamento
- Valor da causa e, se houver, valor da condenação líquido
- Provas relevantes: laudo pericial, jurisprudência aplicável, robustez
  documental — o que sustenta ou enfraquece a tese do cliente
- A classificação e a justificativa que o usuário já sugeriu (o "double
  check" compara contra isso)

Se faltar informação para aplicar a árvore com segurança, **não invente**.
Registre `[VERIFICAR: o que falta e por quê]` no campo de fundamento ou de
limitação, e pergunte ao usuário ou aponte a providência para obter o dado
(ex.: consultar andamento no tribunal, pedir cópia da sentença). Isso vale
tanto para a classificação de risco quanto para qualquer valor financeiro —
nunca preencha um valor de contingência arbitrário só para não deixar célula
vazia.

## Fluxo de trabalho

1. **Confirmar o escopo** com o usuário se não estiver claro: um processo
   específico, a carteira de um cliente, ou todos os processos passivos de
   uma certa fase/valor. Registre esse escopo como "materialidade" no
   relatório (ver `references/metodologia-provisao.md`).
2. **Para cada processo**, aplicar a Camada A (árvore b.1–b.9) para obter a
   classificação mecânica conforme o estágio processual, e depois a Camada B
   (critério de auditoria CPC 25) para verificar se as provas e a força da
   tese sustentam essa classificação ou sugerem ajuste. Documentar as duas
   coisas: onde a árvore colocaria o processo, e se a análise qualitativa
   confirma ou diverge disso.
3. **Comparar com a sugestão do usuário.** Se ele forneceu uma classificação
   e uma justificativa, preencha as colunas correspondentes e marque
   `Divergencia = Sim` sempre que sua conclusão (double-check) não coincidir
   com a dele — mesmo que a diferença seja sutil (ex.: ele disse "possível"
   sem qualificar o grau de incerteza, você identificou elementos que
   apontam para "provável"). A divergência é o produto principal deste
   skill — não a esconda para "concordar por cortesia".
4. **Calcular os quatro campos financeiros** (valor da causa, valor
   econômico envolvido, valor de contingência, valor provisionável) conforme
   a metodologia — nunca copiar automaticamente o valor da causa como valor
   de contingência a partir do momento em que há elementos melhores (sentença,
   acórdão, depósito, garantia).
5. **Montar o CSV** com uma linha por processo, usando exatamente os nomes de
   coluna documentados no cabeçalho de `scripts/montar_planilha_provisao.py`
   (rode `head -35 scripts/montar_planilha_provisao.py` para ver a lista).
   Preencha os 17 campos mínimos (ver referência) mais as colunas de
   double-check.
6. **Gerar a planilha final**:
   ```bash
   python scripts/montar_planilha_provisao.py <analise.csv> <saida.xlsx>
   ```
   O script formata a planilha, colore por classificação de risco
   (Provável/Possível/Remoto) e destaca em vermelho as linhas com
   divergência, além de somar o valor provisionável e contar divergências
   via fórmulas na aba "Resumo".
7. **Recalcular fórmulas** com o script `recalc.py` da skill **xlsx** e
   confirmar `total_errors: 0` antes de entregar.
8. **Apresentar ao usuário liderando pelas divergências** — não pela lista
   completa. Ex.: "de N processos, M concordam com sua classificação; nos
   outros P, o double-check aponta [razão específica]". Separe claramente,
   na sua fala, o que é fato processual, o que é sua avaliação jurídica, e o
   que é recomendação — mesma exigência que vale dentro da planilha.

## Regras de redação herdadas do padrão RDAA

Este skill compartilha a postura analítica da skill `contencioso-rdaa`:
nunca inventar jurisprudência, fatos ou resultados de julgamento — se não
tiver certeza sobre o desfecho de um recurso ou sentença, sinalize
`[VERIFICAR: ...]` em vez de presumir. Cada classificação de risco deve ter
fundamento objetivo e rastreável (decisão, documento, prova, laudo, tese
jurisprudencial) — nunca "possível" ou "provável" sem explicar por quê.

## Quando este skill não é o certo

Se o pedido for sobre qualidade de cadastro da base (campos em branco,
recursos sem processo de origem rastreável, inconsistências de status), isso
é trabalho do skill **correcao-base-rdaa**, não deste. Rode primeiro a
correção da base se a base tiver problemas estruturais conhecidos — uma
análise de provisão em cima de dados de cadastro ruins (ex.: Fase Processual
errada) herda o erro.
