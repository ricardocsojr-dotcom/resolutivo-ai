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

Esta skill orquestra o fluxo completo de produção de uma peça do RDAA,
mas não trata toda peça igual. A classificação C, B ou A define o modo de
produção da peça e não representa risco processual, validade, pertinência ou
qualidade jurídica. Consultas processuais, pesquisa externa e capacidades de
vault são separadas da classificação e não são disparadas apenas pela existência
de um número de processo ou de uma matéria.

## 0. Classificar o nível da peça — SEMPRE PRIMEIRO

| Tipo | O que é | Redação | Pesquisa e estrutura |
|---|---|---|---|
| **C** | Peça muito simples, normalmente resolvida em parágrafos curtos. Exemplos são juntadas, oposições simples, manifestações simples, ciência, concordância e pedidos objetivos de prazo | Direta, sem redação por blocos e sem tópicos complexos | Não consulta vault, não pesquisa e não exige esqueleto |
| **B** | Peça baseada principalmente no que já existe no processo, mas que merece desenvolvimento melhor, explicação mais clara, organização superior, Legal Design ou ilustração. Exemplos são manifestações complexas, memoriais, especificação de provas, impugnações e réplicas desenvolvidas | Redação por blocos permitida e preferencial quando houver divisão útil | Usa os fatos e documentos explicitamente fornecidos. Pesquisa externa somente quando Ricardo pedir ou quando o plano da matéria a autorizar |
| **A** | Peça premium, com todo o conjunto de recursos que o RDAA puder oferecer para o caso | Redação por blocos permitida e preferencial | Esqueleto, fontes selecionadas, pesquisa autorizada, Visual Law, Legal Design, ilustrações, decisões anotadas, crítica por risco e revisão completa quando cabível |

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
- Nos tipos **B e A**, o vault de tese/jurisprudência ("Ementário do
  Resolutivo") é consultado automaticamente antes do esqueleto — ver passo
  9. O tipo **C** nunca consulta. Isso é leitura, não decisão: encontrar ou
  não encontrar conteúdo no vault não altera `nivel_peca`, não substitui
  pesquisa e não aprova tese sozinho.

## Fluxo — nível C

Colete somente os dados mínimos, redija diretamente em parágrafos curtos, faça
revisão objetiva e entregue o DOCX candidato pela publicação protegida. Não
use `contencioso-rdaa` para estratégia, não monte esqueleto, não faça pesquisa,
não acione vault e não transforme o texto em redação por blocos.

## Fluxo — níveis B e A

### 1. Coletar contexto

Se não tiver, pergunte:
- Tipo de peça (inicial, contestação, recurso...)
- Número do processo (se já existente)
- Fatos relevantes do caso
- Pedido principal
- Há prazo para apresentar?

Assim que houver um identificador explícito, use o mesmo diretório isolado de
`.rdaa-run/<matter_id>/` adotado por `publicar_docx.py`. Não combine o estado
de processos diferentes. O orquestrador pode montar pacotes de contexto ao
longo do fluxo, mas não deve repassar o estado completo a cada skill.

Não use `Agent` nem subagente para intermediar motores. A classificação C/B/A
define a profundidade da peça; a divisão de trabalho é fixa: Codex redige,
Antigravity critica e Claude valida/corrige. O Conselho continua sendo uma
consulta isolada de Claude apenas quando Ricardo o pedir ou quando o nível A a
exigir.

### 2. Organizar o material explicitamente fornecido

**Nos tipos B e A, antes de seguir**: execute agora a consulta automática
ao Ementário do Resolutivo (mecânica e regras completas no passo 9, mais
adiante neste arquivo — leia aquela seção antes da primeira execução;
depois de internalizada, basta repetir a mecânica aqui). Resumo mínimo:
identifique a área do direito no contexto já coletado, leia
`wiki/domains/<área>.md` no vault do Ementário e as teses/fontes ligadas a
ele, e registre o que encontrar como `origem: ementario-resolutivo`,
`status: informada`. O tipo C nunca faz isso.

Trabalhe com os fatos, documentos, decisões, teses, fontes e pedidos que
Ricardo fornecer ou selecionar nesta execução, mais o que essa consulta
trouxer nos tipos B/A — e nada além disso. A aprovação de modelo ou peça anterior não aprova o caso
atual. Não confunda "o vault trouxe uma tese candidata" com "a tese está
aprovada para este caso": aprovação continua exigindo seleção explícita no
esqueleto (passo 6).

- **Tipo B**: organize o que já existe no processo, identifique lacunas
  objetivas, proponha desenvolvimento de explicações e indique se Legal Design
  ou ilustração pode melhorar a compreensão. As teses candidatas do Ementário
  (passo 9) entram como material a avaliar, não como base já aceita.
- **Tipo A**: organize o conjunto completo de material fornecido, as teses
  candidatas do Ementário (passo 9) e as fontes selecionadas para a peça
  premium.
- Consulta ao vault operacional ("Procedimentos e Informações") continua
  manual e só acontece se Ricardo pedir expressamente — registre a origem e
  não altere o tipo automaticamente.

### 3. Consulta processual — não fazer

Não há consulta a andamento, movimentação, prazo ou publicação — a capacidade
foi removida do plugin. Redija com os fatos fornecidos. Se a peça depender de
um dado que só o andamento externo forneceria e Ricardo não o trouxe, registre
`[PONTO A CONFERIR]`/pendência e não invente o dado.

### 4. Buscar jurisprudência

Depois de cada pesquisa efetivamente conferida, registre as fontes no estado da
matéria com `contexto_rdaa.py register_research`, preservando o tipo, origem,
localização, trecho literal e, quando disponível, os dados de conferência. Não
atribua `verificada_externamente` a conteúdo apenas reaproveitado de mensagem,
arquivo interno ou histórico. A fonte deve ser selecionada no esqueleto antes
da redação.

- **Tipo B**: nunca pesquise automaticamente. A peça é desenvolvida somente com
  os documentos, fatos e fundamentos já presentes no processo/autos. Pesquisa
  externa só entra se Ricardo pedir expressamente nesta execução.
- **Tipo A**: a pesquisa é automática — é premissa do tipo A, não exige pedido
  ou autorização separada. Realize-a antes do esqueleto. A seleção de fontes
  dentro do resultado da pesquisa continua explícita e não representa
  conclusão automática de pertinência.
- **Tipo C**: não faça pesquisa de jurisprudência ou legislação como parte do
  fluxo padrão.

### 5. Consultar NotebookLM (se disponível)

Uso secundário e somente quando Ricardo pedir. A consulta não é automática em
nenhum nível e não substitui a origem registrada das fontes.

### 6. Montar o esqueleto e aguardar aprovação — ETAPA OBRIGATÓRIA

Confira antes de montar: nos tipos B/A, a consulta automática ao Ementário
do Resolutivo (passo 2/passo 9) já rodou? Se ainda não, rode agora — o
esqueleto não pode ser montado sem essa consulta já ter acontecido nos
tipos B/A.

Execute a skill `esqueleto-peca` para montar a estrutura obrigatória da
peça dos tipos A e B. Inclua requisitos formais do CPC, fontes selecionadas
quando houver pesquisa, teses e decisões explicitamente aprovadas, e o modelo
de estrutura quando um `modelo_id` tiver sido escolhido. Preencha também
`esqueleto.fontes_selecionadas`, `esqueleto.fontes_status`,
`esqueleto.aprovacao` e os `source_ids` de cada bloco. O contexto de redação
deve declarar `nivel_peca`, `modo_redacao`, `redacao_por_blocos` e
`exigir_esqueleto: true`. O tipo C não passa por esta etapa no fluxo padrão.

Nos tipos B/A, `esqueleto-peca` já decide, bloco a bloco, onde vale ênfase em
negrito ou elemento visual (seção "Legal Design planejado" daquela skill) — a
aprovação do esqueleto no passo abaixo cobre isso junto, não é decisão à parte
tomada durante a redação.

Antes de pedir aprovação, cheque o gate de escalonamento de
`esqueleto-peca/SKILL.md` ("Gate de escalonamento manual"). Se algum gatilho
bater, é a mesma pausa por `AskUserQuestion` abaixo — não uma etapa extra.

**Pare aqui de verdade — use a tool `AskUserQuestion`.** Apresente o
esqueleto ao Ricardo e chame `AskUserQuestion` com opções como "aprovar
esqueleto como está" / "pedir ajuste antes de seguir". Uma frase em prosa
tipo "aguardo seu ok" não basta: num fluxo autônomo o modelo pode
simplesmente seguir sem que nada force a pausa. É a chamada da tool que
bloqueia de fato esperando resposta. Não escreva a peça por extenso antes
da aprovação recebida por essa tool — isso existe pra evitar redigir em
cima de tese ou jurisprudência errada, e pra controlar o que entra no
aprovação da estrutura e para preservar as fontes explicitamente selecionadas.

### 7. Codex redige no padrão RDAA

Antes de chamar a skill de redação, monte o pacote `redator` com
`skills/revisor-rdaa/scripts/contexto_rdaa.py`. Passe apenas fatos, teses
aprovadas ou explicitamente selecionadas, decisões aplicáveis, fontes/citações
selecionadas, pendências, regras necessárias, `nivel_peca`, `modo_redacao`,
`redacao_por_blocos` e o `modelo_estrutura` selecionado quando houver. Não
repasse o histórico integral ou o provenance bruto.

Só depois do esqueleto aprovado e validado. Grave o pacote compacto em
`.rdaa-run/<matter_id>/PROMPT-REDACAO.md`.

**Checkpoint manual — padrão desde 2026-08-30.** Não rode o executor pela
sessão do Claude Code (isso ainda conta no limite de uso dele, mesmo sem
`Agent` no meio). Em vez disso, pare aqui e diga a Ricardo, literalmente:
"o pacote está em `.rdaa-run/<matter_id>/PROMPT-REDACAO.md` — abra o Codex
nesta mesma pasta (ele lê `AGENTS.md` sozinho), cole o conteúdo do arquivo,
e traga o rascunho de volta aqui quando terminar." Espere a resposta dele
com o rascunho antes de seguir para o passo 7.5. Não prossiga sozinho.

Só use o executor direto (`executar_motor.py codex --prompt ... --output
...`) se Ricardo pedir explicitamente automação nessa etapa — não é mais o
caminho padrão. O resultado, por qualquer via, é um rascunho, nunca
publicação. Inclua
`contencioso-rdaa/references/redacao-rdaa.md` como regra obrigatória. Se a
matéria for dano moral, inclua também `dano-moral-rct/references/estilo-rct.md`;
se Ricardo pedir explicitamente o padrão da Flávia, inclua
`estilo-flavia-rdaa/references/perfil-flavia.md` — as duas rodam na mesma
chamada do redator, não como etapa separada depois. Siga
estritamente:
- Nos tipos A e B, execute a redação por blocos conforme o esqueleto aprovado.
- No tipo C, redija diretamente em parágrafos curtos, sem converter o texto em
  fluxo de blocos.
- Blocos: Relatório → Fundamentos → Pedidos, quando a estrutura da peça exigir.
- Citações literais das ementas buscadas (nunca paráfrase)
- Toda citação ou fundamento jurisprudencial deve apontar para `source_id`
  selecionado no esqueleto ou para uma fonte posterior revisada
- Sem linguagem arcaica
- Parágrafos curtos
- Comece argumentos afirmando diretamente o objeto, a tese, o vício, o fato ou a consequência. Evite aberturas por negação, ressalva ou justificativa defensiva, como “não se pretende”, “não se busca”, “não se trata”, “não se ignora” e “não se desconhece”. Reescreva positivamente quando o sentido for preservado. Mantenha a negativa quando ela for indispensável para delimitar o objeto, responder a uma afirmação concreta, afastar interpretação específica ou formar contraste jurídico necessário.

### 7.5. Antigravity critica — checkpoint manual

Depois da redação (rascunho do Codex já em mãos), monte outro pacote
compacto — a peça, fatos, fontes e teses necessárias, nunca o raciocínio do
redator — e grave em `.rdaa-run/<matter_id>/PROMPT-CRITICO.md`. Inclua no
pacote a instrução de ler `skills/critico-rdaa/SKILL.md` — é o contrato de
método do crítico (persona de advogado adverso, ACH invertida, o que avaliar
e o que nunca avaliar, formato de saída). O checkpoint manual só mudou quem
executa e como o pacote chega até o Antigravity; a metodologia continua
sendo essa, não uma genérica.

Mesmo checkpoint do passo 7: pare e diga a Ricardo pra abrir o Antigravity
(`agy`) na mesma pasta, colar o conteúdo do arquivo, e trazer a crítica de
volta. Se ele quiser a saída já validada contra
`skills/redigir-peca/references/critica-antigravity.schema.json`, ele passa
o schema pro próprio `agy` na mão; Claude não precisa reforçar isso.

O crítico aponta somente vulnerabilidades, lacunas e pontos a conferir; não
altera arquivos, tese, pedido ou estado. O relatório é alerta estruturado,
nunca um bloqueio ou uma decisão automática. O executor direto
(`executar_motor.py antigravity ...`) continua disponível só se Ricardo
pedir automação explícita nessa etapa.

Para extração documental simples, use `--effort low` ou `medium`; `high` fica
reservado à crítica estratégica. Falha, cota ou timeout pausa o fluxo — nunca
troque de motor silenciosamente.

Faça no máximo **uma chamada crítica por peça B/A**, com pacote curto e sem
loop automático entre motores. Peça C só recebe crítica se Ricardo pedir ou se
a rota registrar override explícito.
Nunca envie o histórico integral da conversa ou o raciocínio privado do
redator.

- Se o crítico apontar vulnerabilidade relevante, encaminhe-a ao Claude no
  passo 8. Claude corrige o que for objetivo; alteração de tese, pedido ou
  estratégia exige pausa e decisão de Ricardo.
- Se a vulnerabilidade remanescente for de **tese central** — não secundária,
  algo que compromete o argumento principal da peça — isso é o gatilho 4 do
  gate de escalonamento (`esqueleto-peca/SKILL.md`): pare com
  `AskUserQuestion` em vez de publicar com essa pendência.
- Se não houver vulnerabilidade relevante, siga direto para o passo 8.
- Guarde o relatório do crítico para informar a correção e a entrega.

### 8. Claude valida e corrige

Claude recebe o rascunho do Codex, o relatório do Antigravity, o esqueleto
aprovado e as fontes selecionadas. Corrige diretamente o que for objetivo. Se
o achado exigir mudança de tese, pedido ou estratégia, pausa e apresenta o
ponto a Ricardo. Em seguida, rode o checklist da skill `revisor-rdaa` —
incluindo `scripts/verificar_estilo.py`
(Passo 1b da própria skill) — antes de entregar. Depois de gerar o DOCX
candidato, use `scripts/publicar_docx.py`: ele roda o `qa_gate.py`, o gate
estrutural e a revisão semântica objetiva quando houver contexto, e só substitui
o arquivo final quando todos os controles objetivos passam. O publicador não
cria regra de redação; ele apenas impede entrega sem QA, sem referência
impossível ou conflito objetivo de identidade, e preserva backup
da versão anterior. Alertas semânticos que dependem de julgamento jurídico
continuam sendo relatados, não corrigidos automaticamente.


"Rodar o checklist" não termina em produzir um relatório. Todo achado
confirmado pelo script ou pelo checklist deve ser corrigido no texto antes de
seguir para a entrega. Isso inclui travessão, ponto-e-vírgula fora de
lista/alínea, tricolon de negação, abertura defensiva recorrente, qualquer dois-pontos e
qualquer aposto explicativo entre parênteses ou travessões pareados — os três
primeiros bloqueiam numa única ocorrência (redacao-rdaa.md §2), só a abertura
defensiva é avaliada por recorrência. A abertura
negativa isolada deve ser avaliada pela função argumentativa e não bloqueada por
palavra-chave. Não pare para perguntar quando a correção for apenas de forma.
Só fica para relatar ao Ricardo o que for ambíguo o suficiente para exigir
julgamento dele, como um `[PONTO A CONFERIR]`. Um relatório que aponta vício e
não é seguido de correção equivale a não ter revisado.


## Entrega

Codex/Antigravity devolvem a peça em texto corrido/Markdown. Converter esse
texto nos blocos tipados que `construir_peca.py` exige (`titulo`, `numerado`,
`citacao` com `referencia`, `alinea`, `abertura` etc.) é trabalho do Claude,
não do redator — não está delegado a mais ninguém. Siga a tabela de
`redacao-rdaa.md` ao montar cada bloco: prosa argumentativa vira `numerado`
com `sequencia` contínua do início ao fim da peça (nunca `paragrafo`, que não
numera); jurisprudência vira `citacao` com a fonte completa no campo
`referencia`, nunca um parágrafo de atribuição separado; a qualificação usada
no quadro (`partes`) é a mesma reaproveitada nos blocos do corpo e dos
pedidos. Um bloco do tipo errado não dá erro na hora — só produz uma peça
sem a formatação RDAA, então confira a estrutura antes de gerar o `.docx`,
não só o conteúdo.

Gere o `.docx` **candidato** usando a skill `formatar-peca` em modo nativo,
`construir_peca.py`, sempre em caminho temporário ou de staging — nunca grave
diretamente no caminho final e nunca use a skill genérica `docx`, que não
aplica o padrão visual RDAA. Em seguida, encaminhe o candidato ao
`publicar_docx.py`, sempre com `--context <contexto_peca.json>` (o mesmo
JSON usado pra gerar o candidato) — sem isso o publicador deriva o
`matter_id` do nome do arquivo de saída, grava o manifesto num
`.rdaa-run` aninhado errado dentro da pasta da matéria, e pula a validação de
contrato da peça, esqueleto e semântica do docx que dependem do contexto. Só
entregue o documento final depois que o publicador retornar `[OK]`. O
publicador executa o gate, preserva backup, mantém o arquivo anterior se
houver falha e substitui o destino de forma atômica. Nome padrão do arquivo
publicado: `[tipo_peca]_[numero_processo]_[data].docx`

Na entrega, relate em uma linha que a peça foi redigida pelo Codex, criticada
pelo Antigravity e validada/corrigida pelo Claude. Qualquer ponto que exija
decisão de tese, pedido ou estratégia permanece explícito para Ricardo.

### 9. Ementário do Resolutivo — consulta automática em B/A, antes do esqueleto

Existem dois vaults distintos, e só um deles entra automaticamente neste
fluxo:
- **Ementário do Resolutivo** (tese e jurisprudência) — vault gerido pelo
  `claude-obsidian`, mora em `~/vaults/ementario-resolutivo` dentro do WSL
  (não mais no OneDrive — motor de escrita exige filesystem nativo Linux).
  Leitura funciona direto pelo caminho de rede
  `\\wsl.localhost\Ubuntu\home\ricar\vaults\ementario-resolutivo` (Read
  normal). Qualquer gravação (nota nova, atualização) deve passar pelas
  skills do `claude-obsidian` (`save`/`wiki-ingest`) executadas via `wsl
  -e ...`, nunca por edição direta de arquivo — isso mantém os ledgers de
  fonte/afirmação consistentes. Consultado **automaticamente nos tipos B e
  A**, depois do passo 1 (contexto coletado) e antes do passo 6
  (esqueleto). O tipo C nunca consulta.
- **Procedimentos e Informações** (operacional, continua no OneDrive) —
  leitura continua **sempre manual**, só com pedido expresso de Ricardo
  (inalterado).

Leia o `CLAUDE.md` do Ementário antes de consultar — ele governa estrutura
e convenções. A consulta:

1. Identifica a área do direito no contexto já coletado (dano moral,
   responsabilidade civil, direito do consumidor, contratos bancários,
   ações declaratórias/indenizatórias, ou outra que o Ementário já tenha)
   e lê o `wiki/domains/<área>.md` correspondente, se existir.
2. A partir dali, lê as teses ligadas em `wiki/concepts/` e as fontes em
   `wiki/sources/` (ementa/trecho sempre literal, com origem).
3. Registra o que encontrar no pacote de contexto com `origem:
   ementario-resolutivo` e `status: informada` — nunca
   `verificada_externamente` só por ter vindo do vault (mesma tabela de
   status de `contratos-agentes.md`). Vira tese aprovada, fonte selecionada
   ou parte do esqueleto somente por decisão explícita no passo 6.
4. Se não encontrar nada relevante para a área, segue normalmente — vault
   vazio não é pendência e não bloqueia a peça.
5. Não substitui pesquisa nova (`buscar-jurisprudencia`/
   `jusbrasil-jurisprudencia`, automática no tipo A) — o Ementário é o que
   já foi decidido/registrado antes; a pesquisa é o que busca precedente
   novo. Os dois podem coexistir na mesma execução.

`provenance.jsonl` continua sendo o ledger local e rastreável da matéria,
independente do vault. Não altere `nivel_peca` por causa do que a consulta
encontrar ou deixar de encontrar.

### 10. Gravação automática no vault — após publicação

Depois que `publicar_docx.py` retornar `[OK]` (passo Entrega), grave
automaticamente um resumo da matéria no vault, sem pedir — isso não é
consulta, é registro do que já aconteceu. Vault:
`C:\Users\ricar\OneDrive\Documentos\Cerébros\Pessoal\Procedimentos e Informações\`.
Leia o `CLAUDE.md` desse subvault antes de escrever, ele governa estrutura e
convenções.

1. Crie ou atualize `wiki/sources/peca-[tipo]_[matter_id]_[data].md` com
   frontmatter mínimo (`type: source`, `title`, `created`) e um resumo:
   tipo de peça, cliente, fatos essenciais, tese, pedidos, decisões
   registradas no `provenance.jsonl`, e status (publicada, hash do
   candidato). Sem prosa longa — é registro, não a peça em si.
2. Se o cliente já tem página em `wiki/entities/`, adicione um `[[wikilink]]`
   de volta para a nota nova e uma linha de atualização. Se não tem, crie a
   entidade seguindo a convenção kebab-case do subvault.
3. Referencie a nota nova em `wiki/index.md` — nunca deixe órfã.
4. Atualize `wiki/hot.md` do subvault com o fato novo, seguindo o limite de
   ~500 palavras e a regra de sobrescrever (não é histórico cumulativo).

Se a peça usou tese ou jurisprudência nova ou relevante (aprovada
explicitamente no passo 6, vinda do Ementário ou de pesquisa nova),
atualize também o **Ementário do Resolutivo**, seguindo o `CLAUDE.md` dele
— gravação via skill `claude-obsidian` (`save`/`wiki-ingest`) executada
com `wsl -e ...`, nunca edição direta de arquivo (mantém os ledgers
consistentes):
5. Tese nova ou refinada → cria ou atualiza a página em `wiki/concepts/`.
   Fonte nova → cria a página em `wiki/sources/` com ementa/trecho literal
   e origem completa. Nunca duplique o resumo operacional do passo 1-4 —
   referencie a matéria por `matter_id`, não copie o conteúdo dela.
6. Vincule a tese/fonte ao domínio correspondente em `wiki/domains/`.
7. Atualize `wiki/index.md` e `wiki/hot.md` do Ementário.

Isso roda uma vez por publicação bem-sucedida, silenciosamente — não pede
`AskUserQuestion` nem aprovação prévia, mas relate na mensagem de entrega que
o registro foi feito (uma linha basta, ou duas se os dois vaults foram
atualizados). Se a publicação falhar (`[ERRO]`), não grave nada em nenhum
vault.

## Nota sobre a integração das skills

Este fluxo combina:
- Classificação de nível (`nivel_peca` C/B/A) → decide profundidade, blocos, esqueleto e a rota de agentes (passo 1)
- `jusbrasil-jurisprudencia` → pesquisa de jurisprudência automática no tipo A (premissa do nível, sem pedido separado), nunca no tipo B/C salvo pedido expresso
- Consulta processual (andamento, publicação, movimentação) → não existe no plugin; não tente
- MCP `NotebookLM` → uso secundário e somente quando Ricardo pedir
- `esqueleto-peca` → estrutura obrigatória + ponto de aprovação via
  `AskUserQuestion` nos tipos A e B; nos tipos B/A também decide, bloco a
  bloco, a ênfase em negrito e o elemento visual planejado (seção "Legal
  Design planejado")
- `legal-design-rdaa` → não é acionada automaticamente por inteiro; a
  mecânica de ênfase em negrito (dosagem, limite) vive em
  `redacao-rdaa.md`, e a tabela de elementos visuais por destinatário
  (`legal-design-rdaa/SKILL.md` §2.4) é só consultada por `esqueleto-peca`
  quando um bloco genuinamente pede elemento visual — invocar a skill
  inteira continua exigindo pedido de Ricardo
- `playbook-modelos` → modelos de estrutura selecionados por `modelo_id`, sem aplicação automática de tese
- `contencioso-rdaa` → núcleo de escrita obrigatório no pacote entregue ao Codex (passo 7)
- `revisor-rdaa` → checklist de qualidade aplicado pelo Claude (passo 8)
- `docx` → entrega protegida
- Ementário do Resolutivo → consulta automática em B/A antes do esqueleto (disparada no passo 2, mecânica completa no passo 9); gravação automática de tese/fonte usada após publicação (passo 10)
- Procedimentos e Informações → leitura sempre manual; gravação automática de registro operacional após publicação (passo 10)
- `gestao-materias` → repositório de documentos-fonte (`DOC-XXX`/`source_id`) por matéria, fora deste fluxo; ver `skills/gestao-materias/SKILL.md`
