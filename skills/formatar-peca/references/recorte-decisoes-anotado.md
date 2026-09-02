# Contrato — recorte de decisões anotado

## Objetivo

Produzir uma cópia visual de uma página ou trecho de decisão, com um ou mais
retângulos vermelhos sem preenchimento sobre regiões explicitamente indicadas.
O arquivo original nunca é alterado. A anotação visual não significa que o
texto destacado seja correto, decisivo, vigente ou suficiente para uma tese.

## Entrada mínima

```json
{
  "tipo": "decisao_anotada",
  "source_path": "/caminho/local/decisao.pdf",
  "source_kind": "pdf",
  "page": 3,
  "render_dpi": 180,
  "crop": [120, 240, 1680, 920],
  "rectangles": [
    {
      "id": "DEC-REC-1",
      "x": 180,
      "y": 310,
      "width": 1220,
      "height": 180,
      "stroke_color": "#FF0000",
      "stroke_px": 4
    }
  ],
  "legenda": "Trecho destacado da decisão — página 3.",
  "texto_pesquisavel": "Trecho literal fornecido pelo usuário ou pela fonte conferida.",
  "source_ids": ["SRC-DECISAO-1"],
  "semantic_ids": ["DEC-REC-1"]
}
```

`page` é 1-based para PDF. Para imagem, deve ser omitido ou igual a 1. As
coordenadas são sempre pixels da página renderizada antes do recorte. `crop`
é `[x, y, width, height]` na mesma base, ou a string `"auto"` para calcular
automaticamente a bounding box dos retângulos com margem. O recorte é opcional;
quando ausente, a página inteira é preservada.

**Novo (2026-09-02):** `crop: "auto"` — calcula automaticamente a bounding box
dos retângulos com uma margem de 20 px em todas as direções, clampada aos
limites da página. Ideal para documentos densos (notas fiscais, relatórios
paisagem) onde o usuário quer destacar uma região específica sem calcular
coordenadas manualmente.

## Regras geométricas

Os retângulos devem estar dentro dos limites da página de origem. Largura e
altura devem ser positivas. A cor padrão é vermelho puro `#FF0000`; o interior
é transparente e não deve cobrir o texto. A espessura padrão é 3 px. O sistema
não redimensiona coordenadas silenciosamente: se a resolução mudar, o manifesto
registra a resolução efetiva e a transformação aplicada.

As coordenadas do retângulo são convertidas para a imagem final após o recorte.
O contrato deve manter as coordenadas originais e as coordenadas finais no
manifesto para permitir auditoria e reprodução.

## Provenance e texto

`source_path`, hash SHA-256, página, resolução, recorte, retângulos e IDs entram
no provenance local. `texto_pesquisavel` deve ser fornecido explicitamente; o
plugin não deve fazer OCR e converter seu resultado em fato ou citação sem
conferência humana. O texto da legenda deve descrever apenas a operação visual,
não afirmar o valor jurídico do trecho.

## Saída

A saída é um novo PNG ou JPEG anotado, acompanhado de um manifesto JSON. O
original fica intacto. A imagem anotada pode ser inserida no DOCX por um bloco
`figura` ou `decisao_anotada`, com legenda, origem, página, texto pesquisável e
IDs semânticos.

## Bloqueios objetivos

A publicação ou geração deve ser bloqueada quando houver arquivo inexistente,
página inválida, coordenada fora da página, largura/altura não positiva,
retângulo sem ID ou recorte impossível. O sistema não bloqueia a decisão de
usar ou não a anotação, nem avalia se o trecho sustenta a tese.
