---
name: proprio-punho
description: Clone opcional do estilo de escrita jurídica do usuário. Use para calibrar um perfil autoral ou quando o usuário pedir expressamente estilo-alvo Ricardo, "no meu estilo" ou equivalente. Não acione automaticamente em toda redação RDAA; o perfil apenas orienta a voz e não substitui o núcleo institucional.
---

# Próprio Punho — clone de peças e estilo de escrita

O nome diz a promessa: a minuta sai como se tivesse sido escrita **de próprio punho** pelo autor. Esta skill faz a IA escrever textos jurídicos **com a cara do autor**: mesma estrutura, mesmo vocabulário, mesmo jeito de argumentar. Ela tem dois modos de operação e uma rotina de melhoria contínua.

**Hierarquia obrigatória:** precisão factual e jurídica → Manual/RDAA → regra
editorial identificada → perfil autoral. Na dúvida entre completar, esclarecer
e reproduzir um traço do autor, preserve completude e clareza.

## Arquivos da skill

| Arquivo | O que é |
|---|---|
| `references/perfil-do-autor.md` | Quem é o autor: papel, quem representa, bloco de assinatura, confidencialidade. Preenchido na **Etapa 0**. |
| `references/guia-de-estilo.md` | O DNA do estilo: tendências verificáveis extraídas das peças do autor. Orienta a voz dentro da hierarquia institucional. |
| `references/anti-estilo.md` | O que o autor NUNCA escreve: expressões de IA proibidas, vetos pessoais e pares antes/depois. |
| `references/analise-de-corpus.md` | O método de engenharia reversa em três camadas (estrutura + argumentação + frase), usado no modo Calibração. |
| `modelos/` | 1–2 peças reais do autor, anonimizadas e completas, para consulta de voz, vocabulário e construção argumentativa. |

> Checagem de estado, nesta ordem: (1) `perfil-do-autor.md` com placeholders `{...}` → rode a **Etapa 0 — Personalização** antes de qualquer coisa; (2) `guia-de-estilo.md` com placeholders → ofereça o **Modo 1 — Calibração** antes de redigir.

## Personalização (início da primeira interação e da criação do clone)

Objetivo: a skill nunca trabalha para um autor genérico. Antes da primeira calibração ou da primeira minuta, monte o perfil de quem está usando.

1. **Pergunte em um bloco só** (não interrogue aos poucos; aceite respostas parciais):
   - Nome e **bloco de assinatura exato** das peças (nome, título, OAB ou matrícula).
   - Papel profissional (advocacia privada, procuradoria, defensoria, assessoria, in-house) e **quem representa habitualmente** (cliente-tipo/ente; polo ativo ou passivo predominante).
   - **Gênero de peça a clonar primeiro** (uma escolha só; contestação ≠ parecer ≠ inicial).
   - Onde mais atua (juizados, varas, tribunais; esfera estadual/federal; comarcas).
   - **Vetos e manias já conhecidos** ("nunca escrevo X", "sempre abro com Y").
   - **Regras de confidencialidade**: padrão de anonimização (default: AUTOR/RÉU, números zerados) e termos que nunca podem aparecer em exemplos e materiais derivados.
2. **Preencha `references/perfil-do-autor.md`** com as respostas e mostre ao usuário para confirmar/corrigir.
3. Vetos declarados no item de manias entram desde já em `anti-estilo.md` (Parte 2, marcados como "declarado pelo autor, pré-calibração").
4. Feche oferecendo o próximo passo natural: **Modo 1 — Calibração** com as peças do gênero escolhido.

Reabra a Etapa 0 sempre que o usuário disser que mudou de função, de cliente-tipo ou de gênero-alvo ("agora quero clonar meus pareceres").

## Modo 1 — Calibração (primeira vez ou atualização)

Quando o usuário pedir para analisar as peças dele, criar/atualizar o clone, ou quando o guia estiver vazio (perfil já preenchido na Etapa 0):

1. **Peça o corpus.** 5 a 10 peças do autor: versão final/protocolada, as melhores dele, e do MESMO gênero definido no perfil (contestação ≠ parecer). Poucas, recentes e boas > muitas e velhas.
2. **Confira a anonimização.** Antes de processar, verifique se há nome de parte, CPF, endereço, número de processo ou dado sensível. Se houver, avise e ofereça anonimizar primeiro (AUTOR/RÉU, dados suprimidos). Não siga com dados sigilosos expostos.
3. **Rode a engenharia reversa** seguindo `references/analise-de-corpus.md` nas camadas de estrutura, argumentação e frase. Não extraia regra de formatação institucional do corpus: ela continua sendo a do RDAA. Padrão de qualidade: **toda tendência tem de ser verificável e vir com exemplo literal extraído das peças**. "Estilo formal e objetivo" é análise de horóscopo — proibido.
4. **Preencha `references/guia-de-estilo.md`** substituindo os placeholders pelas tendências encontradas. Mostre o resultado ao usuário e pergunte o que ele veta ou ajusta.
5. **Popule `modelos/`** com 1–2 peças do corpus escolhidas pelo usuário, anonimizadas e preservadas para consulta textual.
6. **Teste cego.** Peça um caso real JÁ ENCERRADO do autor (só os fatos, sem a peça dele). Gere a minuta, depois compare com a peça que ele realmente protocolou, parágrafo a parágrafo. Cada divergência vira regra nova no guia ou par novo no anti-estilo. Repita até o autor dizer que passaria num teste cego com um colega.

## Modo 2 — Redação (uso diário)

Quando o usuário pedir explicitamente estilo-alvo Ricardo, "no meu estilo" ou equivalente:

1. **Leia** `references/perfil-do-autor.md` (quem assina, quem representa, confidencialidade), `references/guia-de-estilo.md`, `references/anti-estilo.md` e ao menos um arquivo de `modelos/` ANTES de escrever. Endereçamento, preâmbulo e bloco de assinatura saem do perfil.
2. **Entenda o caso** (fatos, tese, pedido). Se faltar informação essencial, pergunte antes de redigir.
3. **Estruture** conforme a peça e o núcleo RDAA; **redija** usando o guia apenas para escolhas de voz compatíveis.
4. **Passe o pente-fino do anti-estilo**: releia a minuta caçando expressões proibidas e padrões de IA; reescreva cada ocorrência no estilo do autor (use os pares antes/depois como referência).
5. **Jurisprudência e doutrina: nunca invente.** Resultado obtido diretamente em Jusbrasil, Jurisprudência.AI ou JusRatio pode ser citado sem segunda conferência. Fonte do Cérebro-Ricar só é conferida se parecer estranha ou se Ricardo pedir. Toda outra citação sem origem confiável sai da minuta ou entra marcada como `[CONFERIR NA FONTE: ...]`.
6. **Aplique a formatação institucional RDAA pela skill `formatar-peca`.** O modelo do autor serve para voz textual; não substitui fonte, margens, destaques, títulos, numeração ou outro padrão visual vigente.
7. **Entregue como rascunho.** Feche lembrando (uma linha, sem sermão) que a minuta exige revisão integral do autor antes de protocolar.

## Modo 3 — Feedback contínuo (o clone melhora a cada peça)

Sempre que o usuário corrigir um trecho da minuta ("eu não escrevo assim", "troca isso por aquilo"):

1. Aplique a correção no texto.
2. **Converta a correção em aprendizado permanente:** vire um par antes/depois em `references/anti-estilo.md` ou uma regra nova em `references/guia-de-estilo.md` (pergunte só se for ambíguo onde encaixar).
3. Confirme em uma linha o que foi registrado, para o usuário saber que o clone aprendeu.

## Limites (inegociáveis)

- O clone reproduz **forma**, não substitui o juízo profissional do autor: revisão humana integral, sempre.
- Jurisprudência sempre com origem identificada; resultado direto de Jusbrasil, Jurisprudência.AI ou JusRatio dispensa segunda conferência. Nada de julgado, lei ou doutrina inventados.
- Dados sigilosos de cliente não entram no corpus nem nos modelos sem anonimização.
