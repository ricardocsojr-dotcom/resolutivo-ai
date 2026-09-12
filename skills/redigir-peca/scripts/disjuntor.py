#!/usr/bin/env python3
import json
import sys
import argparse
from pathlib import Path

def get_matter_state_path(processo):
    candidates = [
        Path.home() / "Resolutivo-Dados" / processo / "matter_state.json",
        Path.home() / "Resolutivo-Dados" / ".rdaa-run" / processo / "matter_state.json",
        Path.home() / "Desktop" / ".rdaa-run" / processo / "matter_state.json",
        Path.cwd() / ".rdaa-run" / processo / "matter_state.json"
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

def record_failure(processo, node_name):
    state_file = get_matter_state_path(processo)
    if not state_file:
        print(f"Erro: matter_state.json não encontrado para {processo}. Falha crítica.")
        return 1

    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)

    if 'disjuntor' not in state:
        state['disjuntor'] = {}
        
    failures = state['disjuntor'].get(node_name, 0)
    failures += 1
    state['disjuntor'][node_name] = failures
    
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        
    print(f"[{node_name}] Falha #{failures} registrada.")

    if failures >= 3:
        state['status'] = 'paralisado'
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"DISJUNTOR ACIONADO: O nó {node_name} falhou 3 vezes.")
        print(f"MATÉRIA {processo} PARALISADA. Intervenção humana necessária.")
        # Pode escalar via notificação ou stdout
        sys.exit(1)
        
    return 0

def reset_node(processo, node_name):
    state_file = get_matter_state_path(processo)
    if not state_file: return
    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)
    if 'disjuntor' in state and node_name in state['disjuntor']:
        state['disjuntor'][node_name] = 0
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("processo")
    parser.add_argument("node_name")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    
    if args.reset:
        reset_node(args.processo, args.node_name)
    else:
        sys.exit(record_failure(args.processo, args.node_name))

if __name__ == "__main__":
    main()

def exigir_liberado(manifest):
    if manifest.get('status') == 'paralisado':
        raise ValueError("Operação negada: matéria paralisada pelo disjuntor.")
    return True
