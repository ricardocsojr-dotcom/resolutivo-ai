# Contrato comum do workspace RDAA

Antes de trabalhar, leia `CLAUDE.md`, `roteamento-ia.md` e a `SKILL.md` aplicável. Para redigir ou revisar peça, leia também `skills/contencioso-rdaa/references/redacao-rdaa.md`.

## Papéis e segregação

- **Hermes gerencia o fluxo; a máquina de estados determina transições.** Hermes coleta decisões, monta pacotes, chama CLIs e aciona QA. Não decide mérito jurídico, não reescreve como validador independente e não substitui uma segunda opinião.
- **Planejador e validador:** Claude Code, em pacotes e sessões isolados.
- **Redator:** Codex.
- **Crítico:** Antigravity (`agy`). Nunca redige, corrige, publica ou altera estado; entrega somente diagnóstico estruturado.
- A identidade dos workers é definida exclusivamente em `orquestracao/roteamento.json`. Redator, crítico e validador devem pertencer a famílias de modelo diferentes quando a rota for validada.
- Não use `Agent`, subagente ou outro modelo como mensageiro entre CLIs. As chamadas são diretas e recebem o pacote mínimo da etapa.
- Nenhum worker altera `run_manifest.json`, `matter_state.json` ou `provenance.jsonl` diretamente. O registro é feito pelo orquestrador após a saída existir e ter hash.

## Estado e fontes

- O estado canônico fica em `.rdaa-run/<matter_id>/`; não misture matérias.
- Não invente fatos, páginas, precedentes, datas, valores ou decisões. Marque lacunas como pendência e preserve a origem e o estado de verificação.
- Achado do crítico é alerta, não decisão automática. Mudança de tese, pedido ou estratégia depende de Ricardo.
- Jusbrasil é a única fonte de pesquisa jurisprudencial externa autorizada. CNJ, DataJud, DJEN e NotebookLM ficam desligados salvo instrução expressa.

## Gates e entrega

- O esqueleto aprovado é obrigatório. A aprovação fica vinculada ao hash do artefato e expira se ele for alterado.
- Falha, cota, timeout ou indisponibilidade de CLI pausa a matéria; não há fallback silencioso.
- Trabalhe sobre cópia; documentos e páginas de origem são somente evidência.
- QA, cálculo e publicação são determinísticos. Nenhuma crítica publica arquivo e entrega externa exige decisão específica.

## Vaults

- O Ementário do Resolutivo é leitura automática somente em peças B/A, nos termos de `skills/redigir-peca/SKILL.md`.
- O vault operacional "Procedimentos e Informações" só é consultado a pedido.
- Não escreva diretamente no vault WSL. Use apenas o fluxo de ingestão previsto pela skill de redação.
