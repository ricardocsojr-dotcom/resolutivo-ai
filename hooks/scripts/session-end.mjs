#!/usr/bin/env node
// Rede de seguranca do SessionEnd: anota as materias PUBLICADAS que ainda nao
// tem registro confirmado no Cerebro-Ricar, pra que o SessionStart da proxima
// sessao cobre o passo 10 de redigir-peca/SKILL.md. Sem isso, o registro so
// aconteceria se alguem lembrasse de pedir, que e exatamente o problema que
// motivou essa automacao.
//
// Correcao 2026-09-11 (bug real): o criterio antigo era `manifest.vault_synced_at`,
// um campo que NENHUM script do repo escreve — nem registrar_cerebro.py, nem
// orquestrador_rdaa.py, que gravam o recibo em `vault.syncs[]`. Consequencia
// dupla: (a) materia efetivamente sincronizada continuava listada como pendente
// pra sempre, e (b) como toda materia aparecia, o aviso virou ruido de fundo e
// parou de ser lido — que e como uma publicacao real ficou sem registro sem
// ninguem notar. O criterio agora e o MESMO do gate `vault_registered` do
// orquestrador: recibo em `vault.syncs[]` com status "registered". Se os dois
// criterios divergirem de novo, o alarme volta a mentir.
//
// Alem disso, so materia em `phase: "published"` entra na lista. Antes da
// publicacao nao existe nada a registrar no Cerebro, entao sinalizar rascunho
// como "pendente de sincronizacao" e falso positivo por construcao.
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

// Mesmo criterio do gate `vault_registered` em orquestrador_rdaa.py: vale o
// recibo gravado em vault.syncs[] com status "registered". O hook nao revalida
// o hash do artefato (isso e responsabilidade do gate, que falha fechado); aqui
// basta saber se ha registro pra decidir se cobra ou nao.
function temRegistroNoCerebro(manifest) {
  const syncs = manifest?.vault?.syncs;
  if (!Array.isArray(syncs)) return false;
  return syncs.some(
    (item) => item?.status === "registered" && item?.vault === "cerebro-ricar",
  );
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
  const manifestPath = path.join(RUN_DIR, matterId, "run_manifest.json");
  const manifest = readJson(manifestPath, null);
  if (!manifest) continue;
  if (manifest.phase !== "published") continue; // nada a registrar antes de publicar
  if (temRegistroNoCerebro(manifest)) continue; // ja sincronizado
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
