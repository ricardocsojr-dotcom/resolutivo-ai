# Schemas por Tipo de Peça

Cada tipo de peça tem campos específicos esperados pelo template. Use estes schemas para saber
exatamente o que extrair da peça redigida.

---

## agravo interno

| Campo | Descrição |
|-------|-----------|
| `enderecamento` | Ex: EXCELENTÍSSIMO SENHOR DOUTOR MINISTRO PRESIDENTE DO SUPERIOR TRIBUNAL DE JUSTIÇA |
| `numero_processo` | Número do processo formatado |
| `nome_agravante` | Nome do agravante/requerente |
| `nome_agravado` | Nome do agravado/requerido |
| `preambulo` | Parágrafo inicial qualificando as partes e a intenção da peça |
| `sumula_processado` | Resumo dos fatos do processo |
| `tempestividade` | Argumento sobre a tempestividade do recurso |
| `merito_recursal` | Fundamentação jurídica detalhada do recurso |
| `pedidos` | Lista de pedidos formulados |
| `data_local` | Padrão "Cidade/UF". Ex: Uberlândia/MG, 6 de maio de 2026. |
| `advogado_assinante` | Nome do advogado que assina a peça e OAB |

---

## agravo de instrumento

| Campo | Descrição |
|-------|-----------|
| `enderecamento` | Tribunal destinatário |
| `numero_processo` | Número do processo de origem |
| `nome_agravante` | Nome do agravante |
| `nome_agravado` | Nome do agravado |
| `preambulo` | Parágrafo inicial qualificando as partes |
| `dos_fatos` | Narração dos fatos relevantes |
| `do_direito` | Fundamentação jurídica |
| `do_cabimento` | Demonstração do cabimento do agravo de instrumento |
| `efeito_suspensivo` | Fundamentos para concessão de efeito suspensivo (fumus boni iuris e periculum in mora) |
| `pedidos` | Pedidos formulados |
| `data_local` | Local e data |
| `advogado_assinante` | Nome do advogado e OAB |

---

## contestação

| Campo | Descrição |
|-------|-----------|
| `enderecamento` | Juízo destinatário |
| `numero_processo` | Número do processo |
| `nome_reu` | Nome do réu/contestante |
| `nome_autor` | Nome do autor |
| `preambulo` | Parágrafo inicial qualificando as partes |
| `preliminares` | Preliminares processuais, se houver (inépcia da inicial, ilegitimidade etc.) |
| `dos_fatos` | Versão dos fatos pelo réu |
| `do_direito` | Fundamentação jurídica da defesa |
| `impugnacao_pedidos` | Impugnação específica aos pedidos do autor |
| `pedidos` | Pedidos do réu (improcedência etc.) |
| `data_local` | Local e data |
| `advogado_assinante` | Nome do advogado e OAB |

---

## recurso especial

| Campo | Descrição |
|-------|-----------|
| `enderecamento` | EGRÉGIO SUPERIOR TRIBUNAL DE JUSTIÇA |
| `numero_processo` | Número do processo de origem |
| `nome_recorrente` | Nome do recorrente |
| `nome_recorrido` | Nome do recorrido |
| `preambulo` | Parágrafo inicial qualificando as partes |
| `sumula_processado` | Histórico processual resumido |
| `tempestividade` | Demonstração da tempestividade |
| `cabimento` | Demonstração do cabimento (art. 105, III, CF) |
| `prequestionamento` | Demonstração do prequestionamento |
| `merito_recursal` | Fundamentação jurídica do recurso especial |
| `pedidos` | Pedidos formulados |
| `data_local` | Local e data |
| `advogado_assinante` | Nome do advogado e OAB |

---

## apelação

| Campo | Descrição |
|-------|-----------|
| `enderecamento` | Tribunal de Justiça destinatário |
| `numero_processo` | Número do processo |
| `nome_apelante` | Nome do apelante |
| `nome_apelado` | Nome do apelado |
| `preambulo` | Parágrafo inicial qualificando as partes |
| `sumula_processado` | Resumo da sentença recorrida e dos fatos |
| `tempestividade` | Demonstração da tempestividade |
| `merito_recursal` | Fundamentos do recurso de apelação |
| `pedidos` | Pedidos formulados |
| `data_local` | Local e data |
| `advogado_assinante` | Nome do advogado e OAB |

---

## embargos de declaração

| Campo | Descrição |
|-------|-----------|
| `enderecamento` | Órgão julgador dos embargos |
| `numero_processo` | Número do processo |
| `nome_embargante` | Nome do embargante |
| `nome_embargado` | Nome do embargado |
| `preambulo` | Parágrafo inicial qualificando as partes |
| `dos_fatos` | Descrição sucinta do julgado embargado |
| `dos_embargos` | Demonstração das omissões, contradições ou obscuridades no acórdão/sentença |
| `efeitos_modificativos` | Se aplicável, fundamento para efeitos modificativos |
| `pedidos` | Pedidos formulados |
| `data_local` | Local e data |
| `advogado_assinante` | Nome do advogado e OAB |

---

## Schema genérico (fallback para tipos sem schema específico)

Usado quando o tipo de peça não consta nos schemas acima (manifestações, petições simples etc.).

| Campo | Descrição |
|-------|-----------|
| `enderecamento` | Destinatário da peça |
| `numero_processo` | Número do processo formatado |
| `partes` | Identificação das partes (autor/réu ou equivalente) |
| `preambulo` | Parágrafo inicial qualificando as partes e a intenção da peça |
| `corpo_da_peca` | Desenvolvimento completo da peça (fatos, fundamentos jurídicos) |
| `pedidos` | Lista de pedidos formulados |
| `data_local` | Local e data |
| `advogado_assinante` | Nome do advogado e OAB |

---

## Mapa de templates disponíveis

| Tipo de peça | Arquivo de template |
|---|---|
| agravo interno | 01_Agravo_Interno_Tag.docx |
| agravo de instrumento | 01. Agravo de Instrumento com pedido de efeito suspensivo.docx |
| contestação | 01. Contestação - Cobap x Sankhya.docx |
| recurso especial | 01. Recurso Especial - Sankya x OGMO.docx |
| recurso extraordinário | 01. Recurso Extraordinário - 85181.docx |
| agravo em recurso especial | Agravo em Recurso Especial - 84652.docx |
| embargos de declaração | 01. Embargos de Declaração.docx |
| apelação | 01. Apelação - Cotrial x Fundo de Investimento.docx |
| recurso inominado | 01. Recurso Inominado - Trivale x Maria das Graças.docx |
| manifestação | 01. Manifestação - Juntada de Comprovante de Pagamento.docx |
| especificação de provas | 01. Especificação de provas - Renan e Romildo.docx |
| impugnação a contestação | 01. Impugnação a contestação - Maria Alice.docx |
| alegações finais | Alegações Finais.docx |
| ação de indenização | 01. Ação de Indenização Danos Morais - Dra. Luciana x Martin 3.5.2026.docx |
| petição | 01. Petição.docx |
| aditivo | Aditivo à minuta de acordo.docx |
| contrarrazões | Contrarrazões à Apelação - 65172.docx |
| memoriais | MEMORIAIS Apelação ISFC x FPTI - julgamento 19.3.2026.docx |
| solicitação perito | 01. Manifestação - Solicitação Perito.docx |
| juntada de custas | 01. Manifestação - Juntada de Custas Postais.docx |
| fallback | 01_Agravo_Interno_Tag.docx |
