---
name: dano-moral-rct
description: >
  Reescreve uma peça de ação de dano moral já redigida (por `contencioso-rdaa`
  dentro do fluxo de `redigir-peca`) para a voz autoral de Ricardo Cesar Souza
  de Oliveira Junior. NÃO é a porta de entrada para redigir a peça — para
  isso, use `redigir-peca`. Aciona automaticamente quando a matéria da peça é
  dano moral, sem precisar de pedido separado; roda como subagente isolado
  sobre o texto já pronto, sem alterar fatos, tese, pedidos, fontes ou IDs.
---

# Skill: Camada de Estilo — Ação de Dano Moral (Voz RCT)

## Contrato de integração com o RDAA

Esta skill é uma camada opcional de estilo para uma peça **já redigida**
(por `contencioso-rdaa`, dentro do fluxo de `redigir-peca`, passo 7.75). Ela
não é um novo tipo de peça, não substitui `redigir-peca`, `contencioso-rdaa`,
`critico-rdaa`, `revisor-rdaa` ou `formatar-peca`, e não redige do zero.

Aciona automaticamente quando a matéria da peça for ação de dano moral —
declarado no contexto ou evidente da tese/pedido selecionados no esqueleto. É
premissa do gênero da peça, não exige pedido separado de Ricardo.

As regras universais do RDAA prevalecem sobre a voz RCT. A saída deve
respeitar as regras sem dois-pontos, sem travessão, sem apostos explicativos
isolados, sem alteração de fatos, tese, pedido, fundamento, fonte, provenance
ou IDs semânticos.

Depois da reescrita, o texto volta para `estilo-flavia-rdaa` (se também se
aplicar), `revisor-rdaa` e `formatar-peca`, que geram o candidato e executam
a publicação protegida. Esta skill nunca grava diretamente o arquivo final.

## Como esta skill deve ser invocada

Invoque via subagente isolado (Agent tool), passando apenas: o texto já
redigido da peça, os fatos e documentos explicitamente selecionados (o que
está provado, o que não está), os réus envolvidos e o tipo de peça. Nunca
passe o histórico da conversa onde a peça foi redigida, nem o raciocínio de
quem escreveu — o isolamento evita que a reescrita apenas preserve frases
"porque já estavam ali".

## Leia primeiro

Antes de reescrever, leia:
1. `contencioso-rdaa/references/redacao-rdaa.md` — núcleo obrigatório de toda peça RDAA
2. `references/estilo-rct.md` — camada específica de dano moral (complementa o núcleo, nunca o substitui)

## O que avaliar e reescrever

Compare o texto de entrada, parágrafo a parágrafo, contra os princípios
inegociáveis da voz RCT — e reescreva o que divergir, preservando
integralmente o conteúdo jurídico e factual:

- **Tese antes dos fatos**: o parágrafo anuncia o que os fatos significam
  antes de narrá-los, ou começa pela narrativa crua?
- **Episódios como padrão**: os fatos aparecem como um padrão que se
  confirma, ou como episódio isolado?
- **Aparência vs. realidade**: há contraste explícito entre o pretexto
  formal e a intenção real, quando os fatos sustentam isso?
- **Densidade moral sem abandono técnico**: o texto carrega peso moral sem
  perder o fundamento legal?
- **Linguagem do réu contra si mesmo**: palavras, atos e omissões dos réus
  já fornecidos estão sendo usados como prova da própria ilicitude?
- **Individualização da responsabilidade**: cada réu está separado onde a
  peça já individualiza atos, ou ficou genérico?
- **Cacoetes robóticos**: "cumpre salientar", "oportuno destacar", "por
  derradeiro" e afins — remover sempre que aparecerem.
- **Números por extenso** em contexto jurídico formal ("vinte mil reais",
  não "R$ 20.000").
- **Marcadores soltos**: listas sem desenvolvimento em prosa — reescrever
  como texto corrido quando a estrutura não exigir lista.

## O que NUNCA fazer

- Nunca altere fato, tese, pedido, fundamento, fonte, provenance ou ID
  semântico — só a forma.
- Nunca invente ou reforce fato/prova que não esteja no material fornecido,
  mesmo que a versão "mais no estilo RCT" soe mais convincente.
- Nunca insira jurisprudência de memória — cite só o que já estava no texto
  de entrada com `source_id` selecionado.
- Nunca decida sozinha por reescrita total da peça — se o desvio for grande
  o bastante para exigir isso, diga isso explicitamente em vez de produzir
  um texto irreconhecível do original.
- Nunca consulte fonte externa, vault, CNJ, DataJud ou Jusbrasil.

## Formato de saída

1. **Peça reescrita** — texto completo, pronto para uso, conteúdo jurídico e
   factual preservado, forma adequada à voz RCT.
2. **Ajustes aplicados** — lista curta do que mudou e por quê (ex.: "tese
   movida para abertura do parágrafo 4", "contraste aparência/realidade
   explicitado no parágrafo 7").
3. **Sinalizações**, se houver: `[VERIFICAR: descrição do que falta]` para
   qualquer trecho que a voz RCT pediria mais densidade mas o material
   fornecido não sustenta.
