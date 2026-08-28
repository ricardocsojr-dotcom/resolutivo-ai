---
name: esqueleto-peca
description: >
  Monta o esqueleto estrutural obrigatório de uma peça processual — os
  requisitos formais que o CPC exige (não a estratégia ou a redação final,
  que continuam com `contencioso-rdaa`/`dano-moral-rct`) — e para o fluxo
  para aprovação do Ricardo antes de qualquer redação completa começar.
  Cobre petição inicial cível, contestação cível, e a família de recursos
  (recurso genérico, apelação, agravo de instrumento) e ação de cobrança.
  Chamada sempre pela skill `redigir-peca` como etapa intermediária — não é
  para ser usada isolada pelo Ricardo.
---

# Esqueleto de Peça — Checklist Estrutural RDAA

Esta skill resolve um problema específico: `contencioso-rdaa` cobre
estratégia (ACH, comportamento adversarial, teses) e estilo de redação, mas
não garante que a peça tenha todos os requisitos formais que o CPC exige.
Essa lacuna é a mesma para petição inicial, contestação, e toda a família de
recursos — por isso está numa skill só, reaproveitada pelas seis situações.

**Não redige a peça inteira.** Entrega uma estrutura (esqueleto) com cada
bloco obrigatório indicado, as ementas selecionadas na busca de
jurisprudência já encaixadas no bloco a que pertencem, e as teses propostas.
Cada fonte escolhida deve chegar com `source_id`, origem, localização, status,
uso e indicação do bloco. O esqueleto deve declarar `fontes_status` e
aprovação explícita. Para aí e espera aprovação antes de `redigir-peca` seguir
para a redação completa via `contencioso-rdaa`/`dano-moral-rct`.

Leia `references/fontes-e-provenance.md` para o contrato de origem, conferência
e inclusão posterior de fontes. Leia também `references/playbook-modelos.md`
quando houver modelo de estrutura selecionado.

## Níveis de peça e modelos de estrutura

A classificação deve ser declarada no contexto como `nivel_peca` com valor `A`,
`B` ou `C`. Ela representa o modo de produção da peça e não representa risco,
validade, pertinência ou qualidade jurídica.

- **Tipo A** é a peça premium. Pode usar todos os recursos aprovados para o
  caso, inclusive pesquisa autorizada, Visual Law, Legal Design, ilustrações,
  decisões anotadas e crítica por risco.
- **Tipo B** é baseado principalmente no que já existe no processo, mas pode
  desenvolver melhor a explicação, a organização, os fundamentos, as provas ou
  o Legal Design. Exemplos incluem manifestações complexas, memoriais,
  especificação de provas e impugnações.
- **Tipo C** é muito simples, em regra escrito com parágrafos curtos e sem
  necessidade de tópicos. Exemplos incluem juntadas, oposições simples e
  manifestações simples.

A redação por blocos é permitida somente nos tipos A e B. O tipo C não entra em
fluxo de redação por blocos, embora o gerador possa usar objetos técnicos
internos para montar parágrafos e assinatura.

Esta skill (montagem do esqueleto em si) não consulta vault nenhum — ela só
recebe o material já organizado por `redigir-peca`, que nos tipos B/A já
inclui o que veio da consulta automática ao Ementário do Resolutivo (passo
9 de `redigir-peca/SKILL.md`). O playbook de modelos organiza somente
estruturas aprovadas e não aplica automaticamente tese, fato, fonte,
pedido ou pertinência jurídica — vindo do vault ou de qualquer outra
origem.

## Gate de escalonamento manual — quando travar antes de redigir

Isto não é mérito, tese ou risco jurídico — é só uma trava de fluxo. Quando
uma das condições abaixo bater, o esqueleto não segue para aprovação normal:
ele para com `AskUserQuestion` (mesma ferramenta do passo de aprovação do
esqueleto) e pede a decisão explícita do Ricardo antes de `redigir-peca`
continuar para a redação completa. Isto existe porque o fluxo A/B hoje roda
sozinho até a publicação — sem essa trava, uma situação sensível seguiria
até o fim sem ninguém parar para olhar.

Gatilhos da v1 (ajustáveis — não são regra jurídica, são limiar operacional):

1. **Valor da causa acima de R$ 500.000,00.** Checagem objetiva sobre o
   campo calculado no bloco "Valor da causa" do checklist. Não infira valor
   não declarado — se o valor não está calculado ainda, isso já é um `[FALTA]`
   normal, não este gatilho.
2. **Tese central sem nenhuma fonte/ementa que a sustente**, no tipo A, depois
   da pesquisa de jurisprudência automática (passo 4 de `redigir-peca`) não
   ter encontrado nada aproveitável. Redigir uma tese "nova" sem qualquer
   precedente interno ou jurisprudência selecionada é decisão de Ricardo, não
   do fluxo.
3. **Bloco essencial com `[VERIFICAR]` ou `[FALTA]`** em pedido, valor da
   causa ou qualificação de parte — lacunas em blocos formais menores (ex.:
   opção por audiência) não travam, só ficam marcadas no esqueleto normal.
4. **Crítico (`critico-rdaa`) aponta vulnerabilidade que a rodada automática
   de correção do passo 7.5 não resolveu por completo.** Hoje isso só vira
   nota na entrega; quando a vulnerabilidade remanescente for de tese central
   (não de forma), trava aqui em vez de publicar com pendência não resolvida.

Não é gatilho: prazo da peça (nunca questionar tempestividade, ver
`CLAUDE.md`), nível da peça (A/B/C não é risco), e conteúdo do Ementário
do Resolutivo (mesmo sendo consultado automaticamente em B/A, o que ele
traz é `status: informada` — não vira sinal automático deste gate nem tese
aprovada sozinho).

Quando travar, apresente ao Ricardo qual gatilho bateu e o dado concreto
(valor declarado, tese sem fonte, bloco faltando, achado do crítico) — não
uma reformulação genérica de "risco alto". `AskUserQuestion` com opções como
"seguir mesmo assim" / "ajustar antes de seguir" / "aguardar mais insumo".

## Quando usar cada checklist

| Tipo de peça | Checklist |
|---|---|
| Petição inicial cível | [Petição inicial](#petição-inicial-cível-cpc-319-320) |
| Ação de cobrança | Petição inicial + [nota específica](#nota-ação-de-cobrança) |
| Contestação cível | [Contestação](#contestação-cível-cpc-335-343) |
| Recurso (quando ainda não se sabe qual cabe) | [Cabimento](#cabimento-recursal) primeiro, depois o checklist do recurso identificado |
| Apelação | [Apelação](#apelação-cpc-1009-1014) |
| Agravo de instrumento | [Agravo de instrumento](#agravo-de-instrumento-cpc-1015-1020) |

---

## Petição inicial cível (CPC 319, 320)

Blocos obrigatórios — marcar `[FALTA]` em qualquer um que não tenha insumo:

1. **Endereçamento** — juízo a que é dirigida (CPC 319, I).
2. **Qualificação completa das partes** — nome, estado civil, existência de
   união estável, profissão, CPF/CNPJ, endereço eletrônico, domicílio e
   residência de autor e réu (CPC 319, II).
3. **Dos fatos e fundamentos jurídicos do pedido** (CPC 319, III) — aqui
   entra o trabalho de `contencioso-rdaa`, este checklist só confirma que o
   bloco existe.
4. **Do pedido, com as especificações** (CPC 319, IV) — inclui pedido
   principal, subsidiário se houver, e os pedidos de praxe (citação, gratuidade
   se cabível, provas, procedência com condenação em custas e honorários).
5. **Valor da causa** (CPC 319, V) — calculado, não deixar em aberto.
6. **Provas com que pretende demonstrar os fatos** (CPC 319, VI).
7. **Opção por audiência de conciliação/mediação** (CPC 319, VII).
8. **Documentos indispensáveis anexados** (CPC 320) — procuração e os
   documentos que fundamentam o pedido.
9. **Tutela provisória, se cabível** (CPC 300 urgência / CPC 311 evidência)
   — marcar se o caso pede e se o pedido está estruturado.

### Nota: ação de cobrança

Mesmo checklist acima, mais atenção a: prescrição (CC 206), se o crédito tem
título executivo (rito comum) ou não (avaliar monitória, CPC 700-702), e
cálculo do valor atualizado anexado como memória (usar a skill `perfil-csv`
depois que o 56/cálculo judicial estiver pronto).

---

## Contestação cível (CPC 335-343)

Prazo: 15 dias úteis da citação (CPC 335), salvo Fazenda Pública/Defensoria
(prazo em dobro, CPC 183/186).

1. **Preliminares cabíveis (CPC 337)** — percorrer a lista e marcar as que
   se aplicam: inexistência/nulidade de citação; incompetência absoluta ou
   relativa; incorreção do valor da causa; inépcia da inicial; perempção;
   litispendência; coisa julgada; conexão; incapacidade da parte ou defeito
   de representação; convenção de arbitragem; ilegitimidade ou falta de
   interesse processual; falta de caução ou prestação exigida por lei;
   indevida concessão de gratuidade.
2. **Impugnação especificada de cada fato da inicial** (CPC 341) — regra
   central: fato não impugnado especificamente presume-se verdadeiro, exceto
   se não admitir confissão, se a inicial não veio com instrumento público
   exigido, ou se contrariar prova dos autos. Este checklist exige percorrer
   a inicial parágrafo a parágrafo e confirmar que nenhum ficou sem resposta
   — a redação da resposta em si é trabalho do `contencioso-rdaa`.
3. **Mérito** — aqui entra a tese, trabalho do `contencioso-rdaa`.
4. **Reconvenção, se cabível** (CPC 343) — cabe na própria contestação.
5. **Provas requeridas.**
6. **Pedido de gratuidade, se cabível.**

---

## Cabimento recursal

Antes de saber qual checklist de recurso usar, resolver:

1. **Que tipo de decisão está sendo atacada?** Sentença → apelação (CPC
   1.009). Decisão interlocutória → agravo de instrumento, se estiver no rol
   do CPC 1.015 (rol mitigado pelo Tema 988 STJ para casos de urgência/risco
   de dano irreparável fora do rol). Erro material/omissão/contradição/
   obscuridade → embargos de declaração (CPC 1.022), cabe contra qualquer
   decisão. Decisão monocrática de relator → agravo interno (CPC 1.021).
2. **Prazo** — 15 dias úteis na regra geral (CPC 1.003 § 5º), 5 dias para
   embargos de declaração (CPC 1.023), 30 dias se Fazenda Pública (CPC 183).
3. **Preparo** — comprovado no ato da interposição, sob pena de deserção
   (CPC 1.007), exceto gratuidade.
4. **Legitimidade e interesse recursal** — houve sucumbência?

---

## Apelação (CPC 1.009-1.014)

1. Tempestividade (15 dias úteis, 30 Fazenda) — data de publicação/
   intimação + termo final calculados.
2. Preparo + porte comprovados (CPC 1.007), salvo gratuidade.
3. Petição de interposição ao juízo a quo + razões ao tribunal — dois
   documentos, não um.
4. **Cada fundamento da sentença combatido especificamente** — não pode ser
   genérico (CPC 1.010, II/III/IV exige impugnação específica).
5. Classificar o erro: *error in procedendo* (vício processual — cerceamento
   de defesa, falta de fundamentação CPC 489 § 1º) ou *error in judicando*
   (vício de mérito — aplicação errada da lei, valoração de prova).
6. Pedido de honorários recursais (CPC 85 § 11).
7. Efeito suspensivo — regra é automático (CPC 1.012), mas checar as
   exceções do § 1º (I a VI) que exigem pedido expresso se a parte quiser
   suspender.

---

## Agravo de instrumento (CPC 1.015-1.020)

1. Decisão está no rol do CPC 1.015? Se não, há risco de prejuízo iminente
   irreparável que justifique a mitigação do Tema 988 STJ?
2. Prazo 15 dias úteis (CPC 1.003 § 5º).
3. Peças obrigatórias (CPC 1.017) — cópia da petição inicial, contestação,
   decisão agravada, certidão de intimação, procurações de todas as partes.
4. Comunicação ao juízo de primeiro grau em até 3 dias (CPC 1.018).
5. Pedido de efeito suspensivo ou antecipação da tutela recursal, se cabível
   (CPC 1.019, I).

---

## Formalidades comuns a toda peça

Abertura fixa, nome da peça em caixa alta + negrito, pedidos em cascata com
parágrafo introdutório numerado antes das alíneas (sem pedido redundante),
fechamento fixo e data "Cidade/UF" estão definidos no núcleo único de
escrita — `contencioso-rdaa/references/redacao-rdaa.md`, seção 2 — que este
esqueleto pressupõe. O que este checklist acrescenta é só o estrutural:

- **Endereçamento**: vocativo direto ao cargo, sem "digníssimo"/"DD" (Manual
  §2.3 — dispensável para qualquer autoridade pública, é redundante).
- **Ordem dos blocos**: cada checklist de peça acima define quais blocos
  existem e em que sequência — a redação do conteúdo de cada bloco segue o
  núcleo.

## Entrega desta skill (o que volta pra `redigir-peca`)

```
ESQUELETO — [tipo de peça] — [processo, se houver]

[cada bloco do checklist aplicável, com o requisito confirmado ou [FALTA]]

Fontes selecionadas:
- [source_id] — [fonte e origem] — [localização] — [uso] — [bloco]

Ementas selecionadas (da busca de jurisprudência):
- [source_id] — [ementa literal] — [em qual bloco entra]
- [source_id] — [ementa literal] — [em qual bloco entra]

Fontes status
- `fontes_status` deve ser `selecionadas`, `sem_fontes` ou `pendente`.
- Uma fonte externa conferida deve conservar `verificada_externamente` e
  `literalidade_confirmada: true`.

Teses propostas:
- [tese 1 — resumo de uma linha]

--
Aguardando aprovação do esqueleto antes de redigir por extenso.
```

`redigir-peca` para aqui e só prossegue para a redação completa depois de
receber o "ok" explícito do Ricardo sobre este esqueleto. O publicador pode
bloquear o candidato quando o contexto declarar `exigir_esqueleto: true` e a
aprovação, a seleção de fontes ou os vínculos estiverem incompletos.
