#!/usr/bin/env node
// Injeta o CLAUDE.md do plugin (perfil do escritório, persona, regras de
// orquestração) como contexto no início de toda sessão. Sem isso, esse
// arquivo fica inerte — o Claude Code não carrega um CLAUDE.md na raiz de
// um plugin como contexto de projeto automaticamente.
import fs from "node:fs";

const claudeMdPath = process.argv[2];

let content = "";
try {
  content = fs.readFileSync(claudeMdPath, "utf8").trim();
} catch {
  process.exit(0);
}

if (content) {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext: content,
    },
  }));
}

process.exit(0);
