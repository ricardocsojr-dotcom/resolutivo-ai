# Contrato de IDs semânticos no DOCX RDAA

## Objetivo

Permitir que o QA confira se registros estruturados do contexto chegaram ao
DOCX final correto, sem mostrar IDs ao usuário, sem alterar texto visível,
formatação, numeração, tabelas, assinaturas ou aparência do documento.

## Marcação interna

Cada bloco que declarar `id` recebe uma marcação interna OOXML associada ao
parágrafo ou tabela gerado. A marcação usa o nome `rdaa_<tipo>_<id>` e não é
renderizada como texto. O identificador original também permanece no contexto e
no estado local; o nome interno é apenas o mecanismo de localização no DOCX.

A marcação deve ser aplicada depois que o handler criar o elemento e antes de o
bloco seguinte ser gerado. Para citação com várias linhas, o intervalo cobre os
parágrafos do mesmo bloco. Para tabela, o intervalo cobre o elemento de tabela.
Para figura, cobre o parágrafo da imagem e a legenda quando houver.

## Blocos apoiados

| Entidade | Blocos candidatos | Verificação |
|---|---|---|
| `fact_ids` | `quadro_processual`, `paragrafo`, `numerado`, `documento` | Presença do ID no bloco declarado |
| `thesis_ids` | `titulo`, `titulo2`, `titulo3`, `numerado`, `sumula`, `citacao` | Presença no bloco ou seção declarada |
| `request_ids` | `alinea`, `numerado`, `documento`, `tabela` | Presença e duplicidade objetiva |
| `source_ids` | `citacao`, `numerado`, `documento`, `figura`, `tabela` | Referência de fonte rastreável |
| `risk_ids` | qualquer bloco explicitamente marcado | Apenas rastreabilidade, sem avaliar risco |

O campo `semantic_ids` pode ser usado como lista geral de IDs quando o bloco
representar mais de uma entidade:

```json
{
  "tipo": "numerado",
  "texto": "Texto do fundamento.",
  "semantic_ids": ["T-1", "F-2", "SRC-3"]
}
```

Os campos específicos (`fact_ids`, `thesis_ids`, `request_ids`, `source_ids` e
`risk_ids`) são preservados para auditoria e podem coexistir com
`semantic_ids`.

## Regras de bloqueio

A ausência de IDs em contextos antigos não bloqueia a geração nem a publicação.
Quando IDs forem declarados, o QA pode bloquear somente:

1. ID declarado no contexto que não aparece no DOCX, quando o bloco de destino
   foi explicitamente identificado;
2. ID duplicado de forma incompatível com o bloco ou entidade;
3. número de processo incompatível com o estado da matéria;
4. referência a entidade inexistente.

Uma entidade declarada sem bloco de destino não deve ser considerada ausente:
o sistema deve registrar `rastreabilidade_incompleta` e solicitar conferência.
O código não pode concluir que uma tese foi omitida apenas porque não recebeu
um bloco de destino.

## Preservação do DOCX

A marcação é interna e não deve criar caracteres, runs, parágrafos vazios,
quebras, alterações de estilo ou campos visíveis. O gerador continua usando os
mesmos handlers e regras tipográficas. Os testes devem comparar texto, tabelas,
formatação estrutural e abertura do documento antes e depois.

## Reversibilidade

O ID é aditivo ao JSON e ao OOXML. Contextos antigos continuam usando o fluxo
legado. Se a marcação falhar, a publicação deve ser bloqueada antes de substituir
o arquivo final; o backup e o candidato anterior permanecem disponíveis.
