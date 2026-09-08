---
name: romano-donadel-slide-style
description: Use when creating RDAA slides. Match HTML and PPTX.
---

# Apresentações Romano Donadel

## Quando usar e objetivo

Criar, revisar ou padronizar apresentações RD em HTML, PPTX e PDF. O padrão é apresentação conduzida pelo orador, não relatório autoexplicativo. A marca é fixa; a composição varia com a mensagem. Mais vida significa escala, ritmo, detalhe gráfico funcional e relações visuais, não mais cores, cartões ou efeitos.

Antes de criar, ler `references/identidade-visual-extraida.md` e `references/direcao-visual-e-paridade.md`. Para briefing reutilizável, usar `templates/prompt-slide-rdaa.md`.

## 1. Precedência e identidade inegociável

Orientação explícita atual de Ricardo > esta skill > padrões extraídos históricos > inspiração externa. Skills de diagrama fornecem geometria e conexões, nunca sua paleta escura, fonte monoespaçada ou layout de dashboard por padrão. Regras de petição (justificação, Tahoma, scroll vertical) não se aplicam aos slides.

| Papel | Cor | Uso |
|---|---|---|
| Tipografia principal | `#63666A` | Títulos, corpo, rótulos, números e legendas; cinza oficial da marca |
| Estrutura e destaque | `#F7A800` | Linhas, contornos, quadros, conectores, nós, organogramas, geometria e ênfase seletiva |
| Fundo | `#FFFFFF` | Superfície predominante |
| Contraste excepcional | `#000000` | Informação focal que realmente necessite mais contraste, não default dos títulos |

Tons neutros claros podem derivar do cinza para planos secundários. Não introduzir azul-marinho/Dark Slate, dourado metálico, gradientes decorativos ou sombras como linguagem da marca. Laranja não é cor de todo o texto: manter rótulos em cinza sobre estruturas laranja. Evitar texto pequeno laranja sobre branco por contraste insuficiente. Se um fundo laranja comprometer o contraste, trocar preenchimento por contorno.

Verde e vermelho são exceções semânticas: somente para status comprovado, risco ou comparação em que acrescentem informação necessária. Usar pontualmente, com rótulo/legenda e significado não dependente só da cor. Não pintar a tese adversária de vermelho nem a nossa de verde por identidade de parte. Não preencher grandes painéis com semáforo por padrão.

Logo oficial `assets/logo_romano_donadel.png`: proporção, transparência e cores intactas; canto superior direito nos slides de conteúdo, com área de respiro. Não redesenhar a marca. Consultar e copiar `templates/romano-donadel-base.pptx` para o projeto como referência nativa; seus layouts não obrigam repetir a mesma composição.

## 2. Tipografia Lato real, não apenas declarada

Lato Regular para textos, Bold para títulos/rótulos e Heavy/Black pontual para ênfase. Não usar todos os textos em bold. Não fazer fallback silencioso para Arial ou fonte do sistema.

Verificar disponibilidade no renderizador, incluindo fontes do usuário, fontes incorporadas e fontes do Office. Nome `Lato` no XML não comprova renderização; ausência em Windows/Fonts também não comprova ausência total. Verificar as fontes efetivamente usadas no PDF e nos renders.

Preferir arquivos locais licenciados/fornecidos, empacotados com licença quando permitido. No HTML, usar `@font-face` local ou incorporado; não depender obrigatoriamente de Google Fonts. Esperar `document.fonts.ready` antes de captura/exportação. Se Lato não puder ser renderizada, informar e resolver antes de aprovação final; não instalar/baixar fontes silenciosamente.

Escala de referência para PPTX 13⅓ × 7½ polegadas: títulos 28–36 pt, texto principal/rótulos 18–24 pt, notas de fonte 10–12 pt. São faixas de partida, não motivo para estourar o quadro. No canvas HTML 1920×1080, mapear proporcionalmente a mesma composição física; não reaproveitar os números em pt como px. Texto substantivo em 9–12 pt é antipadrão. Se não couber, sintetizar, redesenhar ou dividir o slide; não encolher a fonte.

## 3. Narrativa, densidade e composição

Uma mensagem principal por slide. Título curto expressa a relação, pergunta ou conclusão sustentada; não precisa anunciar vitória. Em slides expositivos, meta inicial de 25–45 palavras visíveis, excluindo fonte e rodapé; ultrapassar exige justificativa. O limite antigo de oito palavras por bullet não é absoluto: preservar precisão técnica e condições relevantes. Menos texto não significa texto pequeno.

Antes do código, registrar para cada slide: mensagem, fonte, estado da afirmação (fato/decisão/pedido/hipótese), arquétipo, elemento focal, relação visual, texto visível e material retirado para apoio. Não criar notas do apresentador sem pedido; manter detalhes no documento de conteúdo-fonte.

O visual principal deve ocupar parcela dominante da área útil. Usar respiro deliberado, não cartões enormes com texto miúdo num canto. Não aumentar contêineres para simular preenchimento; trabalhar escala dos próprios elementos, alinhamento e distribuição.

Repertório: mapa de relações, bifurcação de teses, linha do tempo com marcos e faixas temporais, comparação sobre eixo comum, organograma, cadeia causal, camadas de prova, detalhe documental ampliado, composição editorial assimétrica, fotografia documental autorizada com anotações, gráfico com dados reais. Matriz 2×2 exige dois eixos reais; quatro caixas arbitrárias não são matriz. Chevron precisa ser uma forma direcional conectada; quatro cartões não são timeline.

Detalhes funcionais: conectores com sentido, rótulos de ligação, linhas-guia, marcadores de etapas, recortes, contornos de ênfase, inset de documento, pequenas legendas e agrupamentos. Ícones isolados, escudos genéricos e emojis não substituem um diagrama. Não exigir um ícone em cada bloco. Para diagramas, desenhar conexões atrás dos nós, evitar cruzamentos e manter rótulos legíveis.

Variar arquiteturas entre páginas. Não repetir grades de cartões em slides consecutivos sem motivo narrativo. Na exploração de estilo, mostrar três composições realmente distintas do mesmo conteúdo (não três paletas), com as cores RD fixas. Não gerar três decks completos para escolher estilo.

## 3.5 Univocidade Semântica de Dados Visuais (regra crítica, nunca dispensável)

O receptor não é um sócio nem quem redigiu o slide. É o cliente, o juiz, o desembargador — alguém fora da zona de controle do caso. Ele bate o olho uma vez. **Se ele precisar ler a legenda pequena abaixo para entender a relação entre dois números, o slide já falhou**, mesmo que o texto de apoio esteja correto. Não existe correcão via texto pequeno para uma estrutura visual ambígua.

**O erro-padrão a evitar:** colocar dois números grandes lado a lado, no mesmo estilo visual (mesmo tamanho, mesma posição, mesmo peso), quando eles pertencem a categorias semânticas diferentes na argumentação — devido vs. pago, alegado vs. provado, pedido vs. concedido, bruto vs. líquido, valor da causa vs. valor da condenação. Essa composição é lida automaticamente como um placar ("A contra B", duas quantias que se opõem ou se comparam em pé de igualdade). Quando na verdade um número é um subconjunto, uma consequência ou uma parcela do outro, o placar induz a leitura errada — e ninguém vai perceber o erro sem ler o texto pequeno, que é exatamente o que não deveria ser necessário.

**Regra:** antes de desenhar qualquer par ou conjunto de números, declarar a relação lógica entre eles:

| Relação | Estrutura visual correta | Nunca usar |
|---|---|---|
| Um valor é parte/subconjunto do outro (ex.: quanto do total devido já foi pago) | **Decomposição**: uma única barra/círculo representando o todo, dividida em segmentos proporcionais, com o rótulo de cada categoria ancorado no próprio segmento | Dois cartões do mesmo tamanho lado a lado |
| Um valor é a evolução do outro no tempo (ex.: valor original → valor atualizado) | **Waterfall/sequência**: ponto de partida → ajustes → resultado, em linha, com sinal de + ou - explícito em cada etapa | Dois números soltos sem seta ou conector entre eles |
| Dois valores realmente se opõem ou competem (ex.: nossa tese vs. tese adversária, pedido nosso vs. pedido deles) | Comparação lado a lado é válida aqui — mas rotular explicitamente o eixo de comparação no topo | Usar o mesmo layout de comparação para uma relação de parte-todo |
| Um valor é filtro/correção de erro dentro do outro (ex.: duplicidade descontada) | Segmento neutro (cinza, sem destaque de cor) dentro da mesma decomposição, rotulado como ajuste, nunca como dívida nem como pagamento | Omitir o ajuste ou escondê-lo só na nota de rodapé |

**Ancoragem do rótulo:** o texto que desambigua um número ("já pago", "real em aberto", "valor tratado como devido") deve estar no próprio elemento visual ou ligado a ele por linha de chamada curta — nunca relegado a um parágrafo de apoio abaixo do gráfico. Se o rótulo não couber dentro do segmento, usar chamada externa com linha, não mover o rótulo para uma legenda geral no rodapé.

**Teste de validação antes de aprovar qualquer slide com números:** cobrir mentalmente todo o texto de apoio (parágrafos, notas de rodapé, legendas soltas) e perguntar se a relação entre os números ainda é correta e inequívoca só pela geometria, cor e posição. Se a resposta depender do texto pequeno, redesenhar a composição — nunca aumentar ou reescrever o texto de apoio como correção.

Esta regra vale identicamente para Legal Design de peças processuais (`legal-design-rdaa`): a mesma composição "dois números iguais lado a lado" comete o mesmo erro num quadro-resumo de petição.

## 3.6 Hierarquia da ideia central (a conclusão precisa pesar visualmente, não só semanticamente)

Cada slide expositivo carrega uma única ideia central (§3). Essa ideia precisa ser o elemento de MAIOR peso visual do slide depois do título — nunca menos. **Negrito dentro de um parágrafo de corpo, dentro de uma faixa/legenda colorida, NÃO é destaque suficiente**, mesmo que a frase esteja tecnicamente em bold. O leitor lê escala antes de ler peso de fonte; uma oração em negrito do mesmo tamanho do texto ao redor ainda se mistura ao corpo e é processada como legenda/rodapé, não como conclusão.

**Diagnóstico do erro:** a conclusão central foi escrita como uma frase inteira, com conectores e ressalvas ("A tese não é X. É: **Y**"), embutida numa faixa de rodapé em corpo de texto normal (12–13px), com apenas um trecho em negrito. Isso trata a conclusão como legenda explicativa, não como o clímax visual do slide.

**Correção obrigatória:** extrair a ideia central como uma cláusula curta e autônoma (5 a 12 palavras, sem conectores de ressalva) e tratá-la como um elemento visual próprio:

- Escala próxima à do título do slide (na referência de §2: 20–28pt em PPTX; proporção equivalente em HTML — nunca no tamanho do corpo de texto).
- Isolada em bloco próprio, com espaço em branco ao redor, separada fisicamente do texto de apoio/legal que a sustenta.
- Contraste máximo (preto/cinza escuro sobre branco, ou branco sobre área escura) — laranja como marcador de destaque pontual (barra, aspas, sublinha), não como cor de fundo do bloco inteiro.
- Se houver fundação jurídica ou ressalva necessária (ex.: dispositivo legal, precedente), ela vem ABAIXO da conclusão, em corpo de texto normal, claramente subordinada — nunca no mesmo nível visual.

**Teste de validação:** olhar o slide por dois segundos e identificar qual frase o olho pousa primeiro. Se não for a ideia central, refazer a hierarquia — aumentar a conclusão ou reduzir o que compete com ela, nunca só adicionar negrito.

## 4. Uma fonte visual para HTML e PPTX

Não escrever dois decks independentes e chamar de conversão. Criar especificação compartilhada (por exemplo `deck-spec.json`) com IDs estáveis, texto exato, posições normalizadas ou canvas fixo, dimensões, ordem de sobreposição, tipografia, cores, conectores e ativos.

Ambos os formatos devem consumir a mesma composição aprovada. HTML não pode ter um fluxograma que vira bullets no PPTX. Igualdade de texto ou quantidade de slides não comprova paridade visual.

Default: PPTX editável com texto, formas e conectores nativos; figuras complexas podem usar SVG/PNG de alta resolução da mesma fonte, com limitação de editabilidade declarada. Uma versão de fidelidade por imagem de slide inteiro só é alternativa mediante concordância explícita; nunca vendê-la como apresentação nativamente editável.

Projetar com o conjunto de recursos comum aos dois renderizadores. Substituir efeitos CSS sem equivalente por construção compatível antes de aprovar o HTML, ou declarar a diferença e obter decisão. Não prometer equivalência pixel a pixel entre engines sem testar.

HTML: canvas lógico fixo 1920×1080, escalado uniformemente para caber na largura E altura disponíveis, reservando espaço aos controles. `aspect-ratio` com `max-height` não basta. `overflow:hidden` é proteção de canvas, não correção de conteúdo cortado. Manter teclado, contagem de slides e exportação sem controles.

## 5. Integridade do conteúdo jurídico

Nenhum ganho visual autoriza inventar fatos, números, status ou certeza. Proibidos KPIs como “100% blindado”, “zero risco” ou “controle total” sem base verificável. Não apresentar pedido de ajuste como decisão concedida, arquivo gerado como peça protocolada, expectativa de pauta como julgamento marcado, nem prova a obter como prova existente.

Identificar quem se beneficia de cada decisão. Afastar multa imposta à adversária não é automaticamente vitória do nosso cliente. Citações literais e IDs permanecem exatos; sínteses de teses não podem parecer transcrição de precedente. Não alterar estratégia jurídica durante redesign. Inconsistências encontradas devem ser sinalizadas e resolvidas antes de reutilizar o slide.

## 6. Procedimento e verificação

1. Preservar versão anterior e fontes; não sobrescrever anexos do usuário. Ler briefing, marca, referências e conteúdo. Registrar limites de acesso/visão.
2. Criar storyboard e escolher arquétipos por mensagem. Conferir fontes e status das afirmações antes de desenhar.
3. Explorar amostras quando a linguagem ainda estiver em discussão. Consolidar direção escolhida e construir especificação comum.
4. Gerar HTML e PPTX com ativos locais e mesma geometria. Exercer navegação HTML e reabrir PPTX.
5. Renderizar TODAS as páginas do PPTX via PowerPoint ou LibreOffice; capturar TODAS as páginas HTML na mesma proporção. Comparar pares lado a lado em prancha.
6. Medir proporção, objetos fora da área, texto cortado, colisões, carregamento de fontes e cores; inspecionar também composição, legibilidade e sentido dos diagramas. Um diff de pixels pode apoiar, não substituir, julgamento visual.
7. Corrigir na especificação-fonte e renderizar ambos novamente. Registrar por página resultado e diferenças aceitas em `qa-report.json`; incluir evidências e limitações, sem fabricar aprovação.
8. Entregar somente formatos efetivamente verificados, com caminhos e estado claro. Exportação bem-sucedida não significa qualidade aprovada. Se a ferramenta de visão falhar, declarar revisão visual bloqueada e entregar no máximo candidato técnico, não “pronto/aprovado”.

## Armadilhas recorrentes

- Recolorir cartões não corrige composição sem hierarquia.
- Importar o tema de infraestrutura da skill de diagramas descaracteriza RD.
- Referências devem ser examinadas: não alegar inspiração visual em templates que não foram vistos.
- Templates externos oferecem repertório, não autorização para copiar ativos pagos ou substituir a identidade do escritório.
- O preview aberto prova apenas abertura; ler só a capa não verifica o deck.
