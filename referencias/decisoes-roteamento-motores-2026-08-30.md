# Registro de decisões — roteamento de motores (30/08/2026)

> Registro narrativo de uma sessão longa de redesenho do roteamento de IA do
> RDAA. A tabela prescritiva vive em `roteamento-ia.md`; este arquivo é o
> "porquê" por trás dela — útil pra não repetir raciocínio já feito, não pra
> seguir como instrução.

## 1. Ponto de partida

A sessão começou com dois subagentes novos já prontos (`antigravity-worker`,
`codex-worker`), inspirados no modelo de persona do
[block/buzz](https://github.com/block/buzz). Ricardo então pediu uma
simulação: se o Resolutivo.AI fosse uma empresa, quem seriam os
funcionários? Isso levou a um primeiro quadro de "cargos" (redator sênior,
crítico, revisor, paralegal de esqueleto etc.), todos mapeados pra Claude,
com `codex-worker`/`antigravity-worker` como "consultoria externa pontual".

## 2. Estudo do block/buzz

Repositório clonado em `C:\Projetos\_estudo-buzz\buzz` (não faz parte deste
repo). Achados relevantes:

- **`buzz-persona`**: cada persona é um arquivo `.persona.md` (YAML
  frontmatter + corpo = system prompt) que declara seu próprio `model` e
  `runtime` (motor de execução). Um "pack" (`plugin.json`) agrupa várias
  personas com defaults compartilhados. Isso é o que inspirou a ideia de
  roteamento declarativo por papel, em vez de motor hardcoded em prosa.
- **`buzz-workflow`**: fluxo definido em YAML (trigger → steps tipados),
  incluindo uma ação `RequestApproval` — o equivalente exato do nosso
  `AskUserQuestion` no gate de aprovação do esqueleto, só que como dado
  validável em vez de instrução em prosa.
- **`buzz-acp/pool.rs` + `pool_lifecycle.rs`**: motor de concorrência pra um
  relay multiusuário sempre ligado (pool de agentes, steering de turno,
  circuit breaker, wake assíncrono). Avaliado como **engenharia de escala
  que não temos** — não vale copiar pro nosso caso de um advogado, uma
  sessão por vez. Auditoria do Codex confirmou: "o pool ACP inteiro é
  engenharia de escala que não temos... deve ser evitado até existir
  concorrência de verdade."
- **`buzz-dev-mcp`**: servidor MCP que dá shell a um agente, com isolamento
  por sessão (tempdir próprio, processo efêmero por chamada, output
  truncado com artifact de backup, `KillGroup` matando a árvore de processo
  inteira no timeout). **Esse padrão mínimo vale copiar** em qualquer script
  nosso que rode subprocess — não o servidor inteiro, só o invólucro de
  execução segura.

## 3. Agent Teams (feature nativa do Claude Code)

Ricardo trouxe um artigo sobre o modo experimental "Agent Teams" do próprio
Claude Code (líder + colegas paralelos, fila de tarefas compartilhada,
mensagem ponto-a-ponto, lock de arquivo — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`,
já disponível na versão instalada, 2.1.246). Avaliado e **não adotado**: o
ganho real seria só no pedaço genuinamente paralelo do fluxo (pesquisa +
cálculo + leitura de autos, que hoje roda em série sem precisar), mas o
modelo de mensagem livre entre colegas conflita com o isolamento
deliberado do `critico-rdaa` ("olhos frescos" depende de não herdar o
raciocínio do redator), e cada colega é uma sessão paga própria — custo
multiplicado sem necessidade clara pro volume atual do escritório.

## 4. A virada — "todo o roteamento está indo pro Claude"

Ricardo notou que o quadro de cargos concentrava quase tudo em Claude,
inclusive depois de mover o crítico pro Codex. Ponto seu: "sinto que a sua
arquitetura está sempre me limitando", desta vez aplicado à autoalocação de
trabalho, não à disposição de explorar ferramenta nova.

Pedido explícito: o Codex auditar, de forma adversarial, o próprio quadro
que eu tinha desenhado — pergunta direta, "existe papel alocado ao Claude
sem justificativa técnica, só porque quem desenhou o quadro é o próprio
Claude decidindo o próprio papel?".

### Veredito do Codex (auditoria adversarial, íntegra preservada)

> "o desenho concentrou Claude em quase tudo que confere controle
> intelectual do pipeline e deixou Codex apenas como fiscal. Isso não é
> arquitetura de qualidade; é centralização autojustificada."

Papéis que o Codex apontou como autoalocação sem justificativa técnica
real: classificação C/B/A (deveria ser rubrica determinística), consulta ao
Ementário e pesquisa Jusbrasil (recuperação mecânica, não inteligência),
esqueleto ("template + requisito processual, Claude é excesso"), Conselho
reusando o mesmo motor da redação ("a pior autoalocação: preserva os
mesmos vieses e pontos cegos da primeira camada"), correção de achado
objetivo devolvida ao Claude quando o próprio Codex já poderia corrigir
direto, e a própria redação ("preferência do autor do quadro, não critério
técnico" sem teste cego comparativo).

Papéis que o Codex considerou tecnicamente justificados como estão: leitura
de documento longo via Antigravity/Gemini, cálculo judicial em Python puro,
e crítica adversarial em motor diferente do redator.

### Decisão consolidada

- **Redigir a peça → Codex** (nível B; nível A fica com Claude até um nível
  B rodar de verdade por esse esquema — decisão explícita de não aplicar a
  troca no produto premium do escritório sem validação prévia).
- **Crítica + revisor-detecção se fundem** num único pass de "validação" no
  Claude — dois passes separados só faziam sentido quando os dois
  precisavam não ser o motor do redator; virando um só motor de auditoria,
  vira um só pass.
- **Correção de achado objetivo → quem escreveu corrige direto** (sem ida e
  volta desnecessária); só achado que exige julgamento de voz/tese volta
  pro Claude.
- **Conselho nunca reusa o motor do redator.**
- Regra geral nova: **cada papel do fluxo declara seu motor atual como dado
  editável**, não como decisão embutida em prosa dentro de
  `redigir-peca/SKILL.md` — ver `roteamento-ia.md` tabela revisada.

## 5. Legal Design — padrão de ênfase e planejamento no esqueleto

Trilha paralela, já **committada** (`9c5b1de`): nova regra de ênfase em
negrito por oração curta (não termo isolado, não parágrafo inteiro), limite
de uma por tópico, e uma seção nova "Legal Design planejado" no
`esqueleto-peca` que decide, bloco a bloco, onde vale ênfase ou elemento
visual **antes** da redação. Detalhes completos em
`skills/contencioso-rdaa/references/redacao-rdaa.md` e
`skills/esqueleto-peca/SKILL.md`.

## 6. Teste real de pipeline — Agravo de Instrumento 5555700-49.2026.8.09.0107

Rodado com um caso real (TJ-GO, desconsideração inversa de personalidade
jurídica, `Report01788107047031.pdf`, 103 páginas). Cronômetro completo:

| Etapa | Duração |
|---|---|
| Conversão do PDF | 1 min |
| Extração via `antigravity-worker` | ~15 min de agente (achou que o "agravo interno" pedido já tinha sido julgado — mudou o objetivo pra Embargos de Declaração) |
| Tempestividade, classificação, esqueleto (3 reformulações reais de estratégia) | ~20 min |
| Pesquisa Jusbrasil real (derrubou uma tese de "ordem pública" que eu tinha proposto sem fonte) | ~11 min |
| Consolidação com 3 precedentes STJ trazidos por Ricardo, verificados no Jusbrasil | ~7 min |
| Redação completa | ~3 min |
| Crítica via `codex-worker` (achou contradição lógica real no pedido) + verificação factual minha | ~9 min |
| **Total corrido** | **2h46min** (~55min de trabalho de máquina; o resto foi decisão estratégica do Ricardo) |

### Gaps de skill descobertos

- `esqueleto-peca` não cobre Embargos de Declaração nem Recurso Especial —
  só petição inicial, contestação, apelação e agravo de instrumento.
  Precisa de checklist próprio pra cada um.
- Não existe trava automática de "isso já foi julgado, confira antes de
  redigir" — descoberto por leitura manual do `antigravity-worker`, não por
  gate do sistema.

### Achado de custo real

As três chamadas de subagente (`antigravity-worker` + 2x `codex-worker`)
consumiram **371 mil tokens só de wrapper** (112k + 170k + 88k), sem contar
o custo da sessão principal. Causa raiz: `codex-worker`/`antigravity-worker`
via `Agent` tool são sessões Claude autônomas completas — o "mensageiro"
também raciocina, e isso conta no limite de uso tanto quanto qualquer outra
sessão, mesmo quando quem faz o trabalho pesado é outro motor. Dois
problemas concretos:

1. **Caminho documentado errado** em `codex-worker.md` (apontava pro plugin
   errado) — cada chamada gastava uma tentativa falha antes de achar o
   caminho certo. **Corrigido** (`ls -t` resolve a versão instalada num
   comando só).
2. **Subagente usado até quando a tarefa era de um passo só** (ex.: "manda
   este texto pro Codex e devolve a resposta" não precisa de exploração
   autônoma). Regra nova adotada: delegação de um passo só chama o CLI
   direto via Bash na sessão principal; `Agent` tool fica reservado pra
   tarefa que precisa de exploração real e multi-passo.

## 7. Backlog consolidado (nenhum item implementado ainda, exceto o já commitado na seção 5)

1. Testar Codex como redator numa peça nível B real, comparando qualidade
   contra uma versão Claude da mesma peça, antes de mexer em qualquer
   skill de produção.
2. Criar `skills/redigir-peca/references/roteamento-motores.md` — tabela
   declarativa papel→motor dentro do próprio plugin (hoje só existe em
   `roteamento-ia.md`, na raiz do repo).
3. Fundir `critico-rdaa` + `revisor-rdaa` (detecção) num único pacote de
   validação.
4. Ajustar `redigir-peca/SKILL.md` (passo 7 em diante) pra refletir
   Codex-redator + loop de validação com teto de rodadas.
5. Tornar a classificação C/B/A um script determinístico.
6. Separar busca mecânica de julgamento de relevância no Ementário/Jusbrasil
   (exploração, não decidida).
7. Testar esqueleto como template mais determinístico em casos simples B
   (exploração, não decidida).
8. Adotar o padrão mínimo do `buzz-dev-mcp` (matar árvore de processo,
   output limitado + artifact) em scripts que já rodam subprocess.
9. Decidir se o esquema Codex-redator vale pro nível A, só depois do item 1.
10. Checklist de Embargos de Declaração e Recurso Especial em
    `esqueleto-peca` (achado no teste real, seção 6).
11. Passo de checagem de estágio processual atual antes de montar esqueleto,
    quando houver documento de processo anexado (achado no teste real).
12. Aplicar a mesma correção de invocação (item de custo, seção 6) em
    `antigravity-worker.md`, se o mesmo tipo de bug de caminho existir lá.

## 8. Decisão posterior ao teste — sem agentes-mensageiros

Depois de medir os 371 mil tokens de wrapper, Ricardo decidiu retirar os dois
agentes-mensageiros do fluxo e do repositório. A rota operacional passa a ser:

1. Codex redige por chamada direta `codex exec`;
2. Antigravity critica por chamada direta `agy --print`, sem alterar estado;
3. Claude valida e corrige o rascunho, antes dos gates determinísticos e da
   publicação protegida.

O histórico acima permanece como evidência do teste; as referências aos
workers descrevem a arquitetura que foi descartada, não instrução vigente.

## 9. Consolidação final do mesmo dia — contrato comum e executor direto

Ricardo consolidou a decisão: **Codex é o redator de C/B/A, Antigravity é o
crítico e Claude é o corretor/validador**. O nível controla profundidade, não
o motor. Foram implementados `AGENTS.md` como contrato comum e um executor
local mínimo que envia prompts por stdin diretamente às duas CLIs, sem
agente-mensageiro. As camadas RCT/Flávia rodam dentro da mesma chamada do
Codex, sem novo modelo.

No teste real do executor, uma chamada mínima do Antigravity consumiu cerca
de **37 mil tokens de entrada antes do conteúdo útil**, mesmo sem wrapper.
Isso é custo-base da CLI/harness atual, não do script. Consequência operacional:
uma única crítica por peça B/A, pacote curto, sem loop automático; extrações
simples usam esforço baixo/médio e peças C não ganham crítica por padrão.

Também foram corrigidos dois defeitos independentes do desenho de motores:
o hook `SessionEnd` procurava `manifest.json` em vez do canônico
`run_manifest.json`, e o teste de identidade não era coletado pelo pytest.
