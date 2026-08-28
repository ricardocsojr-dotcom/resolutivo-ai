---
name: gestao-materias
description: >
  Organiza a base local de clientes e matérias (contencioso e consultivo) do
  RDAA em C:\Users\ricar\OneDrive\Área de Trabalho\Resolutivo-Dados: cria a estrutura de pastas de um
  cliente ou matéria nova, registra documentos-fonte com ID/hash, confere
  se um documento já registrado foi alterado, abre e resolve pendências,
  gera o pacote de handoff para o Gemini (a única CLI que não instala o
  plugin) continuar peças nível C, e converte relatório de mapeamento de
  acervo em planilha de curadoria pra importação em massa. Ative quando
  Ricardo pedir para
  abrir cliente/processo/projeto novo, registrar ou conferir documentos de
  uma matéria, anotar uma pendência, ou preparar o handoff antes de passar a
  matéria pro Gemini. Não decide tese, não lê o conteúdo dos documentos e
  não substitui `contencioso-rdaa`, `backoffice-juridico` nem o estado de
  `.rdaa-run` (`matter_state.json`) — só organiza os dados e o repositório
  de documentos-fonte.
---

# Gestão de Matérias — RDAA

Camada de dados local, sem banco de dados, Docker, WSL ou serviço em segundo
plano. Cada cliente e cada matéria (contencioso ou consultivo) é uma pasta;
cada arquivo Markdown dentro dela é a única fonte de verdade. O script
`scripts/gestao_materias.py` só mantém essas pastas e arquivos consistentes —
quem decide fato, tese e estratégia continua sendo Ricardo (ou Claude,
quando ele autorizar).

## Estrutura criada

```
Resolutivo-Dados/
  clientes/<cliente>/
    CLIENTE.md
    contencioso/<numero-processo-ou-id>/
      CONTEXTO.md       # narrativa entre peças + próximo passo (não duplica fato/tese)
      FONTES.md          # índice humano dos documentos (gerado a partir de fontes.json)
      fontes.json         # metadados estruturados + sha256 de cada documento (DOC-XXX = source_id)
      PENDENCIAS.md       # abertas / resolvidas
      REGISTRO.md         # histórico cronológico, só cresce
      HANDOFF.md          # pacote compacto para outra IA assumir a matéria
      documentos/01-fontes/
      trabalho/
      entregas/
    consultivo/<projeto-id>/
      [mesma estrutura]
```

Raiz configurável via variável de ambiente `RESOLUTIVO_DADOS_ROOT` (padrão
`C:\Users\ricar\OneDrive\Área de Trabalho\Resolutivo-Dados`). Local,
definitivo — Google Drive não entra como destino desta estrutura.

## Regras que o script aplica

1. **Documento-fonte e entrega nunca são movidos nem apagados.**
   `registrar-documento` e `montar-entrega` só copiam
   (`shutil.copy2`) — nunca movem o arquivo de origem, e nunca sobrescrevem
   uma entrega existente (sufixam `-2`, `-3`... em vez de substituir). A
   única exclusão que existe é `limpar-trabalho`, e só dentro de
   `trabalho/` (rascunhos/scratch) — nunca em `documentos/01-fontes/` ou
   `entregas/`. Por padrão é dry-run (lista, não apaga); exige
   `--confirmar` pra apagar de fato. Apagar de `documentos/01-fontes/` ou
   `entregas/` continua sendo decisão manual do Ricardo no Explorer, fora
   desta skill.
2. **Todo fato deve referenciar documento e página.** O script não impõe isso
   em `CONTEXTO.md` (texto livre, editado por quem redige) nem em
   `registrar-documento` — `--paginas` é recomendado, não obrigatório
   (limitação real: nada aqui bloqueia registrar um documento sem página).
   O que o script garante é que, quando a página for informada, ela fica
   gravada e disponível pra citar junto do hash.
3. **Fato incerto, documento ausente, contradição ou risco de mudar
   pedido/tese não se resolve sozinho.** Isso vira pendência
   (`abrir-pendencia`) e fica parada em `PENDENCIAS.md` até Ricardo decidir
   (`resolver-pendencia`). Nenhum comando desta skill fecha uma pendência
   automaticamente.
4. **Nível da peça (C/B/A) continua sendo definido por Ricardo**, conforme
   `CLAUDE.md` do escritório. Esta skill não participa dessa decisão nem
   escolhe qual IA processa a matéria — só organiza os dados que qualquer
   uma delas vai consumir.
5. **Jurisprudência continua exclusiva do Claude via Jusbrasil**
   (`jusbrasil-jurisprudencia`). Esta skill não pesquisa nada — só guarda o
   que já foi decidido registrar como fonte.
6. **ID de matéria = `matter_id`.** `--id` é normalizado com a mesma regra de
   `skills/revisor-rdaa/scripts/estado_rdaa.py` (`_safe_matter_id`: só
   `[A-Za-z0-9_.-]`, resto vira `-`) — normalmente o número de processo. É o
   mesmo identificador usado em `.rdaa-run/<matter_id>/` pelo pipeline de
   redação, propositalmente, para que os dois lados apontem pra mesma
   matéria sem tradução.
7. **`DOC-XXX` de `fontes.json` é o `source_id`** que `provenance.jsonl`/
   registros de evidência (`contratos-agentes.md`) esperam para citar um
   documento. Este script é quem efetivamente mantém esse registro (hash,
   origem, imutabilidade) — o contrato de agentes já previa o campo, mas
   nada gerava ou validava esse identificador até esta skill existir.
8. **Fato, tese, decisão e risco de uma peça em produção não vivem aqui.**
   Isso é `.rdaa-run/<matter_id>/matter_state.json`, mantido por
   `estado_rdaa.py` e usado só por quem carrega as skills do plugin (Claude
   Code e Codex, que instalam o plugin por completo). `CONTEXTO.md` desta
   skill é só narrativa entre peças — não duplica esse estado.

## Comandos

Todos imprimem JSON em stdout (`{"status": "ok", ...}`) e erro estruturado em
stderr com código (`{"status": "erro", "codigo": ..., "mensagem": ...}`),
saída 1 em falha ou divergência. Rodar com `python scripts/gestao_materias.py <comando> ...`.

| Comando | Uso |
|---|---|
| `novo-cliente --nome "..."` | Cria `clientes/<slug>/CLIENTE.md` |
| `nova-materia --cliente "..." --tipo contencioso\|consultivo --id "..."` | Cria a matéria completa (6 arquivos + 3 pastas) |
| `registrar-documento --cliente ... --tipo ... --id ... --arquivo PATH --doc-tipo ... --origem ... --funcao ... [--relevancia alta\|media\|baixa] [--tags a,b] [--paginas 1-4]` | Copia (se preciso), calcula sha256, grava em `fontes.json`, regenera `FONTES.md`. `--relevancia` é opcional — só preencha quando já existe uma triagem real (ex.: importação em lote a partir de um relatório), não como chute no fluxo comum de "Ricardo manda o documento no chat" |
| `verificar-documentos --cliente ... --tipo ... --id ...` | Recalcula hash de cada fonte registrada; reporta `alterados` e `ausentes` |
| `abrir-pendencia --cliente ... --tipo ... --id ... --descricao "..."` | Adiciona item em `## Abertas` de `PENDENCIAS.md` com ID `PEND-XXX` |
| `resolver-pendencia --cliente ... --tipo ... --id ... --pendencia PEND-XXX --resolucao "..."` | Move o item para `## Resolvidas` com a resolução e data |
| `gerar-handoff --cliente ... --tipo ... --id ...` | Atualiza em `HANDOFF.md` as seções automáticas (pendências abertas + fontes relevantes); seções manuais (o que já foi feito, próximo passo) não são tocadas |
| `montar-entrega --cliente ... --tipo ... --id ... --arquivo PATH [--rotulo "..."] [--anexos DOC-001,DOC-003]` | Copia a peça final pra `entregas/<data>_<rótulo>/` (nunca sobrescreve — sufixa `-2`, `-3`... se já existir uma entrega com o mesmo rótulo no mesmo dia); se `--anexos` for informado, copia também os `DOC-XXX` de `fontes.json` pra `anexos/` dentro dessa pasta; grava `MANIFESTO.md` com peça, hash e anexos |
| `limpar-trabalho --cliente ... --tipo ... --id ... [--confirmar]` | Sem `--confirmar`: só lista o que existe em `trabalho/` (dry-run, não apaga nada). Com `--confirmar`: apaga o conteúdo de `trabalho/` (a pasta em si continua existindo, vazia); avisa (sem bloquear) se `entregas/` ainda estiver vazia |

`REGISTRO.md` recebe uma linha automática a cada ação acima — não editar
entradas antigas manualmente, só o script ou Ricardo adicionam ao final.

## Fluxo típico

1. `novo-cliente` (uma vez por cliente).
2. `nova-materia` ao abrir um processo ou projeto.
3. Conforme documentos chegam: `registrar-documento` para cada um relevante.
4. Se surgir dúvida, documento faltando ou contradição: `abrir-pendencia` e
   parar — não presumir.
5. Antes de passar a matéria pra Gemini (a única CLI que não instala o
   plugin nem lê `.rdaa-run` — usada para peças nível C de texto muito
   padronizado, tipo juntada/oposição simples, onde só o dado processual
   muda): rodar `gerar-handoff` e entregar o conteúdo de `HANDOFF.md` como
   contexto inicial dela.
6. Periodicamente, ou antes de confiar em um documento antigo:
   `verificar-documentos` para pegar arquivo alterado ou removido do disco.
7. Quando a peça final estiver pronta (publicada por `formatar-peca` ou
   equivalente): `montar-entrega`, incluindo como `--anexos` os `DOC-XXX`
   que precisam acompanhar a entrega (provas, documentos citados). Isso
   fecha o pacote do que foi de fato entregue, com hash, num lugar
   estável e datado.
8. Depois de montar a entrega (ou quando os rascunhos em `trabalho/` não
   servem mais): `limpar-trabalho` — rode sem `--confirmar` primeiro pra
   ver o que seria removido, e só confirme depois de olhar a lista.

## Divisão entre Claude Code, Codex e Gemini

Claude Code **e** Codex instalam o plugin `resolutivo-ai` por completo —
os dois carregam as skills e leem/escrevem `.rdaa-run/<matter_id>/`
normalmente. Não há tratamento especial pro Codex aqui: nível A/B e o
roteamento entre os dois já são resolvidos pelos contratos existentes
(`redigir-peca`, `contratos-agentes.md`, `roteamento-executavel.md`).

Gemini é o caso realmente diferente: não instala o plugin, não lê
`.rdaa-run`, não carrega `SKILL.md`. Seu uso é nível C — texto
essencialmente fixo por tipo de peça, variando só dado processual — então
o que ele precisa desta skill é pouco: os dados de identificação da
matéria e, quando cabível, um `DOC-XXX` específico a citar. `HANDOFF.md`
existe principalmente para cobrir esse caso.

## Planilha de curadoria pra importação em massa

`scripts/gerar_planilha_importacao.py --relatorio RELATORIO.md --saida planilha.csv`
lê um relatório de mapeamento de acervo (formato com blocos
`### Workspace: \`nome\`` ou `##### Matéria: \`caminho\`` e campos
`**Grau de Confiança**`, `**Classificação Sugerida**`/`**Classificação
Resolutivo-Dados**` no padrão `cliente > tipo > id`, `**Tipo de Matéria**`,
`**Peça Principal**`, `**Total de Arquivos**`, bullets `[PONTO A
CONFERIR]` e tamanhos entre parênteses tipo `(23.19 MB)`/`(38.7 KB)`) e
gera um CSV com uma linha por matéria: colunas só-leitura vindas do
relatório (`origem`, `cliente_sugerido`, `confianca`, `tipo_sugerido`,
`id_sugerido`, `tipo_de_peca`, `peca_principal`, `total_arquivos`,
`maior_anexo_mb`, `alertas_do_relatorio`) e colunas editáveis
pré-preenchidas com a sugestão (`importar`, `cliente_final`, `tipo_final`,
`id_final`, `observacoes`).

Não cria pasta, não copia arquivo, não decide nada sozinho — só transforma
um relatório de texto em algo que Ricardo edita no Excel: corrige nome de
cliente, decide tipo/id quando o relatório erra ou fica ambíguo, marca
`importar` linha a linha, e usa `maior_anexo_mb` pra filtrar os arquivos
grandes que não quer trazer. O comando que lê essa planilha já revisada e
de fato cria a estrutura em Resolutivo-Dados **não existe ainda** — é a
última etapa, deliberadamente adiada até a planilha estar fechada, e será
delegada a outra CLI quando chegar a hora, não necessariamente executada
pelo Claude Code.

## Pendências também viram post-it (`planner-postit`)

`abrir-pendencia`/`resolver-pendencia` continuam só gravando
`PENDENCIAS.md` — nenhuma chamada de rede entra no script Python, mantendo
o princípio de "sem API embutida" desta skill. A ponte com o Planner é
orquestração, feita por quem está operando (Claude Code ou Codex, se
também tiver a skill `planner-postit` disponível), não pelo script:

1. **Depois de `abrir-pendencia`**, invoque `planner-postit` pra criar o
   post-it correspondente: `category: "trabalho"`, `tag:
   "pendencia-materia"`, `title: "[PENDÊNCIA] {cliente} — {PEND-XXX}"`,
   `notes` com matéria (`{tipo}/{matter_id}`) e a descrição da pendência,
   `date` = hoje. Isso é o que faz a pendência aparecer no briefing diário
   do Ricardo em vez de ficar só dentro da pasta da matéria.
2. **Depois de `resolver-pendencia`**, ache o post-it correspondente
   (`GET .../api/postit?category=trabalho&full=1`, procurando o `PEND-XXX`
   no título) e chame `action: complete` nele. Se não achar ou achar mais
   de um candidato, avise e peça confirmação — mesma regra de não
   adivinhar da própria `planner-postit`.
3. Isso não é automático dentro do script — é um passo a mais que quem
   orquestra (eu) sempre executa em seguida, nas duas pontas.

## Fora do escopo desta skill (deliberado)

Orquestrar a chamada às CLIs (rodar o comando delas via terminal e ler o
retorno) não está implementado aqui. Depois que a base de dados estiver em
uso, isso é um passo barato de adicionar — Claude Code já pode invocar
outra CLI via Bash e usar o `HANDOFF.md` gerado como prompt inicial dela —
mas não foi pedido nesta rodada e não deve ser assumido como pronto.
