#!/usr/bin/env python3
"""
Atalho: Formatar + Entregar em Uma Linha
Para usar quando já tem o DOCX final aprovado.

Uso:
  python3 entregar.py \\
    --docx "caminho/manifestacao_final.docx" \\
    --processo "5012964-89.2023.8.13.0035" \\
    --nome "Manifestação em Cumprimento de Sentença"
"""

import sys
import subprocess
import argparse
from pathlib import Path

def entregar_automaticamente(docx_path, processo, nome):
    """Simples: copia DOCX e converte para PDF"""
    
    print("="*70)
    print(f"ENTREGAR: {nome}")
    print("="*70)
    
    # Caminho do automatizar_peca.py
    cerebro = Path.home() / "cerebro-ricar"
    script = cerebro / "automatizar_peca.py"
    
    if not script.exists():
        print(f"✗ Script não encontrado: {script}")
        sys.exit(1)
    
    # Executar
    cmd = [
        sys.executable,
        str(script),
        "adicionar",
        processo,
        nome,
        docx_path
    ]
    
    result = subprocess.run(cmd, timeout=120)
    
    if result.returncode == 0:
        print("\n" + "="*70)
        print("✓ ENTREGUE")
        print("="*70)
        print(f"\nDesktop/Produção Jurídica/<data>/{processo}/")
        print(f"  ✓ 01. {nome}.docx")
        print(f"  ✓ 01. {nome}.pdf")
        print(f"\nPróximo: Assinar e protocolar no PJe")
    else:
        print("\n✗ Erro ao entregar")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entregar pe\u00e7a ao Desktop")
    parser.add_argument("--docx", required=True, help="Caminho do DOCX final")
    parser.add_argument("--processo", required=True, help="N\u00famero do processo")
    parser.add_argument("--nome", required=True, help="Nome da pe\u00e7a")
    
    args = parser.parse_args()
    entregar_automaticamente(args.docx, args.processo, args.nome)
