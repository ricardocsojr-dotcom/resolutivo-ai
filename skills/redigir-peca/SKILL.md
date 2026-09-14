---
name: redigir-peca
description: >
  Orquestra a redação completa de uma peça processual no padrão RDAA,
  classificando a peça pelo modo de produção (C/B/A), limitando redação por
  blocos a A/B, usando somente o material explicitamente fornecido e acionando
  pesquisa ou consulta processual quando autorizado. Mantém a redação no estilo
  autoral do escritório. Use sempre que Ricardo pedir para
  escrever, redigir, estruturar ou montar uma peça processual — petição
  inicial, contestação, recurso, agravo, embargos, memorial, réplica,
  manifestação ou juntada. Ative com termos como "escreve a inicial", "monta
  a contestação", "faz o recurso", "redige a petição", "estrutura a peça",
  ou qualquer variação que indique produção de documento processual.
---

# Redação de Peça Processual — RDAA

## Como esta skill opera — leia antes de tudo

**O fluxo é governado pelo motor, não por esta leitura.** O assistente nunca
decide a próxima fase por conta própria, por inferência de frase ambígua do
Ricardo, ou por dedução do que "parece" fazer sentido. Toda a sequência,
os gates humanos, o disjuntor de falhas e as transições condicionais vivem em
código: `orquestracao/engine.py` (motor LangGraph), acessado via
`orquestracao/cli.py`.

**Mecânica obrigatória, sempre:**

- **Se houver anexo bruto (PDF escaneado, imagem de AR, print, foto de
  documento):** NUNCA leia/interprete o anexo manualmente com
  `vision_analyze` fatiado em regiões — isso é lento (minutos) e não é o
  papel do agente. Copie o(s) arquivo(s) para `<state_dir>/anexos/` ANTES
  de chamar `cli start`. O motor extrai deterministicamente para
  `packages/intake.md` na fase `intake_ready` (PDF nativo → texto direto;
  PDF escaneado/imagem → OCR local via Tesseract, uma única passagem —
  ver `services/extracao.py`). Depois de `intake_ready` concluído, leia
  `packages/intake.md` normalmente como fonte de fatos — nunca a imagem
  bruta. Se a fase falhar, é porque TODOS os anexos foram ilegíveis
  (fail-safe) — reporte a Ricardo, não tente contornar lendo a imagem à mão.

- **Para Nível C (Peças Simples/Juntadas):**
  Como a peça é simples e dispensa esqueleto e validação prévia, você deve **primeiro** redigir a peça inteira (seguindo as premissas deste chat) e salvá-la em `<state_dir>/packages/writer-input.md`. Somente DEPOIS de criar esse arquivo, chame `python -m orquestracao.cli start <state_dir> --matter-id X --level C`. Se o arquivo já estiver lá, o motor formatará a peça, aplicará o QA e a publicará instantaneamente, em um único comando, sem interrupções.

- **Para Níveis B e A (Complexos):**
  1. Chame `python -m orquestracao.cli start <state_dir> --matter-id X --level B` (ou A).
  2. Leia o campo `"current_phase"`/`"status"` do JSON retornado e execute **literalmente** apenas o que a fase corrente exige — nada a mais, nada a menos.
  3. Ao concluir uma etapa que exige aprovação humana, chame `python -m orquestracao.cli approve <state_dir> --gate <gate> --authority ricardo`.
  4. Repita, consultando `status` a cada passo. Nunca pule uma chamada ao CLI para "economizar tempo" — o próprio motor pula automaticamente fases dispensáveis com base no `roteamento.json`.

Se o motor recusar um avanço (erro `GateError`, `CircuitBreakerError` ou
status `paused`), isso é sinal de bug de sequência ou de disjuntor ativado —
pare e reporte a Ricardo. Use `python -m orquestracao.cli resume` apenas com
autorização explícita dele. Não insista tentando outra fase manualmente.

Só o Ricardo autoriza pular uma etapa, e só quando disser isso de forma
explícita e pontual sobre aquela etapa específica — nunca por dedução. Frases
como "sem validação do Antigravity" descrevem apenas o fluxo padrão de B/C
(que já não aciona Antigravity) e NÃO autorizam pular esqueleto ou o núcleo
de redação. Na dúvida, pergunte antes de escrever.

O que segue abaixo **não é procedimento** — é a inteligência jurídica e
estilística que cada papel (planner/writer/critic/validator) aplica quando o
motor instrui a executá-lo. A classificação de nível é a única decisão
de conteúdo que o assistente toma antes do motor assumir o roteamento.

---

## Classificar o nível da peça — decisão de conteúdo, não do motor

A classificação C, B ou A define o **modo de produção** da peça e não
representa risco processual, validade, pertinência ou qualidade jurídica.
Consultas processuais, pesquisa externa e capacidades de vault são separadas
da classificação e não são disparadas apenas pela existência de um número de
processo ou de uma matéria.

| Tipo | O que é | Redação e Motores | Validação e Estrutura |
|---|---|---|---|
| **C** | Peça muito simples (juntadas, oposições simples, manifestações simples, ciência, concordância, prazo) | Escrita direta pelo **modelo do próprio chat** (sem chamada externa de CLI) | Sem esqueleto, sem consulta a vault, sem validação de LLM externa; direto para compilador nativo e QA protegida |
| **B** | Peça baseada nos autos com desenvolvimento (manifestações complexas, memoriais, especificação de provas, réplicas) | Planejada (esqueleto) e redigida pelo **modelo do próprio chat** (sem chamada de CLI) | Consulta read-only ao Cérebro-Ricar no Cérebro-Ricar; esqueleto aprovado por Ricardo; validação independente pelo **Claude Sonnet 5** (esforço médio); compilador nativo e QA |
| **A** | Peça premium (iniciais complexas, recursos aos tribunais superiores, teses estratégicas) | Planejada pelo **Claude Sonnet 5** (médio); redigida pelo **Codex Terra 5.6** (alto) | Consulta ao Cérebro-Ricar; esqueleto aprovado por Ricardo; crítica pelo **Gemini 3.7 Flash** (Antigravity); validação pelo **modelo do próprio chat**; compilador e QA |

**Como classificar**

- O fluxo deve declarar `nivel_peca` como `A`, `B` ou `C`. Ricardo pode
  declarar o nível diretamente e essa declaração prevalece.
- Pedidos claramente simples, como juntada ou manifestação simples, podem
  seguir o tipo C. Para os demais casos, se Ricardo não declarar o tipo, use B
  como padrão conservador, sem consultar vault para confirmar ou alterar a
  classificação.
- Não altere o nível porque o vault está vazio ou cheio, porque a pesquisa
  encontrou ou não encontrou uma tese, por causa de palavras do texto ou por
  causa de `nivel_risco`. Esses campos são independentes.
- Nos tipos **B e A**, o vault de tese/jurisprudência ("Cérebro-Ricar do
  Resolutivo") é consultado automaticamente antes do esqueleto — o motor
  decide quando. Isso é leitura, não decisão: encontrar ou não encontrar
  conteúdo no vault não altera `nivel_peca`, não substitui pesquisa e não
  aprova tese sozinho.

Depois de classificado o nível, chame o motor via CLI — ele decide toda a
rota a partir daqui (`orquestracao/roteamento.json`).

---

## Inteligência por papel

Cada bloco abaixo é o que o assistente aplica **quando o motor instruir
a executar aquele papel** — nunca antes, nunca por iniciativa própria.

### Papel: Planner — organização de contexto e esqueleto

Trabalhe com os fatos, documentos, decisões, teses, fontes e pedidos que
Ricardo fornecer ou selecionar nesta execução, mais o que a consulta ao
Cérebro-Ricar trouxer nos tipos B/A — e nada além disso. A aprovação de modelo
ou peça anterior não aprova o caso atual. Não confunda "o vault trouxe uma
tese candidata" com "a tese está aprovada para este caso": aprovação
continua exigindo seleção explícita no esqueleto.

**Espelhamento de peça anterior (mesma tese, partes trocadas):** nunca herde
qualificações, valores ou datas do modelo sem recalculá-los contra os
documentos-fonte do caso novo. Adjetivos temporais ("recente", "atual") e
equiparações ("equiparada a", "similar a") do modelo não se transferem
automaticamente — confira a data/fato real do caso novo antes de repetir o
qualificador. Em pedidos que envolvem partilha ou proporção de valores, some
todos os valores-fonte do caso novo (ex.: IRPF, extratos) antes de propor uma
divisão — nunca herde a proporção do modelo como se fosse neutra.

- **Tipo B**: organize o que já existe no processo, identifique lacunas
  objetivas, proponha desenvolvimento de explicações e indique se Legal Design
  ou ilustração pode melhorar a compreensão. As teses candidatas do Cérebro-Ricar
  entram como material a avaliar, não como base já aceita.
- **Tipo A**: organize o conjunto completo de material fornecido, as teses
  candidatas do Cérebro-Ricar e as fontes selecionadas para a peça premium.
- Consulta ao vault operacional ("Procedimentos e Informações") continua
  manual e só acontece se Ricardo pedir expressamente — registre a origem e
  não altere o tipo automaticamente.

**Consulta processual — não fazer.** Não há consulta a andamento,
movimentação, prazo ou publicação. Redija com os fatos fornecidos. Se a peça
depender de um dado que só o andamento externo forneceria e Ricardo não o
trouxe, registre `[PONTO A CONFERIR]`/pendência e não invente o dado.

**Jurisprudência.** Depois de cada pesquisa efetivamente conferida, registre
as fontes preservando o tipo, origem, localização, trecho literal e, quando
disponível, os dados de conferência. Não atribua `verificada_externamente` a
conteúdo que não foi de fato conferido contra a fonte original.

**Esqueleto (tipos A/B).** Estrutura obrigatória via skill `esqueleto-peca`,
incluindo requisitos formais do CPC, fontes selecionadas quando houver
pesquisa, teses e decisões explicitamente aprovadas, e o modelo de estrutura
quando um `modelo_id` tiver sido escolhido. `esqueleto-peca` decide, bloco a
bloco, onde vale ênfase em negrito ou elemento visual — a aprovação do
esqueleto cobre isso junto, não é decisão à parte tomada durante a redação.
Antes de pedir aprovação, cheque o gate de escalonamento de
`esqueleto-peca/SKILL.md` ("Gate de escalonamento manual"); se algum gatilho
bater, registre a pendência e deixe o gate humano do motor decidir a pausa.

O gate humano de aprovação do esqueleto é enforced pelo motor
(`awaiting_skeleton_approval`) — o assistente apresenta o esqueleto a
Ricardo e aguarda; uma frase como "aguardo seu ok" no chat não substitui a
aprovação registrada.

### Papel: Writer — redação no padrão RDAA

Inclua sempre `contencioso-rdaa/references/redacao-rdaa.md` como regra
obrigatória de estilo. Se a matéria for dano moral, inclua também
`dano-moral-rct/references/estilo-rct.md`; se Ricardo pedir explicitamente o
padrão da Flávia, inclua `estilo-flavia-rdaa/references/perfil-flavia.md` —
as duas na mesma execução do redator, não como etapa separada depois.

- Nos tipos A e B, execute a redação por blocos conforme o esqueleto
  aprovado.
- No tipo C, redija diretamente em parágrafos curtos, sem converter o texto
  em fluxo de blocos.
- Blocos: Relatório → Fundamentos → Pedidos, quando a estrutura da peça
  exigir.
- Citações literais das ementas buscadas (nunca paráfrase).
- Toda citação ou fundamento jurisprudencial deve apontar para `source_id`
  selecionado no esqueleto ou para uma fonte posterior revisada.
- Sem linguagem arcaica. Parágrafos curtos.
- Comece argumentos afirmando diretamente o objeto, a tese, o vício, o fato
  ou a consequência. Evite aberturas por negação, ressalva ou justificativa
  defensiva, como "não se pretende", "não se busca", "não se trata", "não se
  ignora" e "não se desconhece". Reescreva positivamente quando o sentido for
  preservado. Mantenha a negativa quando ela for indispensável para delimitar
  o objeto, responder a uma afirmação concreta, afastar interpretação
  específica ou formar contraste jurídico necessário.

**Nível C — regras específicas de estilo:**

- Evite parágrafos curtos em série, frase-tese isolada e uniformidade que
  revele IA; preferir 3–7 linhas quando a ideia comportar, com variação real
  de abertura e extensão.
- A abertura de cada parágrafo argumentativo deve conter uma tese concreta
  fundida ao seu desenvolvimento. Nunca use frases-tese isoladas em linha
  própria.
- Varie a sintaxe inicial entre parágrafos e não inicie dois parágrafos
  seguidos com a mesma palavra/estrutura.
- Não use dois-pontos, travessões, parênteses explicativos nem ponto e
  vírgula em prosa.
- Citações legais somente no padrão "Lei, art. X". Não inclua
  jurisprudência.

**Correção de cliente:** quando o usuário indicar "cliente é a Trivale", a
peça deve ser endereçada a TRIVALE INSTITUIÇÃO DE PAGAMENTO LTDA como
embargante/re, e não Q & P como autora.

Não use `Agent` nem subagente para intermediar motores. A divisão de
trabalho é fixa: Codex redige, Antigravity critica e Claude valida/corrige.
O Conselho continua sendo uma consulta isolada de Claude apenas quando
Ricardo o pedir ou quando o nível A a exigir.

### Papel: Critic (Antigravity) — apenas nível A

Só nível A tem crítica independente; a rota de B e C nunca inclui esse
papel. Faça no máximo **uma chamada crítica por peça A**. Peça B/C só recebe
crítica se Ricardo pedir explicitamente essa exceção pontual (nesse caso, a
rota efetiva daquela matéria deve ser reclassificada para A — não existe
meio-termo silencioso). Nunca envie o histórico integral da conversa ou o
raciocínio privado do redator — apenas a peça, fatos, fontes e teses
necessárias.

O crítico aponta somente vulnerabilidades, lacunas e pontos a conferir; não
altera arquivos, tese, pedido ou estado. O relatório é alerta estruturado,
nunca um bloqueio ou uma decisão automática. Persona de advogado adverso,
ACH invertida — contrato de método completo em `skills/critico-rdaa/SKILL.md`.

- Se o crítico apontar vulnerabilidade relevante, encaminhe-a ao Claude
  (papel Validator). Claude corrige o que for objetivo; alteração de tese,
  pedido ou estratégia exige pausa e decisão de Ricardo.
- Se a vulnerabilidade remanescente for de **tese central** — não
  secundária, algo que compromete o argumento principal da peça — isso é o
  gatilho 4 do gate de escalonamento (`esqueleto-peca/SKILL.md`): pare com
  pergunta explícita ao Ricardo em vez de publicar com essa pendência.
- Guarde o relatório do crítico para informar a correção e a entrega.

### Papel: Validator (Claude) — níveis A e B; nível C pula

Nível C não passa por este papel — é peça de modelo fixo e uso cotidiano
(juntada, ciência, oposição a julgamento virtual, concordância, pedido de
prazo), sem redação por blocos nem argumentação nova a validar. O motor não
exige esse papel quando o estágio `validating` não existe na rota do nível.

**Nível A e B:** Claude recebe o rascunho do redator — no nível A, também o
relatório do crítico — o esqueleto aprovado (quando houver) e as fontes
selecionadas. Corrige diretamente o que for objetivo. Se o achado exigir
mudança de tese, pedido ou estratégia, pausa e apresenta o ponto a Ricardo
— não decide sozinho.

Roda o checklist de qualidade da skill `revisor-rdaa` antes de entregar.
"Rodar o checklist" não termina em produzir um relatório: todo achado
confirmado deve ser corrigido no texto antes de seguir para a entrega. Isso
inclui travessão, ponto-e-vírgula fora de lista/alínea, tricolon de negação,
abertura defensiva recorrente, qualquer dois-pontos e qualquer aposto
explicativo entre parênteses ou travessões pareados — os três primeiros
bloqueiam numa única ocorrência (`redacao-rdaa.md` §2), só a abertura
defensiva é avaliada por recorrência. A abertura negativa isolada deve ser
avaliada pela função argumentativa e não bloqueada por palavra-chave. Não
pare para perguntar quando a correção for apenas de forma. Só fica para
relatar ao Ricardo o que for ambíguo o suficiente para exigir julgamento
dele, como um `[PONTO A CONFERIR]`. Um relatório que aponta vício e não é
seguido de correção equivale a não ter revisado.

**Nível C** roda o mesmo checklist de estilo e o QA gate estrutural antes da
publicação — isso não é validação de mérito jurídico, é controle mecânico
que roda em toda peça, de qualquer nível.

---

## Consulta ao Cérebro-Ricar — regras de epistemologia

Existem dois vaults distintos, e só um deles entra automaticamente neste
fluxo:

- **Cérebro-Ricar** (tese e jurisprudência) — consultado
  automaticamente nos tipos B e A, antes do esqueleto. O tipo C nunca
  consulta.
- **Procedimentos e Informações** (operacional) — leitura sempre manual, só
  com pedido expresso de Ricardo.

Leia o `CLAUDE.md` do Cérebro-Ricar antes de consultar — ele governa estrutura e
convenções.

1. Identifica a área do direito no contexto já coletado (dano moral,
   responsabilidade civil, direito do consumidor, contratos bancários, ações
   declaratórias/indenizatórias, ou outra que o Cérebro-Ricar já tenha) e lê o
   `wiki/domains/<área>.md` correspondente, se existir.
2. A partir dali, lê as teses ligadas em `wiki/concepts/` e as fontes em
   `wiki/sources/` (ementa/trecho sempre literal, com origem).
3. Registra o que encontrar com `origem: cerebro-ricar` e `status:
   informada` — nunca `verificada_externamente` só por ter vindo do vault.
   Vira tese aprovada, fonte selecionada ou parte do esqueleto somente por
   decisão explícita no esqueleto (papel Planner).
4. Se não encontrar nada relevante para a área, segue normalmente — vault
   vazio não é pendência e não bloqueia a peça.
5. Não substitui pesquisa nova (`buscar-jurisprudencia`/
   `jusbrasil-jurisprudencia`, automática no tipo A) — o Cérebro-Ricar é o que
   já foi decidido/registrado antes; a pesquisa é o que busca precedente
   novo. Os dois podem coexistir na mesma execução.

Não altere `nivel_peca` por causa do que a consulta encontrar ou deixar de
encontrar.

---

## Entrega

Converter o texto corrido/Markdown do redator nos blocos tipados que o
compilador exige (`titulo`, `numerado`, `citacao` com `referencia`,
`alinea`, `abertura` etc.) é trabalho do Validator, não do redator. Siga a
tabela de `redacao-rdaa.md` ao montar cada bloco: prosa argumentativa vira
`numerado` com `sequencia` contínua do início ao fim da peça (nunca
`paragrafo`, que não numera); jurisprudência vira `citacao` com a fonte
completa no campo `referencia`, nunca um parágrafo de atribuição separado; a
qualificação usada no quadro (`partes`) é a mesma reaproveitada nos blocos
do corpo e dos pedidos. Um bloco do tipo errado não dá erro na hora — só
produz uma peça sem a formatação RDAA, então confira a estrutura antes de
gerar o `.docx`, não só o conteúdo.

Gere o `.docx` **candidato** usando a skill `formatar-peca` em modo nativo,
sempre em caminho temporário ou de staging — nunca grave diretamente no
caminho final e nunca use a skill genérica `docx`, que não aplica o padrão
visual RDAA. Em seguida, encaminhe o candidato ao publicador
(`publicar_docx.py`), sempre com `--context <contexto_peca.json>` (o mesmo
JSON usado pra gerar o candidato) — sem isso o publicador deriva o
`matter_id` do nome do arquivo de saída e pula a validação de contrato da
peça, esqueleto e semântica do docx que dependem do contexto. Só entregue o
documento final depois que o publicador retornar `[OK]`. O publicador
executa o gate, preserva backup, mantém o arquivo anterior se houver falha e
substitui o destino de forma atômica. Nome padrão do arquivo publicado:
`[tipo_peca]_[numero_processo]_[data].docx`.

Na entrega, relate em uma linha que a peça foi redigida (e, quando
aplicável, criticada pelo Antigravity e validada/corrigida pelo Claude).
Qualquer ponto que exija decisão de tese, pedido ou estratégia permanece
explícito para Ricardo. Relate também, em uma linha, se a matéria foi
registrada no Cérebro-Ricar (ex.: "Registrada em Cérebro-Ricar como
[[matter-XXX]]").

---

## Nota sobre a integração das skills

Este fluxo combina:
- Classificação de nível (`nivel_peca` C/B/A) → decide profundidade, blocos,
  esqueleto e a rota de agentes
- `jusbrasil-jurisprudencia` → pesquisa de jurisprudência automática no tipo
  A (premissa do nível, sem pedido separado), nunca no tipo B/C salvo pedido
  expresso
- Consulta processual (andamento, publicação, movimentação) → não existe no
  plugin; não tente
- MCP `NotebookLM` → uso secundário e somente quando Ricardo pedir
- `esqueleto-peca` → estrutura obrigatória + ponto de aprovação nos tipos A
  e B; nos tipos B/A também decide, bloco a bloco, a ênfase em negrito e o
  elemento visual planejado ("Legal Design planejado")
- `legal-design-rdaa` → não é acionada automaticamente por inteiro; a
  mecânica de ênfase em negrito (dosagem, limite) vive em
  `redacao-rdaa.md`, e a tabela de elementos visuais por destinatário
  (`legal-design-rdaa/SKILL.md` §2.4) é só consultada por `esqueleto-peca`
  quando um bloco genuinamente pede elemento visual — invocar a skill
  inteira continua exigindo pedido de Ricardo
- `playbook-modelos` → modelos de estrutura selecionados por `modelo_id`,
  sem aplicação automática de tese
- `contencioso-rdaa` → núcleo de escrita obrigatório no pacote entregue ao
  redator (papel Writer)
- `revisor-rdaa` → checklist de qualidade aplicado pelo Claude (papel
  Validator)
- `docx` → skill genérica, NÃO usar aqui (ver Entrega)
- Cérebro-Ricar → consulta automática em B/A antes do esqueleto;
  gravação automática de tese/fonte usada após publicação
- Procedimentos e Informações → leitura sempre manual; gravação automática
  de registro operacional após publicação
- `gestao-materias` → repositório de documentos-fonte (`DOC-XXX`/
  `source_id`) por matéria, fora deste fluxo

## Mecânica de controle (referência técnica)

Todo o roteamento, gates, disjuntor e persistência de estado vivem em
código — não neste arquivo:

- `orquestracao/engine.py` — motor único (LangGraph): constrói o grafo,
  controla transições, gates humanos e disjuntor.
- `orquestracao/cli.py` — ponto de entrada único do assistente
  (`start`/`status`/`approve`/`resume`/`abort`/`audit`).
- `orquestracao/roteamento.json` — política declarativa de estágios, gates
  e workers por nível.
- `orquestracao/system_handlers.py` — conecta as fases não-IA (QA,
  publicação, registro no vault) aos serviços em `services/`.
- Disjuntor: bloqueia após 2 falhas consecutivas na mesma fase; só
  `authority: ricardo` libera (`orquestracao.cli resume`).

Este arquivo não descreve mais essa mecânica em texto porque texto pode ser
ignorado ou mal interpretado — o motor não pode.