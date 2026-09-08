#!/usr/bin/env python3
"""
Entregar Peça Jurídica — Copia peça final (+ anexos) para
Desktop/Produção Jurídica, com nomenclatura sequencial correta.

Estrutura:
  Desktop/Produção Jurídica/
  └── YYYY-MM-DD/              (data da PRIMEIRA entrega do processo)
      └── <numero-processo>/
          ├── 01. <nome-peça>.docx
          ├── 01. <nome-peça>.pdf
          ├── 02. <anexo-1>.<ext>
          └── 03. <anexo-2>.<ext>

Se o processo já tem pasta (em qualquer data anterior), a entrega
CONTINUA naquela mesma pasta — não fragmenta por data.

Uso:
  python3 entregar_peca.py peca "<processo>" "<nome-peça>" "<docx>"
  python3 entregar_peca.py anexo "<processo>" "<nome-anexo>" "<arquivo>"
  python3 entregar_peca.py listar ["<processo>"]
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


DESKTOP = Path.home() / "Desktop"
PRODUCAO = DESKTOP / "Produção Jurídica"
CONVERTER = Path(__file__).resolve().parent / "converter_docx_pdf.py"


def pasta_existente_do_processo(numero_processo):
    """Procura em TODAS as pastas de data se o processo já tem pasta.
    Retorna o Path se achar, senão None."""
    if not PRODUCAO.exists():
        return None
    for data_dir in sorted(PRODUCAO.iterdir()):
        if not data_dir.is_dir():
            continue
        candidata = data_dir / numero_processo
        if candidata.is_dir():
            return candidata
    return None


def pasta_do_processo(numero_processo, criar=True):
    """Retorna a pasta do processo, reaproveitando a existente
    (de qualquer data) ou criando uma nova sob a data de hoje."""
    existente = pasta_existente_do_processo(numero_processo)
    if existente:
        return existente

    if not criar:
        return None

    hoje = datetime.now().strftime("%Y-%m-%d")
    nova = PRODUCAO / hoje / numero_processo
    nova.mkdir(parents=True, exist_ok=True)
    return nova


def proximo_sequencial(pasta):
    """Próximo número de sequência (01, 02, 03...) na pasta."""
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
    """Entrega a peça principal: sempre número 01, sempre DOCX+PDF."""
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

    return True


def entregar_anexo(numero_processo, nome_anexo, arquivo_source):
    """Entrega um anexo: próximo número livre, extensão original preservada."""
    arquivo_source = Path(arquivo_source)
    if not arquivo_source.exists():
        print(f"✗ Arquivo não encontrado: {arquivo_source}")
        return False

    pasta = pasta_do_processo(numero_processo)
    seq = proximo_sequencial(pasta)
    ext = arquivo_source.suffix
    destino = pasta / f"{seq:02d}. {nome_anexo}{ext}"

    shutil.copy(arquivo_source, destino)
    print(f"✓ Anexo: {destino}")
    return True


def listar(numero_processo=None):
    if not PRODUCAO.exists():
        print("Nenhuma produção registrada ainda.")
        return

    print(f"\n📁 {PRODUCAO}")
    for data_dir in sorted(PRODUCAO.iterdir()):
        if not data_dir.is_dir():
            continue
        for proc_dir in sorted(data_dir.iterdir()):
            if not proc_dir.is_dir():
                continue
            if numero_processo and proc_dir.name != numero_processo:
                continue
            print(f"\n  {data_dir.name}/{proc_dir.name}/")
            for arq in sorted(proc_dir.iterdir()):
                if arq.is_file():
                    kb = arq.stat().st_size / 1024
                    print(f"    📄 {arq.name}  ({kb:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="comando", required=True)

    p_peca = sub.add_parser("peca", help="Entregar peça principal (sempre 01.)")
    p_peca.add_argument("processo")
    p_peca.add_argument("nome_peca")
    p_peca.add_argument("docx")

    p_anexo = sub.add_parser("anexo", help="Entregar anexo (próximo número)")
    p_anexo.add_argument("processo")
    p_anexo.add_argument("nome_anexo")
    p_anexo.add_argument("arquivo")

    p_listar = sub.add_parser("listar", help="Listar entregas")
    p_listar.add_argument("processo", nargs="?", default=None)

    args = parser.parse_args()

    if args.comando == "peca":
        ok = entregar_peca(args.processo, args.nome_peca, args.docx)
        sys.exit(0 if ok else 1)
    elif args.comando == "anexo":
        ok = entregar_anexo(args.processo, args.nome_anexo, args.arquivo)
        sys.exit(0 if ok else 1)
    elif args.comando == "listar":
        listar(args.processo)


if __name__ == "__main__":
    main()
