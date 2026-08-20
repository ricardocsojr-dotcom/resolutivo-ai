# Resolutivo.AI

Plugin de contencioso cível e consumerista do **Romano Donadel Advogados Associados (RDAA)**.

O identificador técnico do plugin é `resolutivo-ai`. No Claude Code, as skills podem
ser referenciadas com esse namespace, por exemplo `/resolutivo-ai:redigir-peca`.
Os nomes individuais das skills permanecem inalterados para preservar a organização
e o funcionamento interno.

## O que este plugin faz

Transforma o Claude no assistente jurídico sênior do setor Resolutivo do RDAA,
com acesso integrado a:

| Fonte | MCP | Para que serve |
|-------|-----|-----------------|
| **DataJud/CNJ** | `CNJ` | Andamento processual em tempo real |
| **DJEN/DJe** | `CNJ` | Publicações oficiais e intimações |
| **NotebookLM** | `NotebookLM` | Conhecimento interno do escritório |
| **Jusbrasil** | via `buscar-jurisprudencia` (extensão do Chrome) | Ementas literais de qualquer tribunal |

Todas as skills abaixo já vêm dentro do plugin — nada precisa ser instalado
separadamente.

## Skills do plugin

### Redação de peças

| Skill | O que faz |
|-------|-----------|
| `/redigir-peca` | Orquestra o fluxo completo por tipo de produção. C é peça muito simples em parágrafos curtos. B usa o que foi fornecido no processo e permite desenvolvimento, explicação, Legal Design ou ilustração. A é peça premium com todo o conjunto de recursos aprovado. Redação por blocos e esqueleto ficam limitados a A/B. Nenhum nível consulta o vault automaticamente |
| `/esqueleto-peca` | Checklist estrutural (requisitos CPC) por tipo de peça — chamada internamente pelo `redigir-peca`, não usada isolada |
| `/contencioso-rdaa` | Persona, metodologia analítica e regras de redação RDAA — base de qualquer peça, memorial, parecer, contestação, recurso ou análise estratégica de litígio |
| `/dano-moral-rct` | Redige seções específicas de ação de dano moral no estilo autoral de Ricardo Cesar |
| `/formatar-peca` | Gera o `.docx` candidato no padrão visual RDAA e o encaminha à publicação protegida. A entrega só ocorre após QA, backup, hash e substituição atômica |
| `/legal-design-rdaa` | Plain language, Visual Law, infográficos, linhas do tempo — deixa peças e contratos mais claros sem perder rigor técnico |

### Pesquisa e consulta

| Skill | O que faz |
|-------|-----------|
| `/buscar-jurisprudencia` | Jusbrasil (ementas literais) + DataJud opcional quando houver pedido de volume/estatística |
| `/lei-e-sumula` | Texto atualizado de lei ou súmula (STF/STJ) em fonte oficial, sempre com citação literal e link |
| `/consultar-processo` | Andamento processual via DataJud, somente quando Ricardo pedir a consulta |
| `/calculo-judicial` | Correção monetária e juros entre duas datas, com tabelas de índice mantidas localmente |

### Backoffice e operação diária

| Skill | O que faz |
|-------|-----------|
| `/backoffice-diario` | Briefing matinal: publicações DJEN + prazos DataJud + providências do dia |
| `/backoffice-juridico` | Transforma prazos, andamentos e demandas soltas em providências claras com responsável e mensagem pronta (e-mail, WhatsApp, comunicação interna) |
| `/briefing-andamentos` | Roda o Radar Estratégico (script Python) sobre a planilha de andamentos e gera o briefing dos casos críticos |
| `/correcao-base-rdaa` | Diagnostica e corrige a base de contencioso (export CPJ-3C / planilha Resolutivo) — recursos soltos, fichas desatualizadas, campos em branco |

### Revisão e gestão de risco

| Skill | O que faz |
|-------|-----------|
| `/revisor-rdaa` | Checklist técnico (jurídico-estratégico e visual/formatação) antes de protocolar |
| `/analise-provisao-rdaa` | Classifica risco processual (provável/possível/remoto) e faz double-check de provisão/contingência contra CPC 25 / NBC TG 25 |

### Suporte e utilidades

| Skill | O que faz |
|-------|-----------|
| `/conselho-rdaa` | Conselho de decisão (ACH + 5 conselheiros) para decisões reais com alternativas — estratégia, acordo, contratação |
| `/perfil-csv` | Converte tabela de parcelas/cálculos para o formato "perfil", pronto pra colar |
| `/romano-donadel-slide-style` | Identidade visual padrão (cores, tipografia, componentes) para apresentações do escritório |
| `/estilo-flavia-rdaa` | Camada opcional para adaptar uma peça já redigida ao perfil textual da Flávia. Só aciona com pedido explícito ou `estilo_alvo: flavia` |
| `/converter-arquivo-grande` | Extrai texto localmente antes da leitura de arquivos extensos para reduzir contexto. Não instala dependências automaticamente |
| `/previsao-condenacao-rdaa` | Análise de provisão pré-sentença sob demanda, com liquidação determinística e fontes externas opcionais. Não infere risco |

## Catálogo e governança de extensões

As extensões externas e referências de skills são registradas em
`skills/revisor-rdaa/references/catalogo-skills-externas.md`. O catálogo informa
origem, finalidade, acionamento, dependências, status de teste e limites. Nenhum
item externo é ativado por volume, nome de advogado, nome de réu ou existência de
processo. A skill Flávia não prova autoria e a skill de previsão não substitui
análise jurídica.

## Ementário compartilhado (vault Obsidian)

O vault Obsidian permanece como capacidade futura e não é consultado ou gravado
automaticamente por nenhum tipo de peça. A matéria deve trabalhar com fatos,
documentos, decisões e fontes explicitamente fornecidos ou selecionados na
execução. Qualquer consulta ou gravação futura dependerá de pedido expresso e
registro separado de origem e decisão.

## Playbook de modelos de estrutura

A skill `esqueleto-peca` distribui `references/playbook-modelos.md` e um catálogo
local vazio em `references/catalogo-modelos.json`. O playbook organiza estrutura,
versão, blocos, variáveis, dependências, recursos visuais e provenance, mas não
aplica automaticamente tese, fato, fonte, pedido ou pertinência jurídica.

## Estado compartilhado e provenance local

O plugin mantém automaticamente um estado local por matéria em `.rdaa-run/<matter_id>`.

A consulta ao CNJ/DataJud/DJEN não é etapa obrigatória de `/redigir-peca`.
Número de processo no contexto não dispara consulta. Essas fontes continuam
disponíveis quando Ricardo pede andamento, publicação, prazo ou estatística,
ou quando a skill própria de backoffice é acionada.
Esse estado separa fatos explícitos, teses, decisões, pendências e registros de
fontes. As pesquisas conferidas podem ser registradas no `provenance.jsonl` com
origem, localização, trecho literal e status, sem depender de serviço externo.

Antes de chamar conselho, redator, crítico ou revisor, o fluxo pode montar um
pacote de contexto específico para a função com
`skills/revisor-rdaa/scripts/contexto_rdaa.py`. O pacote é menor que o estado
completo e evita repetir histórico irrelevante. O mecanismo não infere tese,
risco, validade, autenticidade ou pertinência jurídica a partir de texto livre.

Quando há estado estruturado, o publicador executa também a revisão semântica
objetiva (`skills/revisor-rdaa/scripts/semantica_rdaa.py`). Ela confere IDs,
referências, identidade do processo e duplicidades objetivas. Somente erros
estruturais verificáveis podem bloquear a entrega; alertas que exigem julgamento
jurídico permanecem como pendências. O sistema registra localmente métricas de
tamanho dos pacotes, sem enviar o conteúdo para serviço externo. O manifesto
local também registra a rota baseada em risco explicitamente declarado, com
agentes `selected` e `omitted`, eventos agregados de agentes, rodadas repetidas
e tentativas bloqueadas de publicação. Um pedido direto de agente fica marcado
como `override_explicito`.
Esses registros são proxies de engenharia, não medição direta de créditos. Quando
blocos do contexto declaram IDs, o gerador grava marcações OOXML invisíveis no
DOCX e o publicador verifica se esses IDs chegaram ao documento; nenhum ID é
mostrado ao usuário nem altera a redação.

O Visual Law continua opcional. Quando usado, o novo bloco `visual` exige tipo
(`timeline`, `matrix`, `flow` ou `confrontation`), função declarada, texto
pesquisável, dados explícitos e IDs semânticos quando houver vínculo com fatos,
fontes ou pedidos. Tabelas preservam texto pesquisável; metadados de figura são
invisíveis. O publicador bloqueia apenas falhas estruturais objetivas.

Decisões podem receber recortes anotados pelo script local
`skills/formatar-peca/scripts/anotar_decisao.py`. O contexto informa a página, o
recorte, as coordenadas e os IDs das caixas; o script gera uma cópia nova com
retângulos vermelhos sem preenchimento, preserva o original e grava manifesto
com hashes e coordenadas antes/depois do recorte. O plugin não escolhe o trecho,
não faz inferência jurídica e não altera a fonte original.

A manutenção administrativa é separada do fluxo de redação. O diagnóstico usa
`skills/revisor-rdaa/scripts/manutencao_rdaa.py inspect .rdaa-run`. A limpeza é
simulada por padrão e, quando explicitamente autorizada com `--apply`, move
estados antigos para quarentena local. Backups não são apagados automaticamente;
restauração exige seleção explícita e preserva a versão atual antes da troca.

## Integrações disponíveis

### 1. CNJ (DataJud + DJEN) — opcional

Servidor próprio, self-contained, em `servers/cnj-server.py` — configurado
pelo `.mcp.json` do plugin quando uma skill de consulta processual, publicação,
backoffice ou estatística for acionada. Não é requisito para redigir ou formatar
uma peça.

### 2. NotebookLM

Defina a variável de ambiente `NOTEBOOKLM_MCP_PATH` apontando para o seu
servidor MCP local do NotebookLM antes de ativar o plugin:
```bash
export NOTEBOOKLM_MCP_PATH=/caminho/para/seu/notebooklm-mcp/server.py
```

### 3. Jusbrasil

`buscar-jurisprudencia` usa a extensão Claude in Chrome com a conta do
Jusbrasil já logada — não é um MCP, é automação de navegador.

## Exemplos de uso

```
"Busca jurisprudência do STJ sobre devolução em dobro de cobrança indevida"
→ Aciona /buscar-jurisprudencia com Jusbrasil; DataJud só se houver pedido de volume ou estatística

"Consulta o processo 0000000-00.0000.8.26.0001"
→ Aciona /consultar-processo com DataJud

"Tem alguma publicação nova no processo 1234567-00.0000.8.26.0000?"
→ Usa MCP CNJ → buscar_publicacoes_dje_cnj()

"Organiza o dia"
→ Aciona /backoffice-diario com DJEN + DataJud + /backoffice-juridico

"Redige a contestação no caso de dano moral por negativação indevida"
→ Aciona /redigir-peca sem consulta automática ao CNJ/DataJud/DJEN

"Quanto devemos provisionar nesse processo?"
→ Aciona /analise-provisao-rdaa

"Roda o radar de andamentos de hoje"
→ Aciona /briefing-andamentos
```

## Changelog

### 3.0.0 (2026-08-20)

- Renomeação completa da identidade do plugin para **Resolutivo.AI**.
- Novo identificador técnico `resolutivo-ai`, conforme o formato exigido pelo Claude Code.
- O novo identificador altera o namespace das skills, mas não altera nomes de skills, scripts, regras jurídicas, caminhos internos ou comportamento funcional.
- A atualização exige reinstalação ou recarregamento do plugin para que o novo namespace seja reconhecido.

### 1.3.0 (2026-08-05)

Unifica a "língua RDAA" num núcleo único de escrita, extraído dos melhores
modelos reais do escritório (apelação, agravos, contrarrazões, manifestações
simples e com títulos):

- **`contencioso-rdaa/references/redacao-rdaa.md` reescrito como Núcleo Único
  de Escrita**: abertura fixa com fundamento legal no primeiro período, tese
  fundida na primeira frase do parágrafo (sem frase-tese isolada — compatível
  com o checklist-3), jurisprudência com aterrissagem, pedidos em cascata,
  fechamento fixo, tabela de dosagem por tipo de peça (manifestação simples →
  recursal extenso → narrativa), sinais de cadência robótica condensados e
  checklist de conformidade usado igualmente na redação e na revisão. Regras
  dos Apontamentos 2026-07 preservadas (títulos sem Da/Do/De, sublinhado
  proibido, extensão de parágrafo, números por categoria).
- **Skills apontadas para o núcleo como leitura obrigatória**:
  `dano-moral-rct` (núcleo primeiro, `estilo-rct.md` como camada),
  `redigir-peca` (passo 7), `esqueleto-peca` e `revisor-rdaa` (listas
  duplicadas viraram remissão — fonte única).
- **Ciclo fechado no revisor**: itens do `checklist-1-juridico.md` que
  nasceram na revisão sem constar da fonte de redação agora citam
  `redacao-rdaa.md` (citação legal, números, verbo de comando, dois-pontos,
  pedidos em cascata).
- Cópia Codex sincronizada com os mesmos arquivos.

### 1.2.0 (2026-07-24)

Adiciona um hook `SessionStart` (`hooks/hooks.json` + `hooks/scripts/session-start.mjs`)
que injeta o `CLAUDE.md` do plugin (perfil do escritório, persona, regras de
orquestração) como contexto automático em toda sessão. Antes, esse arquivo
era inerte — o Claude Code não carrega um `CLAUDE.md` de raiz de plugin como
contexto de projeto, e a "skill de onboarding" que deveria copiá-lo nunca foi
implementada. Isso fazia o plugin só se comportar de forma proativa
(classificar peça, consultar CNJ automaticamente etc.) quando a frase do
usuário batia bem com a descrição de uma skill específica. Com o hook, o
comportamento fica equivalente ao `AGENTS.md` que a versão Codex do mesmo
plugin já carrega nativamente em toda sessão.

### 1.1.0 (2026-07-24)

Melhorias de formatação e redação a partir dos Apontamentos de melhoria do
escritório (revisão de uma peça real contra o Manual de Redação RDAA 2021),
convertidas em regra geral e distribuídas entre `formatar-peca`,
`contencioso-rdaa`, `esqueleto-peca` e `revisor-rdaa`:

- **`formatar-peca` (determinístico, `construir_peca.py`/`verificar_formatacao.py`)**:
  gera primeiro um candidato temporário e nunca grava diretamente no destino final;
  a publicação ocorre pelo `publicar_docx.py` depois do gate protegido. O
  rodapé com linha superior e paginação alinhada à direita (não mais
  centralizada); endereçamento em espaçamento simples com 2 linhas em branco
  depois (antes 1,5 e só 1 enter); mesma correção após o quadro
  Processo/Partes; enter entre linhas de partes diferentes dentro do quadro;
  título com recuo deslocado (2ª linha alinha em 2cm com a 1ª); nome da peça
  opcional em CAIXA ALTA + negrito na abertura; **reversão de destaque** —
  nome da parte e e-mails das assinaturas não usam mais sublinhado (Manual
  §2.9: destaque só por negrito).
- **`contencioso-rdaa/references/redacao-rdaa.md` (fonte canônica)**: regra de
  números por categoria (1-9 extenso, 10+ numeral, nunca repetir "N
  (extenso)"; exceções de data/artigo/valor monetário); citação legislativa
  (diploma antes do dispositivo); títulos nunca começam com Da/Do/De/Dos/Das;
  verbos de comando e dois-pontos tratados como vício **contextual** (nunca
  proibição absoluta); extensão de parágrafo (3-7 linhas confortável, revisar
  acima de 10-12).
- **`esqueleto-peca`**: seção única de formalidades comuns (endereçamento sem
  "digníssimo", nome da peça, pedidos com parágrafo introdutório antes das
  alíneas, checagem de redundância entre pedidos, fecho padronizado, data no
  formato "Cidade/UF").
- **`revisor-rdaa` (checklists 1/2/3)**: itens novos alinhados às regras
  acima, sem duplicar o texto das fontes canônicas.

Ver o plano de implementação para o detalhamento completo por item.
