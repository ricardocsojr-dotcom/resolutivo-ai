#!/usr/bin/env node
// Rede de seguranca para gravacao automatica no vault (ver redigir-peca/SKILL.md
// passo 10). Uma peca publicada ja grava no vault na hora. Isso aqui cobre o
// caso de uma sessao que tocou uma materia mas nunca chegou a publicar nada —
// sem isso, o registro so aconteceria se alguem lembrasse de pedir, que e
// exatamente o problema que motivou essa automacao.
import fs from "node:fs";
import path from "node:path";

const RUN_DIR = path.join(process.cwd(), ".rdaa-run");
const PENDING_PATH = path.join(RUN_DIR, ".pending_vault_sync.json");

function readJson(filePath, fallback) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    return fallback;
  }
}

let matterDirs = [];
try {
  matterDirs = fs
    .readdirSync(RUN_DIR, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name);
} catch {
  process.exit(0); // sem .rdaa-run nesta pasta, nada a fazer
}

const pending = [];
for (const matterId of matterDirs) {
  const manifestPath = path.join(RUN_DIR, matterId, "manifest.json");
  const manifest = readJson(manifestPath, null);
  if (!manifest) continue;
  if (manifest.vault_synced_at) continue; // ja sincronizado
  pending.push({
    matter_id: matterId,
    phase: manifest.phase || null,
    status: manifest.status || null,
    output: manifest.output || null,
  });
}

if (pending.length === 0) {
  try {
    fs.rmSync(PENDING_PATH, { force: true });
  } catch {
    // ignora
  }
  process.exit(0);
}

fs.writeFileSync(PENDING_PATH, JSON.stringify({ pending }, null, 2), "utf8");
process.exit(0);
