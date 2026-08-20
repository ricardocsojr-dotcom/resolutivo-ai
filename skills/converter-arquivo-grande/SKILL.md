---
name: "converter-arquivo-grande"
description: "Converte arquivos grandes (PDF, Word, Excel, PowerPoint) para texto compacto ANTES de ler o conteúdo, evitando gastar créditos processando páginas como imagem — inclui um caminho de OCR (OCRmyPDF/Tesseract) pra PDFs escaneados sem texto embutido. Use sempre que Ricardo mandar, anexar ou apontar para um arquivo grande — processo judicial extenso, autos com centenas de páginas (nativos ou escaneados), contrato longo, planilha grande, apresentação — e pedir para ler, resumir, analisar, extrair trechos ou fazer qualquer coisa com o conteúdo. Ative especialmente quando ele mencionar \"processo gigantesco\", \"arquivo pesado\", \"documento escaneado\", \"economizar créditos\", \"não gastar tokens\", ou pedir explicitamente para converter/rodar o MarkItDown/OCR antes de processar. Não é necessária para arquivos pequenos (poucas páginas) que já são baratos de ler direto."
---

## Por que converter antes de ler

Ler um PDF/DOCX/PPTX grande diretamente custa caro em créditos: cada página de PDF é processada como se fosse uma imagem, o que consome muito mais tokens do que o texto puro equivalente. A ideia desta skill é extrair só o texto (e estrutura básica) do arquivo como um passo de sistema (bash/Python), que não consome créditos de IA, e só depois ler esse texto compacto — que é muito mais barato de processar do que páginas-imagem.

O ganho real não é "arquivo final menor em bytes" (às vezes o texto extraído é maior em bytes que o PDF original, que é comprimido). O ganho é em tokens de leitura por IA. Validado na prática: um PDF de autos processuais com 864 páginas e 106 MB virou um `.md` de 1,5 MB de texto em ~10 segundos — perfeitamente legível e uma fração do custo de ler 864 páginas como imagem.

## Contrato de integração com o RDAA

Use esta skill somente como etapa de ingestão antes da análise. Ela não redige,
não interpreta fatos, não escolhe fontes, não atualiza o estado da matéria e não
publica DOCX. Preserve o arquivo original e registre o caminho do texto extraído
como artefato de trabalho. A extração é uma aproximação operacional e qualquer
trecho crítico deve ser conferido no documento original.

Não instale pacotes, baixe modelos ou acione serviços externos automaticamente.
Se uma ferramenta não estiver disponível, informe a limitação e aguarde
autorização explícita para instalar ou use uma alternativa local já disponível.

## Quando usar

- Ricardo manda, anexa ou aponta para um arquivo grande (processo judicial, contrato extenso, planilha, apresentação) pedindo para ler, resumir, analisar, extrair informação ou responder perguntas sobre o conteúdo.
- Ele menciona explicitamente economizar créditos, "processo gigantesco", arquivo pesado, ou pede para converter/rodar o MarkItDown/OCR.

Não vale a pena para arquivos curtos (poucas páginas) — nesse caso, leia direto com a ferramenta Read normalmente, sem essa etapa extra.

## Restrição importante do ambiente: comandos de shell têm limite de ~45 segundos

Cada chamada de bash roda até por volta de 45s antes de expirar, e processos colocados em background (`nohup ... &`) **não sobrevivem** entre chamadas — o ambiente pode ser reciclado assim que a chamada retorna. Isso significa que qualquer conversão longa (markitdown num PDF de centenas de páginas, ou OCR) precisa ser feita de um jeito que caiba dentro desse tempo, ou dividida em lotes que rodam em chamadas separadas.

### Passo 1 — PDF: tente extração direta com `pypdf` primeiro (rápido, cobre a maioria dos casos)

A maioria dos PDFs de tribunais/processos é nativa (texto embutido), não escaneada. Para esses, extraia direto com `pypdf` — é muito mais rápido que o CLI do markitdown e evita o problema de timeout (864 páginas em ~10s no teste real):

```bash
python3 - <<'EOF'
from pypdf import PdfReader
IN = "/caminho/para/arquivo.pdf"
OUT = "/caminho/para/arquivo.md"
r = PdfReader(IN)
partes = []
chars_por_pagina = []
for i, page in enumerate(r.pages):
    txt = page.extract_text() or ""
    chars_por_pagina.append(len(txt))
    partes.append(f"\n\n--- Página {i+1} ---\n{txt}")
open(OUT, "w").write("".join(partes))
media = sum(chars_por_pagina) / max(len(chars_por_pagina), 1)
print(f"Páginas: {len(r.pages)} | Média de caracteres/página: {media:.0f}")
EOF
```

Se `pypdf` não estiver instalado, não instale automaticamente. Informe a limitação e use uma ferramenta local já disponível ou aguarde autorização explícita.

Olhe a "média de caracteres/página": se estiver muito baixa (poucas dezenas de caracteres ou menos), o PDF é escaneado (imagem, sem texto embutido) — vá para o Passo 2.

### Passo 2 — PDF escaneado: OCR com OCRmyPDF/Tesseract (mais lento, avise antes de rodar)

**Antes de rodar o OCR, avise o Ricardo que o documento parece escaneado e pergunte se ele quer que você rode o OCR** — é bem mais lento que a extração direta (na ordem de 1-2s por página, contra frações de segundo no Passo 1) e mais pesado em processamento. Só prossiga com a confirmação dele.

Verifique se `ocrmypdf`, `tesseract` e o idioma português já estão disponíveis no
ambiente. Não instale pacotes, baixe modelos ou altere o ambiente automaticamente.
Se algum componente faltar, informe Ricardo e aguarde autorização explícita.

Nota: `tesseract --list-langs` só mostra os idiomas disponíveis no ambiente. Se o português ou qualquer componente faltar, não tente corrigir automaticamente. Informe a limitação e aguarde autorização explícita.

Como o OCR de um documento de centenas de páginas não cabe em uma única chamada de 45s, processe em lotes com um arquivo de estado que marca por onde parou — rode o bloco abaixo repetidamente (uma chamada de bash por vez) até ele reportar que chegou na última página:

```bash
export PATH="$PATH:$HOME/.local/bin"
export TESSDATA_PREFIX=~/tessdata
python3 - <<'EOF'
import subprocess, time, os
from pypdf import PdfReader, PdfWriter

IN = "/caminho/para/arquivo.pdf"
STATE = "/caminho/para/arquivo.ocr_state"   # guarda a última página já processada
OUT = "/caminho/para/arquivo.md"

reader = PdfReader(IN)
total = len(reader.pages)
page = int(open(STATE).read().strip()) if os.path.exists(STATE) else 0

t0 = time.time()
with open(OUT, "a") as out:
    while page < total and time.time() - t0 < 35:  # margem de segurança abaixo do limite de 45s
        writer = PdfWriter()
        writer.add_page(reader.pages[page])
        with open("/tmp/_ocr_in.pdf", "wb") as f:
            writer.write(f)
        subprocess.run(
            ["ocrmypdf", "--jobs", "1", "--language", "por", "--force-ocr", "--quiet",
             "/tmp/_ocr_in.pdf", "/tmp/_ocr_out.pdf"],
            check=True,
        )
        texto = PdfReader("/tmp/_ocr_out.pdf").pages[0].extract_text() or ""
        out.write(f"\n\n--- Página {page+1} (OCR) ---\n{texto}")
        page += 1

open(STATE, "w").write(str(page))
print(f"Processadas até a página {page} de {total}")
EOF
```

Repita a chamada até a saída mostrar `page == total`. Isso pode levar várias chamadas em documentos longos — está tudo bem, é o esperado dado o limite de tempo do ambiente. Apague o arquivo `.ocr_state` quando terminar.

## Depois de converter (com ou sem OCR)

1. Leia o arquivo `.md`/texto gerado com a ferramenta Read no lugar do arquivo original. Se ainda for muito extenso, leia em partes (`offset`/`limit`) ou use grep para localizar as seções relevantes antes de ler tudo.
2. Não precisa perguntar antes de apagar arquivos de trabalho temporários (`.md`, `.ocr_state`, PDFs intermediários) depois de usá-los. Só preserve o arquivo convertido se o pedido for "me dá o texto/Markdown desse arquivo".

## Word, Excel, PowerPoint e outros formatos

Para esses formatos (normalmente bem menores, sem o problema de timeout), o MarkItDown funciona direto:

```bash
command -v markitdown >/dev/null 2>&1 || { echo "markitdown indisponível; não instalar automaticamente"; exit 2; }
IN="/caminho/para/arquivo.docx"
OUT="${IN%.*}.md"
markitdown "$IN" -o "$OUT"
wc -c "$OUT"
```

## Limitações a avisar o usuário quando relevante

- Extração direta (pypdf/markitdown) não lê texto de PDFs escaneados — precisa do caminho de OCR (Passo 2), que é mais lento e deve ser confirmado com o usuário antes de rodar.
- OCR não é perfeito: pode errar palavras em imagens de baixa qualidade/resolução. Trate como uma boa aproximação do conteúdo, não como transcrição garantidamente exata — se algum trecho for crítico (valor, data, número de processo), vale conferir contra o original.
- Tabelas complexas e formatação visual podem perder fidelidade na extração via `pypdf`/OCR (é texto corrido) — para documentos onde a estrutura de tabela importa, o MarkItDown preserva melhor, mas é mais lento em PDFs grandes.
- Formatos suportados pelo MarkItDown: PDF, Word, Excel, PowerPoint, imagens (metadados), áudio (metadados/transcrição), HTML, CSV/JSON/XML, ZIP, EPub, URLs do YouTube.

