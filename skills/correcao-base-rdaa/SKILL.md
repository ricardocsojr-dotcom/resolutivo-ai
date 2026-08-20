---
name: correcao-base-rdaa
description: Diagnostica e ajuda a corrigir a base de contencioso do escritório Romano Donadel (export CPJ-3C, planilha "Resolutivo" e equivalentes) — encontra recursos ativos cuja ficha de origem já consta arquivada, recursos "soltos" sem processo de origem rastreável na base, inconsistências entre os campos de status e fase processual, registros de teste, problemas de cadastro em Ação/Cliente/polo (autor ou réu), e campos críticos (Risco, Situação atual, Fase Processual, Resumo/Assunto) em branco ou sem conteúdo útil. Use SEMPRE que Ricardo pedir para "atualizar a base", "corrigir a base", "diagnosticar a base", "conferir o Resolutivo", "achar processo de origem arquivado", "achar recurso solto", "auditar o cadastro do CPJ-3C", ou enviar uma nova exportação do CPJ-3C pedindo para revisar/organizar. Ative também com variações como "roda o diagnóstico da base", "o que precisa ser corrigido na base", "tem processo desatualizado?", mesmo que ele não cite o nome exato do arquivo.
---

# Correção da Base — RDAA (Resolutivo / CPJ-3C)

## O que este skill faz

Recebe um export em Excel do CPJ-3C (planilha "Resolutivo" ou equivalente — uma linha por processo/incidente, com colunas como Ficha, Arquivo Ficha Incidente, Ação, Cliente, Autor, Réu, Fase Processual, Localizador, Situação atual, Resumo/Assunto, Advogado Responsável) e produz um workbook de diagnóstico com achados priorizados e um plano de ação. Não é um script genérico de "limpeza de planilha" — encapsula o entendimento específico de como esse escritório organiza processos e recursos, validado diretamente com Ricardo.

## Entendimento de domínio (não reinvente isto a cada vez)

- **Cada recurso interposto normalmente abre uma NOVA ficha** — não é um sub-registro dentro da ficha de origem. Números de processo repetidos entre fichas diferentes são o comportamento esperado (ex.: um Agravo de Instrumento tem seu próprio número no tribunal, diferente do número de origem; uma Apelação, no estado, costuma manter o mesmo número da ação de origem). **Nunca reporte isso como "duplicidade" ou erro de cadastro** — já foi testado e corrigido: é assim que o escritório trabalha.
- Existe também um padrão legado de sub-fichas (`Arquivo Ficha Incidente` com sufixo `.00`, `.01`, `.02`...) em que vários incidentes/recursos ficam sob a mesma Ficha. Os dois padrões coexistem na base histórica — a lógica de "recurso solto" (ver abaixo) considera ambos antes de concluir que não há origem rastreável.
- O campo **"Localizador"**, apesar do nome, guarda o **status** do registro (ATIVO, ARQUIVADO, ATI-EST, SUSPENSO, etc.) — não confundir com um código de localização física.
- Nem toda "Ação" com a palavra "Embargos" é recurso: Embargos de Declaração e Embargos Infringentes são recursos; Embargos à Execução e Embargos de Terceiro são ações/defesas autônomas. Ver `references/regras-diagnostico.md` para a lista completa de padrões usados.

## Fluxo de trabalho

1. **Localizar o arquivo de entrada.** Se o usuário anexou/apontou um arquivo, use-o. Se não, procure na pasta do projeto por algo como `Resolutivo.xlsx` ou pergunte qual export usar.
2. **Rodar o script de diagnóstico**:
   ```bash
   python scripts/diagnosticar_base.py <entrada.xlsx> <saida.xlsx> --sheet <NOME_DA_ABA>
   ```
   O script lê os dados, aplica todas as classificações (ver `references/regras-diagnostico.md`) e gera o workbook completo (Resumo Executivo, Plano de Ação e abas de detalhe). Ele referencia colunas pelo **nome**, não pela posição — se o export do CPJ-3C mudar de layout e o script falhar reclamando de coluna ausente, ajuste as constantes `COL_*` no topo do script.
3. **Recalcular fórmulas.** O workbook gerado tem fórmulas vivas na aba "Base (dados + auxiliares)" (o achado de origem arquivada recalcula sozinho se o usuário colar uma nova exportação ali). Use o script `recalc.py` da skill **xlsx** para recalcular e confirmar `total_errors: 0` antes de entregar:
   ```bash
   python <caminho-skill-xlsx>/scripts/recalc.py <saida.xlsx> 60
   ```
   Nunca entregue o arquivo sem rodar essa verificação.
4. **Ler os números e comunicar como advogado, não como planilha.** Antes de responder ao usuário, abra o resultado (os prints do script já trazem as contagens) e traduza em risco prático — especialmente a aba "1b. Recursos Soltos", que é o achado mais sensível: significa que a base não tem visibilidade do processo de origem daquele recurso, o que pode indicar processo arquivado e não rastreado, erro de vinculação, ou simplesmente um caso legítimo cuja origem nunca foi cadastrada. Não afirme categoricamente que a origem está arquivada sem confirmação no tribunal — trate como hipótese a verificar.
5. **Copiar o arquivo final para a pasta do usuário e apresentar** com `present_files`, com um resumo objetivo (contagens + os 2-3 achados mais importantes), sem recapitular todo o processo.

## Achados que o script produz (resumo — detalhes em references/regras-diagnostico.md)

| Aba | O que é | Prioridade |
|---|---|---|
| 1. Recursos c Origem Arquivada | Recurso ativo cuja ficha de origem já tem Fase Processual = "Arquivado" | Alta |
| 1b. Recursos Soltos | Recurso sem nenhum registro de origem rastreável na base (nem por nº processo, nem por ficha) | Alta |
| 2. Inconsistencia Status-Fase | Fase Processual diz "Arquivado" mas o campo Status (Localizador) não | Média |
| 3. Registros de Teste | Número de processo literalmente "teste"/"testes" | Baixa |
| 5. Campos Criticos em Branco | Risco, Situação atual e Fase Processual em branco, por advogado | Baixa (mutirão) |
| 6. Acao-Cliente-Polo | Ação em branco; Cliente em branco; Cliente que não bate com Autor nem Réu | Média |
| 7. Qualidade do Resumo | Resumo/Assunto em branco, curto demais ou placeholder (ex.: só repete o número do processo) | Média |

## Quando o usuário pedir algo fora desse escopo padrão

Se Ricardo pedir uma análise ad hoc sobre a base (ex.: "quantos processos a Alessandra tem acima de R$500 mil", "lista os processos da Trivale em fase de recurso") que não é uma das categorias acima, não force o uso do script — leia a planilha diretamente com pandas e responda a pergunta. O script serve para o diagnóstico estrutural recorrente, não para toda pergunta sobre a base.

Para classificar risco/provisão (possível, provável, remoto) de processos individuais segundo a metodologia RDAA, use o skill **analise-provisao-rdaa** — é um assistente separado, focado nisso.
