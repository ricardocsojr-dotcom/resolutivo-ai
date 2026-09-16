---
name: operar-motor-rdaa
description: Use when running RDAA V4 engine or drafting legal pieces.
---

# Operação do Motor RDAA V4 (Plugin de Automação Jurídica)

Este repositório contém o **Motor RDAA V4**, uma engine baseada em LangGraph e Python (`orquestracao/engine.py` e `orquestracao/cli.py`) projetada para orquestrar fluxos de trabalhos jurídicos de alta precisão (níveis A, B e C), desde a triagem de documentos (intake) até a publicação e registro (Cérebro-Ricar).

Você, como assistente IA, é capaz de dirigir essa engine **de forma autossuficiente** usando seu terminal e chamadas de código.

## A Máquina de Estados e a Abordagem Híbrida

A engine foi refatorada para ser **opcionalmente assistida**. O motor **sempre pausa** (`interrupt_before`) antes de invocar um worker autônomo (como `planner`, `writer`, `validator`). 

Quando a engine pausar numa destas fases, VOCÊ decide com o usuário o que fazer:
1. **Fazer Manualmente/Juntos:** Trabalhar no documento colaborativamente usando ferramentas ou chat e dar **`jump`** na engine para a próxima fase.
2. **Rodar a Automação:** Autorizar o sub-agente da engine a gastar tempo/processamento dando **`step`**.

## Fases Intelectuais x Fases Mecânicas — a linha que `jump` nunca cruza

Nem toda fase é igual. Divida sempre a rota (`orquestracao/roteamento.json`) em dois grupos:

- **Fases intelectuais** — pesquisa/planejamento/escrita/crítica/validação
  (`intake_ready`, `sources_ready`, `skeleton_ready`, `drafting`,
  `criticizing`, `validating`). Aqui você tem liberdade total: pode fazer
  com o Ricardo direto no chat e dar `jump` por cima, sem rodar o
  sub-agente da engine.
- **Fases mecânicas** — `qa_passed`, `published`, `vault_registered`.
  Rodam `system_handlers.py` de forma determinística (sem IA) e **nunca
  podem ser puladas por cima**: elas têm que rodar de verdade. O motor já
  recusa sozinho (`GateError`) qualquer `jump` cujo intervalo pulado
  contenha uma dessas fases — não é só uma regra de conduta, é uma
  trava estrutural em `RDAAEngine.jump()`.

**Regra dura sobre o motor de Word:** depois de redigir a peça com o
Ricardo no chat (fase intelectual), o texto final só vira documento
publicável passando pelo motor oficial —
`skills/formatar-peca/scripts/construir_peca.py` (via a skill
`formatar-peca`) — que preenche `outputs[role]["docx_path"]` e
`["context_path"]`. **PROIBIDO** improvisar um gerador de Word próprio
(python-docx cru ou qualquer script novo) ou escrever esses campos
manualmente apontando para um arquivo que não saiu desse motor: você
perde numeração nativa, estilos nomeados, notas de rodapé reais e o
salvamento atômico no local correto — e quebra o contrato que
`handle_qa_passed`/`handle_published`/`handle_vault_registered` exigem
para publicar e registrar no Cérebro.

## Comandos da CLI (`orquestracao/cli.py`)

Execute os seguintes comandos bash na raiz do projeto:

### 1. Inicializar Matéria (rdaa start)
Cria o caso e dispara a fase de *intake_ready* (leitura de anexos).
```bash
python orquestracao/cli.py start /caminho/para/state_dir --matter-id "ID-DO-CASO" --level B --no-ocr
```
**Nota:** Sempre use `--no-ocr` a menos que explicitamente solicitado processamento massivo. O OCR de imagens é demorado e pesado.

### 2. Verificar Status (rdaa status)
Vê em qual etapa o processo está aguardando (json).
```bash
python orquestracao/cli.py status /caminho/para/state_dir
```

### 3. Pular Etapa (rdaa jump) - **Escape Hatch só para fases intelectuais**
Força a mudança para a etapa desejada, essencial quando a tarefa foi feita manualmente via chat. Use somente para saltar por cima de fases intelectuais (`intake_ready`, `sources_ready`, `skeleton_ready`, `drafting`, `criticizing`, `validating`). Nunca tente pular `qa_passed`, `published` ou `vault_registered` — o motor recusa o comando sozinho se o intervalo pulado incluir alguma delas.
```bash
python orquestracao/cli.py jump /caminho/para/state_dir --phase draft_ready --reason "Feito colaborativamente no chat" --authority ricardo
```
Depois de alcançar a última fase intelectual, deixe o grafo seguir sozinho (novo `jump`/`step` normal) para que `qa_passed` → `published` → `vault_registered` rodem de verdade.

### 4. Rodar Worker (rdaa step)
Delega uma tarefa rigorosa e autônoma à engine no momento em que ela está pausada antes de um Worker.
```bash
python orquestracao/cli.py step /caminho/para/state_dir --authority ricardo
```

### 5. Aprovar Gate / Retomar (rdaa approve / rdaa resume)
- **approve:** Preenche gates exigidos de aprovação humana, ex: `skeleton_approval`.
- **resume:** Após falha grave não tratada pelo disjuntor.

---
**Regras de Atuação Autossuficiente:** 
- Nunca engesse o processo.
- Sempre rode `status` antes de opinar.
- Aja ativamente via CLI sem requerer que o usuário digite os scripts python. Levante as opções e, ciente delas, pilote a CLI sozinho.