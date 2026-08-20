---
name: calculo-judicial
description: >
  Calcula atualização monetária e juros de um valor entre duas datas, usando
  as tabelas de índice mantidas localmente e aprovadas no manifesto.
  Índice padrão é sempre TJMG não expurgada, salvo indicação em contrário do
  Ricardo. Use quando ele pedir cálculo de valor atualizado, correção
  monetária, juros de mora, ou informar data de correção/juros e valores
  pra atualizar. Não decide sozinho qual índice usar — isso é sempre
  indicado por quem pede o cálculo.
---

# Cálculo Judicial de Atualização — RDAA

Motor de cálculo de correção monetária + juros. Não decide regra jurídica
de qual índice cabe em cada situação — isso é decisão de quem pede o
cálculo. O padrão, na ausência de indicação, é **TJMG não expurgada**.

## Fonte dos índices

As tabelas ficam localmente em `referencias/indices/`, uma tabela por índice,
no formato CSV `data,valor`. A fonte de cada série deve ser registrada no
manifesto e, quando houver atualização, também em um pacote candidato de
proveniência. O [DrCalc](https://drcalc.net/consultaindices.asp) pode ser
usado como fonte secundária ou conferência. Para fonte primária, preferir o
tribunal ou órgão responsável pela série, como TJMG, TJSP, IBGE ou Banco
Central.

Os perfis iniciais ficam em `references/normalization_profiles.json` e são
apenas mapas técnicos. Perfil não significa aprovação da fonte ou da fórmula.
Os mapeamentos observados do TJMG e do TJSP ficam em
`references/fontes-oficiais-indices.md` e continuam com status candidato. O
atalho `scripts/preparar_fonte_candidata.py` recebe um perfil e um arquivo local
para repetir a preparação sem reescrever parâmetros no contexto do agente. Ele
não baixa a fonte, não promove o índice e não altera o manifesto.

Não há consulta automática ao vivo obrigatória. O Ricardo ou a equipe entrega
o arquivo bruto, planilha, CSV ou PDF, e a skill estrutura uma cópia local sem
alterar o original. O script `scripts/registrar_indice_candidato.py` valida o
CSV, calcula o SHA-256 e grava a proveniência, mas não modifica o manifesto nem
promove o índice para aprovado. Para fontes em XLS, XLSM ou PDF, usar
`scripts/normalizar_indice_candidato.py`. Após o caso dourado aprovado, usar
`scripts/promover_indice_aprovado.py` para escrever uma cópia do manifesto.
O manifesto de origem nunca é sobrescrito automaticamente. Esse promotor exige
proveniência, hashes, fórmula de referência, resultado esperado, resultado
observado, tolerância, responsável e data de aprovação. O candidato permanece
bloqueado se qualquer campo faltar. O normalizador exige mapeamento
explícito da aba e das colunas no Excel ou regex declarada com grupos `data` e
`valor` no PDF. Ele não executa macros, não usa OCR, não reordena registros,
não converte vírgula decimal silenciosamente e não altera o arquivo bruto.

Índices cobertos (confirmados em drcalc.net em 2026-07-19):

| Índice | Categoria no drcalc.net |
|---|---|
| TJMG não expurgada | Índices de Cálculos Judiciais |
| TJSP (INPC/IPCA-15) | Índices de Cálculos Judiciais |
| TJRJ | Índices de Cálculos Judiciais |
| Taxa Legal (art. 406 CC) | Índices de Cálculos Judiciais |
| INPC | Índices de Preços e Custos |
| IPCA | Índices de Preços e Custos |
| IGP-M | Índices de Preços e Custos |
| Selic acumulado mensal | Índices do Mercado Financeiro |
| CDI acumulado mensal | Índices do Mercado Financeiro |
| Poupança nova (após 04/05/2012) | Índices do Mercado Financeiro |

## Rotina de atualização

1. **Base histórica** — já estruturada em `referencias/indices/` com os
   arquivos locais de TJMG, TJSP, TJRJ, Taxa Legal, INPC, IPCA, IGP-M, Selic,
   CDI e Poupança nova. Esses arquivos não ficam automaticamente aprovados
   para o motor em homologação.
2. **Entrada de nova fonte** — receber o arquivo bruto baixado manualmente,
   registrar órgão, URL, competência, código da série e data de coleta, e
   preservar o original fora do CSV normalizado.
3. **Candidato local** — executar `registrar_indice_candidato.py` para
   validar cabeçalho, datas, ordem, duplicidades, valores e SHA-256. A saída
   será um JSON candidato. O script não consulta a internet, não altera o
   manifesto e não substitui o arquivo aprovado.
4. **Homologação** — comparar o candidato com um caso dourado conferido pelo
   escritório. Somente depois dessa comparação o manifesto poderá receber
   `status: aprovado` e a convenção correspondente.
5. Se faltar o mês mais recente na tabela local, bloquear ou avisar antes de
   calcular. Não adivinhar, interpolar ou preencher ausência com zero.

## Cobertura atual das tabelas locais (atualizado em 2026-08-17)

| Arquivo | Período | Frequência |
|---|---|---|
| `tjmg-nao-expurgada.csv` | 1990-01 a 2026-08 | mensal |
| `tjsp.csv` | 1990-01 a 2026-08 | mensal |
| `tjrj.csv` | 1990-01 a 2026-08 | mensal |
| `taxa-legal.csv` | 1995-03 a 2026-08 | diária |
| `inpc.csv` | 1990-01 a 2026-07 | mensal |
| `ipca.csv` | 1990-01 a 2026-07 | mensal |
| `igp-m.csv` | 1990-01 a 2026-07 | mensal |
| `selic.csv` | 1995-02 a 2026-07 | mensal |
| `cdi.csv` | 1990-01 a 2026-07 | mensal |
| `poupanca-nova.csv` | 2012-05 a 2026-08 (aniversários até 03/08) | por data de aniversário (diária) |

Taxa Legal de agosto/2026 foi rateada (acumulado mensal ÷ 31 dias) por falta
da série diária — confirmado com o Ricardo em 2026-08-17. Se a série diária
real do drcalc.net ficar disponível depois, substituir.

`poupanca-nova.csv` usa a data de início de cada período de aniversário
(regra da poupança: rende a cada mês a partir da data do depósito, não no
calendário) como coluna `data` — ao calcular poupança, use a data de
aniversário mais próxima da data de início informada, não o primeiro dia
do mês.

## Fluxo de cálculo

### 1. Coletar os parâmetros — sempre perguntados, nunca inferidos

- Valor principal
- Data de início da correção monetária
- Data de início dos juros (pode ser diferente da correção)
- Taxa de juros, se não for a padrão do índice escolhido
- Data final do cálculo (padrão: hoje)
- Índice — se não informado, usa TJMG não expurgada

### 2. Ler a tabela local do índice escolhido

Ler `referencias/indices/[indice].csv`. Se a tabela não tiver o mês mais
recente necessário, avisar antes de calcular — não interpolar nem estimar.

### 3. Calcular mês a mês

Aplicar o índice de cada mês sobre o saldo, do início ao fim do período.
Juros aplicados separadamente conforme a taxa informada, a partir da data de
início dos juros (que pode ser distinta da data de início da correção). Quando
houver mudança de taxa, usar `juros.tipo=simples_mensal_segmentado` com
segmentos contíguos, datas de início e fim, taxa, unidade, base e convenção.
O suporte preparatório aceita somente `percentual_mensal` em meses completos.
Taxa anual, pró-rata e mudança dentro do mês continuam bloqueadas até fórmula e
caso dourado aprovados. O contrato estrutural fica em
`references/juros-segmentados-schema.json`.


### 4. Entregar

- Planilha/tabela mês a mês (data, índice do mês, saldo corrigido)
- Valor final atualizado
- Índice usado e período coberto, explícitos no topo do resultado

Resultado pode alimentar a skill `perfil-csv` pra formatar no padrão que o
escritório já usa pra colar em outros sistemas.

## Template funcional local

O arquivo `references/template-calculo-rdaa.xlsx` é um template local sem macros,
sem links externos e sem dependência de serviços. Ele foi inspirado na
organização do template TJSP e nos modelos do escritório, mas separa entradas,
resultado do motor, catálogo de fontes, casos dourados e regras declaradas.

As abas são `Instruções`, `Resumo`, `Lançamentos`, `Segmentos de juros`,
`Índices`, `Casos dourados` e `Regras declaradas`. O template serve para
organizar a memória e a
conferência. Ele não escolhe índice nem cria regra jurídica automaticamente.
As linhas vazias começam sem status e o resumo considera uma memória sem
lançamentos como `candidato`, nunca como `aprovado`. O total de cada linha só
é preenchido quando o status da linha é explicitamente `aprovado`.

O script `scripts/renderizar_memoria_template.py` recebe um JSON com metadados,
lançamentos, resultados já calculados, fonte do índice, casos dourados e regras
declaradas. Ele copia o template, transporta os valores explícitos e salva uma
nova planilha. Não baixa dados, não recalcula a aritmética, não escolhe índice,
não aprova candidato e não altera o arquivo-base.

## Motor Python em homologação

Existe uma implementação local em `scripts/calculo_motor.py` com manifesto em
`references/index_manifest.json`. Ela ainda não é acionada pelo fluxo normal da
skill. Todas as séries do manifesto permanecem com status `pendente_validacao`,
portanto o motor bloqueia a execução real até que Ricardo forneça exemplos
dourados com fórmula, convenção de datas e resultado aprovado.

A implementação usa somente a biblioteca padrão, `Decimal`, CSV local e
SHA-256. Ela não busca índices externos, não escolhe índice, não interpola
meses ou dias ausentes, não decide termo inicial e não substitui o cálculo
atual. O modo resumido devolve JSON compacto e o modo detalhado devolve memória
de cálculo local somente quando solicitado.

A integração futura exigirá comparação documentada contra exemplos aprovados e
commit reversível. Até essa aprovação, a skill continua funcionando pelo fluxo
atual descrito acima, e o template permanece uma camada opcional de organização.

## O que esta skill não faz

Não decide qual índice é juridicamente correto pra uma situação (Selic ×
IPCA-E × TR, Fazenda × privado, antes/depois de mudança de regra). Isso é
sempre informado por quem pede o cálculo. Se pedirem cálculo sem informar
índice, usa o padrão (TJMG não expurgada) e avisa que está usando o padrão,
pra dar chance de correção antes de entregar o resultado.
