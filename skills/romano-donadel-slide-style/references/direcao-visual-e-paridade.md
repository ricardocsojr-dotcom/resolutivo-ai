# Direção visual e paridade RD

## Referências consultadas e aplicação

- https://raw.githubusercontent.com/zarazhangrui/frontend-slides/main/SKILL.md — distinguir slides para exposição de slides para leitura; canvas fixo; explorar composições antes do deck completo.
- https://raw.githubusercontent.com/sunchaokun/PPT-Design-Skill/main/skill/references/design-principles.md — arquitetura antes do código, variação estrutural, proibição de cartões repetidos e fonte pequena, preservar identidade durante redesign.
- https://github.com/likaku/Mck-ppt-design-skill — briefing, estrutura, conteúdo, render e QA separados; gates verificáveis, não aprovação verbal do gerador.
- https://github.com/nevertoday/350-layout-compositions — repertório organizado por composição, princípios, tipografia/grid e apresentações. Consultar seção de apresentações e exemplos específicos antes de escolher composição.
- Oreate e Envato citados pelo usuário são referências adicionais, não acervo adquirido. Não declarar avaliação visual de templates quando apenas a página de entrada foi extraída. Não baixar conteúdo premium sem licença/autorização.

Nesta revisão foram lidos os documentos acima, não validadas imagens de todas as galerias. Ideias de processo podem ser adotadas sem importar código; qualquer reutilização de código/ativos deve preservar licença aplicável.

## Tradução para a identidade RD

Mais detalhe visual: relação espacial, hierarquia, marcação documental, conectores precisos, ritmo e escala. Não: navy, gradiente, emojis, efeitos ou semáforo por partido. Tipografia cinza #63666A; estrutura laranja #F7A800; fundo branco.

Exemplos de exploração para um mesmo assunto:
1. Editorial: uma conclusão curta à esquerda, visual documental ampliado à direita, chamadas finas laranja.
2. Relacional: entidade/objeto central, linhas laranja ligando pedidos e decisões; verbos nos conectores, condições em cinza.
3. Temporal: marcos documentados em eixo horizontal, intervalos destacados por contorno e notas compactas; datas não confirmadas ficam fora da linha factual.

## Contrato entre renderizadores

Uma especificação por slide: id, mensagem, estado, fonte, arquétipo, elementos. Cada elemento: id, tipo, x/y/w/h, z, texto, fonte/peso/tamanho, fill/stroke, asset_id e, quando pertinente, from/to de conectores. A unidade-base deve ser única e transformada proporcionalmente para PPTX e HTML.

Usar design tokens comuns. Não converter HTML por interpretação livre do texto. Quando um primitivo não for suportado, escolher equivalente explicitamente, preservar geometria e registrar limitação. Se a figura for rasterizada, manter sua resolução compatível com projeção e indicar editabilidade parcial.

QA de paridade por página: mesma mensagem/texto, posição do logo, tipografia real, quebras de linha, escala, eixos, diagrama, setas, ativos, cores e proporção. Não exigir identidade de antialiasing. Não aceitar perda de conectores ou transformação de diagrama em lista.

## Regressões a impedir

O deck anterior usou scripts diferentes para HTML e PPTX; o HTML continha diagrama SVG e o PPTX tinha outra arquitetura. O PPTX auditado tinha títulos de conteúdo de 17 pt e diversos textos de 9–12 pt, insuficientes para a direção atual de projeção. Atribuir Lato no XML não é prova suficiente; o PDF examinado nesta revisão contém fontes com nome Lato e SegoeUISymbol, portanto não concluir perda total de Lato apenas pela ausência no diretório de fontes do Windows.

Não promover alegações de “100% blindado”, prova documental de reserva ou decisão definitiva sem conferência das fontes do caso. Este diagnóstico não valida o mérito jurídico do deck anterior.
