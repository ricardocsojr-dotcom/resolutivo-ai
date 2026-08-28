# Roteamento de IA por nível de peça — RDAA

> Referência de como distribuir o trabalho entre as CLIs de IA que o
> escritório já paga (Claude Code, Codex, Gemini/Antigravity), sem
> orquestrador automático — nem Hermes, nem OmniRoute, nem qualquer motor de
> regras. O nível da peça é sempre declarado por Ricardo — nenhum roteamento
> reclassifica ou troca a rota sozinho. Trocar de CLI é trocar de
> programa/janela: não existe combo, `/model` unificado, nem fallback de
> assinatura.

## Tabela de roteamento

| Nível | Leitura documental | Planejamento e primeira redação | Revisão e entrega |
|---|---|---|---|
| C | Gemini quando houver volume; Codex em caso simples | Gemini | Codex, com revisão rápida `revisor-rdaa` e formatação |
| B | Gemini | **Claude Code ou Codex** | Codex audita fatos, formata e produz Visual Law determinístico |
| A | Gemini | **Claude Code ou Codex** | Codex audita; quem redigiu retorna somente se houver achado material |

## Regras

1. **Claude Code e Codex são pares, não papéis fixos.** Os dois instalam o plugin `resolutivo-ai` por completo, compartilham `.rdaa-run/<matter_id>/` (fatos, teses, decisões, provenance) e as mesmas skills/contratos (`redigir-peca`, `contratos-agentes.md`, `roteamento-executavel.md`, `estado-provenance.md`). Um não precisa "passar" nada pro outro por arquivo — o estado já é o mesmo. Planejamento e primeira redação B/A ficam por padrão com **Claude Code**, porque foi onde a engenharia do plugin (skills, gates, publicação protegida) foi calibrada e testada primeiro — mas Codex pode assumir a mesma etapa quando Ricardo preferir, sem perda de estado.
2. **Gemini é a única CLI de fora.** Não instala o plugin, não lê `.rdaa-run`, não carrega `SKILL.md`. Usa a skill `gestao-materias` (`HANDOFF.md`/`DOC-XXX`) como ponte, e fica restrito a leitura documental de volume e nível C — texto essencialmente fixo por tipo de peça, variando só dado processual.
3. Codex é responsável por revisão, auditoria de fatos, formatação e Visual Law determinístico com dados verificáveis — pode compartilhar essa função com Claude Code quando o caso pedir, pela mesma lógica da regra 1.
4. **Nenhuma rota é fallback de limite.** Se uma CLI falhar ou atingir cota, o fluxo pausa e Ricardo decide — nunca troca de assinatura silenciosamente. Isso hoje é trivial de garantir: não existe mecanismo automático nenhum entre as três CLIs, a troca é sempre uma decisão explícita.
5. Para infográficos jurídicos: SVG/HTML/Word determinístico. Imagem generativa é só decorativa, nunca contém fato, data, valor, prova ou tese.

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
