# Regra: Entregar Peça Automaticamente

## 3 Formas de Usar

### 1. **Forma Simples** (Recomendada após `formatar-peca`)

Quando você já tem um DOCX final aprovado no QA:

```bash
python3 entregar.py \
  --docx "C:/Users/ricar/cerebro-ricar/.rdaa-run/manifestacao-5012964/manifestacao_final.docx" \
  --processo "5012964-89.2023.8.13.0035" \
  --nome "Manifestação em Cumprimento de Sentença"
```

**Resultado:**
- Copia o DOCX para Desktop/Produção Jurídica
- Converte para PDF automaticamente
- Nomenclatura sequencial (01, 02, 03...)
- Pronto para assinar

---

### 2. **Forma Completa** (Do zero ao fim em uma linha)

Partindo de um JSON de contexto:

```bash
python3 formatar_com_producao.py \
  --context "rdaa_context.json" \
  --processo "5012964-89.2023.8.13.0035" \
  --nome-peca "Manifestação" \
  --tipo "manifestacao"
```

**O que faz:**
1. Constrói DOCX (construir_peca.py)
2. Passa QA (publicar_docx.py)
3. Entrega em Desktop/Produção (automatizar_peca.py)
4. Converte DOCX → PDF
5. Registra no cérebro

---

### 3. **Dentro do Hermes** (CLI do Hermes)

```bash
hermes run --skill automate-peca-producao \
  --param processo="5012964-89.2023.8.13.0035" \
  --param nome="Manifestação" \
  --param docx="manifestacao_final.docx"
```

---

## Estrutura Final

Todas as opções entregam em:

```
Desktop/Produção Jurídica/
└── YYYY-MM-DD/
    └── <processo>/
        ├── 01. <peça>.docx
        ├── 01. <peça>.pdf
        ├── 02. <anexo>.pdf
        └── 03. <anexo>.xlsx
```

## Quando Usar Cada Uma

| Cenário | Forma | Comando |
|---------|-------|---------|
| Já tenho DOCX final | Simples | `entregar.py` |
| Do JSON ao Desktop | Completa | `formatar_com_producao.py` |
| Integração Hermes | CLI | `hermes run --skill` |
| Manual (uma peça) | `automatizar_peca.py` | `python3 automatizar_peca.py adicionar ...` |

## Como Fazer uma Regra (Automação)

Se quer que isso rode **automaticamente** após cada redação:

### Opção A: Integrar ao `formatar-peca` skill

Adicione ao final do `publicar_docx.py`:

```python
# Ao final, automaticamente:
from pathlib import Path
subprocess.run([
    sys.executable,
    str(Path.home() / "cerebro-ricar" / "entregar.py"),
    "--docx", str(docx_final),
    "--processo", context.get("numero_processo"),
    "--nome", context.get("nome_peca")
])
```

### Opção B: Cronjob Hermes

```bash
hermes cronjob create \
  --schedule "after-formatar-peca" \
  --prompt "Entregar peça ao Desktop/Produção Jurídica"
```

### Opção C: Integrar ao skill `redigir-peca`

No final de `redigir-peca`, chamar `formatar_com_producao.py` automaticamente.

---

## Fluxo Recomendado (com Regra)

1. **Redija a peça** com `redigir-peca`
2. **Estruture o JSON** de contexto
3. **Execute `formatar_com_producao.py`**
   ↓ (automático) construir → QA → entregar → PDF
4. **✓ Pronto em Desktop/Produção**
5. Assine e protocole

---

## Exemplo Prático

### Manifesta Manifestação Nível B — 07/09/2026

```bash
# 1. Após formatar-peca (você tem manifestacao_final.docx)
python3 entregar.py \
  --docx "C:/Users/ricar/cerebro-ricar/.rdaa-run/manifestacao-5012964/manifestacao_final.docx" \
  --processo "5012964-89.2023.8.13.0035" \
  --nome "Manifestação em Cumprimento de Sentença"

# Resultado:
# Desktop/Produção Jurídica/2026-09-08/5012964-89.2023.8.13.0035/
#   ├── 01. Manifestação em Cumprimento de Sentença.docx (66 KB)
#   └── 01. Manifestação em Cumprimento de Sentença.pdf (97 KB)

# 2. Pronto!
# Próximo: Abra o PDF, revise, assine e protocole.
```

---

## Arquivos Envolvidos

- `entregar.py` — Atalho simples
- `formatar_com_producao.py` — Fluxo completo (JSON → DOCX → PDF → Desktop)
- `automatizar_peca.py` — Orquestra adição de arquivos
- `converter_docx_pdf.py` — Converte DOCX → PDF via Word

Localização: `C:\Users\ricar\cerebro-ricar\`
