# Backlog de Formatação — Progresso 2026-09-02

**Status:** 4 de 9 items resolvidos (44%)  
**Data:** 2026-09-02  
**Testes:** 129 passed, 3 skipped ✅

---

## Resumo Executivo

Corrigidas 4 questões operacionais do backlog de formatação/estilo RDAA, focando em bloqueadores reais de produção (falsos positivos em gates, cálculos manuais, componentes de design).

---

## Items Resolvidos (4)

### 1️⃣ **verificar_estilo.py — Falsos Positivos** ✅
- **Problema:** Script marcava erros em rótulos de parte (`Autor:`, `Réu:`, `Corrés:`)
- **Solução:** Detectar por keyword, sem limite de 80 caracteres
- **Commit:** `e9661de`

### 2️⃣ **verificar_formatacao.py — "Item 3b"** ✅
- **Problema:** Limite de 80 chars falhava com nomes longos
- **Solução:** Remover limite, adicionar keywords `Corré:/Corrés:`
- **Commit:** `e9661de`

### 4️⃣ **Auto-fit de Altura para Imagens Retrato** ✅
- **Problema:** `width_cm` default 14 estoura página
- **Solução:** Calcular largura max para 55% altura útil (~13,5 cm)
- **Arquivo:** `skills/formatar-peca/scripts/construir_peca.py`
- **Commit:** `29d2283`

### 7️⃣ **Gerador de Diagrama Cadeia Única** ✅
- **Problema:** Sem componente reutilizável para fluxos multi-ator
- **Solução:** `gerar_cadeia_fluxo.py` — gerador SVG parametrizado
- **Input:** Spec JSON (titulo, etapas, destacadas, ponto_central)
- **Output:** SVG até 6 etapas com/sem destaque laranja
- **Arquivo:** `skills/legal-design-rdaa/scripts/gerar_cadeia_fluxo.py`
- **Commit:** `514cab5`

---

## Items Abertos (5)

| # | Descrição | Esforço |
|---|-----------|---------|
| 3 | Imagens densas ilegíveis (recorte automático) | Médio |
| 5 | Inserir prints com marcação (OCR + loop) | Alto |
| 6 | Publicador com lock detection | Baixo |
| 8 | Design de tabelas (presets) | Baixo |
| 9 | Repetição de abertura de parágrafo | Alto |

---

## Arquivos Modificados

| Arquivo | Mudança |
|---------|---------|
| `skills/revisor-rdaa/scripts/verificar_estilo.py` | +37 linhas (keywords de parte) |
| `skills/formatar-peca/scripts/verificar_formatacao.py` | -3/+1 linhas (remove limite) |
| `skills/formatar-peca/scripts/construir_peca.py` | +23 linhas (auto-fit altura) |
| `skills/legal-design-rdaa/scripts/gerar_cadeia_fluxo.py` | +172 linhas (gerador SVG) |
| `skills/legal-design-rdaa/examples/cadeia-unica-calu-spec.json` | NOVO (exemplo spec) |
| `referencias/backlog-formatacao-estilo.md` | Atualizado (status items) |
| `skills/formatar-peca/references/schema_blocos.md` | Atualizado (figura) |

---

## Validação

✅ **Testes:** 129 passed, 3 skipped (0% de regressão)  
✅ **Sintaxe:** py_compile OK em todos os scripts  
✅ **Gerador SVG:** Testado com exemplo CALU (funciona)  
✅ **Gates:** Sem falsos positivos em nomes longos  

---

## Commits Adicionados

```
514cab5 feat: gerador de diagramas cadeia única (item 7)
29d2283 feat: auto-fit de altura para imagens retrato (item 4)
0b87e99 docs: guia prático das correções de formatação
7b5f46e docs: sumário de correções do backlog de formatação
e9661de fix: corrigir falsos positivos em verificar_estilo.py / verificar_formatacao.py
```

---

## Documentação Criada

- **CORRECOES-BACKLOG-2026-09.md** — Sumário técnico completo
- **GUIA-PRATICO-FORMATACAO-2026-09.md** — Referência prática
- **README-ORQUESTRADOR.md** — Referência rápida orquestração

---

## Próximas Prioridades

1. **Item 6 (Baixo):** Publicador com lock detection (~2h)
2. **Item 8 (Baixo):** Design de tabelas presets (~3h)
3. **Item 3 (Médio):** Imagens densas com recorte automático (~4h)
4. **Item 7.2:** Integração cadeia_unica no `construir_peca.py` (~2h)

---

## Decisões Técnicas

1. **Keywords de parte (item 1):** Solução simples e robusto, sem dependência de borda completa.
2. **Remoção de limite 80 (item 2):** Heurística frágil; melhor apenas borda + keyword.
3. **Auto-fit (item 4):** Limite a 55% altura útil fornece margem de segurança para parágrafo seguinte.
4. **Gerador SVG (item 7):** Parametrizado em JSON para reutilização sem modificação de código.

---

## Impacto em Produção

✅ **Sem workarounds:** Nenhuma reescrita de nomes necessária  
✅ **Gates automáticos:** Passam sem avisos falsos  
✅ **Layout predizível:** Imagens retrato cabem na página  
✅ **Componentes reutilizáveis:** Diagramas de fluxo em qualquer matéria  

**Pronto para uso imediato em todas as matérias RDAA.**
