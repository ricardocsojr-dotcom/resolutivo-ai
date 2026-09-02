# Roteamento de IA e controle de workflow — RDAA

A política executável está em `orquestracao/roteamento.json`. Este documento explica o desenho; não é fonte concorrente de regras.

## Arquitetura

```text
Ricardo → Hermes (gerente) → máquina de estados determinística
                              ├─ Claude: planejamento e validação
                              ├─ Codex: redação autoral
                              ├─ Agy: extração longa e crítica adversarial
                              └─ Python: estado, cálculo, QA e DOCX
```

Hermes apresenta status, coleta aprovações, monta pacotes mínimos e chama workers. Ele não decide mérito jurídico, não avalia se uma crítica foi resolvida e não conta como segunda opinião independente do Codex.

## Papéis vigentes

| Papel | Worker | Limite |
|---|---|---|
| Planejamento, esqueleto e validação | Claude Code | sessão/pacote isolados |
| Redação | Codex | somente saída de texto; nunca publica |
| Crítica adversarial e extração longa | Antigravity (`agy`) | nunca redige, corrige, publica ou altera estado |
| Orquestração e gates | Hermes + `orquestrador_rdaa.py` | não toma decisão jurídica |
| Cálculo, QA e DOCX | scripts Python | determinísticos |

A rota válida exige que redator, crítico e validador tenham famílias de modelo distintas. O manifesto registra provider, família, CLI, hashes, duração e ID de sessão quando a CLI o fornece.

## Nível e risco

- C/B/A determina o fluxo mínimo.
- Baixo/médio/alto/crítico é eixo separado e só pode escalar o fluxo.
- C com risco alto sobe para B; risco crítico sobe para A.
- B sempre inclui crítica independente; A inclui conselho e gates adicionais.

## Fluxo

```text
initialized → intake_ready → [vault_context_ready em B/A] → [sources/council] → skeleton_ready
→ awaiting_skeleton_approval → skeleton_approved → drafting → draft_ready
→ [criticizing → critique_ready] → validating → candidate_ready
→ qa_passed → release_ready → published → vault_registered
```

A máquina de estados não permite pular fases. A aprovação do esqueleto grava o hash do arquivo; qualquer alteração invalida a aprovação. Cada papel tem fases permitidas na política e é validado **antes** de qualquer chamada externa. Em peça A, uma vulnerabilidade de tese central abre o gate condicional `strategy_exception`, bloqueando novas transições até a decisão humana ser registrada.

## Execução direta

Chamadas de worker passam pelo executor, sem `Agent` ou subagente mensageiro:

```text
py -3.14 skills/redigir-peca/scripts/executar_motor.py codex --prompt ... --output ... --state-dir .rdaa-run/<matter_id> --role writer
py -3.14 skills/redigir-peca/scripts/executar_motor.py antigravity --prompt ... --output ... --schema ... --state-dir .rdaa-run/<matter_id> --role critic
py -3.14 skills/redigir-peca/scripts/executar_motor.py claude --prompt ... --output ... --state-dir .rdaa-run/<matter_id> --role validator
```

Falha, quota ou timeout bloqueia a matéria. Não existe fallback silencioso de assinatura ou motor.

## Fontes e exceções

Jurisprudência externa continua exclusiva do Jusbrasil. Ementário é consultado em B/A conforme a skill de redação. DataJud, DJEN e NotebookLM ficam desligados salvo instrução expressa.

O conector `integracao_obsidian.py` monta o pacote fechado `EMENTARIO-CONTEXTO.json` a partir do domínio e de seus links diretos para teses/fontes. Ele é somente leitura, preserva hash de cada nota, marca todo conteúdo como `informada` e redige metadados de matérias históricas antes de formar o pacote. A etapa `vault_context_ready` exige esse pacote registrado e íntegro. Após publicação, `vault_registered` exige recibo hashável do registro operacional; uma solicitação pendente de ingestão no Ementário não pode encerrar a matéria.

Quando houver fato incerto, fonte ausente, contradição relevante ou mudança potencial de tese/pedido, o fluxo registra pendência e aguarda Ricardo. Nenhum worker conclui por inferência.

## Histórico

O fluxo manual de 30/08/2026 foi substituído porque mantinha passos repetitivos fora do estado compartilhado. A nova automação preserva a decisão que rejeitou subagentes como transporte: workers são sempre CLIs chamadas diretamente, em contextos isolados.
