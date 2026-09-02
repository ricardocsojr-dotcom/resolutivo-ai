# Contrato executável de roteamento RDAA

A implementação canônica é `orquestracao/roteamento.json` e `skills/redigir-peca/scripts/orquestrador_rdaa.py`.

## Entradas permitidas

A rota recebe `nivel_peca` (C/B/A) e `nivel_risco` (baixo/médio/alto/crítico) explicitamente declarados. Complexidade determina o fluxo mínimo; risco pode apenas escalá-lo. Nenhuma classificação implícita a partir de tamanho, palavras-chave ou conversa altera a rota.

## Saída persistida

`run_manifest.json` registra:

- rota declarada e rota efetiva;
- worker, provider, família de modelo, CLI e identificador de modelo quando o worker o devolver;
- estágios, gates obrigatórios e gates condicionais exigidos;
- transições, aprovações e hashes;
- execuções, saídas e duração.

## Invariantes

1. `writer.model_family != critic.model_family`.
2. `writer.model_family != validator.model_family`.
3. Hermes não conta como worker independente de mérito jurídico.
4. Workers produzem arquivos; o orquestrador registra os resultados depois de verificar a existência e o hash.
5. Fases são sequenciais; aprovação de esqueleto é inválida se o arquivo mudar.
6. Falhas pausam. Não há fallback silencioso.

A rota organiza engenharia de workflow; não escolhe tese, não confirma fonte, não substitui Ricardo e não converte alerta crítico em decisão.
