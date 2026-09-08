# Sistema de Versões — Preserva Formatação na Iteração

## O Problema

Você formata a peça (negrito, print, indentação), pede uma correção, e quando gero a nova versão, a formatação se perde.

## A Solução

**Gestor de Versões** rastreia cada versão com suas tags. Permite:
1. Voltar a versões anteriores
2. Ver exatamente o que mudou
3. Preservar histórico completo
4. Aplicar correções sem perder formatação anterior

## Fluxo Típico

### Passo 1: Primeira publicação (V001)

```bash
# Após gerar manifestacao_final.docx com formatar-peca
python3 gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  salvar "manifestacao_final.docx" \
  --motivo "Publicação inicial" \
  --tags negrito print
```

✓ Salvo como: **V001 — Publicação inicial**

### Passo 2: Você formata manualmente

- Adiciona negrito em termos importantes
- Formata citações (impressão elegante)
- Ajusta espaçamentos
- Arquivo fica: `manifestacao_v1_formatada.docx`

### Passo 3: Você pede uma correção

"Ricardo, reescreva o parágrafo 5 (onde fala sobre execução por expropriação) de forma mais contundente"

### Passo 4: Eu gero nova versão (V002)

```bash
# Após gerar manifestacao_v2.docx com as correções
python3 gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  salvar "manifestacao_v2.docx" \
  --motivo "Reescrita parágrafo 5 — execução mais contundente" \
  --tags negrito print parágrafo-5-reescrito
```

✓ Salvo como: **V002 — Reescrita parágrafo 5**

### Passo 5: Você reaplica formatação

- Copia `v001_...docx` para referência visual
- Reaplica negrito no parágrafo 5 novo
- Verifica se print saiu bem
- Arquivo fica: `manifestacao_v2_formatada.docx`

### Passo 6: Próxima iteração (se precisar)

Repete do passo 3.

## Comandos de Referência

### Listar todas as versões com detalhes

```bash
python3 gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  listar
```

**Saída:**
```
================================================================================
HISTÓRICO: Manifestação em Cumprimento de Sentença
Processo: 5012964-89.2023.8.13.0035
================================================================================

V001 ✓ ATIVA
  Data: 2026-09-08T08:17:08
  Motivo: Publicação inicial
  Tags: negrito, print
  Arquivo: v001_Manifestação em Cumprimento de Sentença.docx
  Tamanho: 66.0 KB
  Parágrafos: 68, Tabelas: 1

V002 ✓ ATIVA
  Data: 2026-09-09T10:30:22
  Motivo: Reescrita parágrafo 5 — execução mais contundente
  Tags: negrito, print, parágrafo-5-reescrito
  Arquivo: v002_Manifestação em Cumprimento de Sentença.docx
  Tamanho: 67.2 KB
  Parágrafos: 70, Tabelas: 1
```

### Carregar versão anterior para referência

```bash
python3 gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  carregar --numero 1 --para "v1_referencia.docx"
```

✓ Salvo em `v1_referencia.docx` — use para copiar formatação

### Comparar duas versões

```bash
python3 gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  comparar 1 2
```

**Saída:**
```
================================================================================
COMPARAÇÃO: V1 vs V2
================================================================================

V1 (Publicação inicial)
  Data: 2026-09-08T08:17:08
  Tamanho: 66.0 KB
  Parágrafos: 68

V2 (Reescrita parágrafo 5)
  Data: 2026-09-09T10:30:22
  Tamanho: 67.2 KB
  Parágrafos: 70

Diferenças:
  Tamanho: +1.2 KB
  Parágrafos: +2
```

### Fazer backup de todas as versões

```bash
python3 gestor_versoes.py \
  --processo "5012964-89.2023.8.13.0035" \
  --peca "Manifestação em Cumprimento de Sentença" \
  backup
```

✓ Backup criado em: `.rdaa-versoes/.../backups/20260909_143521/`

## Estrutura de Arquivos

```
C:\Users\ricar\cerebro-ricar\
└── .rdaa-versoes/
    └── 5012964-89.2023.8.13.0035/
        └── Manifestação em Cumprimento de Sentença/
            ├── v001_Manifestação em Cumprimento de Sentença.docx (66 KB)
            ├── v002_Manifestação em Cumprimento de Sentença.docx (67 KB)
            ├── v003_Manifestação em Cumprimento de Sentença.docx (68 KB)
            ├── historico.json  ← rastreia tudo
            └── backups/
                └── 20260909_143521/
                    ├── v001_...docx
                    ├── v002_...docx
                    ├── historico.json
```

## Tags Recomendadas

Use tags descritivas para marcar o que foi alterado:

```bash
--tags negrito              # tem negrito aplicado
--tags print                # pronto para impressão
--tags parágrafo-5          # parágrafo 5 foi alterado
--tags citação-formatada    # citação longa formatada
--tags rodapé-revisado      # notas de rodapé revisadas
--tags jurisprudência-nova  # jurisprudência adicionada
--tags acréscimo            # texto adicionado
--tags deleção              # texto removido
--tags reordenação          # parágrafos reordenados
```

## Caso de Uso Real

### Cenário: Manifestação com múltiplas correções

```
V001: Publicação inicial (66 KB, 68 parágrafos)
      Tags: negrito, print
      ↓
      [Você formata: negrito, print OK]
      
V002: Reescrita parágrafo 5 (67 KB, 70 parágrafos)
      Tags: negrito, print, parágrafo-5-reescrito
      ↓
      [Você reaplica negrito no parágrafo novo]
      
V003: Adição jurisprudência parágrafo 7 (68 KB, 72 parágrafos)
      Tags: negrito, print, jurisprudência-stj-2025
      ↓
      [Você formata jurisprudência nova]
      
V004: Reordenação — pedidos antes de fundamento (69 KB, 75 parágrafos)
      Tags: negrito, print, reordenação-estrutural
      ↓
      [Você revê toda a estrutura]
      
✓ FINAL: v004 pronto para assinar e protocolar
```

## Integração Automática

Se quiser que o gestor salve automaticamente a cada novo DOCX, integre ao `formatar_com_producao.py`:

```python
from gestor_versoes import GestorVersoesPeca

# No final da etapa 3 (entregar):
gestor = GestorVersoesPeca(processo, nome_peca)
gestor.salvar_versao(
    docx_final,
    motivo=f"Gerado automaticamente",
    tags=["auto-gerado"]
)
print(f"✓ Versão salva no gestor")
```

## Localização

**Script:** `C:\Users\ricar\cerebro-ricar\gestor_versoes.py`

**Versões armazenadas:** `C:\Users\ricar\cerebro-ricar\.rdaa-versoes\`

**Skill:** `gestor-versoes-peca` (Hermes)
