# Correção pendente: caminho do NotebookLM em `.mcp.json`

## O problema

O arquivo `.mcp.json` deste plugin aponta o servidor `NotebookLM` direto para
um caminho fixo desta máquina:

```json
"NotebookLM": {
  "command": "C:\\Users\\ricar\\AppData\\Roaming\\uv\\tools\\notebooklm-mcp-cli\\Scripts\\notebooklm-mcp.exe",
  "args": []
}
```

Isso contradiz o próprio `README.md` do plugin, que descreve outra forma de
configurar (variável de ambiente `NOTEBOOKLM_MCP_PATH`):

```bash
export NOTEBOOKLM_MCP_PATH=/caminho/para/seu/notebooklm-mcp/server.py
```

Ou seja: o código faz uma coisa, a documentação descreve outra. Hoje isso não
atrapalha porque o plugin só roda nesta máquina, com este usuário Windows
(`ricar`). O problema aparece se:

- você trocar de computador ou reinstalar o Windows;
- o usuário do Windows mudar de nome;
- alguém mais no escritório tentar instalar o plugin na própria máquina;
- a ferramenta `notebooklm-mcp-cli` for reinstalada em outro local pelo `uv`.

Em qualquer um desses casos, o MCP `NotebookLM` vai falhar ao iniciar, e o
sintoma será só "NotebookLM não conecta" — sem pista óbvia de que a causa é
um caminho hardcoded.

## Como corrigir quando for necessário

**Opção simples (sem mexer em nada agora):** se um dia o NotebookLM parar de
conectar, confirme primeiro se o caminho acima ainda existe na máquina atual
(`C:\Users\<usuário>\AppData\Roaming\uv\tools\notebooklm-mcp-cli\Scripts\notebooklm-mcp.exe`).
Se o usuário do Windows mudou, é só atualizar essa string em `.mcp.json`.

**Opção correta (alinha código com o README):** trocar o `.mcp.json` para ler
de uma variável de ambiente, do mesmo jeito que o CNJ já faz com
`${CLAUDE_PLUGIN_ROOT}`:

```json
"NotebookLM": {
  "command": "${NOTEBOOKLM_MCP_PATH}",
  "args": []
}
```

E então definir `NOTEBOOKLM_MCP_PATH` uma vez no ambiente (ou em um arquivo
`.env` do plugin, se o formato usado suportar). Isso deixa o plugin portátil
entre máquinas/usuários sem precisar editar `.mcp.json` toda vez.

## Status

Nenhuma alteração foi feita em `.mcp.json` — este arquivo é só o registro do
problema para quando vocês decidirem corrigir. Mantido como está, por decisão
do Ricardo em 2026-07-19.
