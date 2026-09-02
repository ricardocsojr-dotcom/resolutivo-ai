# Guia Prático: Correções de Formatação (2026-09-02)

## Problema: Script marca erros que não existem em quadro de partes

### Antes (comportamento quebrado)
```
❌ Contestação CALU, proc. 5506114-45.2026.8.09.0074
Corrés: APROLI, Associação dos Produtores de Leite do Município de Ipameri, 
        e Cooperativa Agropecuária de Catalão, COACAL
```

**Resultado:** Gate falhava porque:
1. Linha tem >80 caracteres → heurística de detecção falhava
2. "Corrés:" não estava em `KEYWORDS_CAIXA` → não reconhecia como parte
3. Exigia workaround: encurtar nomes para `Corrés: APROLI e COACAL`

---

## Solução: 2 Patches Simples

### 1. `verificar_estilo.py` — Detectar Rótulos de Parte Automaticamente

**Mudança:** Adicionar lista de keywords de rótulos de parte e verificar se linha começa com qualquer um deles.

```python
# Linha 218-223 em verificar_estilo.py (NOVO)
_KEYWORDS_PARTE = (
    'Autor:', 'Autora:', 'Réu:', 'Ré:', 'Corré:', 'Corrés:',
    'Requerente:', 'Requerido:', 'Requerida:', 'Embargante:', 'Embargado:',
    # ... (veja o arquivo para lista completa)
)

# Linha 226
if any(p.strip().lower().startswith(k.lower()) for k in _KEYWORDS_PARTE):
    continue  # Exime linha de parte, independente de tamanho
```

**Vantagem:** Tolerante com tamanho de linha.

---

### 2. `verificar_formatacao.py` — Remover Limite de 80 Caracteres

**Mudança:** Remover o `or (':' in texto and len(texto) < 80)` da detecção de caixa, e adicionar keywords de "Corré"/`Corrés"`.

**Antes:**
```python
caixa_processo = [p for p in paragrafos if _border_top(p) is not None
                  and (any(k.lower() in textos[paragrafos.index(p)].lower() for k in KEYWORDS_CAIXA)
                       or (':' in textos[paragrafos.index(p)] and len(textos[paragrafos.index(p)]) < 80))]
```

**Depois:**
```python
caixa_processo = [p for p in paragrafos if _border_top(p) is not None
                  and any(k.lower() in textos[paragrafos.index(p)].lower() for k in KEYWORDS_CAIXA)]

# Em KEYWORDS_CAIXA (linha 323-334), adicionar:
'Corré:', 'Corré ', 'Corre:', 'Corre ', 'Corrés:', 'Corrés ', 'Corres:', 'Corres ',
```

**Vantagem:** Explícito e robusto — borda + keyword, sem limite mágico.

---

## Verificação

```bash
# Testar que scripts rodam sem erro
py -3.14 skills/revisor-rdaa/scripts/verificar_estilo.py seu-documento.docx
py -3.14 skills/formatar-peca/scripts/verificar_formatacao.py seu-documento.docx

# Rodar suite de testes
py -3.14 -m pytest tests/test_qa_engineering.py -v
# Esperado: 6 passed

py -3.14 -m pytest -q --tb=no
# Esperado: 129 passed, 3 skipped
```

---

## Quando Usar

✅ **Use agora:**
- Qualquer matéria com litisconsorte (Corrés:) com nome longo
- Quadro de partes em geral (sem workarounds de tamanho)

✅ **Benefício automático:**
- Nenhuma reescrita de nomes por tamanho
- Gate passa sem avisos falsos
- Revisão mais limpa

---

## Histórico

| Data | Item | Status |
|------|------|--------|
| 2026-09-01 | Descoberto em CALU | ❌ Bloqueado |
| 2026-09-01 | Workaround: encurtar nomes | ⚠️ Contorno |
| 2026-09-02 | Patch 1: verificar_estilo.py | ✅ Corrigido |
| 2026-09-02 | Patch 2: verificar_formatacao.py | ✅ Corrigido |
| 2026-09-02 | Regressão: 129 passed | ✅ Validado |

---

## Próximo no Backlog

**Item 3 (Médio):** Imagens densas ilegíveis  
- Relatórios em paisagem, notas fiscais — não cabe na página mesmo com auto-fit.
- Solução proposta: recorte automático pela bounding box dos retângulos + margem.

**Item 4 (Baixo):** Auto-fit de altura  
- Imagens retrato a 14 cm estouram. Precisa limite de fração da página.

Veja `CORRECOES-BACKLOG-2026-09.md` para detalhes completos.
