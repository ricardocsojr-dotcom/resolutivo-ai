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
| Leitura/extração de documento longo (autos, contrato extenso) | Antigravity/Gemini, chamado diretamente via `agy` | Estável, comprovado em teste real (30/08) |
| **Redigir a peça (voz autoral)** | **Codex** (níveis C, B e A) | **Decidido por Ricardo em 30/08/2026** |
| Camadas de estilo pós-redação (RCT/Flávia) | Mesmo motor da redação | Consequência da decisão acima |
| Crítica adversarial (tese, lacunas e vulnerabilidades) | Antigravity/Gemini, chamado diretamente via `agy` | Decidido |
| Validar e corrigir (forma + fidelidade ao esqueleto/tese) | Claude, sempre que Codex redigiu | Decidido |
| Corrigir achado objetivo (checklist mecânico) | Claude, como corretor | Decidido |
| Corrigir achado que exige julgamento de voz/tese | Claude | Decidido |
| Conselho (nível A) | Claude, isolado — nunca o mesmo motor do redator | Decidido |
| Cálculo judicial | Script Python determinístico, não é IA | Estável |

Ver `referencias/decisoes-roteamento-motores-2026-08-30.md` para o raciocínio completo (auditoria adversarial que motivou a virada, achados do teste real de pipeline, gaps de skill descobertos).

## Regras

1. **Cada papel do fluxo declara seu motor atual, não é fixo por natureza do papel.** A tabela acima é o estado hoje, não uma lei — trocar o motor de um papel é editar uma linha aqui, não uma regra de arquitetura nova. Isso resolve o problema achado em 30/08/2026 de "roteamento perdido" (decisão de motor hardcoded em prosa dentro de `redigir-peca/SKILL.md`).
2. **Nenhum papel de auditoria/crítica pode ser o mesmo motor que escreveu a peça sendo auditada.** Regra central desde 30/08/2026 — vale pra crítica estratégica, validação de forma e Conselho.
3. **Gemini/Antigravity não redige nem publica.** Faz leitura/extração e crítica adversarial por chamada direta via `agy`; seus achados são proposta, nunca alteração de tese, pedido ou estado.
4. **Não use `Agent` como mensageiro entre CLIs.** Chamadas a Codex e Antigravity são feitas diretamente da sessão principal pelo executor de `redigir-peca`. O wrapper de um subagente Claude consumiu ~90-170 mil tokens por chamada no teste de 30/08 e foi removido do fluxo.
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
- **Claude → Antigravity**: para extração ou crítica, use o executor direto de `redigir-peca`, que envia o recorte por `stream-json` e recebe a resposta sem wrapper. `HANDOFF.md` permanece disponível somente para uma continuação manual mais ampla.
- Nenhuma CLI abre outra automaticamente. Se Ricardo pedir pra Claude Code orquestrar isso via terminal (rodar o comando da outra CLI e ler o retorno), isso é um passo manual de cada vez, não uma automação permanente — ver "Fora do escopo" em `skills/gestao-materias/SKILL.md`.

## Nota de origem

Esta tabela nasceu de uma arquitetura anterior que usava o Hermes como dispatcher automático entre Claude Code, Codex e Antigravity — descartada por experiência de uso ruim. Depois passou pelo OmniRoute (interface única com combos por assinatura) — também descartado, em 2026-08-26, junto com a decisão de reconstruir a orquestração sem depender de WSL nem de motor automático. O Ementário adotado depois continua armazenado no WSL, mas não executa a orquestração. A lógica de divisão de trabalho por nível foi preservada nas duas transições; o que mudou foi o mecanismo de execução.

**Revisão de 2026-08-30**: a tabela por nível (C/B/A → CLI) foi substituída por uma tabela por papel (função do fluxo → motor), depois de um estudo do `block/buzz` e de uma auditoria adversarial do quadro anterior. O teste real do mesmo dia mostrou que a separação de papéis funciona, mas invalidou o uso de subagentes como transporte: três wrappers consumiram cerca de 371 mil tokens. A arquitetura vigente usa chamadas diretas, Codex como redator de todos os níveis, Antigravity como crítico e Claude como corretor — ver `referencias/decisoes-roteamento-motores-2026-08-30.md`.
