# Laboratório isolado — Resolutivo.AI

## Estado do laboratório

- **Diretório:** `C:\Users\ricar\Desktop\resolutivo-ai-lab`
- **Branch:** `lab/rdaa-core`
- **Baseline:** tag local `lab-baseline-state-dir-guard`
- **Push:** desabilitado (`origin` mantém fetch; push aponta para `DISABLED`)
- **Dados reais:** `.rdaa-run/` não foi copiado; Cérebro-Ricar não integra o laboratório.
- **Regra:** nenhuma alteração deste diretório entra em `main` por cópia manual. Somente commits selecionados, nova revisão independente e testes no repositório de produção poderão ser promovidos.

## Contrato do agente de engenharia

O agente trabalha somente neste diretório e só pode receber tarefas que indiquem:

1. objetivo e critério de aceite;
2. arquivos e capacidades autorizadas;
3. limite de tempo/tentativas/custo;
4. testes exigidos;
5. resultado esperado como diff/commit local, nunca push ou merge.

Ele não recebe montagem de:

- `C:\Projetos\resolutivo-ai`;
- `C:\Users\ricar\cerebro-ricar`;
- `.rdaa-run/` de produção;
- OneDrive de peças, tokens, certificados ou credenciais.

## RDAA-CORE-001 — identidade e estado canônicos

### Objetivo

Eliminar bifurcação de estado por paths derivados: toda matéria deve possuir um único estado canônico em `.rdaa-run/<matter_id>/`.

### Aceite

- `MatterId` e `StateDir` têm validação central reutilizada pelos pontos mutantes.
- O manifesto, o diretório e o `matter_id` devem coincidir.
- `publicar_docx.py` não infere um estado alternativo a partir de `--output`.
- Existe reconciliação `--dry-run`, com recibo, backup e sem exclusão direta.
- Casos de path aninhado, variação de caixa, `..`, symlink externo e ID divergente falham antes de escrita.
- Fluxo e2e sintético passa; nenhuma matéria real é usada.

### Fora de escopo

- reescrever redação, regras jurídicas, modelos ou documentos existentes;
- migrar dados reais no primeiro ciclo;
- publicar, registrar no Cérebro ou chamar OpenViking.

## POCKET-001 — edição portátil e cognitiva

### Produto

Uma edição do plugin Resolutivo.AI para **ChatGPT Web** e **Hermes hospedado**, sem MCP, terminal, browser local, aplicativos, arquivos locais, Cérebro, OpenViking ou estado de matéria.

A edição Pocket não é uma integração entre ChatGPT e Hermes. É a mesma política cognitiva empacotada para dois runtimes com capacidades diferentes.

### Arquitetura alvo

```text
editions/pocket/
  pocket-policy.json             # fonte de verdade: capacidades, limites e roteamento
  chatgpt/
    INSTRUCTIONS.md              # pronto para configurar um Custom GPT
    knowledge/                   # material curado, sem casos, clientes ou segredos
  hermes/
    skills/                      # skills cognitivas leves, sem scripts mutantes
  tests/
    test_pocket_contract.py      # valida política e artefatos gerados
```

`pocket-policy.json` é a fonte de verdade. O texto de ChatGPT e as skills Hermes devem ser gerados ou validados contra ele; não manter regras duplicadas manualmente.

### Capacidades permitidas

- triagem e enquadramento de problema jurídico a partir do conteúdo fornecido;
- estratégia, análise, mapa de riscos e questões a confirmar;
- estrutura de peça e rascunho textual claramente marcado como rascunho;
- revisão textual e identificação de lacunas;
- pesquisa web somente quando a capacidade estiver habilitada pelo runtime e a resposta identificar a fonte;
- pacote de continuidade para a edição Desktop.

### Capacidades proibidas

- alegar leitura de Cérebro, OpenViking, Cérebro-Ricar, Obsidian, arquivos locais, sistemas judiciais ou e-mail;
- criar, alterar ou ler `.rdaa-run`, manifestos, documentos, DOCX, PDFs locais ou planilhas;
- publicar, protocolar, assinar, calcular prazo real, registrar no Cérebro ou declarar que um gate foi aprovado;
- chamar CLI, MCP, automação de navegador, aplicativo desktop, PJeOffice ou ferramentas do computador;
- transformar dados não fornecidos em fatos verificados, precedentes, datas, valores ou estado processual.

### Skills mínimas

1. **intake-pedido** — separa fatos fornecidos, lacunas, objetivo e premissas.
2. **estrategia-contencioso** — análise estratégica sem declarar prova ou tese como confirmada.
3. **rascunho-rdaa** — escreve material não publicado conforme o estilo RDAA.
4. **revisao-rdaa** — identifica falhas de coerência, prova e redação; não publica nem corrige estado.
5. **handoff-desktop** — produz um pacote Markdown para o fluxo local prosseguir.

Nenhuma skill Pocket tem `scripts/`, acesso a paths, instrução de terminal ou promessa de integração externa.

### Contrato de saída

Quando o usuário pedir uma ação indisponível, a Pocket deve dizer com precisão:

> "A edição Pocket não tem acesso ao ambiente operacional. Posso preparar o pacote para continuação na edição Desktop, mas não posso executar ou confirmar essa ação."

O pacote de continuidade deve separar: fatos fornecidos, pendências, fontes, decisão humana necessária e rascunho/estrutura produzidos. Nunca deve alegar sincronização ou publicação.

### Critérios de aceite

- Custom GPT configurável somente com `INSTRUCTIONS.md` e os arquivos de `knowledge/`.
- Hermes hospedado funciona somente com as skills Pocket e sem MCPs/apps locais.
- Testes confirmam que todo artefato Pocket declara limites e não contém instruções de execução local.
- Testes confirmam que toda referência interna está presente no bundle de conhecimento.
- Não há nomes de clientes, matérias reais, paths locais, tokens, credenciais, registros Cérebro ou `.rdaa-run` no pacote distribuível.
- Cinco cenários de regressão cobrem: pedido de publicação, pedido de consulta a Cérebro, pedido de protocolo, pesquisa sem fonte e handoff ao Desktop.

### Fora de escopo

- sincronização automática entre ChatGPT Web e Hermes;
- memória compartilhada entre runtimes;
- MCP, actions, connectors, browser automation ou qualquer aplicativo local;
- substituição da edição Desktop em operações reais.

## Regra de promoção

Uma entrega do laboratório somente pode ser considerada para `main` após:

1. testes específicos + suíte integral verdes;
2. revisão independente read-only aprovada;
3. comparação explícita com este contrato;
4. nova execução dos testes na cópia de produção;
5. decisão de Ricardo para promover commits selecionados.
