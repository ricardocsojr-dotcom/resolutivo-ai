#!/usr/bin/env node
// Injeta o CLAUDE.md do plugin (perfil do escritório, persona, regras de
// orquestração) como contexto no início de toda sessão. Sem isso, esse
// arquivo fica inerte — o Claude Code não carrega um CLAUDE.md na raiz de
// um plugin como contexto de projeto automaticamente.
//
// Também verifica se o hook de SessionEnd (session-end.mjs) deixou matérias
// pendentes de sincronização com o vault (sessão anterior tocou o estado mas
// nunca publicou nada) e injeta um lembrete acionável — essa é a rede de
// segurança da gravação automática descrita em redigir-peca/SKILL.md passo 10.
import fs from "node:fs";
import path from "node:path";

const claudeMdPath = process.argv[2];

let content = "";
try {
  content = fs.readFileSync(claudeMdPath, "utf8").trim();
} catch {
  content = "";
}

const pendingPath = path.join(process.cwd(), ".rdaa-run", ".pending_vault_sync.json");
let pendingNote = "";
try {
  const pending = JSON.parse(fs.readFileSync(pendingPath, "utf8")).pending || [];
  if (pending.length > 0) {
    const list = pending
      .map((item) => `- ${item.matter_id} (fase: ${item.phase || "desconhecida"})`)
      .join("\n");
    pendingNote =
      "\n\n---\n\nATENÇÃO — sincronização de vault pendente: a(s) matéria(s) abaixo " +
      "foram tocadas numa sessão anterior sem publicar nada, então a gravação " +
      "automática do passo 10 de redigir-peca/SKILL.md nunca rodou.\n" +
      list +
      "\nAntes de continuar, siga o passo 10 pra cada uma (grave o resumo no " +
      "vault, marque `vault_synced_at` no manifesto de cada matéria via " +
      "`update_manifest`). Depois disso a pendência some sozinha na próxima " +
      "sessão.";
  }
} catch {
  pendingNote = "";
}

const fullContent = (content + pendingNote).trim();

if (fullContent) {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext: fullContent,
    },
  }));
}

process.exit(0);
