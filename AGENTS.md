# Contrato comum do workspace RDAA

Este arquivo vale igualmente para Codex e Antigravity. Antes de trabalhar,
leia `CLAUDE.md`, `roteamento-ia.md` e a `SKILL.md` aplicável. Para redigir ou
revisar peça, leia também
`skills/contencioso-rdaa/references/redacao-rdaa.md`.

## Papéis

- **Codex redige** peças C, B e A e aplica no mesmo trabalho as camadas de
  estilo autorizadas.
- **Antigravity critica** a estratégia com contexto isolado e também pode
  extrair documentos longos. Não redige, corrige, publica nem altera estado.
- **Claude orquestra, valida e corrige** o rascunho. Mudança de tese, pedido ou
  estratégia depende de Ricardo.
- Não use `Agent`, subagente ou outro modelo como mensageiro entre CLIs. A
  chamada é direta e recebe somente o pacote mínimo da etapa.

## Estado e fontes

- O estado canônico fica em `.rdaa-run/<matter_id>/`; não misture matérias.
- Não invente fatos, páginas, precedentes, datas, valores ou decisões. Marque
  lacunas como pendência e preserve a origem e o estado de verificação.
- Achado do crítico é alerta, não decisão automática nem bloqueio mecânico.
- Jusbrasil é a única fonte de pesquisa jurisprudencial externa autorizada.
  CNJ, DataJud, DJEN e NotebookLM ficam desligados salvo instrução expressa.

## Vaults

- O Ementário do Resolutivo é leitura automática somente em peças B/A, nos
  termos de `skills/redigir-peca/SKILL.md`.
- O vault operacional "Procedimentos e Informações" só é consultado a pedido.
- Não escreva diretamente no vault WSL. Use apenas o fluxo de ingestão previsto
  pela skill de redação.

## Entrega

- Trabalhe sobre cópia; documentos e páginas de origem são somente evidência.
- Nenhuma crítica publica arquivo. A entrega passa por Claude, `revisor-rdaa`
  e pela publicação protegida de `formatar-peca`.
