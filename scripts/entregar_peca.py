#!/usr/bin/env python3
"""
Entregar Peça Jurídica — Copia peça final (+ anexos) para
Desktop/Produção Jurídica, com nomenclatura sequencial correta.
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

DESKTOP = Path.home() / "Desktop"
TEMP = Path.home() / "Resolutivo-Dados"
PRODUCAO = DESKTOP / "Produção Jurídica"
CONVERTER = Path(__file__).resolve().parent / "converter_docx_pdf.py"

def pasta_do_processo(numero_processo):
    hoje = datetime.now().strftime("%Y-%m-%d")
    pasta = PRODUCAO / hoje / numero_processo
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta

def proximo_sequencial(pasta):
    if not pasta.exists():
        return 1
    numeros = []
    for arq in pasta.iterdir():
        if arq.is_file():
            prefixo = arq.name.split(".", 1)[0].strip()
            if prefixo.isdigit():
                numeros.append(int(prefixo))
    return max(numeros) + 1 if numeros else 1

def converter_para_pdf(docx_path, pdf_path):
    if not CONVERTER.exists():
        print(f"⚠ Conversor não encontrado: {CONVERTER}")
        return False
    result = subprocess.run(
        [sys.executable, str(CONVERTER), str(docx_path), str(pdf_path)],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode == 0 and pdf_path.exists():
        return True
    print(f"⚠ Falha na conversão: {result.stderr or result.stdout}")
    return False

def entregar_peca(numero_processo, nome_peca, docx_source):
    docx_source = Path(docx_source)
    if not docx_source.exists():
        print(f"✗ DOCX não encontrado: {docx_source}")
        return False

    pasta = pasta_do_processo(numero_processo)

    docx_destino = pasta / f"01. {nome_peca}.docx"
    pdf_destino = pasta / f"01. {nome_peca}.pdf"

    shutil.copy(docx_source, docx_destino)
    print(f"✓ DOCX: {docx_destino}")
    
    if converter_para_pdf(docx_destino, pdf_destino):
        print(f"✓ PDF:  {pdf_destino}")
    else:
        print(f"⚠ PDF não gerado — DOCX está entregue, converta manualmente")

    # Copiar anexos do Temp (Resolutivo-Dados ou .rdaa-run/processo)
    temp_proc_dirs = [
        TEMP / numero_processo,
        TEMP / ".rdaa-run" / numero_processo,
        DESKTOP / ".rdaa-run" / numero_processo,
        Path.cwd() / ".rdaa-run" / numero_processo,
    ]
    
    for temp_proc_dir in temp_proc_dirs:
        if temp_proc_dir.exists():
            search_dirs = [temp_proc_dir / "anexos", temp_proc_dir]
            for src_dir in search_dirs:
                if not src_dir.exists():
                    continue
                for arquivo in sorted(src_dir.iterdir()):
                    if arquivo.is_file() and arquivo.suffix.lower() not in ('.docx', '.json', '.jsonl'):
                        seq = proximo_sequencial(pasta)
                        nome_anexo = arquivo.stem
                        destino = pasta / f"{seq:02d}. {nome_anexo}{arquivo.suffix}"
                        if not destino.exists():
                            shutil.copy(arquivo, destino)
                            print(f"✓ Anexo puxado do Temp: {destino}")
                break
            break
            
    return True

def entregar_peca_adicional(numero_processo, nome_peca, docx_source):
    docx_source = Path(docx_source)
    if not docx_source.exists():
        return False
    pasta = pasta_do_processo(numero_processo)
    seq = proximo_sequencial(pasta)
    docx_destino = pasta / f"{seq:02d}. {nome_peca}.docx"
    pdf_destino = pasta / f"{seq:02d}. {nome_peca}.pdf"
    shutil.copy(docx_source, docx_destino)
    converter_para_pdf(docx_destino, pdf_destino)
    return True

def entregar_anexo(numero_processo, nome_anexo, arquivo_source):
    arquivo_source = Path(arquivo_source)
    if not arquivo_source.exists():
        return False
    pasta = pasta_do_processo(numero_processo)
    seq = proximo_sequencial(pasta)
    destino = pasta / f"{seq:02d}. {nome_anexo}{arquivo_source.suffix}"
    shutil.copy(arquivo_source, destino)
    return True

def listar(numero_processo=None):
    if not PRODUCAO.exists():
        return
    for data_dir in sorted(PRODUCAO.iterdir()):
        if not data_dir.is_dir(): continue
        for proc_dir in sorted(data_dir.iterdir()):
            if not proc_dir.is_dir(): continue
            if numero_processo and proc_dir.name != numero_processo: continue
            print(f"{data_dir.name}/{proc_dir.name}/")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="comando", required=True)

    p_peca = sub.add_parser("peca", help="Entregar peça principal + puxar anexos (sempre 01.)")
    p_peca.add_argument("processo")
    p_peca.add_argument("nome_peca")
    p_peca.add_argument("docx")
    
    p_adi = sub.add_parser("peca-adicional", help="Entregar peça adicional")
    p_adi.add_argument("processo")
    p_adi.add_argument("nome_peca")
    p_adi.add_argument("docx")
    
    p_anex = sub.add_parser("anexo", help="Entregar anexo individualmente")
    p_anex.add_argument("processo")
    p_anex.add_argument("nome_anexo")
    p_anex.add_argument("arquivo")
    
    p_list = sub.add_parser("listar", help="Listar entregas")
    p_list.add_argument("processo", nargs="?", default=None)

    args = parser.parse_args()

    if args.comando == "peca":
        sys.exit(0 if entregar_peca(args.processo, args.nome_peca, args.docx) else 1)
    elif args.comando == "peca-adicional":
        sys.exit(0 if entregar_peca_adicional(args.processo, args.nome_peca, args.docx) else 1)
    elif args.comando == "anexo":
        sys.exit(0 if entregar_anexo(args.processo, args.nome_anexo, args.arquivo) else 1)
    elif args.comando == "listar":
        listar(args.processo)

if __name__ == "__main__":
    main()
