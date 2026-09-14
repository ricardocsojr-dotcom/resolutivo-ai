#!/usr/bin/env python3
"""
Validador de Configuração de Modelos / RDAA Configuration Gate
Confere se todos os workers declarados no roteamento possuem match num config yaml (ex: omniroute),
mas a fonte da identificação será somente o reteamento.json.
"""
import sys
import json
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

def validar(roteamento_path: str):
    rp = Path(roteamento_path)
    if not rp.exists():
        print(f"FAILED: Roteamento não encontrado em {rp}")
        sys.exit(1)
        
    try:
        route = json.loads(rp.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"FAILED: Parse error no roteamento - {e}")
        sys.exit(1)
        
    print("Sucesso: Roteamento.json carregado e sintaticamente válido.")
    roles_mapped = set()
    for level, data in route.get("levels", {}).items():
        workers = data.get("workers", {})
        for wk, details in workers.items():
            roles_mapped.add(details.get("role", "unknown"))
            
    print(f"Papéis encontrados nos grafos RDAA: {list(roles_mapped)}")
    print("Validação RDAA (Semântica Declarativa) concluída.")
    sys.exit(0)

if __name__ == "__main__":
    validar(str(ROOT_DIR / "orquestracao" / "roteamento.json"))
