# Contratos de estado, provenance e contexto entre agentes

## 1. Finalidade

Este documento define como as skills do RDAA compartilham informações entre pesquisa, conselho, crítica, redação e revisão. O contrato existe para reduzir releitura e consumo de contexto, não para limitar a capacidade jurídica do plugin.

O estado completo continua sendo persistido por matéria em `.rdaa-run/<matter_id>/`. Cada agente recebe um pacote menor, montado para a tarefa específica. O agente não precisa reler o histórico inteiro da conversa, todas as skills ou todos os registros do caso.

> **Regra central:** o mecanismo transporta informação explicitamente fornecida ou registrada. Ele não conclui, a partir de texto livre, que uma fonte é válida, que uma tese é correta, que uma prova é autêntica ou que um risco existe.

## 2. Compatibilidade com o estado existente

O contrato usa os campos já existentes em `matter_state.json` e `provenance.jsonl`:

| Estado persistido | Função | Observação |
|---|---|---|
| `facts` | Fatos e metadados explícitos do caso | Não são fatos inferidos pelo sistema |
| `theses` | Teses fornecidas ou aprovadas explicitamente | Podem permanecer como strings legadas ou objetos estruturados |
| `citations` | Citações e referências selecionadas | O pacote expõe somente as necessárias à tarefa |
| `decisions` | Decisões e vereditos registrados explicitamente | Não são inventados pelo registrador |
| `pending` | Pendências e pontos a conferir | Permanecem visíveis até resolução explícita |
| `provenance.jsonl` | Ledger de origem de fontes, trechos e documentos | Registros são deduplicados por `id` estável |

O pacote de contexto é uma projeção do estado. Ele não substitui `matter_state.json`, não altera o conteúdo do DOCX e não apaga campos que não sejam relevantes para uma tarefa.

## 3. Contrato de fonte e provenance

Cada resultado de pesquisa que entrar no estado deve ser representado por um registro com, no mínimo, estes campos:

```json
{
  "id": "SRC-5f29a1c3",
  "tipo": "jurisprudencia",
  "fonte": "Jusbrasil",
  "localizacao": "URL ou identificador oficial",
  "trecho": "Texto literal fornecido pela pesquisa",
  "status": "verificada_externamente",
  "origem": "buscar-jurisprudencia",
  "usos": ["fundamentacao.tese-1"],
  "conferencia": {
    "metodo": "navegador",
    "observacao": "fonte aberta e conferida pela skill de pesquisa"
  }
}
```

Os valores aceitos para `tipo` são abertos, mas devem descrever a natureza do registro, como `jurisprudencia`, `lei`, `sumula`, `tema_repetitivo`, `processo`, `documento`, `figura`, `nota_rodape`, `vault` ou `outro`. O contrato não exige que uma pesquisa seja reduzida a um desses tipos se a fonte real exigir outro rótulo.

`fonte` deve conservar o nome, identificador ou referência fornecida pela pesquisa. `localizacao` deve conservar URL, número do processo, artigo, página, arquivo ou outra localização informada. `trecho` deve ser literal quando a skill de origem exigir literalidade. O registrador não reescreve e não resume o trecho. `conferencia` pode conservar método, data, operador ou observação explícita da etapa, mas nunca representa validação jurídica automática.

| Status | Significado | Quem pode atribuir |
|---|---|---|
| `verificada_externamente` | O resultado foi apresentado pela skill como conferido na fonte externa indicada | A operação de pesquisa ou seu chamador, por declaração explícita |
| `informada` | O dado veio no contexto, no vault ou do usuário, sem confirmação automática pelo plugin | O mecanismo de ingestão |
| `pendente` | A fonte, vigência, autenticidade ou outro aspecto precisa de conferência | O agente ou usuário, explicitamente |
| `sem_fonte` | Existe um trecho ou citação no contexto, mas não veio origem identificável | O mecanismo de ingestão, sem inferência adicional |

`verificada_externamente` não pode ser preenchido apenas porque um texto contém uma URL ou parece uma ementa. A função de registro precisa receber esse status de forma explícita. O sistema não acessa serviços novos nem cria verificação implícita.

O `id` deve ser estável para o mesmo registro. Quando a skill de origem já fornecer um identificador, ele deve ser preservado. Quando não fornecer, o mecanismo pode gerar um identificador determinístico a partir do tipo, localização e trecho, sem usar o identificador como prova de validade.

## 4. Contrato de evidência

Evidência é uma afirmação ou documento que um agente recebeu ou registrou para análise. O contrato separa a existência da evidência da conclusão sobre seu valor diagnóstico.

```json
{
  "id": "EV-17",
  "descricao": "Contrato juntado no evento 42",
  "source_id": "DOC-abc123",
  "localizacao": "autos/evento-42",
  "status": "informada",
  "origem": "contexto_json"
}
```

O estado pode carregar evidências sem atribuir automaticamente força probatória, autenticidade, pertinência ou valor diagnóstico. Se um agente produzir uma avaliação, ela deve ser registrada como saída explícita daquele agente, vinculada à evidência por `source_id` ou `id`.

## 5. Contrato de tese, hipótese e decisão

Teses e hipóteses são conteúdo jurídico ou estratégico produzido por usuário ou agente. O estado apenas conserva o que foi explicitamente fornecido ou aprovado.

Uma tese estruturada pode usar:

```json
{
  "id": "T-1",
  "texto": "Texto explícito da tese",
  "status": "aprovada",
  "origem": "conselho-rdaa",
  "fundamentos": ["SRC-5f29a1c3"],
  "pendencias": ["P-2"]
}
```

Os valores de `status` de tese, hipótese e decisão são informativos e não são inferidos pelo registrador. Exemplos aceitos incluem `proposta`, `aprovada`, `rejeitada`, `alternativa`, `pendente` e `registrada`, desde que atribuídos pelo fluxo responsável.

Uma decisão deve conservar a alternativa ou o veredito que foi explicitamente produzido, suas razões se fornecidas, a evidência-pivot se identificada e o próximo passo se declarado. O estado não escolhe vencedor, não calcula probabilidade e não converte uma hipótese em tese aprovada.

## 6. Pacote de contexto

Todo pacote deve possuir um envelope curto:

```json
{
  "schema_version": "1",
  "matter_id": "identificador-da-materia",
  "task_type": "redator",
  "generated_at": "timestamp UTC",
  "facts": [],
  "sources": [],
  "theses": [],
  "hypotheses": [],
  "decisions": [],
  "pending": [],
  "rules": []
}
```

Campos não relevantes devem ser omitidos ou enviados como listas vazias, conforme a implementação. O contrato de seleção é:

| Tarefa | Recebe | Não recebe por padrão |
|---|---|---|
| `pesquisa` | fatos necessários, pergunta/tema explícito, pendências relacionadas e fontes já utilizadas | decisões internas não relacionadas e peça integral |
| `conselho` | fatos, evidências, teses existentes, hipóteses alternativas, pendências e fontes relacionadas | texto integral da peça e histórico completo da conversa |
| `redator` | fatos, teses aprovadas ou explicitamente selecionadas, fontes/citações selecionadas, decisões aplicáveis e regras RDAA | provenance irrelevante, hipóteses descartadas sem indicação de uso e histórico bruto |
| `critico` | fatos necessários, tese em análise, hipóteses alternativas, evidências e pendências relevantes | raciocínio privado do redator, histórico da aprovação e decisões que possam induzir complacência |
| `revisor` | regras aplicáveis, fontes/citações usadas, fatos necessários para conferência, pendências e relatório do crítico quando pertinente | autorização para alterar tese, estratégia ou mérito |
| `formatador` | fatos formais, blocos do documento, dados de assinatura, esqueleto aprovado e regras visuais | histórico jurídico e fontes que não aparecem no documento |

O isolamento do crítico é funcional: ele recebe dados do caso e da tese a ser atacada, mas não recebe o caminho de raciocínio que levou o redator àquela tese. Isso preserva a crítica adversarial sem impedir o compartilhamento de fatos e fontes necessários.

## 7. Contrato de entrada e saída por agente

| Agente | Entrada mínima | Saída que pode ser registrada |
|---|---|---|
| Pesquisa | tema ou pergunta explícita, filtros e fatos necessários | fontes, trechos literais, identificadores, URLs, status declarado e pendências de pesquisa |
| Conselho | decisão, alternativas, fatos, evidências e teses | hipóteses, matriz ACH, vieses, veredito, evidência-pivot e próximo passo |
| Redator | fatos, teses aprovadas, fontes selecionadas, regras e decisão aplicável | blocos redacionais, referências utilizadas, pendências preservadas e contexto de geração |
| Crítico | peça ou tese em análise, fatos, hipóteses e evidências | contratese, vulnerabilidades, teses não exploradas, pontos a verificar e correções recomendadas |
| Revisor | peça, regras, referências, pendências e resultados objetivos | diagnóstico, pontos a conferir, inconsistências formais e correções sem alteração de mérito |
| Formatador/publicador | contexto da peça e candidato DOCX | resultado do QA, manifesto de publicação, backup e provenance dos blocos efetivamente publicados |

As saídas não são convertidas automaticamente em fatos, teses aprovadas ou fontes verificadas. O orquestrador precisa indicar explicitamente o tipo de cada registro e, quando necessário, solicitar aprovação ou confirmação. Para peças processuais, o pacote do redator deve incluir o esqueleto aprovado, os `source_id` selecionados e os vínculos de cada fonte com bloco e uso.

## 8. Regras de redução de contexto

A montagem do pacote deve selecionar por `matter_id`, tipo de tarefa, identificadores referenciados e estado explícito. Ela não deve enviar o arquivo completo de estado quando apenas uma fração for necessária.

A seleção pode ser conservadora: na dúvida, incluir um registro relacionado e marcar sua origem, em vez de resumir ou alterar seu sentido. O ganho de créditos deve vir da eliminação de material irrelevante e repetido, não da supressão de fatos, teses, fontes ou pendências necessárias.

Toda saída do pacote deve ser serializável em JSON, determinística para o mesmo estado e independente de serviços externos. A função de montagem não faz chamada de API, não pesquisa a internet e não executa julgamento jurídico.

## 9. Compatibilidade e reversibilidade

O campo `--context` continua opcional nos fluxos existentes. Contextos antigos podem continuar usando strings em `teses`, `pendencias` ou `citations`; a montagem deve transportá-los sem exigir migração imediata. Novos registros estruturados são aditivos.

A gravação é local, deduplicada e reversível por backup do diretório `.rdaa-run/<matter_id>/`. O ZIP original do plugin não é alterado. Qualquer falha ao montar contexto deve bloquear apenas a passagem daquele pacote e não substituir o DOCX final.
