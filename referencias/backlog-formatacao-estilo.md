# Backlog de formatação e estilo — RDAA

Arquivo vivo. Vamos alimentando durante o dia com atritos de formatação,
geração de DOCX e cadência de redação que aparecem nas peças. Não é para
corrigir agora — é para juntar material e planejar uma correção posterior
no gerador (`construir_peca.py`), nos validadores (`verificar_estilo.py`,
`verificar_formatacao.py`) e no núcleo de redação (`redacao-rdaa.md`).

Convenção: cada item tem **data**, **onde apareceu**, **o atrito**, **ideia
de correção**. Status: `aberto` / `em análise` / `corrigido`.

---

## Parte 1 — Atritos de formatação e geração

### 1. `verificar_estilo.py` — falsos positivos de dois-pontos e aposto
- **Data:** 2026-09-01
- **Onde:** contestação CALU (proc. 5506114-45.2026.8.09.0074), rodando o script sobre o `.md`/`.docx`.
- **Atrito:** o script marca como erro bloqueante:
  - as linhas do quadro de partes (`Autor:`, `Ré:`, `Corrés:`) — mas o núcleo **exige** dois-pontos entre rótulo e parte no quadro;
  - o `EMENTA:` e a referência entre parênteses da citação literal de jurisprudência — mas citação literal é isenta (commit `cfbdd4f`) e a referência entre parênteses ao fim da ementa é o formato obrigatório do núcleo.
  - No `.docx` final esses falsos positivos somem (o gerador tipa quadro e citação como blocos próprios), então o gate passa. O problema é só ao rodar o script direto no rascunho, o que confunde a revisão.
- **Correção:** `checar_dois_pontos()` agora detecta rótulos de parte (`Autor:`, `Réu:`, `Corré:`, `Corrés:`, etc.) e os exime automaticamente, sem depender de borda completa. Tolerante com tamanho de linha.
- **Status:** ✅ corrigido (commit 2026-09-02)

### 2. `verificar_formatacao.py` — "Item 3b" quebra com linha de parte longa
- **Data:** 2026-09-01
- **Onde:** contestação CALU, primeira geração.
- **Atrito:** o gate exige 2 parágrafos vazios após o quadro Processo/partes. A detecção do "último parágrafo da caixa" (`caixa_processo[-1]`) usava `KEYWORDS_CAIXA` **ou** `':' in texto and len(texto) < 80`. A linha `Corrés: APROLI, Associação dos Produtores de Leite do Município de Ipameri, e Cooperativa Agropecuária de Catalão, COACAL` tem mais de 80 caracteres e "Corrés:" não estava nas keywords, então essa linha (apesar de ter borda) não foi reconhecida como parte da caixa. Resultado: o gate achou 0 parágrafos vazios após a "Ré:" e bloqueou. Contornei encurtando para `Corrés: APROLI e COACAL`.
- **Correção:** Removido limite de 80 caracteres na detecção de caixa. Agora a detecção é apenas por borda + keyword (sem limite de tamanho). Adicionados "Corré:", "Corré ", "Corrés:", "Corrés " e variantes sem acento às keywords.
- **Status:** ✅ corrigido (commit 2026-09-02)

### 3. Legenda de figura em 9pt
- **Data:** 2026-09-01
- **Onde:** contestação CALU, provas anotadas.
- **Atrito:** Ricardo pediu legenda de figura menor.
- **Correção:** `bloco_figura` em `construir_peca.py` mudado de `Pt(9)` para `Pt(8)`; `schema_blocos.md` atualizado. Vale para o escritório todo.
- **Status:** corrigido

### 4. Imagens densas ficam ilegíveis mesmo grandes
- **Data:** 2026-09-01
- **Onde:** Figuras 1 (relatório "Captação por Dia", paisagem) e 2 (DANFE inteiro) da contestação CALU.
- **Atrito:** relatório de sistema em modo paisagem e nota fiscal completa não ficam legíveis em nenhuma largura que caiba na página. Os retângulos vermelhos e a legenda carregam o sentido, mas o corpo do documento vira textura. O `crop` do `anotar_decisao.py` existe, mas exige coordenadas manuais.
- **Ideia:** opção de recorte automático pela bounding box dos próprios retângulos + margem (ex.: `crop: "auto"` no spec), para a figura mostrar só a faixa relevante do documento em tamanho legível.
- **Status:** aberto

### 4. `width_cm` default 14 estoura a altura da página em imagem retrato
- **Data:** 2026-09-01
- **Onde:** Figura 2 (DANFE) da contestação CALU — a 14 cm de largura daria ~19,7 cm de altura.
- **Atrito:** não há auto-fit à área útil da página (A4 menos margens ~25,7 cm de altura, e menos ainda se o parágrafo seguinte tiver que caber). Tive que calcular e setar `width_cm` manualmente (10,5) em duas figuras.
- **Correção:** `bloco_figura()` agora calcula automaticamente a largura máxima para imagens não estouraem 55% da altura útil da página (~13,5 cm). Para imagens retrato, a altura é o fator limitante; a função ajusta a largura proporcionalmente. Usa o menor entre: largura solicitada, largura calculada, default 14cm.
- **Impacto:** ✅ Nenhuma conta manual necessária. Imagens retrato cabem automaticamente.
- **Status:** ✅ corrigido (commit 2026-09-02)

### 7. ✅ Esquema de fluxo e responsabilidades (cadeia única) — componente criado

- **Data:** 2026-09-01
- **Onde:** contestação CALU. Ricardo pediu esquema de cadeia (fornecimento → agregação → venda → pagamento → repasse) com identidade visual do escritório.
- **Feito agora (protótipo):** Diagrama SVG em `.rdaa-run/5506114-45.2026.8.09.0074/provas/cadeia-unica-calu.svg` com paleta oficial (`#F7A800` destaque, `#63666A` estrutura).
- **Correção (2026-09-02):** 
  - Criado `gerar_cadeia_fluxo.py` — gerador Python parametrizado de diagramas SVG
  - Input: spec JSON com `titulo`, `subtitulo`, lista de `etapas` (numero, titulo, ator, descricao, prova), `ponto_central`, `disclaimer`, `etapas_destacadas`
  - Output: SVG renderizado (até 6 etapas, com/sem destaque em laranja)
  - Exemplo spec: `skills/legal-design-rdaa/examples/cadeia-unica-calu-spec.json`
  - Teste gerado: `cadeia-unica-calu-gerado.svg` (funciona!)
- **Próximos passos (backlog):**
  - Integrar no `construir_peca.py` como novo `visual_tipo: "cadeia-unica"`
  - Adicionar ao `esqueleto-peca` como sugestão quando caso tem fluxo multi-ator
  - Permitir geração direta de PNG via PIL (para compatibilidade com Legacy Word)
- **Status:** ✅ Componente criado e testado; integração pendente

### 8. Inserir prints já com a marcação do que é importante — workflow a facilitar
- **Data:** 2026-09-01
- **Onde:** contestação CALU, Figuras 2 a 4 (relatório de captação, NF-e 000.090, extrato BMP).
- **Feito agora:** funcionou, mas foi trabalhoso. O `anotar_decisao.py` já produz a cópia da página com retângulo vermelho + legenda, mas exige **coordenadas de pixel na mão**. O processo real foi: renderizar as páginas do PDF em PNG, chutar coordenadas, desenhar retângulos de teste, olhar o resultado, corrigir, repetir 2-3 vezes por imagem, e só então rodar o `anotar_decisao.py`. As páginas de documento dos autos costumam ser **imagem pura, sem camada de texto**, então `page.search_for()` não acha nada.
- **Backlog:**
  - Caminho A (OCR): rodar Tesseract na página para obter as bounding boxes das palavras, casar com o trecho que o advogado descreveu ("marque a linha do destinatário", "o valor total", "as duas linhas de PIX para a APROLI") e posicionar o retângulo automaticamente. Confirmar visualmente antes de gravar.
  - Caminho B (loop de preview): o próprio agente desenha retângulos candidatos, renderiza, se autocorrige contra a imagem, e só entrega quando está no lugar — sem o operador dar coordenada. É o que foi feito hoje na mão; dá para empacotar.
  - Caminho C (seleção pelo Ricardo): abrir a página no visualizador de PDF (skill `pdf-viewer`) e deixar ele marcar a área; o script converte a marcação em spec do `anotar_decisao.py`.
  - Somar com o item 4 (recorte automático pela bbox dos retângulos + margem) — marcar E recortar na mesma passada, para a figura sair legível.
  - Entrada por linguagem natural no spec: além de `rectangles` com x/y/w/h, aceitar `destaques: ["texto ou descrição da região"]` e deixar o resolvedor (OCR ou agente) achar as coordenadas.
  - Prever isso no `esqueleto-peca` / `redigir-peca`: uma lista "provas a destacar" (qual documento, qual trecho, por quê) definida no esqueleto, para as figuras anotadas serem planejadas e não improvisadas na hora de gerar o DOCX.
- **Status:** aberto (protótipo manual entregue nesta matéria; ver Figuras 2 a 4 e `provas/prova-*-anotada.*`)

### 9. Design de tabelas — colunas inconsistentes entre tabelas comparáveis
- **Data:** 2026-09-01
- **Onde:** cumprimento de sentença Elglobal x Rodrigo (proc. 0130354-80.2018.8.13.0702), memória de cálculo com dois créditos recíprocos.
- **Atrito:** montei duas tabelas de valor atualizado lado a lado na mesma peça (crédito de Rodrigo, quatro parcelas; crédito de Elglobal, uma parcela). Ambas tinham juros de 1% a.m. aplicados no cálculo, mas só a tabela do crédito de Elglobal tinha coluna "Juros desde" — a do crédito de Rodrigo só mostrava "Correção desde" e o valor final já com juros embutidos, sem coluna própria. Ricardo leu a peça e achou que os juros não tinham sido aplicados ao lado de Rodrigo, quando na verdade estavam lá, só invisíveis na tabela. Corrigi adicionando a coluna em ambas (republicação `_rev3`, sem alteração de valores).
- **Causa:** o bloco `tabela` do `construir_peca.py` é genérico (`cabecalho`/`linhas`/`alinhamentos` livres) — cada tabela é montada solta pelo contexto JSON, sem template nem checagem de que tabelas comparáveis (mesma matéria, mesmo tipo de memória de cálculo) usem o mesmo conjunto de colunas.
- **Ideia:** criar um preset/variante de tabela para memória de cálculo judicial (ex.: `visual_tipo: memoria-calculo` no `construir_peca.py`, ou um helper na skill `calculo-judicial`/`perfil-csv` que já devolve o bloco `tabela` pronto) com colunas fixas — `Parcela/Valor histórico`, `Correção desde`, `Juros desde` (omitir só se genuinamente não houver juros, nunca por omissão), `Valor atualizado (data-base)` — para que, numa mesma peça com mais de um crédito, as tabelas saiam automaticamente no mesmo formato. Vale também como checagem do `verificar_formatacao.py`/`qa_gate.py`: se duas tabelas do tipo memória de cálculo aparecem na mesma peça com número de colunas diferente, sinalizar para conferência antes de publicar.
- **Status:** aberto (correção pontual feita nesta matéria, item de design ainda não generalizado)

### 6. ✅ Publicador não substitui arquivo aberto no Word

- **Data:** 2026-09-01
- **Onde:** republicação da contestação CALU depois dos ajustes de Ricardo.
- **Atrito:** `construir_peca.py` passou no QA mas quebrou com `PermissionError: [WinError 5]` no `os.replace`, porque o `.docx` final estava aberto no Word do Ricardo. Tive que publicar em `contestacao_..._rev1.docx`.
- **Correção (2026-09-02):**
  - Detectar `PermissionError` / `WinError 5` no `os.replace()`.
  - Em vez de falhar, publicar automaticamente em `{base}_rev{N}.docx` (encontrando próximo sufixo livre).
  - Avisar ao usuário em stderr: arquivo está travado, reintegre manualmente.
  - Não bloqueia o workflow, apenas avisa.
- **Impacto:** ✅ Sem interrupção no workflow; usuário notificado para reintegrar.
- **Status:** ✅ corrigido (commit 2026-09-02)

---

## Parte 2 — Pesquisa: repetição de abertura de parágrafo

Problema recorrente: a IA abre vários parágrafos seguidos com a mesma
preposição/artigo ou com a mesma estrutura sintática (`A... / A... / As...`,
`O... / O... / Os...`, ou `Nesse sentido, / Dessa forma, / Além disso,`).
Fica robótico mesmo quando os substantivos mudam.

### Por que acontece

O modelo tende a usar marcadores discursivos muito prováveis para sinalizar
relação lógica entre parágrafos. Em texto jurídico isso é ainda mais
visível: "Nesse sentido...", "Nesse contexto...", "Dessa forma...", "Além
disso...", "Por outro lado...". O problema não é a palavra em si, é a
**estrutura probabilística repetida**: `[conector] + vírgula + afirmação`.
Depois que o modelo entra nessa cadência, tende a mantê-la. O mesmo vale
para `[artigo] + [substantivo] + [verbo]` — três parágrafos assim seguidos
já soam mecânicos ainda que "A decisão / O contrato / Os documentos" tenham
palavras diferentes, porque a estrutura é idêntica.

### Só prompt não resolve

Colocar "evite repetir conectores" no prompt ajuda, mas não bloqueia. Para
impedir de verdade é preciso combinar **instrução de escrita + validação
posterior** (linter que rejeita a geração e manda reescrever só as aberturas
sinalizadas).

### Projetos no GitHub

- **Vale** — linter de prosa altamente configurável, tipo ESLint para texto.
  Dá para criar regras próprias e reprovar geração que viola o padrão.
  Link informado: <https://github.com/vale-cli/vale> (conferir o repositório
  canônico — o projeto Vale costuma estar em `errata-ai/vale`).
  Há configs de Vale voltadas a detectar "AI slop", incluindo "formulaic
  transitions". Ricardo mencionou um exemplo recente da AWS com config
  explícita para "formulaic transitions" e outros sinais de prosa gerada por
  IA (achar o link).
- **slopless** (`BioInfo/slopless`) — <https://github.com/BioInfo/slopless>.
  Cria regras para Claude/LLMs contra transições mecânicas, aberturas
  padronizadas, comprimento uniforme de parágrafos, paralelismos artificiais
  e outras estruturas previsíveis. O autor recomenda usar regras, skills e
  hooks em vez de entupir o prompt, e alerta contra copiar o repositório
  inteiro (regras demais geram conflito).
- **WRITING.md** (`Anbeeld/WRITING.md`) — <https://github.com/Anbeeld/WRITING.md>.
  Proposta de eliminar "generic signposts", cadência repetida, estruturas
  organizadas demais e formatos previsíveis de parágrafo. Tem versões para
  `CLAUDE.md`, `AGENTS.md` e skills.

### Arquitetura sugerida (camadas)

```
WRITING.md               → regras gerais de boa escrita
slopless/writing-voice   → anti-AI-slop e anti-padrão estrutural (versão enxuta)
RDAA-writing.md          → regras específicas da redação jurídica RDAA
style_guard.py           → validação objetiva antes da entrega
```

Não copiar os repositórios inteiros — fazer uma versão enxuta e adaptada.
A terceira camada (regra RDAA própria) é o que os projetos genéricos não
personalizam sozinhos.

### Regra de redação proposta (para o `RDAA-writing.md` / núcleo)

**Variação sintática entre parágrafos.** Evitar repetir a mesma estrutura
gramatical na abertura de parágrafos próximos. É especialmente indesejável
iniciar sucessivamente parágrafos com `A... / A... / As...` ou `O... /
O... / Os...`. Trocar só o substantivo não caracteriza variedade — "A
decisão... / A documentação... / A alegação..." e "O contrato... / O
Autor... / O entendimento..." usam todas a estrutura `[ARTIGO] +
[SUBSTANTIVO]`.

Ao revisar, comparar as primeiras 3 a 5 palavras de cada parágrafo. Se dois
ou mais parágrafos próximos começarem pela mesma construção sintática,
reescrever pelo menos um. Variar naturalmente entre: sujeito direto; oração
subordinada; circunstância temporal; retomada do fato narrado; consequência
do argumento anterior; construção verbal; referência documental.

**Não corrigir com conector artificial.** É proibido resolver a repetição
apenas trocando a abertura por "Nesse sentido", "Dessa forma", "Além disso",
"Ademais", "Com efeito", "Sob essa perspectiva", "Nessa linha", "Diante
disso". A variedade tem que vir da construção da frase, não de um marcador
plugado na frente.

**Janela.** Em cada bloco de 4 a 5 parágrafos: no máximo 1 pode começar com
conector; no máximo 2 podem começar com `[artigo] + [substantivo]`; nunca 3
consecutivos com a mesma estrutura; nenhuma expressão inicial repetida.

**Não quebrar em parágrafos demais.** Não criar um parágrafo novo só para
introduzir uma conclusão, consequência ou transição que caberia no parágrafo
anterior. Vício típico de IA: cada parágrafo vira uma unidade lógica
independente e a cadência fica "tese + expansão".
Exemplo ruim: "O contrato não foi firmado pela Ré. Além disso, nenhum
pagamento foi feito à empresa. Nesse sentido, inexiste vínculo contratual.
Dessa forma, não há responsabilidade." → melhor: "O contrato não foi firmado
pela Ré e nenhum pagamento lhe foi feito, o que afasta o vínculo contratual
e a responsabilidade imputada."

### `style_guard.py` — o que o script deveria detectar

Não precisa entender português a fundo. Basta olhar o começo de cada
parágrafo e pontuar (não bloquear tudo — pontuar):

- `PARAGRAPH_OPENING_ARTICLE` — sequência de `A / O / As / Os` em parágrafos próximos.
- `REPEATED_FIRST_WORD` — mesma primeira palavra (limite 2).
- `REPEATED_FIRST_BIGRAM` — mesmo par inicial ("A decisão", "A decisão") (limite 1).
- `REPEATED_CONNECTOR` — "Nesse sentido", "Dessa forma" etc. como abertura.
- `MECHANICAL_CONNECTOR_CHAIN` — "Além disso → Nesse sentido → Dessa forma".
- `REPEATED_SYNTACTIC_OPENING` — mesma estrutura (`ARTIGO+SUBSTANTIVO`, `PREP+ARTIGO+SUBSTANTIVO`, `CONJUNÇÃO+ORAÇÃO`) em janela curta, mesmo com palavras diferentes.
- `UNIFORM_PARAGRAPH_LENGTH` — parágrafos quase todos do mesmo tamanho.
- `EXCESSIVE_PARAGRAPH_BREAKS` — muitos parágrafos de uma frase só.

Parâmetros de referência:
```
MAX_CONNECTOR_OPENINGS = 0.20   # fração dos parágrafos
MAX_IDENTICAL_FIRST_WORD = 2
MAX_IDENTICAL_FIRST_BIGRAM = 1
# janela de 4 parágrafos: no máx. 2 com [artigo]+[substantivo], nunca 3 consecutivos
```

Pontuação em vez de bloqueio absoluto (repetir "A decisão..." duas vezes às
vezes é natural; o alvo é a cadência estatística, não uma nova camisa de
força):
```
0-2 problemas → PASS
3-5           → REVIEW
6+            → FAIL → devolve pra LLM reescrever SÓ as aberturas sinalizadas
```

Ao devolver para a LLM: "o texto falhou no style guard, reescreva apenas as
aberturas sinalizadas, não altere fatos, fundamentos, pedidos, citações,
datas ou valores". Nunca "reescreva tudo" — isso deteriora peça que já
estava boa.

Cuidado com o efeito inverso: proibir totalmente `A`/`O` faz a IA fabricar
"Quanto a...", "No que se refere...", "Sob esse prisma..." só para passar no
teste. Por isso janela + pontuação, não proibição.

### Estado atual no RDAA (o que já existe e o que falta)

- `skills/revisor-rdaa/scripts/verificar_estilo.py` **já tem**
  `checar_aberturas_consecutivas` e `checar_aberturas_repetidas`, e os dois
  são bloqueantes no gate.
- **Limitação:** `_assinatura_abertura` normaliza a abertura removendo
  `a/o/as/os/de/da/...` como palavras vazias e compara o sujeito+verbo de
  conteúdo. Então "A decisão reconheceu" vira `decisão reconheceu` e "A
  documentação demonstra" vira `documentação demonstra` — assinaturas
  diferentes, **não flagra** a monotonia `[ARTIGO]+[SUBSTANTIVO]+[VERBO]`.
  `checar_aberturas_repetidas` também não pega, porque compara os 4
  primeiros tokens literais.
- **Falta:** um detector de **estrutura** (POS-tag leve ou heurística) que
  reconheça `[artigo def.]+[substantivo]` como um padrão e conte ocorrências
  em janela deslizante, além do detector de conector-como-abertura com
  fração máxima. É exatamente a camada 3 que os projetos genéricos não dão.
- `checklist-3-estilometria.md` já descreve "cadência homogênea" (regra
  geral, seção A/E/M) mas depende de leitura qualitativa da LLM revisora —
  não tem contrapartida objetiva no script para o caso `[artigo]+[subst.]`.

### Próximo passo (quando formos corrigir)

1. Escrever o `RDAA-writing.md` enxuto com as regras acima e plugar no
   pacote do redator (passo 7 de `redigir-peca`) e no `revisor-rdaa`.
2. Estender `verificar_estilo.py` com o detector estrutural + janela +
   pontuação, mantendo o resultado como parte do gate (`publicar_docx.py`).
3. Avaliar Vale como camada extra (regras `.yml` para os vícios lexicais —
   "cumpre destacar", "importa ressaltar", "não se trata de X, mas de Y",
   travessão, dois-pontos) rodando junto do `qa_gate.py`.
4. Decidir se o loop "falhou → LLM reescreve só as aberturas" entra no
   checkpoint manual (Codex) ou vira um passo do Claude na validação.
