---
name: orquestrar-rdaa
description: Use when managing an RDAA matter. Controls its workflow.
---

# Orquestração RDAA no Hermes

Use esta skill para administrar uma matéria de ponta a ponta sem transformar Hermes em redator, crítico ou decisor jurídico. Hermes controla estado, contexto, aprovação humana e chamadas diretas; os motores entregam saídas isoladas.

## Quando usar

- Ricardo pedir para abrir, continuar, pausar, retomar, verificar ou publicar uma matéria.
- Houver peça C/B/A com mais de uma etapa ou mais de um motor.
- For necessário chamar Codex, Claude ou Antigravity e manter proveniência.

Não use para pular uma aprovação humana, decidir mérito jurídico, ou substituir a revisão independente por uma resposta do modelo-base do Hermes.

## Fonte canônica

Leia antes de agir:

1. `HERMES.md`;
2. `AGENTS.md`;
3. `orquestracao/roteamento.json`;
4. a `SKILL.md` jurídica aplicável;
5. `skills/revisor-rdaa/references/contratos-agentes.md` quando montar pacote de worker.

O estado persistido é `espaço de estado do processo.json`. Kanban e conversa não são fontes de verdade.

## Procedimento

1. **Identificar a matéria e a rota.** Use o nível declarado por Ricardo. Se ele não declarar e não houver classificação documentada, use B como padrão conservador; risco só pode escalar a rota.
   ```text
Ação gerenciada automaticamente pelo Orquestrador Central.
```
   Critério: a rota exibida tem nível efetivo, fases, workers e gates.

2. **Inicializar ou recuperar o manifesto.** Use `read_file` para ler o manifesto existente. Se não existir, inicialize uma única vez.
   ```text
Ação gerenciada automaticamente pelo Orquestrador Central.
```
   Critério: `run_manifest.json` existe e sua rota corresponde à classificação.

3. **Consultar o Ementário em B/A.** Depois de `intake_ready`, selecione o domínio já identificado no contexto, gere o pacote somente leitura, registre o hash e avance a etapa específica. O tipo C não executa este passo.
   ```text
Ação gerenciada automaticamente pelo Orquestrador Central.
```
   Critério: o pacote tem origem `ementario-resolutivo`, status `informada`, hashes e nenhum dado de matéria histórica no conteúdo entregue ao worker. O achado não aprova tese.

4. **Avançar somente uma fase por vez.** Use `advance` antes de chamar um worker. Não infira conclusão pela conversa.
   ```text
Ação gerenciada automaticamente pelo Orquestrador Central.
```
   Critério: a transição foi gravada e a fase autoriza o papel pretendido.

5. **Tratar gates humanos.** Para esqueleto ou decisão estratégica, apresente o artefato e use `clarify`. Registre apenas uma aprovação real, vinculada ao arquivo aprovado.
   ```text
Ação gerenciada automaticamente pelo Orquestrador Central.
```
   Sem aprovação, mantenha o estado bloqueado. Nunca crie aprovação em nome de Ricardo.

6. **Executar o worker isolado.** Monte o pacote mínimo no diretório da matéria e use o executor com `--state-dir` e `--role`. O executor recusa motor, papel ou fase incompatíveis antes da chamada externa.
   ```text
Ação gerenciada automaticamente pelo Orquestrador Central.
```
   Critério: saída existe, hash foi registrado e nenhum worker escreveu diretamente no manifesto.

7. **Preservar segregação.** Codex redige; Antigravity critica; Claude planeja, valida ou corrige em contexto novo. Nunca use a mesma família de modelo em redator, crítico e validador. Não use `delegate_task` como mensageiro entre CLIs.

8. **Falhar fechado.** Quota, timeout, saída inválida, lock ou conflito de rota bloqueiam a matéria. Registre a falha e apresente as opções; não faça fallback silencioso e não publique.

9. **Registrar e sincronizar no Cérebro-Ricar.** Depois da publicação real, (_disparo automatizado via motor_) grava a matéria e alimenta o índice OpenViking com `vectors_only`; o retorno deve conter `openviking_sync.success: true` antes de registrar `vault_registered`. Em caso de falha, preserve o Cérebro e reporte a pendência.

10. **Gerar painel quando precisar de visão operacional.**
   ```text
Ação gerenciada automaticamente pelo Orquestrador Central.
```
   Abra o arquivo com `desktop_preview` para acompanhar etapa, aprovações, execuções e histórico.

## Pitfalls

- O registro no Cérebro-Ricar após publicação atualiza automaticamente `wiki/operacional/` e as partes/clientes em `wiki/entities/`, sincronizando ambos no OpenViking. Em produção, a publicação é bloqueada determinística e ruidosamente (exit 1) se o registro no Cérebro falhar — nunca ignore falhas pós-publicação.
- O lock protege mutações do manifesto; não execute dois workers para a mesma matéria ao mesmo tempo.
- Uma aprovação fica inválida se o hash do artefato mudar.
- `model_ids` só aparece quando a CLI devolve essa informação; não invente identificador de modelo. O executor Claude aplica teto de US$ 1 por chamada salvo override explícito.
- A publicação continua no QA determinístico de `formatar-peca`; gerar um DOCX não autoriza entrega externa.
- O `claude-obsidian` não está disponível no WSL quando este conector foi instalado; por isso a escrita no Ementário permanece bloqueada até o runner transacional estar disponível. A consulta read-only funciona e não altera o vault.

## Verificação

Use `status` para confirmar a matéria e gere o painel antes de reportar progresso:

```text
Ação gerenciada automaticamente pelo Orquestrador Central.
```

Critério final: manifesto, artefatos, hashes, aprovações e fase concordam; testes do projeto permanecem verdes.
