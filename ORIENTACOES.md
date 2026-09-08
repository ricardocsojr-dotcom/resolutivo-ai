# Orientações RDAA — Automação de Peças Jurídicas (2026-09-08)

## 📋 Resumo das Novas Automações

### 1. **Entrega Automática de Peças**
   - Script: `scripts/entregar.py` ou `scripts/formatar_com_producao.py`
   - Destino: `Desktop/Produção Jurídica/YYYY-MM-DD/<processo>/`
   - Resultado: DOCX + PDF auto-gerado
   - Numeração: 01, 02, 03... (sequencial)

### 2. **Gestão de Versões com Preservação de Formatação**
   - Script: `scripts/gestor_versoes.py`
   - Rastreia: V001, V002, V003...
   - Preserva: negrito, print, tabs de versões anteriores
   - Permite: comparar, voltar, backup automático

### 3. **Conversão DOCX → PDF Automática**
   - Script: `scripts/converter_docx_pdf.py`
   - Via: Microsoft Word COM (fallback: LibreOffice)
   - Integrada: em `automatizar_peca.py` e `formatar_com_producao.py`

---

## 🚀 Fluxo Recomendado (Passo a Passo)

### A. Primeira Redação

```bash
# 1. Redija a peça com redigir-peca ou manualmente
# 2. Estruture o JSON (rdaa_context.json)
# 3. Execute:

python3 formatar_com_producao.py \
  --context rdaa_context.json \
  --processo "5012964-89.2023.8.13.0035" \
  --nome-peca "Manifestação em Cumprimento de Sentença" \
  --tipo "manifestacao"

# Resultado:
# ✓ DOCX construído, QA passou, PDF gerado
# ✓ Entregue em Desktop/Produção Jurídica/2026-09-08/5012964.../
#   - 01. Manifestação em Cumprimento de Sentença.docx
#   - 01. Manifestação em Cumprimento de Sentença.pdf
```

### B. Você Formata Manualmente

```
# Abra o DOCX em Desktop/Produção Jurídica/...
# Aplicar:
  - Negrito em termos-chave
  - Formatação de citações (elegante para print)
  - Ajuste de espaçamentos e indentação
# Salve como: manifestacao_v1_formatada.docx
```

### C. Você Pede Correção

```
"Ricardo, reescreva o parágrafo 5 (sobre execução por expropriação) 
de forma mais contundente. Mantenha o negrito e print que formatei."
```

### D. Eu Gero Nova Versão (V002)

```bash
# 1. Gero novo DOCX com as correções (estrutura preservada)
# 2. Passo pelo formatar-peca
# 3. Entrego e registro:

python3 scripts/gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  salvar "manifestacao_v2.docx" \
  --motivo "Reescrita parágrafo 5 — execução contundente" \
  --tags parágrafo-5-reescrito negrito print

# Histórico registra:
# V001: Publicação inicial (68 parágrafos)
# V002: Reescrita parágrafo 5 (70 parágrafos) ← NOVA
```

### E. Você Reaplica Formatação (se necessário)

```
# Abra a V001 para referência:
python3 scripts/gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  carregar --numero 1 --para "v1_referencia.docx"

# Compare a V1 com V2, reaplique negrito/print no parágrafo 5
```

### F. Próximas Iterações

Volta ao passo C (pede correção) → D → E → ...

---

## 📂 Estrutura de Armazenamento

```
Desktop/Produção Jurídica/
└── 2026-09-08/
    └── 5012964-89.2023.8.13.0035/
        ├── 01. Manifestação em Cumprimento de Sentença.docx
        ├── 01. Manifestação em Cumprimento de Sentença.pdf
        ├── 02. Cálculo Atualizado.xlsx
        └── 03. Jurisprudência STJ.pdf

.rdaa-versoes/
└── 5012964-89.2023.8.13.0035/
    └── Manifestação em Cumprimento de Sentença/
        ├── v001_Manifestação....docx
        ├── v002_Manifestação....docx
        ├── v003_Manifestação....docx
        ├── historico.json
        └── backups/
```

---

## 🔧 Comandos Rápidos

### Entregar Peça Simples (DOCX já aprovado)

```bash
python3 scripts/entregar.py \
  --docx "caminho/manifestacao_final.docx" \
  --processo "5012964-89.2023.8.13.0035" \
  --nome "Manifestação em Cumprimento de Sentença"
```

### Entregar Peça Completa (JSON → DOCX → PDF → Desktop)

```bash
python3 scripts/formatar_com_producao.py \
  --context rdaa_context.json \
  --processo "5012964-89.2023.8.13.0035" \
  --nome-peca "Manifestação" \
  --tipo "manifestacao"
```

### Salvar Versão (para rastreamento)

```bash
python3 scripts/gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  salvar "manifestacao_v2.docx" \
  --motivo "Reescrita parágrafo 5" \
  --tags parágrafo-5-reescrito negrito
```

### Listar Todas as Versões

```bash
python3 scripts/gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  listar
```

### Comparar Versões

```bash
python3 scripts/gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  comparar 1 2
```

### Carregar Versão Anterior (para referência)

```bash
python3 scripts/gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  carregar --numero 1 --para "v1_referencia.docx"
```

### Backup de Todas as Versões

```bash
python3 scripts/gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  backup
```

### Adicionar Anexo (documento adicional)

```bash
python3 scripts/automatizar_peca.py anexo \
  "5012964-89.2023.8.13.0035" \
  "Cálculo Atualizado" \
  "caminho/calculo.xlsx"
```

---

## 🏷️ Tags Recomendadas

Ao salvar versão, use tags descritivas:

```bash
--tags negrito              # tem negrito aplicado
--tags print                # pronto para impressão
--tags parágrafo-5          # parágrafo 5 foi alterado
--tags citação-formatada    # citação longa elegante
--tags rodapé-revisado      # notas de rodapé verificadas
--tags jurisprudência-nova  # jurisprudência adicionada
--tags acréscimo            # texto adicionado
--tags deleção              # texto removido
--tags reordenação          # parágrafos reordenados
--tags estrutura-final      # estrutura aprovada
```

---

## 📋 Checklist: Fluxo Completo

- [ ] 1. Redação (redigir-peca ou manual)
- [ ] 2. Estruture JSON (rdaa_context.json)
- [ ] 3. Execute `formatar_com_producao.py`
- [ ] 4. DOCX + PDF entregues em Desktop/Produção
- [ ] 5. Salve V001 com `gestor_versoes.py`
- [ ] 6. Formatar manualmente (negrito, print, etc)
- [ ] 7. Pede correção (se necessário)
- [ ] 8. Eu gero V002
- [ ] 9. Salve V002 com `gestor_versoes.py`
- [ ] 10. Reaplique formatação (se V002 mudou estrutura)
- [ ] 11. Próxima iteração (ou pronto para assinar)

---

## 📚 Documentação Completa

- `REGRA_ENTREGAR.md` — Como entregar peças (3 formas)
- `VERSOES_README.md` — Sistema de versões em detalhes
- `skills/formatar-peca/` — Gerador DOCX nativo RDAA
- `skills/automate-peca-producao/` — Automação de entrega
- `skills/gestor-versoes-peca/` — Gestor de versões

---

## 🔗 Integração Hermes

Todos os scripts podem ser chamados via Hermes CLI:

```bash
# Skill: formatar-peca-com-producao
hermes skill --name formatar-peca-com-producao \
  --context rdaa_context.json \
  --processo "5012964..." \
  --nome "Manifestação"

# Skill: automate-peca-producao
hermes skill --name automate-peca-producao \
  --docx "manifestacao_final.docx" \
  --processo "5012964..." \
  --nome "Manifestação"

# Skill: gestor-versoes-peca
hermes skill --name gestor-versoes-peca \
  --processo "5012964..." \
  --peca "Manifestação" \
  --action listar
```

---

## ⚠️ Dependências

- Windows + Microsoft Word (ou LibreOffice)
- Python 3.10+
- python-docx
- pathlib, json, datetime, shutil

---

## 🎯 Regra de Ouro

**Sempre salve versões quando há mudanças significativas.**

```bash
# Ao enviar nova versão para você:
python3 scripts/gestor_versoes.py ... salvar \
  "novo_docx.docx" \
  --motivo "Correção: [descrição]" \
  --tags [tag1] [tag2]
```

Assim, você tem histórico completo e pode voltar/comparar quando necessário.

---

## 📍 Localização dos Scripts

```
C:\Projetos\resolutivo-ai\
├── scripts/
│   ├── gestor_versoes.py
│   ├── automatizar_peca.py
│   ├── converter_docx_pdf.py
│   ├── entregar.py
│   └── formatar_com_producao.py
├── REGRA_ENTREGAR.md
├── VERSOES_README.md
└── ORIENTACOES.md (este arquivo)
```

---

**Data:** 2026-09-08  
**Versão:** 1.0  
**Status:** ✓ Operacional
