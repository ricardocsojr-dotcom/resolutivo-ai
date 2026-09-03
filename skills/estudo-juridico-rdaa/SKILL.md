---
name: estudo-juridico-rdaa
description: >
  Workflow de pesquisa jurídica profunda do RDAA — não produz peça processual,
  produz um estudo de pensamento visual (mapa de caso, fluxograma de tese,
  linha do tempo, matriz de precedentes) pra entender um tema a fundo,
  teoricamente e jurisprudencialmente, antes de decidir estratégia. Use quando
  Ricardo pedir pra "estudar a fundo" um tema, "montar um mapa do caso",
  "mapear a jurisprudência sobre", "entender esse instituto direito",
  "aprofundar antes de decidir a estratégia", ou qualquer variação que
  indique um mergulho teórico/jurisprudencial anterior e independente da
  redação de uma peça. Ative também quando o pedido for claramente sobre
  compreensão de um tema (abstrato ou de um caso concreto já em andamento),
  não sobre protocolar algo.
---

# Estudo Jurídico Profundo — RDAA

Isto não é `redigir-peca`. Não tem qualificação de partes, não tem pedido, não
vai a protocolo. É um **braço de estudo**: aprofundar um tema teoricamente e
jurisprudencialmente (quando o tema for jurídico) e entregar isso como um
estudo de pensamento visual — mapas, fluxogramas, linha do tempo — na
linguagem direta do Núcleo Único de Escrita do RDAA.

Serve como insumo para `contencioso-rdaa` (que decide estratégia de um caso
concreto) e para `redigir-peca` (que produz a peça em si) — não substitui
nenhum dos dois. Também não é `buscar-jurisprudencia` isolado: aquela skill
entrega ementas pontuais pra citar; esta orquestra teoria + jurisprudência +
lei + visual num único aprofundamento.

## Quando usar

- Ricardo quer entender a fundo um instituto ou tema jurídico, com ou sem
  caso concreto associado.
- Ricardo quer um "mapa do caso" — visão estruturada dos fatos, atores,
  teses possíveis e precedentes antes de decidir como agir.
- Ricardo pede pra mapear divergência jurisprudencial sobre um tema (visão
  de ambos os lados, não só o lado favorável).
- Qualquer pedido de aprofundamento que anteceda — e não substitua — a
  decisão estratégica ou a redação.

## O que esta skill não faz

- Não decide estratégia processual (isso é `contencioso-rdaa`, com base no
  que este estudo levantar).
- Não redige peça, não tem pedido, não vai a protocolo.
- Não inventa doutrina, autor, obra, página, jurisprudência ou dispositivo
  legal. Toda citação de lei/súmula/jurisprudência é literal e vem de fonte
  conferida (ver passos 3 e 4).
- Não consulta andamento processual (a capacidade foi removida do plugin).

## Fluxo

### 1. Delimitar o tema e o escopo

Antes de pesquisar, parafraseie o recorte em 1-2 frases e confirme com
Ricardo se não estiver óbvio pelo pedido — evita gastar esforço na direção
errada. Identifique:

- **Tema abstrato ou caso concreto?** Se for uma matéria já em andamento,
  identifique o `matter_id` em `.rdaa-run/` pra linkar o estudo ao estado
  compartilhado (passo 7). Se for tema abstrato sem matéria associada, siga
  sem `matter_id` — não crie matéria artificial só pra ter onde registrar.
- **Área do direito** — ajuda a decidir se vale consultar o Ementário do
  Resolutivo antes de pesquisar de novo (mesma lógica do passo 9 de
  `redigir-peca`, mas aqui é sempre automático, não só nos níveis B/A,
  porque esta skill inteira já é sobre aprofundamento).
- **Pergunta central do estudo** — o que precisa ficar respondido ao final.

### 2. Levantamento teórico

Construa o arcabouço conceitual do tema (institutos, requisitos, correntes
doutrinárias conhecidas). **Honestidade de fonte**: não há hoje uma fonte de
doutrina verificada conectada a este plugin (Jusbrasil doutrina não foi
habilitado como fonte automática) — trate esta camada como leitura
sistemática de conhecimento geral, não como citação de fonte externa
conferida. Nunca cite autor, obra, edição ou página específicos que você não
tenha certeza absoluta de que existem; se quiser nomear uma corrente
doutrinária amplamente consolidada, identifique-a como tal sem fabricar
referência bibliográfica precisa. Marque esse bloco no estudo como leitura
teórica, distinto dos blocos de jurisprudência e lei (que são citação
literal conferida).

### 3. Levantamento jurisprudencial

Acione `buscar-jurisprudencia` (que por sua vez usa `jusbrasil-jurisprudencia`
como fonte primária). Diferente do uso pontual dessa skill, aqui o objetivo é
mapear o **panorama**, não só achar uma ementa pra citar:

- Busque precedentes **favoráveis e contrários** — um estudo de verdade
  mostra a divergência, não só o lado que interessa.
- Priorize STJ, depois TJSP, depois TJMG, depois demais tribunais conforme a
  origem do tema (mesma ordem do `CLAUDE.md`).
- Toda ementa é citação literal com origem, nunca paráfrase — mesma regra de
  sempre.

### 4. Levantamento legal

Acione `lei-e-sumula` para os dispositivos e súmulas que fundamentam o tema.
Confira vigência antes de citar (mesma regra da própria skill).

### 5. Mapeamento visual

Antes de montar a página, **carregue as skills `artifact-design` e
`artifact-diagramming`** — são pré-requisito do próprio funcionamento do
Artifact e calibram o quanto de investimento visual o estudo merece.

Monte os elementos visuais que fizerem sentido pro tema (nem todo estudo
precisa de todos):

| Elemento | Quando usar |
|---|---|
| Mapa conceitual da tese | Tema com múltiplos institutos/requisitos relacionados entre si |
| Linha do tempo | Houver caso concreto com fatos datados |
| Fluxograma de requisitos/decisão | Tese com etapas lógicas encadeadas (ex.: "configura dano moral se A e (B ou C)") |
| Matriz de precedentes | Jurisprudência dividida — cruzar tribunal × favorável/contrário × peso |

Os princípios de conteúdo de `legal-design-rdaa` (hierarquia clara, nada
ornamental, nunca inventar valor/fato, precisão vocabular) valem aqui
também — mas sem a restrição de impressão em preto e branco, que é
específica de peça protocolada. O estudo é pra tela, pode usar cor com
função.

### 6. Texto de acompanhamento

Escreva seguindo o Núcleo Único de Escrita do RDAA
(`contencioso-rdaa/references/redacao-rdaa.md` — leitura obrigatória):
linguagem direta, ordem direta, tese fundida na primeira frase de cada
parágrafo, sem firulas nem expressões arcaicas. A estrutura não é a de uma
peça (sem "dos fatos/do direito/dos pedidos") — organize por sub-tema do
estudo, cada seção respondendo uma pergunta específica.

### 7. Publicar como Artifact

Publique a página (favicon, título específico do tema — não genérico).
Diagramas em Mermaid/SVG conforme `artifact-diagramming`. Entregue o link.

### 8. Registrar no estado compartilhado (se houver `matter_id`)

Se o estudo estiver ligado a uma matéria, registre jurisprudência e lei
usadas com `contexto_rdaa.py`:

```
python3 skills/revisor-rdaa/scripts/contexto_rdaa.py .rdaa-run/<matter_id> register \
  --source-type jurisprudencia --content-json <arquivo.json>
```

Mesma regra de sempre: só `verificada_externamente` quando a fonte foi
conferida nesta execução (passos 3 e 4 já conferem).

### 9. Gravação automática no Cérebro-Ricar

Ao final de todo estudo publicado, grave automaticamente no Cérebro-Ricar
(`C:\Users\ricar\cerebro-ricar\`) — sem pedir, do mesmo jeito que `redigir-peca`
faz (script `registrar_cerebro.py`). Leia `CLAUDE.md` do Cérebro antes de
escrever.

Crie/atualize os seguintes arquivos em `wiki/`:

1. **Tese nova ou refinada** → `wiki/concepts/[kebab-case].md`
   - Frontmatter: `type: concept`, `title`, `domain: [area]`, `status: aprovada`
   - Conteúdo: resumo da tese + fundamento legal + link pro Artifact publicado
   - Linkada ao domain: `[[domain-link]]`

2. **Fonte jurisprudência/lei nova** → `wiki/sources/[PREC-NNN ou LEI-NNN].md`
   - Frontmatter: `type: source`, `title`, `court`, `date`, `origin: artifact`
   - Conteúdo: **ementa/trecho literal** (nunca resumo)
   - Referencie o link do Artifact, não copie tudo

3. **Vincule ao domínio** → atualizar `wiki/domains/[area].md`
   - Adicionar wikilink da tese/fonte nova no corpo do arquivo

4. **Atualize índices**
   - `index.json` → recount automático (script faz)
   - `hot.md` → adicione linha "Estudo novo: [tema] [[artifact-link]]"

**Script de automação:**
```bash
python3 skills/estudo-juridico-rdaa/scripts/registrar_estudo_cerebro.py \
  --theme "Tema do estudo" \
  --artifact-url "https://artifact.link" \
  --concepts "[tese1, tese2]" \
  --sources "[PREC-001, LEI-CIVIL]" \
  --domain "direito-contratual"
```

Relate na entrega que o registro foi feito (uma linha basta). Se o estudo
não produziu tese ou fonte nova (ex.: confirmou o que já tá no Cérebro,
sem achado novo), não crie registro redundante — mencione que não houve
complemento por esse motivo.

## Nota sobre integração

- `buscar-jurisprudencia` / `jusbrasil-jurisprudencia` → jurisprudência (passo 3)
- `lei-e-sumula` → lei e súmula (passo 4)
- `legal-design-rdaa` → princípios de conteúdo visual (passo 5), adaptados pra tela
- `artifact-design` / `artifact-diagramming` → execução técnica do Artifact (passo 5, pré-requisito)
- Núcleo de escrita RDAA (`contencioso-rdaa/references/redacao-rdaa.md`) → tom e estrutura do texto (passo 6)
- `contencioso-rdaa` → consome o estudo pra decidir estratégia (não é acionado por esta skill, é quem usa a saída dela depois)
- `claude-obsidian` (`save`/`wiki-ingest`) → gravação no Ementário (passo 9)
