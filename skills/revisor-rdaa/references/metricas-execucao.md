# Métricas locais de execução RDAA

## Princípio

O plugin não tem acesso ao medidor interno de créditos do Claude Code. Por isso,
não deve declarar economia de créditos como fato. Ele registra apenas proxies
locais comparáveis entre execuções.

> Bytes e itens de contexto são medidas de engenharia; não são equivalentes
> diretos a créditos cobrados pelo Claude Code.

## Medidas

| Métrica | Fonte | Interpretação segura |
|---|---|---|
| `context_packs.bytes` | serialização do pacote por agente | volume de contexto enviado ao agente |
| `context_packs.items` | listas do pacote | quantidade de registros transportados |
| `agent_events.count` | eventos explícitos do fluxo | quantas tarefas foram registradas |
| `agent_events.reruns` | eventos com `rerun: true` | repetição registrada |
| `semantic_rounds` | manifesto da matéria | rodadas de correção por achado |
| `route.required/recommended` | risco explicitamente declarado | agentes necessários ou recomendados |
| `publish_attempts` | manifesto | tentativas de publicação |
| `blocked_attempts` | manifesto | tentativas bloqueadas por gate |

O sistema não mede tokens efetivos, tempo do modelo, custo financeiro ou
qualidade jurídica. Essas métricas exigiriam dados do ambiente do Claude Code ou
avaliação humana.

## Comparação

Um benchmark local deve usar o mesmo contexto anonimizado e comparar:

1. tamanho do estado completo contra cada pacote por agente;
2. quantidade de agentes exigidos/recomendados pela rota;
3. número de rodadas semânticas e tentativas de publicação;
4. presença de registros duplicados ou reprocessados.

A comparação é válida somente entre a mesma fixture, o mesmo tipo de tarefa e o
mesmo conjunto de campos. Não se deve comparar peças jurídicas diferentes como
se fossem uma prova causal de economia.

## Roteamento

A rota é conservadora. Sem nível ou risco declarado, o manifest registra apenas
as etapas obrigatórias de QA/revisão. Conselho e crítico aparecem como
`recommended` somente quando o contexto declara nível alto ou médio. Nenhuma
classificação é inferida do texto livre.
