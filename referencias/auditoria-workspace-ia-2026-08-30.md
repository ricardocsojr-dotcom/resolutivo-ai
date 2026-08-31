# Auditoria do workspace de IA — 2026-08-30

## Veredito

**Suficiente como arquitetura local após as correções desta auditoria; ainda
não implantado nas cópias instaladas das CLIs.** O núcleo é deliberadamente
simples: arquivos compartilhados, contrato comum, uma chamada direta por
papel e gates de publicação já existentes. Não há razão atual para criar um
“OS” com servidor, daemon, banco, fila ou painel.

## O que foi verificado

- CLIs presentes: Claude Code, Codex e Antigravity.
- Estado canônico existente em `.rdaa-run/<matter_id>/` e publicação protegida.
- Dois vaults distintos: operacional sob demanda e Ementário automático B/A.
- Ementário WSL com estrutura e ledgers válidos, auditado somente em leitura.
- Testes determinísticos do plugin.
- Contratos de redação, crítica, estilo, gestão de matéria e roteamento.

## Correções aplicadas

1. `AGENTS.md` passou a ser o contrato comum de Codex e Antigravity.
2. Papéis consolidados: Codex redige C/B/A; Antigravity critica; Claude corrige.
3. Removido o restante das instruções de `Agent tool` nas etapas de peça.
4. Camadas RCT/Flávia passaram a integrar a mesma execução do redator.
5. Executor direto usa stdin, sandbox somente leitura e saída validada.
6. Crítica recebeu schema estável, mas continua consultiva e não bloqueante.
7. Hook `SessionEnd` corrigido para ler `run_manifest.json`.
8. Teste de identidade passou a ser executado e aceita versão semântica.
9. Contradição entre os dois vaults foi eliminada em `CLAUDE.md`.
10. Versão elevada a 3.3.2 para não confundir a fonte corrigida com caches 3.3.1.

## Auditoria adversarial cruzada

### Antigravity sobre a parte do Codex

Achados aceitos:

- `--effort high` não deve valer para extração simples; o executor agora aceita
  low/medium/high e reserva high para crítica.
- O timeout padrão de 20 minutos era largo; foi reduzido para 10 minutos.
- A saída NDJSON real possui o resultado aninhado em `result`; o primeiro
  parser estava errado. O smoke test real encontrou e a correção foi validada.
- Codex ganhou `--color never` para impedir ruído ANSI.

Achados rejeitados ou modulados:

- O schema não é “validado manualmente pela stdlib”; quem o impõe é a própria
  CLI Antigravity por `--json-schema`.
- `stream-json` não é emulação criada pelo projeto; é o modo oficial de enviar
  prompt longo por stdin à CLI.
- O executor não substitui a orquestração do Claude: executa uma chamada e
  devolve um artefato; Claude continua decidindo a etapa seguinte.
- Crítica não bloqueante não é paradoxo. Julgamento jurídico não pode virar
  gate automático; risco central exige decisão humana pelo contrato.
- `-C` define diretório de trabalho, não injeta automaticamente todo o repo no
  prompt; a sandbox ainda é somente leitura.

### Codex sobre a parte do Antigravity

A primeira auditoria do Antigravity encontrou corretamente as contradições de
papel, vault e ausência de contrato comum. Quatro recomendações estavam erradas:

- `agy --print < arquivo` não é o transporte correto no PowerShell nem resolve
  prompts longos; o modo documentado é `stream-json`.
- `publicar_docx.py --matter` não existe; a publicação recebe input/output.
- O caminho WSL do Ementário já estava explícito em `redigir-peca`.
- Transformar o veredito do crítico em bloqueio automático daria autoridade
  jurídica a uma saída probabilística; por isso ficou apenas como alerta.

## Custo medido

O wrapper anterior consumiu 371 mil tokens em três chamadas. Sem wrapper, um
smoke test mínimo do Antigravity ainda registrou aproximadamente 37 mil tokens
de entrada, vindos do harness, ferramentas e regras carregadas pela própria
CLI. Portanto o ganho é grande, mas não torna a crítica barata. Política
recomendada já incorporada ao contrato: uma crítica compacta por peça B/A,
sem loops entre modelos; nível C sem crítica automática.

## Engenharias pesquisadas — somente inspiração, não aplicar agora

- `AGENTS.md`: manter instruções de comportamento separadas das skills. Já
  aproveitado apenas no contrato comum.
  https://github.com/nbiish/agents-standard
- Aider architect/editor: confirma o valor de separar autor e corretor, mas
  também registra que duas chamadas aumentam custo e duração. Não adotar o
  framework; os papéis locais já cobrem o necessário.
  https://github.com/Aider-AI/aider/blob/main/aider/website/docs/usage/modes.md
- Block Buzz Persona Pack: boa distinção entre base comum e papel específico.
  Não adotar packs, filas ou times; o `AGENTS.md` mais as skills já entregam a
  mesma separação com menos infraestrutura.
  https://github.com/block/buzz/blob/main/crates/buzz-persona/PERSONA_PACK_SPEC.md
- Agent Client Protocol: útil para editores conversarem com agentes, mas não
  resolve o problema jurídico nem reduz o custo-base das CLIs. Reavaliar só se
  surgir necessidade real de uma interface única.
  https://github.com/agentclientprotocol

## Pendência de implantação

As instalações locais do plugin ainda apontam para cópias 3.3.1 e podem conter
os workers antigos. A fonte 3.3.2 está pronta; publicar/reinstalar é uma ação
separada, porque altera as instalações globais das três CLIs. Até isso ocorrer,
rode o fluxo a partir deste checkout para garantir que o contrato novo seja o
carregado.
