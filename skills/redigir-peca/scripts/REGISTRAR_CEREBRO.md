## Automação: Registro no Cérebro Após Publicação

### O que faz

`registrar_cerebro.py` — chamado **após `publicar_docx.py` retornar [OK]** — grava automaticamente a matéria publicada em `C:\Users\ricar\cerebro-ricar\`:

- Cria/atualiza `wiki/operacional/matter-XXX.md`
- Recount e atualiza `index.json`
- Atualiza `hot.md` com a peça nova

**Zero manual. Zero pedido.**

### Quando chamar

**Fluxo no Hermes:**
1. Peça redija, critica, valida
2. `publicar_docx.py` finaliza → `[OK]`
3. **Imediatamente depois:**
   ```bash
   py -3.14 skills/redigir-peca/scripts/registrar_cerebro.py \
     .rdaa-run/<matter_id>/ \
     --matter-id <matter_id> \
     --level <C|B|A>
   ```

### Exemplo

```bash
py -3.14 skills/redigir-peca/scripts/registrar_cerebro.py \
  .rdaa-run/silvio-afonso-esclarecimento-saneador/ \
  --matter-id silvio-afonso-esclarecimento-saneador \
  --level B
```

**Resposta:**
```json
{
  "success": true,
  "matter_id": "silvio-afonso-esclarecimento-saneador",
  "file": "C:\\Users\\ricar\\cerebro-ricar\\wiki\\operacional\\matter-silvio-afonso-esclarecimento-saneador.md",
  "level": "B",
  "title": "Manifestação de Esclarecimento — Saneador",
  "process_number": "5033450-63.2025.8.13.0702",
  "timestamp": "2026-09-03T10:40:00Z"
}
```

### Integração no orquestrador

**Futuro:** integrar no `orquestrador_rdaa.py` como **hook automático** após `vault_registered`. Por enquanto, chamada manual via CLI.
