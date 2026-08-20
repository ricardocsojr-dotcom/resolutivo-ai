# Decisões finais — 57 Agents Advocacia × plugin Resolutivo.AI

Tabela de providências por robô, fechada após a análise completa (comparativo de
arquitetura, revisão de código do plugin **Resolutivo.AI** (`resolutivo-ai`), e
decisões do Ricardo ponto a ponto). Este documento substitui o `mapeamento-57-agentes-rdaa.md`
como referência de trabalho — aquele fica como histórico da análise.

Status usados:
- **CONSTRUIR AGORA** — desbloqueado, pode começar já.
- **CONSTRUIR — BACKLOG** — aprovado, mas fica pra depois por prioridade.
- **CONSTRUIR — AGUARDANDO MATERIAL** — aprovado, falta você me passar algo.
- **CONSTRUIR — AGUARDANDO DECISÃO** — gap real identificado, mas você ainda
  não deu o sim/não explícito.
- **ABSORVER** — não vira entrega própria; o conhecimento entra em outra skill.
- **NÃO CONSTRUIR — REDUNDANTE** — já coberto pelo que existe.
- **NÃO CONSTRUIR — SEM UTILIDADE** — baixo valor, descartado.
- **NÃO CONSTRUIR — FORA DE ESCOPO** — área que o RDAA não pratica.

## 1 · Prazos & Acompanhamento

| # | Agente | Providência |
|---|--------|-------------|
| 01 | Monitor DJE/DJEN | NÃO CONSTRUIR — confirmado pelo Ricardo: nossa arquitetura atual já é equivalente pro uso dele (controladoria cobre monitoramento amplo por outro sistema; consulta pontual já é o 03/`consultar-processo`). |
| 02 | Lembrete de prazo | CONSTRUIR AGORA — modo de consulta rápida via automação de navegador no Prazo Fácil (prazofacil.com.br). Uso: conferência pontual de uma data, **não** fonte de referência primária. |
| 03 | Andamento processual | NÃO CONSTRUIR — REDUNDANTE. Confirmado pelo Ricardo com o mesmo racional do 01 — arquitetura atual já equivalente. |
| 04 | Intimação | ABSORVER — sem skill própria. Conhecimento (classificação do ato, detecção de vício, ciência × resposta obrigatória) fica disponível pra uso manual quando você acionar redação de peça. |
| 05 | Ciência | CONSTRUIR — apenas como template extra dentro do fluxo de redação de peça. Baixo esforço. |

## 2 · Petições & Documentos

| # | Agente | Providência |
|---|--------|-------------|
| 06 | Petição inicial cível | **CONSTRUÍDO** em 2026-07-19 — checklist CPC 319/320 na skill nova `esqueleto-peca`, chamada pelo `redigir-peca` como etapa de aprovação obrigatória antes da redação. `contencioso-rdaa` não foi alterado. |
| 07 | Contestação cível | **CONSTRUÍDO** em 2026-07-19 — checklist CPC 335-343 (preliminares do 337, impugnação especificada do 341, reconvenção do 343) na mesma skill `esqueleto-peca`. |
| 08 | Recurso (cabimento) | **CONSTRUÍDO** em 2026-07-19 — árvore de cabimento (apelação × agravo × embargos de declaração × agravo interno) na `esqueleto-peca`. |
| 09 | Parecer jurídico | CONSTRUIR — BACKLOG. Formato consultivo que não existe hoje (tudo que existe é orientado a litígio). |
| 10 | Procuração | NÃO CONSTRUIR — SEM UTILIDADE. |

## 3 · Pesquisa Jurídica

| # | Agente | Providência |
|---|--------|-------------|
| 11 | Jurisprudência STJ/STF | ABSORVER no 14 — a parte útil (classificação de vinculação/tema) entra no `tese-repetitiva`; não duplicar o mecanismo de busca de ementa que já existe. Ver explicação detalhada na resposta de 2026-07-19. |
| 12 | Doutrina | NÃO CONSTRUIR SEPARADO — ABSORVER em `jusbrasil-jurisprudencia`. Ricardo identificou que o Jusbrasil já disponibiliza seção de doutrina/artigos, com o mesmo mecanismo de extração literal via Chrome já usado pra ementa. Basta habilitar a busca nessa seção — não precisa de skill nova nem do modo restrito que eu tinha proposto. |
| 13 | Lei e súmula | CONSTRUIR AGORA — fontes já definidas: Portal da Legislação (planalto.gov.br/legislacao), Normas.leg.br, LeisEstaduais.com.br, Leis.org (estadual/municipal); STF (sumariosumulas) e STJ (repetitivos + SCON) pra súmula. Baixo risco — texto oficial estável. |
| 14 | Tese repetitiva | CONSTRUIR — BACKLOG. Absorve a parte útil do 11. Fonte real: página oficial de repetitivos do STJ (processo.stj.jus.br/repetitivos/temas_repetitivos) e repercussão geral do STF — não depende da memória do modelo. |
| 15 | Ementário | **CONSTRUÍDO** em 2026-07-19 — vault Obsidian inicializado em `OneDrive - RD\Resolutivo\001. AGENDA DIÁRIA\CEREBRO`. `redigir-peca` consulta o vault no início (passo 2) e grava no final (passo 9). Refinado no mesmo dia com a classificação C/B/A (ver nota abaixo): nível A sempre força pesquisa nova mesmo com tese mapeada, nível B usa só o que já está no vault, nível C nem consulta. Ainda não testado em uso real. |

## 4 · Atendimento ao Cliente

| # | Agente | Providência |
|---|--------|-------------|
| 16 | Triagem novo caso | CONSTRUIR — BACKLOG. Aprovado. |
| 17 | Orientação inicial | CONSTRUIR — BACKLOG. Aprovado. |
| 18 | Onboarding cliente | CONSTRUIR — BACKLOG. Confirmado (falta pacote formal: contrato + procuração + LGPD + cadastro). |
| 19 | Follow-up cliente | CONSTRUIR — BACKLOG. Confirmado (falta régua sistemática por tipo de cliente). |
| — | (22 e 25 tratados nas categorias 5 e 6 abaixo) | |

## 5 · Contratos & Compliance

| # | Agente | Providência |
|---|--------|-------------|
| 20 | Revisão de cláusula | CONSTRUIR — BACKLOG. Dentro do escopo (análise de cláusula pra defesa/pré-processual). |
| 21 | Comparação de contratos | CONSTRUIR — BACKLOG. Dentro do escopo. |
| 22 | LGPD / Direito Digital | CONSTRUIR — BACKLOG. Confirmado. Ricardo esclareceu que não tem relação com `dano-moral-rct` — construir como skill independente, sem tentar integrar com a peça de dano moral. |
| 23 | Due diligence | CONSTRUIR — BACKLOG. Dentro do escopo — útil pra entender contexto de operação societária em defesa processual. |

## 6 · Operação do Escritório

| # | Agente | Providência |
|---|--------|-------------|
| 24 | Cobrança de honorários | CONSTRUIR — DESBLOQUEADO. Calculadora de referência pra precificar honorários de casos **novos**, manual. Tabelas recebidas em 2026-07-19: `referencias/honorarios/tabela-oab-mg.pdf` e `referencias/honorarios/tabela-oab-sp-2026.pdf`. |
| 25 | Agenda de audiência | CONSTRUIR — BACKLOG. Confirmado — construir os roteiros de oitiva + geração de `.ics`, complementando o que `backoffice-juridico` já cobre (categoria "PROVIDÊNCIAS AUDIÊNCIA"). |
| 26 | Resumo de processo | CONSTRUIR — BACKLOG. Aprovado — usa a skill `pdf` já disponível + o agente 26 do pacote como referência de padrão mínimo de informação (case brief, linha do tempo, tabela de partes/provas, prognóstico). |
| 27 | Backup do escritório | NÃO CONSTRUIR — FORA DE ESCOPO. |

## 7 · Peças por área do direito

| # | Agente | Providência |
|---|--------|-------------|
| 28 | Apelação cível | **CONSTRUÍDO** em 2026-07-19 — checklist específico (tempestividade, preparo, error in procedendo × in judicando, efeito suspensivo CPC 1.012) na `esqueleto-peca`. |
| 29 | Agravo de instrumento | **CONSTRUÍDO** em 2026-07-19 — checklist específico (rol CPC 1.015 + Tema 988 STJ, peças obrigatórias CPC 1.017, comunicação CPC 1.018) na `esqueleto-peca`. |
| 30 | Ação de cobrança | **CONSTRUÍDO** em 2026-07-19 — nota específica dentro do checklist de petição inicial (prescrição, rito comum × monitória, memória de cálculo). |
| 31–33 | Trabalhista | NÃO CONSTRUIR — FORA DE ESCOPO. |
| 34–38 | Família e Sucessões | CONSTRUIR — BACKLOG, baixa prioridade (base pequena, mas mantida). |
| 39–40 | Criminal | NÃO CONSTRUIR — FORA DE ESCOPO. |
| 41–42 | Tributário | NÃO CONSTRUIR — FORA DE ESCOPO. |
| 43–45 | Empresarial | CONSTRUIR — BACKLOG. Dentro do escopo (contexto societário para defesa). |
| 46 | CDC prática abusiva | CONSTRUIR — BACKLOG, baixa prioridade. Uso raro, como contra-argumentação em casos específicos de cliente. |
| 47–48 | Imobiliário (despejo, renovatória) | CONSTRUIR — BACKLOG. Frente imobiliária dentro do escopo. |
| 49–50 | Usucapião (extra/judicial) | CONSTRUIR — BACKLOG. Idem, frente imobiliária. |
| 51–53 | Previdenciário | NÃO CONSTRUIR — FORA DE ESCOPO (completamente). |
| 54 | Cumprimento de sentença | CONSTRUIR — DESBLOQUEADO, mas fica entre as últimas tarefas por prioridade (conforme combinado). Minutas recebidas em 2026-07-19: `referencias/cumprimento-sentenca/modelo-pessoa-privada-romano-x-minare.docx` (CPC 513/523, SISBAJUD/RENAJUD/INFOJUD/CNIB, multa+honorários 10%) e `modelo-pessoa-publica-romano-x-detran-go.pdf` (CPC 534/535, requisição de pagamento/RPV, sem SISBAJUD direto). |
| 55 | Impugnação ao cumprimento | CONSTRUIR — BACKLOG. Aprovado sem ressalva — sugiro construir junto do 54, já que são a mesma fase processual (execução), mesmo o 54 estando mais atrás na fila. |
| 56 | Cálculo judicial de atualização | CONSTRUIR — DESBLOQUEADO. Fonte confirmada: drcalc.net tem as 10 tabelas (TJMG não expurgada, INPC, IPCA, Selic, Taxa Legal, TJSP, IGP-M, Poupança nova, TJRJ, CDI). Regra simplificada pelo Ricardo em 2026-07-19: **índice padrão é sempre TJMG não expurgada**, sem detecção automática de qual índice cabe em qual situação — se precisar de outro índice, ele pede explicitamente. Ele informa data de início de correção, data de início de juros e os valores por cálculo; a skill não decide isso sozinha. Plano de dados seguue o mesmo: base histórica completa uma vez, rotina mensal busca só o mês novo. Resultado alimenta `perfil-csv`. |
| 57 | Minuta de contrato de serviços | NÃO CONSTRUIR — SEM UTILIDADE. |

## Pendências antes de definir a ordem de construção

Atualizado em 2026-07-19 — todas as pendências de material/decisão foram
resolvidas. 15 trocou de NotebookLM pra Obsidian (vault já inicializado em
`OneDrive - RD\Resolutivo\001. AGENDA DIÁRIA\CEREBRO`), 54 e 24 receberam
os arquivos de referência, 56 teve a regra simplificada (índice padrão fixo,
sem detecção automática). Nada mais bloqueia o início da construção — falta
só decidir a ordem (ver seção "Fases de construção" abaixo).

## Fases de construção propostas

**Fase 1 — sem dependência:**
- [x] Checklist estrutural (06+07+08+28+29+30) — skill `esqueleto-peca`, construída em 2026-07-19.
- [x] Gatilho do ementário (15) no `redigir-peca` — construído em 2026-07-19, **testado em uso real em 2026-07-19**: manifestação à impugnação aos embargos à execução, processo 5065372-25.2025.8.13.0702 (Cotrial/Vicente x Massari FIDC). Fluxo completo validado ponta a ponta: classificação nível A (vault vazio → sem tese aderente → escalada automática), pesquisa de jurisprudência obrigatória (achou e descartou corretamente uma linha de tese que não se aplicava ao caso — FIDC ≠ factoring), esqueleto aprovado pelo Ricardo com ajustes pontuais, redação via `contencioso-rdaa`, autorrevisão via `revisor-rdaa`, entrega em `.docx` via `formatar-peca` (native mode, `construir_peca.py`, verificação de formatação passou), gravação no vault (primeira gravação real: 1 tese + 1 ementa em `empresarial`). Peça entregue no diretório local de testes reais.
- [x] 13 (lei e súmula) — skill `lei-e-sumula` construída em 2026-07-19.
- [x] 12 (extensão do jusbrasil pra doutrina) — absorvido em `jusbrasil-jurisprudencia`, seção doutrina/artigos adicionada em 2026-07-19 (zip repactuado).
- [x] 56 (coleta histórica de índices) — skill `calculo-judicial` construída. Base histórica concluída em 2026-07-19: Ricardo entregou `csv indice histórico.xlsx` com os 10 índices completos, estruturado em `referencias/indices/*.csv`. Atualização mensal: primeira tentativa de automação via clique simulado na tela falhou por ler a página rápido demais (não era anúncio bloqueando, era eu checando antes da navegação terminar); corrigido e **confirmado funcionando** clicando o botão direto via JS + esperando ~2s antes de ler — validado em TJMG e CDI. Rotina mensal automatizada documentada na SKILL.md.

**Fase 2 — backlog simples:** 09, 14, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26.

**Fase 3 — baixa prioridade:** 34–38, 43–45, 46, 47–50.

**Fase 4 — desbloqueada, material recebido:** 54, 24.

## Classificação C/B/A (2026-07-19)

Ideia do Ricardo: nem toda peça merece o mesmo esforço de pesquisa. Adicionado
como passo 0 do `redigir-peca`, antes de tudo:

- **C** — trâmite puro (juntada, manifestação simples, embargos de
  declaração simples): zero pesquisa, pula vault/jurisprudência/esqueleto.
- **B** — tese já mapeada no vault, sem controvérsia nova: usa só o que o
  vault já tem, pesquisa de jurisprudência nova vira opcional/fallback.
- **A** — tese extensa, nova, ou alta complexidade/valor/risco: pesquisa de
  jurisprudência nova é **obrigatória**, mesmo com tese mapeada no vault.

Regra de transição automática: B sem tese aderente no vault vira A — falta
de base é, por si só, motivo pra pesquisa obrigatória. Ricardo pode
sobrepor a classificação a qualquer momento.

Ajuste em 2026-07-19: em nível B, a skill **não decide sozinha** pular a
pesquisa nova — para e pergunta ("achei a tese X mapeada, quer que eu
pesquise mesmo assim?"). Só nível A é automático (pesquisa sempre
obrigatória); em B a decisão de economizar tempo é sempre do Ricardo.

## Por que comecei pelo checklist estrutural + ementário

Escolha minha (Ricardo pediu "o que você entender mais lógico"): dos itens
sem bloqueio, esse par era o único com **dependência real** entre si — o
gatilho do 15 só faz sentido depois de existir um ponto de aprovação de
esqueleto no `redigir-peca`, e esse ponto de aprovação é justamente o
checklist estrutural do 06/07/08/28/29/30. Também é o item de maior alcance
(toca toda peça que o escritório produz) e o mais discutido/validado nesta
análise inteira. 13, 12 e 56 são independentes entre si e do resto — seguem
na fila, sem motivo técnico pra ordem entre eles.

## Revisão da classificação C/B/A e do vault automático — 2026-08-20

A decisão anterior sobre C/B/A, registrada acima, fica supersedida quanto ao uso automático do vault e quanto ao significado dos níveis.

- **Tipo A** é peça premium, com todo o conjunto de recursos aprovados para o caso e redação por blocos permitida.
- **Tipo B** é peça baseada principalmente no que já existe no processo, mas com desenvolvimento melhor, explicação, organização, Legal Design ou ilustração quando útil. A redação por blocos é permitida.
- **Tipo C** é peça muito simples, em regra formada por parágrafos curtos e sem necessidade de tópicos. A redação por blocos não integra esse fluxo.

Nenhum tipo consulta o vault automaticamente. O `nivel_peca` é separado de `nivel_risco`. A consulta ao vault permanece capacidade futura ou operação expressamente solicitada, sem alterar o tipo por causa do conteúdo encontrado.

A decisão também registra a criação do playbook local de modelos de estrutura. O playbook organiza modelos, blocos, variáveis, dependências, recursos visuais, provenance, versão e diff, sem aplicar automaticamente tese, fato, fonte, pedido ou pertinência jurídica.


## Decisão de integração seletiva de skills anexadas

Em 20 de agosto de 2026, foram avaliadas as skills `estilo-flavia-rdaa`, `data-storytelling`, `converter-arquivo-grande` e `previsao-condenacao-rdaa`, além dos repositórios públicos indicados por Ricardo.

A skill da Flávia foi integrada como camada opcional para contexto explícito `estilo_alvo: flavia`. Ela não prova autoria, não altera mérito, não consulta vault automaticamente e deve obedecer às regras universais de redação e publicação do RDAA.

A conversão de arquivos grandes foi integrada como ingestão local para reduzir contexto. Não instala pacotes, não baixa modelos, não executa OCR sem autorização e não altera o arquivo original.

A previsão de condenação foi integrada como módulo sob demanda por `modo: previsao_condenacao`. O script de liquidação é determinístico, mas recebe o risco como entrada estruturada e não infere risco, pertinência ou autenticidade. Vault, Jusbrasil, CNJ e DataJud permanecem fora de qualquer disparo automático.

O data storytelling foi incorporado somente como referência local de Legal Design para tipos A e B, subordinada à identidade visual RDAA. Não foram incorporadas bibliotecas, catálogos em massa, serviços pagos, infraestrutura SaaS, exportação externa ou dependências Node.
