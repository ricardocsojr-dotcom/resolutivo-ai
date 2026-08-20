---
name: lei-e-sumula
description: >
  Busca o texto atualizado de dispositivo legal (federal, estadual ou
  municipal) e de súmula (STF ou STJ, incluindo tema repetitivo/repercussão
  geral) em fontes oficiais gratuitas, sempre citando literalmente com link
  de origem. Use sempre que Ricardo pedir o texto de um artigo de lei, uma
  súmula, precisar saber se uma lei foi revogada ou está em vigor, ou
  precisar de fundamentação legal pronta pra uma peça. Ative com termos como
  "qual o texto do artigo", "essa lei ainda está em vigor", "me dá a súmula
  sobre", "texto da lei estadual/municipal sobre", ou qualquer variação que
  indique busca de dispositivo legal ou súmula.
---

# Lei e Súmula — RDAA

Busca texto oficial de lei e súmula em fontes públicas — nunca recita de
memória. Risco de erro aqui é baixo comparado a doutrina (item 12 do
backlog): texto de lei e súmula é canônico e as fontes abaixo são oficiais,
mas ainda assim toda citação deve vir com link de origem pra conferência.

## Fontes por tipo

| O que buscar | Fonte |
|---|---|
| Lei/decreto federal | [Portal da Legislação](http://www4.planalto.gov.br/legislacao) |
| Lei federal com linha do tempo de alterações | [Normas.leg.br](https://normas.leg.br) |
| Lei/decreto estadual | [LeisEstaduais.com.br](https://leisestaduais.com.br/) |
| Lei/decreto municipal | [Leis.org](https://leis.org/) |
| Súmula do STF (vinculante ou ordinária) | [portal.stf.jus.br/jurisprudencia/sumariosumulas.asp](https://portal.stf.jus.br/jurisprudencia/sumariosumulas.asp) |
| Súmula do STJ | [scon.stj.jus.br/SCON/sumstj](https://scon.stj.jus.br/SCON/sumstj/) |
| Tema repetitivo do STJ | [processo.stj.jus.br/repetitivos/temas_repetitivos](https://processo.stj.jus.br/repetitivos/temas_repetitivos/) — mesma fonte usada pela skill `tese-repetitiva` |

## Fluxo

### 1. Identificar o que buscar

- Artigo de lei: qual código/lei (CPC, CC, CDC, CLT, CF, lei especial) +
  número do artigo.
- Súmula: número + tribunal (STF ou STJ) — se não souber o número, pergunte
  o tema pra buscar por assunto na página do tribunal.
- Lei estadual/municipal: qual estado/município + assunto ou número da lei.

### 2. Buscar na fonte correta (tabela acima)

Use `WebFetch` na URL correspondente. Para lei federal, prefira o Normas.leg.br
quando precisar saber se o dispositivo foi alterado/revogado — ele mostra a
linha do tempo de redações. Use o Portal da Legislação quando só precisar do
texto vigente.

### 3. Verificar vigência

Antes de citar, confirme no próprio texto da fonte se o dispositivo está:
- **Vigente na redação atual** — cite normalmente, indicando a lei que deu
  a redação se houver sido alterado.
- **Revogado** — avise isso explicitamente antes de citar, nunca cite lei
  revogada como se estivesse em vigor sem o aviso.
- **Com vacatio legis em curso** — avise a data de início de vigência.

### 4. Citar literalmente

Nunca parafraseie o texto legal ou de súmula — mesma regra do
`jusbrasil-jurisprudencia`. Formato de entrega:

```
[Lei/Código, art. X] — [situação: vigente / revogado / vacatio]

> [texto literal do dispositivo]

Fonte: [URL]
```

Para súmula:

```
Súmula [número] do [STF/STJ]

> [texto literal da súmula]

Fonte: [URL]
```

### 5. Se não encontrar

Nunca complete de memória. Informe que não achou na fonte oficial e pergunte
se o Ricardo tem outra referência, ou tente reformular a busca (ex.: número
de lei estadual variando por ano de compilação).

## Registro no estado compartilhado

Depois de conferir o texto na fonte oficial e a situação de vigência, registre o
resultado no estado local da matéria com `contexto_rdaa.py`, usando `register_research`
e o tipo `lei`, `sumula` ou `tema_repetitivo`. Preserve o artigo ou número,
a redação literal, a URL oficial e a situação informada pela pesquisa.

O status `verificada_externamente` só deve ser usado quando a conferência na
fonte indicada foi efetivamente concluída. Uma referência recebida do vault,
do usuário ou do histórico sem nova conferência permanece `informada` ou
`pendente`; o registrador não confirma vigência por conta própria.

Antes da redação, o orquestrador monta o pacote `redator` com as fontes legais
selecionadas. Para a revisão, monta `revisor` com as regras e fontes necessárias,
sem enviar o estado completo da matéria.

## Nota

Usada diretamente ou chamada por `redigir-peca` (nível A) quando a peça
precisa de fundamentação legal específica além da jurisprudência.
