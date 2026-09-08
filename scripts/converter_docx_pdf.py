#!/usr/bin/env python3
"""
Converter DOCX para PDF usando COM Windows (Word)
Fallback para exportar como PDF via Document.save()
"""
import sys
import os
from pathlib import Path

def convert_docx_to_pdf_com(docx_path, pdf_path):
    """Converter DOCX para PDF usando COM do Windows (Word)"""
    try:
        import win32com.client
        
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        # Abrir documento
        doc = word.Documents.Open(os.path.abspath(docx_path))
        
        # Salvar como PDF
        doc.SaveAs2(os.path.abspath(pdf_path), FileFormat=17)  # 17 = wdFormatPDF
        doc.Close()
        word.Quit()
        
        return True
    except Exception as e:
        print(f"[WARN] COM Word falhou: {e}")
        return False

def convert_docx_to_pdf_libreoffice(docx_path, pdf_path):
    """Converter DOCX para PDF usando LibreOffice headless"""
    import subprocess
    
    try:
        # Procurar LibreOffice em caminhos comuns
        libreoffice_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
        
        soffice = None
        for path in libreoffice_paths:
            if os.path.exists(path):
                soffice = path
                break
        
        if not soffice:
            return False
        
        # Converter
        cmd = [
            soffice,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", os.path.dirname(os.path.abspath(pdf_path)),
            os.path.abspath(docx_path)
        ]
        
        subprocess.run(cmd, check=True, timeout=120)
        return True
    except Exception as e:
        print(f"[WARN] LibreOffice falhou: {e}")
        return False

def convert_docx_to_pdf_docx2pdf(docx_path, pdf_path):
    """Converter DOCX para PDF usando docx2pdf"""
    try:
        from docx2pdf import convert
        convert(docx_path, pdf_path)
        return True
    except ImportError:
        print("[WARN] docx2pdf não instalado")
        return False
    except Exception as e:
        print(f"[WARN] docx2pdf falhou: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Uso: python converter_docx_pdf.py <docx_input> <pdf_output>")
        sys.exit(1)
    
    docx_path = sys.argv[1]
    pdf_path = sys.argv[2]
    
    if not os.path.exists(docx_path):
        print(f"[ERRO] Arquivo não encontrado: {docx_path}")
        sys.exit(1)
    
    # Tentar conversores em ordem de preferência
    methods = [
        ("COM Word", convert_docx_to_pdf_com),
        ("LibreOffice", convert_docx_to_pdf_libreoffice),
        ("docx2pdf", convert_docx_to_pdf_docx2pdf),
    ]
    
    for name, method in methods:
        print(f"Tentando {name}...", file=sys.stderr)
        if method(docx_path, pdf_path):
            if os.path.exists(pdf_path):
                print(f"[OK] PDF gerado: {pdf_path}")
                sys.exit(0)
    
    print(f"[ERRO] Nenhum conversor disponível", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
