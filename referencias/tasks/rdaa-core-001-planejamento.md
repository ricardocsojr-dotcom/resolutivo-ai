# RDAA-CORE-001 — Planejamento controlado

## Papel atual

**Planejador:** Claude ACP.

Esta tarefa é somente de diagnóstico e plano. Não implementar, não criar commit, não alterar configuração do Canvas e não acessar qualquer path fora de `/projects/resolutivo-ai-lab`.

A única escrita autorizada é o artefato final `referencias/plans/rdaa-core-001.md`. Não altere nenhum outro arquivo.

## Contexto

O laboratório é uma cópia isolada do plugin Resolutivo.AI. O bug observado foi bifurcação de estado: ferramentas derivavam `state_dir` de `--output` e criavam `.rdaa-run` aninhado; uma primeira proteção já bloqueia o padrão e tem regressões em `tests/test_publicar_docx_state_dir_aninhado.py`.

A próxima entrega deve ser a solução de raiz, descrita em `referencias/roadmap-laboratorio-rdaa.md`, seção **RDAA-CORE-001**.

## Escopo de análise

Leia somente o necessário para mapear:

1. todos os pontos de entrada que recebem, inferem ou escrevem `state_dir`/`matter_id`;
2. quais são mutantes e quais apenas leem estado;
3. contratos atuais de manifesto, lock, publicação, registro e execução de workers;
4. testes já existentes que devem ser preservados ou estendidos;
5. migração segura para uma validação central sem quebrar os fluxos normais.

## Restrições não negociáveis

- Não usar arquivos reais, Cérebro, OpenViking, MCP, navegador, e-mail, OneDrive, `.rdaa-run` produtivo ou rede para conteúdo jurídico.
- Não propor reescrita geral de skills, roteamento jurídico ou documentos.
- Não inferir uma operação de limpeza destrutiva. Reconciliação deve iniciar em `--dry-run`, com backup, recibo e sem exclusão direta.
- Não gastar outro modelo nesta etapa.
- Não tentar corrigir, executar testes ou criar qualquer arquivo além do plano autorizado.

## Saída obrigatória

Escreva a proposta em `referencias/plans/rdaa-core-001.md` e reproduza um resumo no Canvas. O arquivo deve conter estas seções e nesta ordem:

1. **Diagnóstico comprovado** — arquivos/funções e o mecanismo exato de cada risco.
2. **Fronteira canônica proposta** — API/tipos mínimos para `MatterId`, `StateDir` e manifesto.
3. **Plano incremental** — no máximo cinco commits, cada um reversível e testável.
4. **Matriz de testes** — casos positivos, negativos e e2e sintético.
5. **Riscos e compatibilidade** — o que pode quebrar e como preservar dados existentes.
6. **Contrato para o implementador Codex** — instrução fechada, sem margem para refatoração fora de escopo.

Critério de qualidade: todo passo precisa apontar arquivo real e teste verificável. Onde faltar prova, declare lacuna; não invente.
