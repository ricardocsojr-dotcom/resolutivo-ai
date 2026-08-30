# Roteamento de IA por nível de peça — RDAA

> Referência de como distribuir o trabalho entre as CLIs de IA que o
> escritório já paga (Claude Code, Codex, Gemini/Antigravity), sem
> orquestrador automático — nem Hermes, nem OmniRoute, nem qualquer motor de
> regras. O nível da peça é sempre declarado por Ricardo — nenhum roteamento
> reclassifica ou troca a rota sozinho. Trocar de CLI é trocar de
> programa/janela: não existe combo, `/model` unificado, nem fallback de
> assinatura.

## Tabela de roteamento (revisada 2026-08-30)

| Papel no fluxo | Motor | Status |
|---|---|---|
| Orquestração do fluxo inteiro, classificar C/B/A, coletar contexto, esqueleto | Claude Code | Estável |
| Leitura/extração de documento longo (autos, contrato extenso) | Antigravity/Gemini (`antigravity-worker`) | Estável, comprovado em teste real (30/08) |
| **Redigir a peça (voz autoral)** | **Codex** (nível B) · Claude (nível A, por ora) | **Decidido, ainda não testado na prática** — nível A permanece com Claude até um nível B rodar por esse esquema |
| Camadas de estilo pós-redação (RCT/Flávia) | Mesmo motor da redação | Consequência da decisão acima |
| Validar (forma + fidelidade ao esqueleto/tese) — substitui crítica e revisor-detecção como passes separados | Claude, sempre que outro motor redigiu | Decidido |
| Corrigir achado objetivo (checklist mecânico) | Quem escreveu (Codex ou Claude) | Decidido |
| Corrigir achado que exige julgamento de voz/tese | Claude | Decidido |
| Conselho (nível A) | Claude, isolado — nunca o mesmo motor do redator | Decidido |
| Cálculo judicial | Script Python determinístico, não é IA | Estável |

Ver `referencias/decisoes-roteamento-motores-2026-08-30.md` para o raciocínio completo (auditoria adversarial que motivou a virada, achados do teste real de pipeline, gaps de skill descobertos).

## Regras

1. **Cada papel do fluxo declara seu motor atual, não é fixo por natureza do papel.** A tabela acima é o estado hoje, não uma lei — trocar o motor de um papel é editar uma linha aqui, não uma regra de arquitetura nova. Isso resolve o problema achado em 30/08/2026 de "roteamento perdido" (decisão de motor hardcoded em prosa dentro de `redigir-peca/SKILL.md`).
2. **Nenhum papel de auditoria/crítica pode ser o mesmo motor que escreveu a peça sendo auditada.** Regra central desde 30/08/2026 — vale pra crítica estratégica, validação de forma e Conselho.
3. **Gemini/Antigravity é a única CLI só de leitura.** Não decide tese, não escreve peça, só lê/extrai e relata via `antigravity-worker` (ou `gestao-materias`/`HANDOFF.md` pra uso manual fora de subagente).
4. **Delegação de um passo só usa Bash direto, não subagente autônomo.** Achado em 30/08/2026: rodar `codex-worker`/`antigravity-worker` via `Agent` tool custa ~90-170 mil tokens de wrapper por chamada, mesmo quando a tarefa é só "manda X, recebe resposta". Reservar o subagente autônomo pra tarefa que precisa de exploração real (ler documento grande, auditar repositório); delegação simples de um comando só chama o CLI direto via Bash na sessão principal.
5. **Nenhuma rota é fallback de limite.** Se uma CLI falhar ou atingir cota, o fluxo pausa e Ricardo decide — nunca troca de assinatura silenciosamente.
6. Para infográficos jurídicos: SVG/HTML/Word determinístico. Imagem generativa é só decorativa, nunca contém fato, data, valor, prova ou tese.

## Protocolo de exceção

Se qualquer CLI encontrar fato incerto, documento ausente, contradição relevante ou risco de alteração de pedido:

1. não completa a peça por inferência;
2. abre uma pendência na matéria e pausa o estágio;
3. solicita segunda análise independente de outra CLI, limitada ao ponto e às referências documentais;
4. apresenta as duas análises a Ricardo;
5. somente Ricardo decide. A decisão não retoma a matéria automaticamente.

Não há terceira análise automática, pesquisa externa automática nem correção silenciosa.

## Fontes externas

DataJud, DJEN e NotebookLM continuam bloqueados por padrão (consulta manual, só a pedido de Ricardo — ver `CLAUDE.md`). **Exceção desde 2026-08-26**: o Ementário do Resolutivo (vault de tese/jurisprudência) é consultado **automaticamente** por `redigir-peca` em peça nível B/A, antes do esqueleto (passo 9) — não é mais autorização por matéria, é comportamento padrão do nível. Pesquisa **nova** de jurisprudência (Jusbrasil, via `jusbrasil-jurisprudencia`) continua tarefa do Claude e automática só no tipo A; no tipo B exige pedido expresso.

## Mecanismo de execução (sem orquestrador)

Não existe interface única nem motor de regras escolhendo CLI sozinho — quem decide a etapa é sempre Ricardo (ou Claude, seguindo instrução dele).

- **Claude Code ↔ Codex**: nenhuma ponte de dados é necessária. Os dois leem/escrevem o mesmo `.rdaa-run/<matter_id>/` — trocar de CLI no meio de uma peça é só abrir a outra janela apontando pro mesmo diretório de trabalho.
- **Claude Code/Codex → Gemini**: usar `gestao-materias` (`gerar-handoff`) e colar o conteúdo de `HANDOFF.md` como contexto inicial da sessão do Gemini — é a única CLI que precisa desse pacote, porque não compartilha `.rdaa-run` nem skills.
- Nenhuma CLI abre outra automaticamente. Se Ricardo pedir pra Claude Code orquestrar isso via terminal (rodar o comando da outra CLI e ler o retorno), isso é um passo manual de cada vez, não uma automação permanente — ver "Fora do escopo" em `skills/gestao-materias/SKILL.md`.

## Nota de origem

Esta tabela nasceu de uma arquitetura anterior que usava o Hermes como dispatcher automático entre Claude Code, Codex e Antigravity — descartada por experiência de uso ruim. Depois passou pelo OmniRoute (interface única com combos por assinatura) — também descartado, em 2026-08-26, junto com a decisão de reconstruir a organização do escritório do zero, sem WSL nem orquestrador automático algum. A lógica de divisão de trabalho por nível foi preservada nas duas transições; o que mudou foi o mecanismo de execução, que hoje é: cada CLI na sua própria janela, coordenada por Ricardo.

**Revisão de 2026-08-30**: a tabela por nível (C/B/A → CLI) foi substituída por uma tabela por papel (função do fluxo → motor), depois de um estudo do `block/buzz` (persona com motor declarado em arquivo) e de uma auditoria adversarial pedida ao próprio Codex sobre o quadro anterior, que apontou concentração de trabalho em Claude sem justificativa técnica em vários pontos ("centralização autojustificada", nas palavras do Codex). Um teste real de pipeline no mesmo dia (agravo de instrumento real, TJ-GO) validou a arquitetura de subagentes e achou um problema de custo real — ver `referencias/decisoes-roteamento-motores-2026-08-30.md`.
