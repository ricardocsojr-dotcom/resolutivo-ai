# Contrato de Visual Law rastreável

## Princípio

Visual Law é uma camada opcional de compreensão. O plugin não deve criar figura,
timeline, matriz, fluxo ou confronto apenas para ornamentar a peça. Quando um
elemento visual for usado, ele deve ter função jurídica ou explicativa declarada,
texto pesquisável e vínculo rastreável com os registros do caso.

## Tipos apoiados

| `visual_tipo` | Uso permitido | Representação inicial |
|---|---|---|
| `timeline` | ordenar fatos ou atos processuais explicitamente fornecidos | tabela de eventos |
| `matrix` | comparar critérios, posições ou documentos declarados | tabela comparativa |
| `flow` | mostrar sequência de etapas ou decisão explicitamente descrita | tabela/fluxo textual |
| `confrontation` | colocar versões ou elementos em contraste | tabela lado a lado |
| `figure` | imagem ou diagrama local com função declarada | figura com legenda |

A representação por tabela é preferível quando permite texto pesquisável e não
prejudica a leitura. Uma imagem só deve ser usada quando o contexto fornecer o
arquivo e os metadados necessários.

## Campos do bloco

```json
{
  "tipo": "visual",
  "visual_tipo": "timeline",
  "funcao_visual": "Ordenar os atos explicitamente fornecidos",
  "texto_pesquisavel": "Evento 1 — data informada — ato informado",
  "cabecalho": ["Data", "Evento", "Fonte"],
  "linhas": [["Data informada", "Ato informado", "A-SOURCE-1"]],
  "semantic_ids": ["A-VISUAL-1"],
  "source_ids": ["A-SOURCE-1"],
  "fact_ids": ["A-FACT-1"]
}
```

`funcao_visual` é obrigatória para o novo tipo `visual`. `visual_tipo` deve ser
um dos tipos apoiados. `texto_pesquisavel` deve reproduzir, sem inferência,
os dados que a visualização apresenta. IDs de fonte, fato, tese, pedido ou
risco são opcionais individualmente, mas qualquer ID fornecido deve existir no
estado/provenance para que a revisão objetiva possa conferi-lo.

## Segurança jurídica

O gerador não interpreta a ordem dos eventos, não calcula precedência, não
escolhe a versão verdadeira e não converte cor, posição ou proximidade em
conclusão jurídica. O elemento visual apenas reproduz dados explicitamente
fornecidos.

A ausência de `funcao_visual`, tipo inválido ou referência impossível é erro
estrutural do bloco novo e pode bloquear a publicação. A ausência de elemento
Visual Law não é erro. Alertas sobre clareza, ênfase, proporção ou conveniência
continuam sujeitos a revisão humana.

## Preservação visual e acessibilidade

A representação deve permanecer pesquisável no texto do DOCX. Imagens recebem
legenda e texto pesquisável invisível apenas quando esse texto for explicitamente
fornecido; a marcação interna não altera a aparência. Tabelas mantêm estilos,
alinhamentos e texto visível RDAA.
