---
name: jusbrasil-jurisprudencia
description: >
  Busca jurisprudência no Jusbrasil usando a conta logada do usuário no Chrome
  e retorna citações literais das ementas encontradas. Use esta skill sempre que
  Ricardo pedir para buscar jurisprudência, encontrar precedentes, localizar
  acórdãos, pesquisar decisões judiciais, ou precisar de ementa de algum
  tribunal — mesmo que não mencione o Jusbrasil explicitamente. Ative também com
  termos como "busca jurisprudência sobre", "encontra precedente de", "qual o
  entendimento dos tribunais sobre", "acha acórdão sobre", "pesquisa no
  Jusbrasil", "me dá a ementa de", "preciso de jurisprudência sobre", ou
  qualquer variação que indique pesquisa de jurisprudência ou precedentes
  judiciais. Esta skill é essencial para fundamentar peças processuais com
  citações literais precisas.
---

# Jusbrasil — Busca de Jurisprudência com Citação Literal de Ementa

Esta skill usa a extensão do Claude no Chrome para acessar o Jusbrasil com a
conta logada do usuário e retornar citações literais de ementas de
jurisprudência, prontas para uso em peças processuais.

## Pré-requisitos

- A extensão do Claude no Chrome deve estar conectada (`mcp__Claude_in_Chrome__*`)
- O usuário deve estar logado no Jusbrasil no navegador Chrome

Se a extensão não estiver disponível, informe o usuário que é necessário
conectar a extensão do Claude no Chrome antes de usar esta skill.

## Fluxo de execução

### Passo 1 — Coletar os parâmetros da busca

Se o usuário não informou o tema, pergunte:
1. **Tema ou termo de busca** (ex: "negativação indevida", "dano moral atraso de voo")
2. **Tribunal** (opcional — STJ, STF, TJSP, TJMG, TRF, etc. Se não informado, busca em todos)
3. **Quantidade de ementas** (padrão: 3)

### Passo 2 — Navegar até o Jusbrasil

Use `mcp__Claude_in_Chrome__navigate` para acessar:
```
https://www.jusbrasil.com.br/jurisprudencia/
```

Aguarde a página carregar. Se o Jusbrasil redirecionar para login, pare e
informe o usuário: *"Você precisa estar logado no Jusbrasil no Chrome. Faça o
login e me avise para continuar."*

### Passo 3 — Executar a busca

Use `mcp__Claude_in_Chrome__find` para localizar o campo de busca principal.
Em seguida, clique no campo com `mcp__Claude_in_Chrome__computer` e digite o
termo de busca. Pressione Enter para buscar.

Se o usuário especificou um tribunal, aplique o filtro correspondente após os
resultados carregarem (use `mcp__Claude_in_Chrome__find` para localizar o
filtro de tribunal).

### Passo 4a — Ranquear os resultados antes de abrir qualquer um

Use `mcp__Claude_in_Chrome__get_page_text` para ler a **página de resultados
inteira** (não abra nenhum acórdão ainda). Cada resultado já vem com tribunal,
data e um trecho curto — o suficiente para julgar relevância sem gastar uma
navegação por item.

Não pegue simplesmente os N primeiros na ordem que o Jusbrasil devolve — essa
ordem mistura texto e data, não necessariamente o que mais fundamenta a peça.
Olhe todos os resultados visíveis na primeira página e escolha os N melhores
segundo:

1. **Hierarquia do tribunal** — STJ/STF pesam mais que TJ, que pesa mais que
   1ª instância, salvo pedido explícito de jurisprudência local/TJ específico.
2. **Atualidade do entendimento** — prefira decisão mais recente, a menos que
   o trecho curto indique que ela mesma cita/reafirma uma súmula ou tema
   repetitivo mais antigo e consolidado (aí a mais antiga/fundante pode valer
   mais).
3. **Aderência real ao tema**, não só à palavra-chave — o trecho precisa
   indicar que o caso trata do mesmo fato/tese, não apenas conter os mesmos
   termos em contexto diferente.

Se o tribunal foi especificado pelo usuário, aplique o filtro correspondente
antes desta leitura (use `mcp__Claude_in_Chrome__find` para localizar o filtro
de tribunal). Se a primeira página não tiver bons candidatos suficientes,
pode navegar pra próxima página de resultados antes de decidir — ainda sem
abrir nenhum acórdão individual.

### Passo 4b — Extrair as ementas dos escolhidos

Só agora, para cada resultado selecionado no passo 4a:

1. Clique no resultado com `mcp__Claude_in_Chrome__computer`
2. Aguarde a página do acórdão carregar
3. Use `mcp__Claude_in_Chrome__get_page_text` para extrair o conteúdo completo
4. Localize e copie a **ementa literal** (seção geralmente marcada como "EMENTA"
   ou "Ementa" no documento)
5. Anote também: tribunal, número do processo, data do julgamento e relator
6. Volte à lista de resultados com `mcp__Claude_in_Chrome__navigate` para o URL
   anterior, ou use o botão voltar

### Passo 5 — Apresentar os resultados

Formate cada ementa desta forma:

---

**[TRIBUNAL] — [Número do processo]**
*Relator: [Nome] | Julgado em: [Data]*

> [EMENTA LITERAL — reproduza palavra por palavra, exatamente como consta no
> documento original, incluindo maiúsculas e pontuação originais]

Disponível em: [URL do acórdão no Jusbrasil]

---

Repita para cada ementa encontrada, separando-as com a linha `---`.

Após todas as ementas, adicione uma linha resumindo:
> *[N] ementas encontradas para "[termo buscado]"[, filtro: tribunal X]*

## Regras importantes

- **Literalidade é inegociável.** A ementa deve ser copiada exatamente como
  aparece no documento — sem paráfrases, sem cortes, sem reordenação. O usuário
  usará o texto em peças processuais e qualquer alteração pode comprometer a
  citação.

- **Se a ementa for muito longa**, copie-a integralmente mesmo assim. O usuário
  seleciona o que usar — não cabe à skill decidir o que é relevante.

- **Se não encontrar resultados relevantes**, tente variações do termo de busca
  antes de reportar insucesso. Por exemplo: "negativação indevida" → "inscrição
  indevida cadastros restritivos".

- **Acesse apenas páginas do Jusbrasil** (jusbrasil.com.br). Não siga links
  externos.

- **Sessão expirada ou paywall**: se o Jusbrasil bloquear o acesso a um
  acórdão específico por limite de visualizações ou sessão expirada, pule para
  o próximo resultado e informe o usuário.
