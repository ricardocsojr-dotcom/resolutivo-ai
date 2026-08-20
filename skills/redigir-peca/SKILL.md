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
- Nenhum tipo consulta o vault automaticamente. O vault permanece fora do
  fluxo padrão até que Ricardo peça expressamente essa capacidade em uma etapa
  futura.

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

Antes de acionar agentes adicionais, o orquestrador deve consultar a rota
executável e persistir sua decisão:

```bash
python3 skills/revisor-rdaa/scripts/semantica_rdaa.py \
  .rdaa-run/<matter_id> route [--level <nivel>] [--agent <agente>]
```

O resultado contém `selected` e `omitted`. Sem `nivel_risco`/`risk_level` ou
risco explicitamente registrado no contexto, a rota seleciona apenas revisão
semântica e revisor; conselho e crítico ficam em `omitted`. O tipo da peça, a
classificação automática C/B/A, a extensão do texto e palavras do contexto não
substituem uma declaração explícita de risco para essa decisão. Se Ricardo pedir
expressamente conselho ou crítico, use `--agent` como override e o manifesto
registrará `override_explicito`.

### 2. Organizar o material explicitamente fornecido

Não consulte o vault automaticamente em nenhum nível. Trabalhe somente com os
fatos, documentos, decisões, teses, fontes e pedidos que Ricardo fornecer ou
selecionar nesta execução. A aprovação de modelo ou peça anterior não aprova o
caso atual.

- **Tipo B**: organize o que já existe no processo, identifique lacunas
  objetivas, proponha desenvolvimento de explicações e indique se Legal Design
  ou ilustração pode melhorar a compreensão. Não busque base no vault.
- **Tipo A**: organize o conjunto completo de material fornecido e as fontes
  selecionadas para a peça premium. Não busque base no vault.
- Se Ricardo pedir expressamente uma consulta futura ao vault, trate-a como
  capacidade adicional daquela execução, registre a origem e não altere o tipo
  automaticamente.

### 3. Consultar o processo — OPCIONAL

A existência de número de processo **não** dispara consulta automática ao
CNJ/DataJud. Execute `consultar-processo` somente se Ricardo pedir andamento,
última decisão, movimentação, prazo ou situação atual, ou se o contexto trouxer
uma instrução explícita para consulta processual.

Se a peça puder ser redigida com os fatos já fornecidos, siga diretamente para
a pesquisa e a estruturação. Se alguma informação externa for necessária mas a
consulta não tiver sido solicitada, registre `[PONTO A CONFERIR]`/pendência e não
invente o dado. A consulta continua disponível como skill independente.

### 4. Buscar jurisprudência

Depois de cada pesquisa efetivamente conferida, registre as fontes no estado da
matéria com `contexto_rdaa.py register_research`, preservando o tipo, origem,
localização, trecho literal e, quando disponível, os dados de conferência. Não
atribua `verificada_externamente` a conteúdo apenas reaproveitado de mensagem,
arquivo interno ou histórico. A fonte deve ser selecionada no esqueleto antes
da redação.

- **Tipo B**: não pesquise automaticamente. Pesquise somente se Ricardo pedir
  ou se houver autorização explícita no plano desta matéria. A peça pode ser
  desenvolvida com os documentos e fundamentos já presentes no processo.
- **Tipo A**: a pesquisa ampla pode ser autorizada e, quando estiver no plano
  aprovado da matéria, deve ser realizada antes do esqueleto. A seleção de
  fontes continua explícita e não representa conclusão automática de pertinência.
- **Tipo C**: não faça pesquisa de jurisprudência ou legislação como parte do
  fluxo padrão.

### 5. Consultar NotebookLM (se disponível)

Uso secundário e somente quando Ricardo pedir. A consulta não é automática em
nenhum nível e não substitui a origem registrada das fontes.

### 6. Montar o esqueleto e aguardar aprovação — ETAPA OBRIGATÓRIA

Execute a skill `esqueleto-peca` para montar a estrutura obrigatória da
peça dos tipos A e B. Inclua requisitos formais do CPC, fontes selecionadas
quando houver pesquisa, teses e decisões explicitamente aprovadas, e o modelo
de estrutura quando um `modelo_id` tiver sido escolhido. Preencha também
`esqueleto.fontes_selecionadas`, `esqueleto.fontes_status`,
`esqueleto.aprovacao` e os `source_ids` de cada bloco. O contexto de redação
deve declarar `nivel_peca`, `modo_redacao`, `redacao_por_blocos` e
`exigir_esqueleto: true`. O tipo C não passa por esta etapa no fluxo padrão.

**Pare aqui de verdade — use a tool `AskUserQuestion`.** Apresente o
esqueleto ao Ricardo e chame `AskUserQuestion` com opções como "aprovar
esqueleto como está" / "pedir ajuste antes de seguir". Uma frase em prosa
tipo "aguardo seu ok" não basta: num fluxo autônomo o modelo pode
simplesmente seguir sem que nada force a pausa. É a chamada da tool que
bloqueia de fato esperando resposta. Não escreva a peça por extenso antes
da aprovação recebida por essa tool — isso existe pra evitar redigir em
cima de tese ou jurisprudência errada, e pra controlar o que entra no
aprovação da estrutura e para preservar as fontes explicitamente selecionadas.

### 7. Redigir no padrão RDAA

Antes de chamar a skill de redação, monte o pacote `redator` com
`skills/revisor-rdaa/scripts/contexto_rdaa.py`. Passe apenas fatos, teses
aprovadas ou explicitamente selecionadas, decisões aplicáveis, fontes/citações
selecionadas, pendências, regras necessárias, `nivel_peca`, `modo_redacao`,
`redacao_por_blocos` e o `modelo_estrutura` selecionado quando houver. Não
repasse o histórico integral ou o provenance bruto.

Só depois do esqueleto aprovado e validado. Use a skill `contencioso-rdaa`
(ou `dano-moral-rct` se for ação de dano moral) para a redação. O pacote do
redator recebe o esqueleto aprovado e as fontes selecionadas, não o
provenance bruto inteiro. Qualquer uma
das duas camadas parte do mesmo núcleo de escrita —
`contencioso-rdaa/references/redacao-rdaa.md` — lido como primeiro passo
obrigatório (a seção de dosagem do núcleo diz o que acrescentar por tipo
de peça). Siga estritamente:
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

### 7.5. Crítica estratégica — antes da revisão de qualidade

Somente se `critico-rdaa` estiver em `route.selected`, monte o pacote
`critico` e invoque a skill `critico-rdaa` como **subagente isolado** (Agent
tool), passando a peça recém-redigida junto apenas dos fatos, fontes, evidências,
teses e hipóteses necessários. Se o crítico estiver em `route.omitted`, não o
acione automaticamente; registre a omissão no manifesto e siga para o revisor.
Um pedido explícito de Ricardo pode selecioná-lo por override. Nunca passe o
histórico desta conversa, o raciocínio privado do redator ou o esqueleto
aprovado. O isolamento é o que garante que o crítico julgue com olhos frescos,
sem herdar o raciocínio de quem redigiu.

- Se o crítico apontar vulnerabilidades reais ou teses não exploradas:
  volte automaticamente ao passo 7 para uma rodada de correção com
  `contencioso-rdaa`/`dano-moral-rct` — não pare para perguntar, isso
  aconteceria só uma vez, de forma autônoma, para manter o fluxo rápido em
  peças B/A. Depois de corrigir, siga para o passo 8, mesmo que ainda
  reste alguma vulnerabilidade menor não resolvida (guarde essa pendência
  para relatar na entrega).
- Se não houver vulnerabilidade relevante, siga direto para o passo 8.
- Guarde o relatório do crítico (achados e o que mudou, ou "sem
  divergência relevante") para citar na seção Entrega.

### 7.75. Camada opcional de estilo Flávia

Somente quando o pedido ou o contexto declarar `estilo_alvo: flavia`, invoque
`estilo-flavia-rdaa` como subagente isolado depois da redação e da crítica
estratégica, se houver. Passe o texto existente, o tipo de peça e o pacote factual
mínimo. Não passe histórico da conversa, raciocínio privado, provenance bruto,
vault ou fontes não selecionadas. A camada pode rodar no máximo três rodadas e
não pode alterar fatos, tese, pedidos, fontes, IDs ou estrutura obrigatória.

Depois da saída, rode novamente `verificar_estilo.py` e o checklist do revisor.
Se houver violação de regra RDAA, a camada deve ser corrigida ou rejeitada antes
da geração do DOCX candidato. Sem `estilo_alvo: flavia`, não acione a skill por
inferência de assinatura, destinatário ou nome mencionado no documento.

### 8. Revisar

Após redigir (e após a rodada de crítica estratégica em B/A), monte o pacote
`revisor` com `contexto_rdaa.py`, incluindo somente regras, fontes/citações
utilizadas, fatos necessários para conferência, pendências e o relatório
explícito do crítico quando houver. Em seguida, rode o checklist da skill
`revisor-rdaa` — incluindo `scripts/verificar_estilo.py`
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
seguir para a entrega. Isso inclui travessão recorrente, ponto-e-vírgula em
cadeia, tricolon de negação, abertura defensiva recorrente, qualquer dois-pontos e
qualquer aposto explicativo entre parênteses ou travessões pareados. A abertura
negativa isolada deve ser avaliada pela função argumentativa e não bloqueada por
palavra-chave. Não pare para perguntar quando a correção for apenas de forma.
Só fica para relatar ao Ricardo o que for ambíguo o suficiente para exigir
julgamento dele, como um `[PONTO A CONFERIR]`. Um relatório que aponta vício e
não é seguido de correção equivale a não ter revisado.


## Entrega

Gere o `.docx` **candidato** usando a skill `formatar-peca` em modo nativo,
`construir_peca.py`, sempre em caminho temporário ou de staging — nunca grave
diretamente no caminho final e nunca use a skill genérica `docx`, que não
aplica o padrão visual RDAA. Em seguida, encaminhe o candidato ao
`publicar_docx.py`. Só entregue o documento final depois que o publicador
retornar `[OK]`. O publicador executa o gate, preserva backup, mantém o arquivo
anterior se houver falha e substitui o destino de forma atômica. Nome padrão do
arquivo publicado: `[tipo_peca]_[numero_processo]_[data].docx`

Quando `critico-rdaa` estiver em `route.selected`, a mensagem de entrega a
Ricardo sempre relata o resultado do passo 7.5: o que o crítico apontou e o que
foi corrigido por causa disso, ou que não houve divergência relevante. Quando o
agente estiver em `route.omitted`, relate que a crítica não foi acionada porque
não havia risco explícito ou pedido de override. A rodada de correção
automática do passo 7.5 não pede aprovação prévia, mas nunca fica
invisível — Ricardo precisa saber que a peça foi reescrita e por quê antes
de protocolar.

### 9. Ementário e vault — capacidade futura, sem execução automática

Nenhum nível consulta ou grava no vault automaticamente neste fluxo. O
`provenance.jsonl` continua sendo o ledger local e rastreável da matéria.

Se Ricardo solicitar expressamente uma consulta ou gravação no vault em uma
execução futura, trate isso como uma operação separada, com origem, decisão,
resultado e possibilidade de auditoria. Não transforme o vault em premissa do
tipo B, não altere o tipo por causa do conteúdo encontrado e não grave
ementas ou teses sem decisão explícita.

## Nota sobre a integração das skills

Este fluxo combina:
- Classificação de nível (`nivel_peca` C/B/A) → decide profundidade, blocos e esqueleto
- `jusbrasil-jurisprudencia` → pesquisa de jurisprudência somente quando autorizada e selecionada
- MCP `CNJ` → dados processuais somente quando `consultar-processo` ou uma consulta estatística/publicação for acionada explicitamente
- MCP `NotebookLM` → uso secundário e somente quando Ricardo pedir
- `esqueleto-peca` → estrutura obrigatória + ponto de aprovação via
  `AskUserQuestion` nos tipos A e B
- `playbook-modelos` → modelos de estrutura selecionados por `modelo_id`, sem aplicação automática de tese
- `contencioso-rdaa` / `dano-moral-rct` → redação
- `critico-rdaa` → crítica estratégica isolada, conforme rota de risco e autorização
- `revisor-rdaa` → qualidade
- `docx` → entrega protegida
- Vault → capacidade futura, sem consulta ou gravação automática
