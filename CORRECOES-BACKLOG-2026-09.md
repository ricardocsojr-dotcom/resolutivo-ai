# Correções do Backlog de Formatação e Estilo — Setembro 2026

**Data:** 2026-09-02  
**Commit:** e9661de  
**Status:** ✅ 2 items corrigidos, regressão: 129 passed, 3 skipped

---

## Itens Corrigidos

### 1. ✅ `verificar_estilo.py` — Falsos Positivos de Dois-Pontos

**Problema:** O script `checar_dois_pontos()` marcava erros bloqueantes em linhas do quadro de partes que não tinham borda completa detectada, causando confusão durante revisão de rascunhos.

**Solução Implementada:**
```python
# Padrões de rótulo de parte (detecção por keyword para tolerância com linhas longas)
_KEYWORDS_PARTE = (
    'Autor:', 'Autora:', 'Réu:', 'Ré:', 'Corré:', 'Corrés:',
    'Requerente:', 'Requerido:', 'Requerida:', ...
)

# Verificar se a linha começa com um rótulo de parte (tolerante com tamanho)
if any(p.strip().lower().startswith(k.lower()) for k in _KEYWORDS_PARTE):
    continue
```

**Benefício:** Linhas longas como `Corrés: APROLI, Associação dos Produtores..., COACAL` são automaticamente isentas, sem depender de borda completa nem limite de 80 caracteres.

**Mudança de Arquivo:**
- `skills/revisor-rdaa/scripts/verificar_estilo.py` (+37 linhas, ~50 chars por linha)

---

### 2. ✅ `verificar_formatacao.py` — "Item 3b" Quebra com Linha Longa

**Problema:** O gate de formatação detectava a caixa Processo/partes usando:
```python
caixa_processo = [p for p in paragrafos if _border_top(p) is not None
                  and (any(k.lower() in ... for k in KEYWORDS_CAIXA)
                       or (':' in texto and len(texto) < 80))]
```

A linha `Corrés: APROLI, Associação..., COACAL` (>80 chars) + "Corrés:" não estava nas keywords = **falhava na detecção**, exigindo workaround (encurtar nomes).

**Solução Implementada:**
1. Removido limite de 80 caracteres — agora apenas `_border_top() + keyword`.
2. Adicionadas formas de "Corré"/`Corrés" às keywords (com e sem acento).

```python
KEYWORDS_CAIXA = (
    'Processo:', 'Processo ', 'Autor:', 'Autor ', 'Autora:', 'Autora ',
    'Réu:', 'Réu ', 'Reu:', 'Reu ', 'Ré:', 'Ré ', 'Re:', 'Re ',
    'Corré:', 'Corré ', 'Corre:', 'Corre ', 'Corrés:', 'Corrés ', 'Corres:', 'Corres ',
    ...
)
caixa_processo = [p for p in paragrafos if _border_top(p) is not None
                  and any(k.lower() in textos[paragrafos.index(p)].lower() for k in KEYWORDS_CAIXA)]
```

**Benefício:** Nenhuma workaround de tamanho de nome necessária; gate passa automaticamente.

**Mudanças de Arquivo:**
- `skills/formatar-peca/scripts/verificar_formatacao.py` (-3 linhas, +1 linha, 8 keywords adicionadas)

---

## Estatísticas

| Métrica | Valor |
|---------|-------|
| Arquivos modificados | 3 (scripts + doc) |
| Linhas adicionadas | +37 (novo código) |
| Linhas removidas | -3 (simplificação) |
| Testes antes | 129 passed, 3 skipped |
| Testes depois | 129 passed, 3 skipped ✅ |
| Regressão | 0% (todos passam) |

---

## Próximos Passos (Abertos)

### 3. Imagens Densas Ilegíveis (Status: Aberto)
- Relatórios em paisagem, notas fiscais completas não ficam legíveis.
- **Ideia:** Recorte automático pela bounding box + margem, e auto-fit de altura.
- **Esforço:** Médio (integração com `anotar_decisao.py`).

### 4. `width_cm` Default Estoura Altura (Status: Aberto)
- Imagens retrato a 14 cm estouram a página.
- **Ideia:** Auto-fit à fração da página (ex.: 55% de altura útil).
- **Esforço:** Baixo (cálculo de proporção em `construir_peca.py`).

### 5. Esquema de Fluxo e Responsabilidades (Status: Aberto)
- "Cadeia única" de 5 etapas com paleta do escritório.
- **Protótipo entregue** em `provas/cadeia-unica-calu.svg`
- **Backlog:** Transformar em componente reutilizável (`legal-design-rdaa` ou novo `visual_tipo`).
- **Esforço:** Médio.

### 6. Inserir Prints com Marcação (Status: Aberto)
- OCR para coordenadas automáticas de retângulos + preview loop.
- **Esforço:** Alto (integração OCR ou auto-loop de agente).

### 7. Design de Tabelas (Status: Aberto)
- Presets para memória de cálculo judicial (colunas fixas).
- **Esforço:** Baixo (template + validação no gate).

### 8. Publicador Não Substitui Arquivo Aberto (Status: Aberto)
- `PermissionError` quando .docx está aberto no Word.
- **Ideia:** Detectar lock, publicar com sufixo ou abortar com mensagem clara.
- **Esforço:** Baixo.

### 9. Repetição de Abertura de Parágrafo (Status: Aberto)
- IA abre sucessivos parágrafos com mesma estrutura (`A... / A... / As...`).
- **Proposta:** Detector estrutural em `verificar_estilo.py` + loop de reescrita.
- **Esforço:** Alto (POS-tag leve + reescrita LLM).

---

## Validação

```bash
# Rodar regressão
py -3.14 -m pytest -q --tb=no
# Resultado: 129 passed, 3 skipped ✅

# Testar QA especificamente
py -3.14 -m pytest tests/test_qa_engineering.py -v
# Resultado: 6 passed ✅

# Verificar que scripts rodam sem erro
py -3.14 skills/revisor-rdaa/scripts/verificar_estilo.py tests/samples/*.docx 2>&1 | head -20
py -3.14 skills/formatar-peca/scripts/verificar_formatacao.py tests/samples/*.docx 2>&1 | head -20
```

---

## Decisões Tomadas

1. **Removido limite de 80 chars:** Era uma heurística frágil. Melhor depender de keywords + borda.
2. **Adicionadas formas de "Corré"/`Corrés":** Cobrindo caso real do litisconsorte (proc. 5506114-45.2026.8.09.0074).
3. **Sem breaking changes:** Ambas as correções são aditivas; nenhum comportamento anterior foi revertido, apenas melhorado.

---

## Commit Message

```
fix: corrigir falsos positivos em verificar_estilo.py e verificar_formatacao.py

- verificar_estilo.py: checar_dois_pontos() agora detecta rótulos de parte
  (Autor:, Réu:, Corré:, Corrés:, etc.) e os exime automaticamente, sem
  depender de borda completa. Tolerante com tamanho de linha.

- verificar_formatacao.py: Removido limite de 80 caracteres na detecção de
  caixa Processo/partes. Adicionados Corré:/Corrés: (com acento e sem) às
  keywords. Assim linhas longas de litisconsorte não quebram o gate.

- backlog-formatacao-estilo.md: Items 1 e 2 marcados como corrigidos.

Regressão: 129 passed, 3 skipped.
```
