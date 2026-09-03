# Setup: Cérebro-Ricar & Automação (2026-09-03)

## Estrutura

**Cérebro único local:** `C:\Users\ricar\cerebro-ricar\`

```
cerebro-ricar/
├── CLAUDE.md              # Convenções (regra de ouro)
├── index.json             # Auto (count + metadata)
├── hot.md                 # Últimas 48h (max 500 palavras)
└── wiki/
    ├── domains/           # Áreas jurídicas (10 arquivos)
    ├── concepts/          # Teses jurídicas (12 arquivos)
    ├── sources/           # Jurisprudência literal PREC-NNN (19 arquivos)
    ├── entities/          # Clientes, partes (vazio, alimentado)
    ├── operacional/       # Matérias publicadas (vazio, alimentado)
    └── pessoal/           # Lembretes, reflexões (vazio, alimentado)
```

**Dados:**
- Migrados do WSL Ementário: 10 domains, 12 concepts, 19 sources
- Estrutura YAML frontmatter (type, title, domain, status, created, etc)
- Convenções em `CLAUDE.md`

## Automação

### 1. Peças Publicadas → Cérebro

**Script:** `skills/redigir-peca/scripts/registrar_cerebro.py`

**Quando chamar:** Após `publicar_docx.py` retornar `[OK]`

```bash
py -3.14 skills/redigir-peca/scripts/registrar_cerebro.py \
  .rdaa-run/<matter_id>/ \
  --matter-id <matter_id> \
  --level C|B|A
```

**Faz:**
- Cria `wiki/operacional/matter-XXX.md` com partes, pedidos, status
- Recount `index.json`
- Atualiza `hot.md`

**Integração:** Manual via CLI (futuro: hook no orquestrador)

### 2. Estudos Jurídicos → Cérebro

**Script:** `skills/estudo-juridico-rdaa/scripts/registrar_estudo_cerebro.py`

**Quando chamar:** Após publicar estudo como Artifact

```bash
py -3.14 skills/estudo-juridico-rdaa/scripts/registrar_estudo_cerebro.py \
  --theme "Desconsideração Tema 643 STJ" \
  --artifact-url "https://artifact.link/xyz" \
  --concepts "Conceito 1" "Conceito 2" \
  --sources "PREC-001" "PREC-011" \
  --domain "direito-empresarial-societario-e-agronegocio"
```

**Faz:**
- Cria `wiki/concepts/[conceito].md` para cada conceito
- Cria `wiki/sources/[PREC-NNN].md` para cada fonte
- Linkeia ao domain em `wiki/domains/[domain].md`
- Recount `index.json`
- Atualiza `hot.md`

## Sincronização & Backup

- **Cérebro-Ricar local:** `C:\Users\ricar\cerebro-ricar\`
- **Peças publicadas:** `C:\Users\ricar\OneDrive - RD\Área de Trabalho\Romano\Peças\...`
- **State & provenance:** `.rdaa-run/<matter_id>/` (git-ignored, sincronizado via vault)
- **Backup:** Seu procedimento normal (Git, OneDrive, etc)

## Remoções & Simplificação

✅ **WSL Ubuntu:** Removido 2026-09-03 (libera RAM, zero perda)
✅ **Ementário WSL:** Migrado → Cérebro-Ricar local
✅ **claude-obsidian:** Não mais necessário (usava WSL)
✅ **Obsidian pesado:** Descartado
✅ **.gitignore:** Robusto (`.rdaa-run/`, peças, caches ignorados)

## Próximos Passos

1. **Integrar no orquestrador:** Fazer registros automáticos após `vault_registered`
2. **Sincronização 3 matérias congeladas:** Resolver `.pending_vault_sync.json`
3. **Ampliar Hermes:** WhatsApp, agenda de prazos, acesso workspace (pendência sábado)

## Referências

- `CLAUDE.md` — convenções do cérebro
- `.gitignore` — exclusões de git
- `skills/redigir-peca/scripts/REGISTRAR_CEREBRO.md` — instruções detalhadas
- `skills/estudo-juridico-rdaa/SKILL.md` — passo 9 corrigido
