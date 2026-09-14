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
atalho a automação provida pelo motor LangGraph recebe um perfil e um arquivo local
para repetir a preparação sem reescrever parâmetros no contexto do agente. Ele
não baixa a fonte, não promove o índice e não altera o manifesto.

Não há consulta automática ao vivo obrigatória. O Ricardo ou a equipe entrega
o arquivo bruto, planilha, CSV ou PDF, e a skill estrutura uma cópia local sem
alterar o original. O script a automação provida pelo motor LangGraph valida o
CSV, calcula o SHA-256 e grava a proveniência, mas não modifica o manifesto nem
promove o índice para aprovado. Para fontes em XLS, XLSM ou PDF, usar
a automação provida pelo motor LangGraph. Após o caso dourado aprovado, usar
a automação provida pelo motor LangGraph para escrever uma cópia do manifesto.
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
3. **Candidato local** — executar a automação provida pelo motor LangGraph para
   validar cabeçalho, datas, ordem, duplicidades, valores e SHA-256. A saída
   será um JSON candidato. O script não consulta a internet, não altera o
   manifesto e não substitui o arquivo aprovado.
4. **Homologação** — comparar o candidato com um caso dourado conferido pelo
   escritório. Somente depois dessa comparação o manifesto poderá receber
   `status: aprovado` e a convenção correspondente.
5. Se faltar o mês mais recente na tabela local, bloquear ou avisar antes de
   calcular. Não adivinhar, interpolar ou preencher ausência com zero.

## Cobertura atual das tabelas locais (atualizado em 2026-08-27)

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
| `poupanca-nova.csv` | 2012-05 a 2026-08 (aniversários até 26/08) | por data de aniversário (diária) |

`poupanca-nova.csv` usa a data de início de cada período de aniversário
(regra da poupança: rende a cada mês a partir da data do depósito, não no
calendário) como coluna `data` — a convenção `aniversario_deposito` exige que
`data_inicio_correcao` seja a própria data do depósito e `data_final` caia
exatamente num aniversário mensal seguinte (o motor projeta os ciclos
mensais a partir do início e recusa `data_final` fora do ciclo).

`taxa-legal.csv` armazena a fração diária pro rata já calculada (Selic
mensal menos IPCA-15 mensal do mês anterior, com piso zero, dividida pelos
dias do mês de referência — metodologia do BCB/CMN Resolução 5.171/2024) —
o mesmo valor se repete em todo dia corrido de um mesmo mês de referência.
A convenção `dias_corridos_semiaberto` soma (juros simples, sem
capitalização) os valores diários no intervalo **[data_inicio, data_final)**
— o dia final não entra na soma, ao contrário de todas as outras
convenções do motor, porque é assim que a própria Calculadora do Cidadão do
BCB conta os dias corridos.

## Fluxo de cálculo

### Coletar os parâmetros — sempre perguntados, nunca inferidos

- Valor principal
- Data de início da correção monetária
- Data de início dos juros (pode ser diferente da correção)
- Taxa de juros, se não for a padrão do índice escolhido
- Data final do cálculo (padrão: hoje)
- Índice — se não informado, usa TJMG não expurgada

### Ler a tabela local do índice escolhido

Ler `referencias/indices/[indice].csv`. Se a tabela não tiver o mês mais
recente necessário, avisar antes de calcular — não interpolar nem estimar.

### Calcular mês a mês

Aplicar o índice de cada mês sobre o saldo, do início ao fim do período.
Juros aplicados separadamente conforme a taxa informada, a partir da data de
início dos juros (que pode ser distinta da data de início da correção). Quando
houver mudança de taxa, usar `juros.tipo=simples_mensal_segmentado` com
segmentos contíguos, datas de início e fim, taxa, unidade, base e convenção.
O suporte preparatório aceita somente `percentual_mensal` em meses completos.
Taxa anual, pró-rata e mudança dentro do mês continuam bloqueadas até fórmula e
caso dourado aprovados. O contrato estrutural fica em
`references/juros-segmentados-schema.json`.


### Entregar

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

O script a automação provida pelo motor LangGraph recebe um JSON com metadados,
lançamentos, resultados já calculados, fonte do índice, casos dourados e regras
declaradas. Ele copia o template, transporta os valores explícitos e salva uma
nova planilha. Não baixa dados, não recalcula a aritmética, não escolhe índice,
não aprova candidato e não altera o arquivo-base.

**Template simples** (`references/template-calculo-simples-rdaa.xlsx` +
a automação provida pelo motor LangGraph, criado em 2026-08-27): pra casos
com um índice só e sem juros segmentados/múltiplos lançamentos complexos.
Uma aba `Cálculo` (uma linha por parcela, coluna `Tipo` = Principal,
Honorários ou Custas) + uma aba `Notas` (lista de linhas de texto livre,
racional do cálculo). Sem as abas de governança do template completo —
proveniência e caso dourado continuam só no `index_manifest.json`.


Implementação local com manifesto em `references/index_manifest.json`, só
biblioteca padrão + `Decimal` + CSV local + SHA-256. Não busca índice
externo, não interpola mês/dia ausente, não decide termo inicial.

**Status em 2026-08-27**: os 10 índices do manifesto (`tjsp` simples e
`tjmg-fator-atualizacao` foram retirados por serem duplicados) têm caso
dourado aprovado e calculam de verdade —
`tjmg-nao-expurgada`, `tjsp-tabela-pratica`, `selic`, `cdi`, `ipca`,
`inpc`, `igp-m` (conferidos contra a API do Banco Central,
a automação provida pelo motor LangGraph), `tjrj` (conferido contra a série
histórica completa do DrCalc, colada por Ricardo — a tabela do TJRJ é
atualizada anualmente, não mês a mês, por isso repete o mesmo valor
durante o ano; `avisar_cobertura: true` avisa até que mês está
atualizado toda vez que for usado), `poupanca-nova` (série BCB SGS 195,
conferida dia a dia contra a API e contra a Calculadora do Cidadão do
próprio BCB — implementada a convenção `aniversario_deposito`, que
faltava no motor) e `taxa-legal` (não existe como série SGS numérica, só
como calculadora oficial do BCB — conferida contra ela em dois casos;
implementada a convenção `dias_corridos_semiaberto`, juros simples com
soma pro rata, que também faltava no motor). Um bug real de ordenação no
CSV local do `taxa-legal` (duas linhas de agosto/2026 duplicadas fora de
posição no fim do arquivo, impedindo o motor de carregar o índice
inteiro) foi corrigido nessa homologação.

**Mês com índice negativo (deflação) exige declaração explícita** — campo
`tratamento_indice_negativo`, obrigatório só quando o período selecionado
realmente contém um mês negativo (mesmo padrão do
`tratamento_periodo_parcial`; sem declarar, erro
`indice_negativo_sem_tratamento`):
- `piso_zero_no_mes` — mês negativo não reduz o saldo, contribui fator 1
  (nenhuma correção naquele mês). Regra padrão do escritório.
- `aplicar_integralmente` — deflação reduz o saldo corrigido normalmente
  (comportamento anterior, disponível só por pedido explícito).

O modo resumido devolve JSON compacto e o modo detalhado devolve memória de
cálculo local somente quando solicitado.

**Índices com fonte automática no BCB** — `selic`, `cdi`, `ipca`, `inpc`,
`igp-m` e `poupanca-nova` têm série no SGS do Banco Central
(a automação provida pelo motor LangGraph --indice NOME --csv referencias/indices/NOME.csv
--data-inicial AAAA-MM-DD`, sem chave de API). Poupança usa a série 195, uma
linha por dia de aniversário — a mesma lógica de data+valor do script já
funciona sem alteração, confirmado em 2026-08-27.

**Índice sem fonte automática** (ex.: TJRJ, Taxa Legal) — atualização manual
via a automação provida pelo motor LangGraph --indice NOME --csv
referencias/indices/NOME.csv --arquivo-novo NOVO.csv`: só adiciona data
nova, recusa sobrescrever valor existente que divirja (mesma regra do
a automação provida pelo motor LangGraph). Taxa Legal não tem série SGS numérica — só a
Calculadora do Cidadão do BCB, que não expõe API; conferir manualmente
contra ela quando atualizar. Manifesto pode marcar `"avisar_cobertura":
true` num índice — toda vez que ele for usado, o resultado inclui em
`avisos` até que mês está atualizado (`indice_<nome>_atualizado_ate_<data>`),
pra nunca passar despercebido.

## Alertas de implementação verificados em 09/09/2026

- O CSV canônico fica em `C:/Projetos/resolutivo-ai/referencias/indices/`, não dentro da pasta da skill.
- TJMG usa `fator_acumulado`, sem essa divisão. Porém o ramo de fatores não implementa o piso de deflação mensal: passar `piso_zero_no_mes` não basta. Para o padrão do escritório, é necessário aplicar e auditar `produto(max(1, indice_mes/indice_anterior))`, distinguindo esse ajuste da aplicação integral da tabela oficial. Não afirmar que o motor aplicou o piso sem testar.
- Na conferência TJMG, razões do CSV e fatores oficiais arredondados podem divergir em casas além da sétima. Registrar as diferenças e verificar a igualdade dos valores monetários arredondados para cada principal real; não afirmar identidade exata dos fatores.
- O portal TJMG carrega os links dos índices dinamicamente. HTML obtido por requests pode trazer só `LumisPortal.renderInterfaceInstance`. Chrome DevTools MCP, leitura DOM após carregamento, permitiu obter links oficiais PDF/XLS; não concluir ausência da tabela pelo HTML estático.

## O que esta skill não faz

Não decide qual índice é juridicamente correto pra uma situação (Selic ×
IPCA-E × TR, Fazenda × privado, antes/depois de mudança de regra). Isso é
sempre informado por quem pede o cálculo. Se pedirem cálculo sem informar
índice, usa o padrão (TJMG não expurgada) e avisa que está usando o padrão,
pra dar chance de correção antes de entregar o resultado.