# PROMPT — Auditoria de consistência do fluxo completo de redigir-peca (2026-08-31)

Antigravity: leia `AGENTS.md` na raiz deste repositório primeiro. Seu papel
aqui é auditoria cética independente do PACOTE INTEIRO do fluxo de redação
de peças, não só das mudanças de hoje — não corrija nada, não redija nada,
não altere nenhum arquivo. Devolva só o relatório.

## Escopo — mapeie antes de auditar

Comece lendo `skills/redigir-peca/SKILL.md` do início ao fim e liste, você
mesmo, toda skill/script/referência que ele invoca ou pressupõe direta ou
indiretamente (ex.: `esqueleto-peca`, `contencioso-rdaa` e sua
`references/redacao-rdaa.md`, `legal-design-rdaa`, `formatar-peca` e seus
scripts (`construir_peca.py`, `verificar_formatacao.py`),
`revisor-rdaa` e seus scripts (`verificar_estilo.py`, `qa_gate.py`,
`publicar_docx.py`, `estado_rdaa.py`, `contexto_rdaa.py`,
`semantica_rdaa.py`, `seguro.py`), `jusbrasil-jurisprudencia`,
`buscar-jurisprudencia`, `consultar-processo`, `estilo-flavia-rdaa`,
`critico-rdaa` (verifique se ainda é referenciado em algum lugar ou se
ficou órfão desde que a crítica passou a ser feita pelo Antigravity via
checkpoint manual), `executar_motor.py`, `critica-antigravity.schema.json`,
o `AGENTS.md` e `roteamento-ia.md` da raiz, e o `CLAUDE.md` do projeto. Não
se limite a esta lista — ela é um ponto de partida, não o escopo final.
Audite o grafo completo que você mesmo mapear, não um subconjunto.

## Contexto — mudanças recentes conhecidas (não é o limite da auditoria)

Hoje rodei a primeira peça nível A real pelo novo fluxo sem
agente-mensageiro (Codex redige, você critica, Claude valida). Na revisão
visual do `.docx` gerado, o Ricardo pediu 4 correções estruturais que só
foram implementadas no código, nunca escritas em nenhuma skill:

1. `construir_peca.py` — quadro Processo/partes preserva `:` entre rótulo e
   parte (`Autora: Trivale...`); a qualificação usada no quadro deve ser
   reaproveitada no corpo/pedidos em vez da razão social; `bloco_citacao`
   ganhou parâmetro `referencia`, anexada entre parênteses ao final da
   ementa, na mesma fonte 9pt, sem parágrafo separado; `bloco_paragrafo_recuo`
   passou a processar `**negrito**`/`<b>` inline (antes só texto puro).
2. `verificar_formatacao.py` — `KEYWORDS_CAIXA` ganhou formas femininas
   (Autora, Ré, Requerida...), antes só reconhecia masculinas.
3. `verificar_estilo.py` — três mudanças: (a) `checar_aposto_explicativo`
   isenta parágrafos de estilo "RDAA Citação"; (b)
   `checar_dois_pontos`/`listar_dois_pontos` isentam parágrafos com borda
   completa nos 4 lados (a caixa Processo/partes); (c)
   `checar_aberturas_consecutivas` reescrita do zero: antes comparava a
   primeira palavra literal de parágrafos consecutivos, agora constrói uma
   "assinatura" normalizada (remove numeração inicial e conectivo de
   transição de abertura — lista fechada: "assim", "além disso", "nesse
   sentido", "por sua vez" —, reduz demonstrativo + substantivo genérico
   como "esse contexto"/"essa circunstância"/"essa situação"/"este cenário"
   a um marcador comum, corta no primeiro "que" ou vírgula pra isolar
   sujeito+verbo, compara isso entre parágrafos consecutivos).
4. `qa_gate.py`, `publicar_docx.py`, `executar_motor.py` — reconfiguram
   stdout/stderr pra UTF-8 no Windows (mesmo fix já aplicado antes em
   `construir_peca.py`/`verificar_formatacao.py`).

Nenhuma dessas convenções (numeração contínua real nos parágrafos
argumentativos via bloco `numerado`, citação+referência no mesmo bloco,
reaproveitar a qualificação do quadro no corpo) está escrita em
`redacao-rdaa.md`, `esqueleto-peca/SKILL.md` ou `redigir-peca/SKILL.md` —
só existem como comportamento de código. Trate isso como UM dos achados
esperados, não como o único.

## O que auditar — no fluxo inteiro, não só no que mudou hoje

1. **Conflito entre o que uma skill escrita diz e o que o código
   efetivamente permite/bloqueia.** Releia cada skill do grafo que você
   mapeou contra o código que a implementa/valida. Aponte qualquer frase de
   skill que descreve um comportamento que o código não reproduz, qualquer
   coisa que o código proíbe e uma skill recomenda, e qualquer instrução
   duplicada ou contraditória entre duas skills diferentes (ex.: duas
   descrições diferentes de como citar jurisprudência, dois critérios
   diferentes de quando pesquisar, duas definições diferentes do que é
   "achado objetivo" corrigível sem pausa).
2. **Papéis e fronteiras (Codex/Antigravity/Claude).** Confira se
   `AGENTS.md`, `roteamento-ia.md` e `redigir-peca/SKILL.md` descrevem a
   mesma divisão de papéis, sem ponto cego (ex.: algo que nenhum dos três
   está claramente encarregado de fazer, ou algo que dois deles pensam ser
   responsabilidade própria).
3. **Lacuna de documentação real, não hipotética.** As convenções novas
   listadas na seção anterior deveriam entrar em qual arquivo de skill, e
   com que redação mínima, pra sobreviver a uma sessão futura sem este
   contexto de conversa? Se encontrar outras convenções na mesma situação
   (só no código, nunca escritas), liste também.
4. **Cobertura real da normalização de `checar_aberturas_consecutivas`.**
   As listas `_CONECTIVOS_TRANSICAO` e `_DEMONSTRATIVO_GENERICO` são
   curtas e fechadas, calibradas com um único exemplo real. Cite pelo
   menos 3 padrões de abertura repetitiva plausíveis em peça jurídica que
   passariam despercebidos hoje (falso negativo).
5. **Isenções por estilo/borda ("RDAA Citação", borda completa) —
   cobertura real.** Existe algum caminho no plugin (outra skill, outro
   script, um contexto montado à mão) que gera citação de jurisprudência ou
   quadro Processo/partes SEM passar pelos blocos padrão de
   `construir_peca.py`? Se existir, a isenção não pega lá.
6. **Skill órfã ou stale.** `critico-rdaa` ainda é referenciado por algum
   fluxo ativo, ou ficou para trás desde que a crítica virou papel do
   Antigravity via checkpoint manual? Procure outros candidatos a órfão no
   mesmo padrão.
7. **Qualquer outro conflito, lacuna ou contradição** que você achar no
   fluxo completo e que não esteja listado acima — não se limite ao que
   pedi.

## Regras

- Não altere nenhum arquivo do repositório.
- Não corrija, não redija — aponte achados com evidência (arquivo + trecho).
- Separe achados em: (a) conflito real confirmado por leitura do código,
  (b) risco plausível não confirmado, (c) sugestão de onde documentar.
- Devolva o relatório em texto corrido/markdown para eu colar de volta na
  conversa com o Claude Code.
