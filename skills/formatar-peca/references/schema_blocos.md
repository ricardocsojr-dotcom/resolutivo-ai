# Schema de blocos — native mode (construir_peca.py)

O corpo da peça é uma **lista de blocos tipados**, não um texto único. O gerador constrói a estrutura com **numeração nativa do Word (OOXML)**, estilos nomeados RDAA e alinhamento tipográfico exato.

## JSON de contexto completo

```json
{
  "enderecamento": "EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA 2ª VARA CÍVEL DA COMARCA DE UBERLÂNDIA/MG",
  "numero_processo": "0159944-40.1997.8.13.0702",
  "uf_processo_originario": "MG",
  "partes": "Autor: Mayara Almeida Jorge\nRéu: Nome do Réu S/A",
  "blocos": [
    { "tipo": "abertura", "nome_parte": "MAYARA ALMEIDA JORGE", "resto": ", já devidamente qualificada nos autos, vem apresentar ", "nome_peca": "RECURSO DE APELAÇÃO", "resto_depois": ", pelas razões a seguir expostas." },
    { "tipo": "sumula", "texto": "Súmula do Recurso: Pretende-se a reforma integral da sentença diante da flagrante nulidade probatória." },
    { "tipo": "numerado", "texto": "Requer o recebimento do recurso no duplo efeito.", "sequencia": "interposicao" },
    { "tipo": "assinaturas" },

    { "tipo": "inicio_razoes", "enderecamento": "EGRÉGIO TRIBUNAL DE JUSTIÇA DO ESTADO DE MINAS GERAIS", "titulo_razoes": "RAZÕES DO RECURSO DE APELAÇÃO", "sequencia": "razoes" },

    { "tipo": "titulo", "texto": "dos fatos e do direito", "sequencia": "razoes" },
    { "tipo": "numerado", "texto": "Primeiro parágrafo do bloco com <b>termo em negrito</b> e <i>termo em itálico</i>.", "sequencia": "razoes", "nota_rodape": "STJ, REsp 1.999.888/MG." },
    { "tipo": "titulo2", "texto": "Da Nulidade da Decisão Recorrida", "sequencia": "razoes" },
    { "tipo": "numerado", "texto": "Segundo parágrafo sob o subtópico.", "sequencia": "razoes" },
    { "tipo": "titulo3", "texto": "prova documental conclusiva", "sequencia": "razoes" },
    { "tipo": "numerado", "texto": "Parágrafo sob o sub-subtópico.", "sequencia": "razoes" },

    { "tipo": "titulo", "texto": "dos pedidos", "sequencia": "razoes" },
    { "tipo": "alinea", "texto": "primeiro pedido em alínea principal;", "nivel": 0, "sequencia": "razoes" },
    { "tipo": "alinea", "texto": "subitem i em algarismo romano;", "nivel": 1, "sequencia": "razoes" },
    { "tipo": "alinea", "texto": "segundo pedido em alínea principal.", "nivel": 0, "sequencia": "razoes" },

    { "tipo": "figura", "image_path": "caminho/para/imagem.png", "legenda": "Organograma probatório.", "width_cm": 11.0 },
    { "tipo": "decisao_anotada", "image_path": "caminho/para/decisao-anotada.png", "annotation_manifest": "caminho/para/decisao-anotada.json", "pagina": 3, "legenda": "Trecho destacado da decisão — página 3.", "texto_pesquisavel": "Trecho literal fornecido.", "source_ids": ["SRC-DECISAO-1"], "semantic_ids": ["DEC-REC-1"] },

    { "tipo": "tabela", "cabecalho": ["Item", "Descrição", "Status"], "linhas": [["1", "Perícia", "Concluída"]], "alinhamentos": ["center", "left", "center"] },
    { "tipo": "visual", "visual_tipo": "timeline", "funcao_visual": "Ordenar atos explicitamente fornecidos", "texto_pesquisavel": "Evento 1 — data informada — ato informado", "cabecalho": ["Data", "Evento", "Fonte"], "linhas": [["Data informada", "Ato informado", "Fonte informada"]], "semantic_ids": ["VISUAL-1"] },

    { "tipo": "titulo", "texto": "dos documentos anexos", "sequencia": "razoes" },
    { "tipo": "documento", "texto": "Procuração e atos constitutivos.", "sequencia": "razoes" },
    { "tipo": "documento", "texto": "Guia de preparo recursal quitada.", "sequencia": "razoes" },
    { "tipo": "citacao", "texto": "Trecho transcrito longo (mais de 3 linhas), linha 1.\nLinha 2 da transcrição." },
    { "tipo": "assinaturas" }
  ],
  "data_local": "Uberlândia/MG, 08 de agosto de 2026."
}
```

## Tabela Completa de Tipos de Bloco

| `tipo` | Campos / Parâmetros | Especificação Tipográfica e de Numeração RDAA |
|---|---|---|
| `abertura` | `nome_parte`, `resto`, `nome_peca` (opc), `resto_depois` (opc) | Parágrafo de qualificação. `nome_parte` em **negrito**. `nome_peca` em CAIXA ALTA + negrito. |
| `titulo` | `texto`, `sequencia` (opc), `reiniciar` (opc) | **Título Nível 1** (Seção). Numeração nativa em Romano (`I.`, `II.`). CAIXA ALTA, negrito, borda inferior, espaçamento 0/0. |
| `titulo2` | `texto`, `sequencia` (opc), `reiniciar` (opc) | **Título Nível 2** (Subtópico). Numeração nativa decimal (`1.`, `2.`), centralizado, negrito, preserva caixa (Manual §3.1 — Title Case), sem borda. |
| `titulo3` | `texto`, `sequencia` (opc), `reiniciar` (opc) | **Título Nível 3** (Sub-subtópico). Numeração nativa por letras minúsculas com ponto (`a.`, `b.`), recuo 4cm, CAIXA ALTA, negrito, borda inferior. |
| `numerado` | `texto`, `sequencia` (opc), `reiniciar` (opc), `nota_rodape` (opc) | **Parágrafo do corpo**. Numeração nativa decimal (`1.`, `2.`). Numeral na margem 0cm, tab para 2cm, 2ª linha retorna à margem 0cm. |
| `alinea` | `texto`, `nivel` (0 ou 1, default 0), `sequencia` (opc) | **Alínea de pedido**. `nivel: 0` -> `a)`, `b)` (3cm); `nivel: 1` -> `i)`, `ii)` (4cm). Numeração nativa. |
| `documento` | `texto`, `sequencia` (opc), `reiniciar` (opc) | **Item de documentos**. Numeração nativa decimal com parêntese (`1)`, `2)`) em negrito (3cm). |
| `sumula` | `texto`, `italic` (opc) | **Súmula / Síntese executiva**. Recuo esquerdo 2,5cm, recuo direito 2cm, itálico, justificado, entrelinha 1.5, sem borda, sem bullets. |
| `inicio_razoes` | `enderecamento` (opc), `titulo_razoes` (opc), `sequencia` (opc) | **Transição de recurso composto**. Insere quebra de página, reinicia sequências de numeração e injeta cabeçalho opcional das Razões. |
| `quebra_pagina` | *(nenhum)* | Insere uma quebra de página antes do próximo bloco automático. Use para manter o fecho e as assinaturas juntos. |
| `citacao` | `texto`, `italic` (opc), `bold` (opc) | **Citação longa (> 3 linhas)**. Recuo 2cm, entrelinha simples, tamanho 9pt, sem aspas. |
|| `figura` | `image_path`, `legenda` (opc), `width_cm` (opc, default 14.0) | **Figura/Imagem**. Centralizada. Nunca amplia além do tamanho físico original. Auto-fit de altura: limita largura para caber em 55% da altura útil da página (~13,5 cm). Para retrato, altura é fator limitante; função ajusta largura proporcionalmente. Legenda opcional em 8pt/itálico. ✅ 2026-09-02 |
| `decisao_anotada` | `image_path`, `texto_pesquisavel`, `annotation_manifest` (opc), `pagina` (opc), IDs (opc) | **Recorte de decisão anotado**. Usa imagem produzida pelo anotador local; a origem e o manifesto devem ser preservados quando declarados. |
| `tabela` | `cabecalho` (opc), `linhas`, `alinhamentos` (opc) | **Tabela de dados genérica**. Tabela centralizada no documento. Cabeçalho em negrito. Alinhamento opcional por coluna (`left`, `center`, `right`). |
| `visual` | `visual_tipo`, `funcao_visual`, `texto_pesquisavel`, `linhas`, `cabecalho` (opc), IDs (opc) | **Visual Law tipado**. `visual_tipo`: `timeline`, `matrix`, `flow` ou `confrontation`. Renderizado em tabela pesquisável; exige função declarada e não infere fatos. |
| `assinaturas` | *(nenhum)* | **Tabela de Assinaturas**. Tabela 2x2 com os signatários RDAA (permite múltiplas tabelas em recursos compostos). |
| `quadro_processual` | `numero_processo`, `partes` | **Quadro Processual**. Caixa com borda contendo o número do processo e qualificação das partes. |

## Seleção de OAB e assinaturas

O contexto pode declarar `uf_processo_originario` com a sigla de duas letras ou o nome do estado. O gerador não infere a UF do número de processo, endereçamento ou texto livre. Quando a UF é informada, Wanderley recebe a inscrição cadastrada para aquela UF e Flávia recebe a inscrição de Minas Gerais, exceto em São Paulo, onde usa a inscrição paulista cadastrada. Se a UF não estiver no cadastro de Wanderley, a geração é bloqueada para evitar assinatura incorreta. Sem UF declarada, preserva-se o padrão de Minas Gerais.

Os e-mails da tabela de assinaturas são hyperlinks `mailto:` azuis e sublinhados, como no padrão visual fornecido. A publicação continua passando pelo candidato temporário e pelo gate protegido.

## Regras Importantes

1. **Citação Curta vs. Citação em Bloco**:
   - **Citação Curta (até 3 linhas)**: Inserir diretamente no parágrafo `numerado`, entre aspas e em itálico (`<i>"citação curta..."</i>`).
   - **Citação Longa (> 3 linhas)**: Usar o bloco `citacao` (recuo 2cm, entrelinha simples, 9pt).

2. **Notas de Rodapé Reais**:
   - Qualquer bloco `numerado` aceita a chave `"nota_rodape": "texto da citação/fonte"`. O gerador constrói a nota de rodapé real em `word/footnotes.xml` com chamada no corpo (`w:footnoteReference`).

3. **Formatação Inline**:
   - O campo `texto` de qualquer bloco suporta `<b>texto</b>` / `**texto**` (negrito) e `<i>texto</i>` / `*texto*` (itálico).
