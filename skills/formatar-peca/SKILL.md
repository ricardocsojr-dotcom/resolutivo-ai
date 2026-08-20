---
name: formatar-peca
description: >
  Gera um arquivo Word (.docx) candidato e o encaminha à publicação protegida usando o gerador nativo RDAA (construir_peca.py).
  Use SEMPRE ao final de qualquer redação de peça processual — depois de redigir-peca, contencioso-rdaa,
  dano-moral-rct ou qualquer outra redação jurídica — para entregar somente o documento publicado no padrão RDAA
  com numeração nativa do Word (OOXML), estilos nomeados, notas de rodapé reais e checklist de verificação pós-geração.
  Ative com: "gera o docx", "formata a peça", "salva como Word", "gera o arquivo", "entrega a peça",
  "converte para Word", "quero o Word dessa peça", ou automaticamente como última etapa do fluxo redigir-peca.
---

# Formatar Peça — RDAA (Gerador Nativo OOXML)

Constrói a peça processual `.docx` parágrafo a parágrafo com **numeração nativa do Word (`numbering.xml`)**, fontes Tahoma 10.5pt, estilos RDAA nomeados, notas de rodapé reais e validação estrutural automática via XML.

---

## Fluxo Principal Obrigatório (Native Mode — `construir_peca.py`)

**Não utilize `docxtpl` com campo único para o corpo da peça.** O gerador nativo `scripts/construir_peca.py` é o fluxo primário e obrigatório, garantindo numeração nativa do Word (renumerável após edição), geometria exata por bloco e validação pós-geração.

### 1. Montar o JSON de contexto por blocos

Copie o texto da peça redigida na conversa **literalmente** para uma lista de `blocos` tipados. Ver `references/schema_blocos.md` para o contrato completo.

#### Resumo dos Tipos de Bloco Suportados:

| `tipo` | Parâmetros Principais | Uso e Formatação |
|---|---|---|
| `abertura` | `nome_parte`, `resto`, `nome_peca` (opcional), `resto_depois` | Parágrafo de qualificação inicial. `nome_parte` em **negrito**. `nome_peca` em CAIXA ALTA + negrito. |
| `titulo` | `texto`, `sequencia` (opcional), `reiniciar` (opcional) | Título Nível 1 (Seção principal). Numeração nativa Romana (`I.`, `II.`), CAIXA ALTA, negrito, borda inferior. |
| `titulo2` | `texto`, `sequencia` (opcional), `reiniciar` (opcional) | Título Nível 2 (Subtópico). Numeração nativa decimal (`1.`, `2.`), centralizado, negrito, preserva a caixa (Manual §3.1). |
| `titulo3` | `texto`, `sequencia` (opcional), `reiniciar` (opcional) | Título Nível 3 (Sub-subtópico). Numeração nativa por letras com ponto (`a.`, `b.`), recuo 4cm, CAIXA ALTA, negrito, borda inferior. |
| `numerado` | `texto`, `sequencia` (opcional), `reiniciar` (opcional) | Parágrafo numerado do corpo. Numeração nativa decimal (`1.`, `2.`). Numeral na margem 0cm, tab para 2cm, 2ª linha volta à margem 0cm. Suporta `<b>` e `<i>` inline. |
| `alinea` | `texto`, `nivel` (0 ou 1), `sequencia` (opcional) | Alínea de pedido. `nivel: 0` -> `a)`, `b)` (3cm); `nivel: 1` -> `i)`, `ii)` (4cm). |
| `documento` | `texto`, `sequencia` (opcional) | Item de lista de documentos anexos. Numeração nativa decimal com parêntese (`1)`, `2)`) em negrito (3cm). |
| `citacao` | `texto`, `italic` (opcional), `bold` (opcional) | Transcrição longa (> 3 linhas). Recuo 2cm, entrelinha simples, fonte 9pt, sem aspas. |
| `sumula` | `texto`, `italic` (opcional) | Súmula / síntese executiva da peça. Recuo esquerdo 2,5cm, recuo direito 2cm, itálico, justificado, sem borda, sem bullets. |
| `figura` | `image_path`, `legenda` (opcional), `width_cm` (opcional), `funcao_visual`/`texto_pesquisavel` (opcionais) | Imagem centralizada com legenda opcional; metadados pesquisáveis não alteram a aparência. |
| `decisao_anotada` | `image_path`, `texto_pesquisavel`, `annotation_manifest` (opcional), `pagina` (opcional), IDs (opcionais) | Cópia anotada de decisão com recorte e retângulos previamente produzidos pelo anotador local. |
| `tabela` | `cabecalho` (opcional), `linhas` | Tabela de dados genérica com cabeçalho em negrito. |
| `visual` | `visual_tipo`, `funcao_visual`, `texto_pesquisavel`, `linhas`, IDs opcionais | Timeline, matriz, fluxo ou confronto em tabela pesquisável, com função declarada e vínculo semântico. |
| `inicio_razoes` | `enderecamento` (opcional), `titulo_razoes` (opcional) | Transição para a folha de Razões Recursais em recursos compostos. Injeta quebra de página e reinicia automaticamente as sequências de numeração. |
| `assinaturas` | *(nenhum)* | Injeta a tabela de assinaturas (permite recursos compostos com assinaturas na interposição e nas razões). |
| `quadro_processual` | `numero_processo`, `partes` | Injeta caixa com borda contendo dados do processo e partes em qualquer ponto. |

---

### Regra objetiva de títulos

Os campos `texto` dos blocos `titulo`, `titulo2` e `titulo3`, assim como `titulo_razoes`, não podem conter dois pontos, travessão ou meio-travessão. O gerador bloqueia o contexto antes de criar o DOCX e o verificador estrutural repete a conferência no arquivo produzido. A regra vale somente para títulos. Não transforma hífens internos de palavras ou sinais de outras estruturas em título.

### 2. Salvar contexto e gerar o candidato temporário

Salve o payload JSON e execute `scripts/construir_peca.py`:

```bash
cat > /tmp/rdaa_context.json << 'EOF'
{
  "enderecamento": "EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA ...",
  "numero_processo": "0159944-40.1997.8.13.0702",
  "partes": "Autor: Mayara Almeida Jorge\nRéu: Fulano de Tal S/A",
  "blocos": [
    { "tipo": "abertura", "nome_parte": "MAYARA ALMEIDA JORGE", "resto": ", já qualificada, vem apresentar ", "nome_peca": "CONTRARRAZÕES", "resto_depois": "." },
    { "tipo": "titulo", "texto": "dos fatos" },
    { "tipo": "numerado", "texto": "Primeiro parágrafo do corpo com <b>termo em negrito</b>.", "nota_rodape": "Jurisprudência citada em nota de rodapé real." }
  ],
  "data_local": "Uberlândia/MG, 08 de agosto de 2026."
}
EOF

mkdir -p /tmp/rdaa-candidatos
python3 <skill_path>/scripts/construir_peca.py \
    --context /tmp/rdaa_context.json \
    --output /tmp/rdaa-candidatos/peca_candidata.docx
```

---

### 3. Publicação protegida e verificação obrigatória

O DOCX deve ser gerado primeiro como **candidato**, obrigatoriamente em caminho temporário ou de staging. Nunca use o caminho final como `--output` de `construir_peca.py`. A entrega final passa pelo publicador protegido, que executa o gate de formatação e estilometria antes de substituir qualquer arquivo existente:

```bash
python3 <skill_path>/../revisor-rdaa/scripts/publicar_docx.py \
    --input outputs/peca_candidata.docx \
    --output outputs/peca_final.docx \
    --qa-json outputs/peca_final.qa.json \
    --context /tmp/rdaa_context.json
```

O publicador só substitui `peca_final.docx` se o gate retornar `PASS`. Se falhar, o arquivo final anterior permanece intacto; o candidato fica disponível para diagnóstico. Antes de substituir um arquivo existente, o publicador cria backup local e realiza a troca de forma atômica.

O gate verifica no XML do `.docx`:
1. **Destaques**: sublinhado proibido fora da exceção institucional da abertura.
2. **Títulos**: numeração nativa (`w:numPr`), borda inferior e espaçamento 0/0.
3. **Parágrafos Numerados**: alinhamento com `tabStop` em 2cm (1134 twips) e retorno de 2ª linha à margem 0.
4. **Alíneas e Documentos**: numeração nativa e recuos de 3cm (1701 twips) / 4cm (2268 twips).
5. **Endereçamento e Quadro**: espaçamento simples e 2 parágrafos em branco de separação.
6. **Cabeçalho**: logo e parágrafo de respiro depois da logo.
7. **Assinaturas**: margem interna, estrutura e ordem depois do fecho.
8. **Rodapé**: presença de campos `PAGE`/`NUMPAGES` e linha do site em 7pt/dourado (`FFC000`).
9. **IDs semânticos**: quando o contexto declarar IDs em blocos, o gerador grava marcações OOXML invisíveis e o publicador confere sua presença sem alterar o texto visível.
10. **Visual Law rastreável**: blocos `visual` exigem tipo, função, linhas e texto pesquisável; o publicador confere o texto no DOCX e bloqueia somente falhas estruturais objetivas.
11. **Decisões anotadas**: use o anotador local antes de inserir `decisao_anotada`; a origem permanece intacta, o manifesto registra coordenadas e o DOCX recebe apenas a cópia anotada e o texto explicitamente fornecido.

Quando o contexto JSON é informado, o publicador atualiza automaticamente facts, teses explícitas, pendências, semantic_blocks e provenance; ele não infere conteúdo jurídico a partir do texto livre. O usuário continua recebendo apenas o arquivo final. Os arquivos de candidato, estado, backup e QA são artefatos internos do fluxo.
