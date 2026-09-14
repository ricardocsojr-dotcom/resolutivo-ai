#!/usr/bin/env python3
"""
Motor proxy de retrocompatibilidade RDAA -> LangGraph.
Abraça as assinaturas antigas e mapeia-as para o LangGraph CLI.
"""
import sys
import json
from pathlib import Path
from copy import deepcopy

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from langgraph_engine import EngineCLI, _write_manifest

def inicializar_execucao(state_dir: str | Path, matter_id: str, piece_level: str = "B", **kwargs):
    cli = EngineCLI(str(state_dir))
    return cli._execute("start", payload={"matter_id": matter_id, "nivel_peca": piece_level})

def avancar_fase(state_dir: str | Path, phase: str, **kwargs):
    cli = EngineCLI(str(state_dir))
    return cli._execute("submit", payload={"worker_cli": "legacy-proxy"})

def registrar_execucao(state_dir: str | Path, *args, **kwargs):
    cli = EngineCLI(str(state_dir))
    cli._execute("submit", payload={"worker_cli": "legacy-proxy"})

def registrar_falha(state_dir: str | Path, phase: str, **kwargs):
    cli = EngineCLI(str(state_dir))
    cli._execute("fail")

def registrar_aprovacao(state_dir, gate, content_or_hash, approved_by="ricardo", **kwargs):
    cli = EngineCLI(str(state_dir))
    cli._execute("approve", payload={"authority": approved_by.lower()})

def decidir_disjuntor(state_dir: str | Path, action: str, authority: str, reason: str = ""):
    cli = EngineCLI(str(state_dir))
    if action == "resume":
        cli._execute("resume", payload={"authority": authority, "reason": reason})

def registrar_consulta_vault(state_dir, vault, artifact_path, **kwargs):
    _append_vault_sync(state_dir, vault, direction="read")

def registrar_sincronizacao_vault(state_dir, vault, direction, **kwargs):
    _append_vault_sync(state_dir, vault, direction)

def _append_vault_sync(state_dir, vault, direction):
    m = _read_manifest(state_dir)
    m.setdefault("vault_syncs", []).append({"vault": vault, "direction": direction})
    _write_json(Path(state_dir) / "run_manifest.json", m)

def ler_estado(state_dir):
    return EngineCLI(str(state_dir))._execute("status")

def _read_manifest(state_dir: str | Path):
    pt = Path(state_dir) / "run_manifest.json"
    if not pt.exists(): return {}
    return json.loads(pt.read_text(encoding="utf-8"))

def _write_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def validar_inicio_worker(state_dir, role, engine=""):
    """Se certifica que nao estamos iniciando work onde as maquinas barram via o CLI novo status"""
    s = EngineCLI(str(state_dir))._execute("status")
    if s.get("status") in ["blocked", "paused"]:
        raise ValueError(f"Motor bloqueado. Interrupcao: {s}")
