# Fontes oficiais de índices

Este arquivo registra fontes candidatas e não equivale à homologação de fórmula ou resultado. Cada série precisa de caso dourado aprovado antes de receber status `aprovado` no manifesto.

## TJMG

A página institucional do [Fator de Atualização Monetária do TJMG](https://www.tjmg.jus.br/portal-tjmg/processos/indicadores/fator-de-atualizacao-monetaria.htm) apresenta arquivos mensais em PDF e XLS e informa que os fatores são baseados na variação de ORTN, OTN, BTN, TR, IPC-r e INPC.

O XLS de agosto de 2026 foi baixado localmente como candidato e preservado fora do pacote do plugin. O mapeamento observado é o seguinte.

| Campo | Valor observado |
|---|---|
| Aba | `Plan1` |
| Cabeçalho | Linha 9 |
| Dados | Linhas 10 a 751 |
| Ano | Coluna A |
| Mês em português | Coluna B |
| Índice | Coluna C |
| Tipo proposto | `fator_acumulado` |
| Unidade proposta | `fator` |
| Status | `candidato` |

A conversão de XLS legado é feita em diretório temporário por LibreOffice, sem modo interativo. A biblioteca não executa macros. Como o contêiner XLS antigo não permite a mesma inspeção de macros do XLSX, a proveniência registra essa limitação e a promoção permanece bloqueada.

## TJSP

A planilha oficial de atualização monetária e juros enviada pelo escritório foi usada como referência estrutural. O candidato local da Tabela Prática TJSP usa a aba `ÍNDICES`, a data na coluna `A`, a Tabela Prática observada na coluna `O` e a faixa 7 a 748, encerrada na última linha com fator preenchido na versão recebida.

| Campo | Valor observado |
|---|---|
| Aba | `ÍNDICES` |
| Data | Coluna A |
| Série candidata | Coluna O |
| Tipo proposto | `fator_acumulado` |
| Unidade proposta | `fator` |
| Status | `candidato` |

O perfil é específico da planilha recebida. Outra versão da planilha deve ser mapeada novamente, pois não se deve assumir que colunas, faixa ou nome de série permaneçam iguais.

## Regra de promoção

A normalização gera CSV e pacote JSON com hashes, cobertura e proveniência. O promotor só escreve uma cópia do manifesto quando existe caso dourado aprovado, fórmula de referência, convenção declarada, resultado esperado, resultado observado, tolerância, responsável e data de aprovação. O manifesto de origem e os índices aprovados não são substituídos automaticamente.
