#!/usr/bin/env python3
"""
Gestor de Versões de Peças — Preserva formatação e permite iterar
Mantém histórico completo e permite voltar a versões anteriores
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from docx import Document

class GestorVersoesPeca:
    def __init__(self, processo, nome_peca):
        self.processo = processo
        self.nome_peca = nome_peca
        self.cerebro = Path.home() / "cerebro-ricar"
        
        # Diretório de versões
        self.dir_versoes = self.cerebro / ".rdaa-versoes" / processo / nome_peca
        self.dir_versoes.mkdir(parents=True, exist_ok=True)
        
        # Arquivo de histórico
        self.historico_path = self.dir_versoes / "historico.json"
    
    def carregar_historico(self):
        """Carrega o histórico de versões"""
        if self.historico_path.exists():
            with open(self.historico_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "processo": self.processo,
            "peca": self.nome_peca,
            "criada": datetime.now().isoformat(),
            "versoes": []
        }
    
    def salvar_versao(self, docx_path, motivo="Correção", tags=None):
        """
        Salva uma nova versão do DOCX
        Args:
            docx_path: caminho do DOCX a ser versionado
            motivo: descrição da mudança (ex: "Formatação", "Correção jurídica")
            tags: lista de tags (ex: ["negrito-parágrafo-5", "print-corrigido"])
        """
        historico = self.carregar_historico()
        
        # Número da próxima versão
        num_versao = len(historico["versoes"]) + 1
        
        # Copiar DOCX para arquivo versionado
        nome_arquivo = f"v{num_versao:03d}_{self.nome_peca}.docx"
        docx_versionado = self.dir_versoes / nome_arquivo
        
        if not Path(docx_path).exists():
            print(f"✗ Arquivo não encontrado: {docx_path}")
            return None
        
        shutil.copy(docx_path, docx_versionado)
        
        # Extrair informações do DOCX
        try:
            doc = Document(docx_versionado)
            num_paragrafos = len(doc.paragraphs)
            num_tabelas = len(doc.tables)
        except:
            num_paragrafos = 0
            num_tabelas = 0
        
        # Registrar versão no histórico
        versao = {
            "numero": num_versao,
            "data": datetime.now().isoformat(),
            "motivo": motivo,
            "tags": tags or [],
            "arquivo": nome_arquivo,
            "tamanho_kb": docx_versionado.stat().st_size / 1024,
            "paragrafos": num_paragrafos,
            "tabelas": num_tabelas,
            "ativo": True  # Última versão é a ativa
        }
        
        # Desativar versão anterior se houver
        for v in historico["versoes"]:
            v["ativo"] = False
        
        historico["versoes"].append(versao)
        historico["ultima_atualizacao"] = datetime.now().isoformat()
        
        # Salvar histórico
        with open(self.historico_path, 'w', encoding='utf-8') as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Versão {num_versao} salva: {nome_arquivo}")
        return {
            "versao": num_versao,
            "arquivo": docx_versionado,
            "motivo": motivo
        }
    
    def carregar_versao(self, numero_versao=None):
        """
        Carrega uma versão anterior
        Se numero_versao for None, carrega a última
        """
        historico = self.carregar_historico()
        
        if not historico["versoes"]:
            print("✗ Nenhuma versão encontrada")
            return None
        
        if numero_versao is None:
            versao = historico["versoes"][-1]
        else:
            versao = next((v for v in historico["versoes"] if v["numero"] == numero_versao), None)
            if not versao:
                print(f"✗ Versão {numero_versao} não encontrada")
                return None
        
        arquivo = self.dir_versoes / versao["arquivo"]
        
        if not arquivo.exists():
            print(f"✗ Arquivo de versão não encontrado: {arquivo}")
            return None
        
        print(f"✓ Versão {versao['numero']} carregada ({versao['motivo']})")
        return arquivo
    
    def listar_versoes(self):
        """Lista todas as versões com seus detalhes"""
        historico = self.carregar_historico()
        
        print(f"\n{'='*80}")
        print(f"HISTÓRICO: {self.nome_peca}")
        print(f"Processo: {self.processo}")
        print(f"{'='*80}")
        
        if not historico["versoes"]:
            print("Nenhuma versão registrada")
            return
        
        for v in historico["versoes"]:
            ativo = "✓ ATIVA" if v["ativo"] else "  "
            tags_str = ", ".join(v["tags"]) if v["tags"] else "-"
            
            print(f"\nV{v['numero']:03d} {ativo}")
            print(f"  Data: {v['data']}")
            print(f"  Motivo: {v['motivo']}")
            print(f"  Tags: {tags_str}")
            print(f"  Arquivo: {v['arquivo']}")
            print(f"  Tamanho: {v['tamanho_kb']:.1f} KB")
            print(f"  Parágrafos: {v['paragrafos']}, Tabelas: {v['tabelas']}")
    
    def comparar_versoes(self, v1, v2=None):
        """
        Compara duas versões
        Se v2 for None, compara a v1 com a última
        """
        if v2 is None:
            historico = self.carregar_historico()
            v2 = historico["versoes"][-1]["numero"] if historico["versoes"] else None
        
        historico = self.carregar_historico()
        versao1 = next((v for v in historico["versoes"] if v["numero"] == v1), None)
        versao2 = next((v for v in historico["versoes"] if v["numero"] == v2), None)
        
        if not versao1 or not versao2:
            print("✗ Uma ou ambas as versões não encontradas")
            return
        
        print(f"\n{'='*80}")
        print(f"COMPARAÇÃO: V{v1} vs V{v2}")
        print(f"{'='*80}")
        
        print(f"\nV{v1} ({versao1['motivo']})")
        print(f"  Data: {versao1['data']}")
        print(f"  Tamanho: {versao1['tamanho_kb']:.1f} KB")
        print(f"  Parágrafos: {versao1['paragrafos']}")
        
        print(f"\nV{v2} ({versao2['motivo']})")
        print(f"  Data: {versao2['data']}")
        print(f"  Tamanho: {versao2['tamanho_kb']:.1f} KB")
        print(f"  Parágrafos: {versao2['paragrafos']}")
        
        # Diferenças
        diff_tamanho = versao2['tamanho_kb'] - versao1['tamanho_kb']
        diff_paragrafos = versao2['paragrafos'] - versao1['paragrafos']
        
        print(f"\nDiferenças:")
        print(f"  Tamanho: {diff_tamanho:+.1f} KB")
        print(f"  Parágrafos: {diff_paragrafos:+d}")
    
    def criar_backup(self):
        """Cria backup de todas as versões"""
        backup_dir = self.dir_versoes / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copiar todos os arquivos
        for arquivo in self.dir_versoes.glob("*.docx"):
            shutil.copy(arquivo, backup_dir)
        
        # Copiar histórico
        shutil.copy(self.historico_path, backup_dir)
        
        print(f"✓ Backup criado: {backup_dir}")
        return backup_dir

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestor de versões de peças jurídicas")
    parser.add_argument("--processo", required=True, help="Número do processo")
    parser.add_argument("--peca", required=True, help="Nome da peça")
    
    subparsers = parser.add_subparsers(dest="comando", help="Comando")
    
    # Comando: salvar
    save_parser = subparsers.add_parser("salvar", help="Salvar nova versão")
    save_parser.add_argument("docx", help="Caminho do DOCX")
    save_parser.add_argument("--motivo", default="Atualização", help="Motivo da mudança")
    save_parser.add_argument("--tags", nargs="+", help="Tags (ex: negrito print)")
    
    # Comando: carregar
    load_parser = subparsers.add_parser("carregar", help="Carregar versão")
    load_parser.add_argument("--numero", type=int, help="Número da versão (default: última)")
    load_parser.add_argument("--para", help="Salvar em (default: stdout)")
    
    # Comando: listar
    subparsers.add_parser("listar", help="Listar versões")
    
    # Comando: comparar
    comp_parser = subparsers.add_parser("comparar", help="Comparar versões")
    comp_parser.add_argument("v1", type=int, help="Versão 1")
    comp_parser.add_argument("v2", nargs="?", type=int, help="Versão 2 (default: última)")
    
    # Comando: backup
    subparsers.add_parser("backup", help="Criar backup")
    
    args = parser.parse_args()
    
    gestor = GestorVersoesPeca(args.processo, args.peca)
    
    if args.comando == "salvar":
        result = gestor.salvar_versao(
            args.docx,
            motivo=args.motivo,
            tags=args.tags
        )
        if result:
            print(f"\n✓ Pronto para continuar da versão {result['versao']}")
    
    elif args.comando == "carregar":
        arquivo = gestor.carregar_versao(args.numero)
        if arquivo:
            if args.para:
                shutil.copy(arquivo, args.para)
                print(f"✓ Copiado para: {args.para}")
            else:
                print(f"✓ Arquivo: {arquivo}")
    
    elif args.comando == "listar":
        gestor.listar_versoes()
    
    elif args.comando == "comparar":
        gestor.comparar_versoes(args.v1, args.v2)
    
    elif args.comando == "backup":
        gestor.criar_backup()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
