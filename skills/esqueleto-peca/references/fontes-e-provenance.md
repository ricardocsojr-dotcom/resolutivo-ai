# Fontes e provenance no esqueleto

## Objetivo

O esqueleto é o momento preferencial para escolher as jurisprudências e demais fontes que fundamentarão a peça. A regra reduz o risco de uma informação interna, uma ementa não conferida ou uma referência sem origem aparecer na redação final sem controle.

Isso não impede inclusão posterior. Uma fonte posterior deve ser registrada como adição posterior, com motivo e nova conferência, sem apagar o registro da aprovação do esqueleto.

## Campos do esqueleto

```json
{
  "status": "aprovado",
  "aprovacao": {
    "status": "aprovado",
    "por": "Ricardo",
    "observacao": "Aprovado para redação"
  },
  "fontes_selecionadas": [
    {
      "source_id": "SRC-5f29a1c3",
      "uso": "fundamentacao.tese-1",
      "bloco": "fundamentos",
      "status": "verificada_externamente",
      "origem": "buscar-jurisprudencia",
      "fonte": "Jusbrasil",
      "localizacao": "URL ou identificador oficial",
      "literalidade_confirmada": true
    }
  ],
  "blocos": [
    {
      "id": "fundamentos",
      "source_ids": ["SRC-5f29a1c3"]
    }
  ]
}
```

## Regras objetivas

| Regra | Enforcement |
|---|---|
| Toda fonte selecionada possui `source_id` | Bloquear esqueleto inválido |
| Cada `source_id` é único na seleção | Bloquear duplicidade ambígua |
| Cada fonte selecionada informa `uso` e `bloco` | Bloquear seleção sem destino de redação |
| Fonte externa verificada informa origem, fonte, localização e literalidade | Bloquear registro incompleto |
| Fonte informada ou pendente permanece identificada como tal | Não promover automaticamente a verificada |
| Fonte escolhida existe no provenance da matéria | Bloquear referência órfã |
| Esqueleto aprovado contém aprovação explícita | Impedir redação automática sem aprovação |
| Inclusão posterior informa `adicionado_apos_esqueleto` e `motivo` | Permitir acréscimo sem apagar a trilha inicial |

O verificador não decide se uma jurisprudência é pertinente, válida ou suficiente. Ele somente confere presença de origem, estado, localização, identificadores e vínculo declarado ao bloco.

## Fluxo recomendado

1. Pesquisar e conferir a jurisprudência na fonte indicada.
2. Registrar o resultado no provenance com texto literal e localização.
3. Montar o esqueleto com as fontes selecionadas, o bloco de uso e o vínculo por `source_id`.
4. Apresentar o esqueleto ao Ricardo e aguardar aprovação explícita.
5. Montar o pacote do redator incluindo o esqueleto aprovado e somente as fontes selecionadas.
6. Redigir a peça.
7. Se uma fonte posterior for necessária, registrá-la como adição posterior e submetê-la à revisão antes da publicação.

O fluxo não extrai origem a partir de texto livre. Uma citação sem identificador ou localização fica pendente e não deve ser tratada como fonte conferida.
