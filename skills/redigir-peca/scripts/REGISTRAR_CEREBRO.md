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

### Integração no fluxo

Após `publicar_docx.py` retornar `[OK]`, `registrar_cerebro.py`:

1. grava/atualiza a matéria no Cérebro-Ricar;
2. chama `sincronizar_openviking.py` sobre `wiki/operacional`;
3. usa `vectors_only` por padrão, preservando a privacidade do conteúdo jurídico;
4. cria `OPENVIKING-RECIBO.json` quando o servidor confirma o processamento.

O orquestrador pode validar esse recibo com:

```bash
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py \
  register-vault-sync .rdaa-run/<matter_id> \
  --vault cerebro-ricar \
  --artifact .rdaa-run/<matter_id>/OPENVIKING-RECIBO.json
```

Se o OpenViking estiver indisponível, o registro no Cérebro-Ricar permanece preservado, mas o retorno do script indica sincronização pendente e a matéria não deve ser considerada `vault_registered`.

### Sincronização manual/reconciliação

Para reconstruir o índice derivado de uma coleção:

```bash
py -3.14 skills/redigir-peca/scripts/sincronizar_openviking.py \
  --path "C:/Users/ricar/cerebro-ricar/wiki/operacional" \
  --processing-mode vectors_only
```

O script mantém `.openviking-sync-state.json` no Cérebro-Ricar, compara SHA-256 e só usa `create` para URI nova ou `replace` para URI já conhecida. Não use `--watch-interval` para caminhos locais: o servidor OpenViking rejeita watchers de arquivos locais.

`vectors_only` é o padrão para impedir que peças, matérias e jurisprudência sejam enviadas ao VLM externo. `semantic_and_vectors` só deve ser usado quando Ricardo autorizar esse tratamento para a coleção específica.
