## Automação: Registro no Cérebro Após Publicação

### O que faz

`registrar_cerebro.py` — chamado **após `publicar_docx.py` retornar [OK]** — grava automaticamente a matéria publicada em `C:\Users\ricar\cerebro-ricar\`:

- Cria/atualiza `wiki/operacional/matter-XXX.md`
- Recount e atualiza `index.json`
- Atualiza `hot.md` com a peça nova

**Zero manual. Zero pedido.**

### Quando chamar

**Fluxo não exposto como script.** A etapa de registro no cérebro ocorre de forma autônoma como fase tratada por um _system handler_ dentro da máquina de estados (via `orquestracao.cli`). Nenhuma invocação manual avulsa é suportada para evitar deriva de histórico.

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
4. cria `OPENVIKING-RECIBO.json` quando o servidor confirma o processamento;
5. **grava o recibo `CEREBRO-RECIBO.json` em `vault.syncs[]` do `run_manifest.json`**, que é o array exigido pelo gate `vault_registered`.

O passo 5 é automático desde 2026-09-11. Antes disso o recibo só existia em disco e `vault.syncs[]` ficava vazio, então a matéria publicada e registrada de verdade travava antes do último estágio até alguém rodar `register-vault-sync` à mão. **Não chame `register-vault-sync` manualmente após `registrar_cerebro.py`** — o registro já aconteceu e o comando existe apenas para reconciliação de matéria antiga ou recibo de outro vault:

```bash
py -3.14 skills/redigir-peca/scripts/orquestrador_rdaa.py \
  register-vault-sync .rdaa-run/<matter_id> \
  --vault cerebro-ricar \
  --artifact .rdaa-run/<matter_id>/CEREBRO-RECIBO.json
```

Se o OpenViking estiver indisponível, ou se o recibo não entrar no manifesto, o script devolve `success: false` com `cerebro_registered: true` — o registro no Cérebro-Ricar permanece preservado, mas a matéria **não** pode ser considerada `vault_registered`.

### Sincronização manual/reconciliação

Para reconstruir o índice derivado de uma coleção:

```bash
py -3.14 skills/redigir-peca/scripts/sincronizar_openviking.py \
  --path "C:/Users/ricar/cerebro-ricar/wiki/operacional" \
  --processing-mode vectors_only
```

O script mantém `.openviking-sync-state.json` no Cérebro-Ricar, compara SHA-256 e só usa `create` para URI nova ou `replace` para URI já conhecida. Não use `--watch-interval` para caminhos locais: o servidor OpenViking rejeita watchers de arquivos locais.

`vectors_only` é o padrão para impedir que peças, matérias e jurisprudência sejam enviadas ao VLM externo. `semantic_and_vectors` só deve ser usado quando Ricardo autorizar esse tratamento para a coleção específica.
