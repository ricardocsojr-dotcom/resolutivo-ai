#!/usr/bin/env python3
"""
Automação: RDAA Peça → Produção Jurídica (Desktop)
Estrutura:
  Desktop/Produção Jurídica/
  └── YYYY-MM-DD/
      └── <processo>/
          ├── 01. <nome-peça>.docx
          ├── 01. <nome-peça>.pdf
          ├── 02. <anexo-1>.pdf
          └── ...
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
import subprocess

class AutomacaoPecaJuridica:
    def __init__(self):
        self.desktop = Path.home() / "Desktop"
        self.producao_juridica = self.desktop / "Produção Jurídica"
        self.hoje = datetime.now().strftime("%Y-%m-%d")
        self.converter_script = Path.home() / "cerebro-ricar" / "converter_docx_pdf.py"
    
    def criar_estrutura(self, numero_processo):
        """Cria a estrutura de pastas para a data e processo"""
        pasta_processo = self.producao_juridica / self.hoje / numero_processo
        pasta_processo.mkdir(parents=True, exist_ok=True)
        return pasta_processo
    
    def adicionar_peca(self, numero_processo, nome_peca, docx_source, tipo="word"):
        """
        Adiciona uma peça jurídica (DOCX → PDF).
        Args:
            numero_processo: "5012964-89.2023.8.13.0035"
            nome_peca: "Manifestação em Cumprimento de Sentença"
            docx_source: caminho do DOCX de origem
            tipo: "word" (padrão) para converter DOCX→PDF
        """
        pasta_processo = self.criar_estrutura(numero_processo)
        
        # Descobrir o número sequencial
        sequencial = self._proximo_sequencial(pasta_processo)
        
        nome_arquivo = f"{sequencial:02d}. {nome_peca}"
        docx_destino = pasta_processo / f"{nome_arquivo}.docx"
        pdf_destino = pasta_processo / f"{nome_arquivo}.pdf"
        
        # Copiar DOCX
        if os.path.exists(docx_source):
            shutil.copy(docx_source, docx_destino)
            print(f"✓ DOCX: {docx_destino.name}")
        else:
            print(f"✗ DOCX não encontrado: {docx_source}")
            return False
        
        # Converter para PDF
        if tipo == "word":
            success = self._converter_docx_pdf(docx_destino, pdf_destino)
            if success:
                print(f"✓ PDF: {pdf_destino.name}")
            else:
                print(f"⚠ PDF não foi gerado")
                return False
        
        return True
    
    def adicionar_anexo(self, numero_processo, nome_anexo, arquivo_source):
        """
        Adiciona um anexo à pasta do processo.
        Args:
            numero_processo: "5012964-89.2023.8.13.0035"
            nome_anexo: "Cálculo Atualizado"
            arquivo_source: caminho do arquivo (qualquer tipo)
        """
        pasta_processo = self.criar_estrutura(numero_processo)
        
        # Descobrir o número sequencial
        sequencial = self._proximo_sequencial(pasta_processo)
        
        # Preservar extensão
        ext = Path(arquivo_source).suffix
        nome_arquivo = f"{sequencial:02d}. {nome_anexo}{ext}"
        arquivo_destino = pasta_processo / nome_arquivo
        
        if os.path.exists(arquivo_source):
            shutil.copy(arquivo_source, arquivo_destino)
            print(f"✓ Anexo: {arquivo_destino.name}")
            return True
        else:
            print(f"✗ Arquivo não encontrado: {arquivo_source}")
            return False
    
    def _proximo_sequencial(self, pasta_processo):
        """Retorna o próximo número sequencial de arquivo"""
        if not pasta_processo.exists():
            return 1
        
        arquivos = list(pasta_processo.glob("[0-9][0-9].*"))
        if not arquivos:
            return 1
        
        maximos = []
        for arq in arquivos:
            try:
                num = int(arq.name.split(".")[0])
                maximos.append(num)
            except:
                pass
        
        return max(maximos) + 1 if maximos else 1
    
    def _converter_docx_pdf(self, docx_path, pdf_path):
        """Converte DOCX para PDF usando o script conversor"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.converter_script), str(docx_path), str(pdf_path)],
                timeout=120,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and os.path.exists(pdf_path):
                return True
            else:
                print(f"⚠ Erro na conversão: {result.stderr}")
                return False
        except Exception as e:
            print(f"⚠ Exceção: {e}")
            return False
    
    def listar_producao(self):
        """Lista a estrutura atual de produção"""
        if not self.producao_juridica.exists():
            print("Nenhuma produção registrada")
            return
        
        print(f"\n📁 {self.producao_juridica.name}/")
        for data_dir in sorted(self.producao_juridica.iterdir()):
            if data_dir.is_dir():
                print(f"   └── {data_dir.name}/")
                for processo_dir in sorted(data_dir.iterdir()):
                    if processo_dir.is_dir():
                        print(f"       └── {processo_dir.name}/")
                        for arquivo in sorted(processo_dir.iterdir()):
                            print(f"           📄 {arquivo.name}")

def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 automatizar_peca.py listar")
        print("  python3 automatizar_peca.py adicionar <numero_processo> <nome_peca> <docx_source>")
        print("  python3 automatizar_peca.py anexo <numero_processo> <nome_anexo> <arquivo_source>")
        sys.exit(1)
    
    automatizacao = AutomacaoPecaJuridica()
    
    comando = sys.argv[1].lower()
    
    if comando == "listar":
        automatizacao.listar_producao()
    
    elif comando == "adicionar":
        if len(sys.argv) < 5:
            print("Erro: Faltam argumentos")
            sys.exit(1)
        numero_processo = sys.argv[2]
        nome_peca = sys.argv[3]
        docx_source = sys.argv[4]
        
        print(f"Adicionando peça: {nome_peca}")
        if automatizacao.adicionar_peca(numero_processo, nome_peca, docx_source):
            print(f"✓ Peça adicionada com sucesso")
        else:
            print(f"✗ Erro ao adicionar peça")
            sys.exit(1)
    
    elif comando == "anexo":
        if len(sys.argv) < 5:
            print("Erro: Faltam argumentos")
            sys.exit(1)
        numero_processo = sys.argv[2]
        nome_anexo = sys.argv[3]
        arquivo_source = sys.argv[4]
        
        print(f"Adicionando anexo: {nome_anexo}")
        if automatizacao.adicionar_anexo(numero_processo, nome_anexo, arquivo_source):
            print(f"✓ Anexo adicionado com sucesso")
        else:
            print(f"✗ Erro ao adicionar anexo")
            sys.exit(1)
    
    else:
        print(f"Comando desconhecido: {comando}")
        sys.exit(1)

if __name__ == "__main__":
    main()
