# Contrato executável de roteamento RDAA

## Objetivo

A rota define quais agentes são obrigatórios, recomendados ou omitidos em uma
execução. Ela reduz chamadas desnecessárias sem restringir a capacidade de
acionamento quando Ricardo pedir explicitamente.

## Entrada permitida

A rota pode usar somente:

1. `nivel_risco` ou `risk_level` declarado no contexto;
2. um item de `riscos` com `nivel` e `origem` explicitamente registrados;
3. um argumento de nível fornecido pelo orquestrador;
4. um agente solicitado explicitamente por Ricardo.

O sistema não usa tipo da peça, extensão do texto, palavras-chave ou classificação
inferida para decidir risco.

## Saída

| Campo | Significado |
|---|---|
| `required` | Sempre executado: revisão semântica e revisor RDAA |
| `recommended` | Agentes acionados pela rota de risco declarado |
| `explicit` | Agentes pedidos diretamente, mesmo fora da recomendação automática |
| `selected` | União deduplicada de `required`, `recommended` e `explicit` |
| `omitted` | Agentes opcionais não selecionados nesta execução |
| `selection_source` | `conservadora`, `risco_declarado` ou `override_explicito` |
| `reason` | Motivo textual rastreável da seleção |

## Regras

Sem nível ou risco declarado, `selected` contém somente QA/revisão e `omitted`
contém conselho e crítico. Nível médio seleciona o crítico. Nível alto seleciona
crítico e conselho. Um pedido explícito pode selecionar qualquer agente
opcional, mas a rota deve registrar `override_explicito` e o agente solicitado.

A rota não substitui o julgamento do advogado. Ela apenas decide quais rotinas
de engenharia e agentes de apoio serão chamados. A decisão jurídica continua
na saída explícita dos agentes e de Ricardo.

## Persistência

A rota final é gravada em `run_manifest.json` antes da publicação, junto com a
origem da seleção e os agentes omitidos. Isso permite auditar por que uma rotina
foi acionada ou não e evita repetir a leitura do estado completo.
