#!/usr/bin/env python3
"""
Formatar Peça RDAA + Entregar Automaticamente
Combina: construir_peca.py → publicar_docx.py → automatizar_peca.py
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

class PublicadorComProducao:
    def __init__(self, context_json, processo, nome_peca, tipo="peca"):
        self.context_path = Path(context_json)
        self.processo = processo
        self.nome_peca = nome_peca
        self.tipo = tipo
        
        # Caminhos base
        self.skill_formatar = Path("C:/Projetos/resolutivo-ai/skills/formatar-peca")
        self.cerebro = Path.home() / "cerebro-ricar"
        self.skill_automate = Path.home() / "AppData" / "Local" / "hermes" / "skills" / "automate-peca-producao"
        
        # Fallback para skill_automate se não existir
        if not self.skill_automate.exists():
            self.skill_automate = self.cerebro
        
        # Diretório de trabalho
        self.workdir = self.context_path.parent
    
    def validar_dependencias(self):
        """Verifica se os scripts necessários existem"""
        skill_revisor = Path("C:/Projetos/resolutivo-ai/skills/revisor-rdaa")
        
        scripts_necessarios = [
            self.skill_formatar / "scripts" / "construir_peca.py",
            skill_revisor / "scripts" / "publicar_docx.py",
            self.skill_automate / "scripts" / "automatizar_peca.py",
        ]
        
        for script in scripts_necessarios:
            if not script.exists():
                print(f"✗ Script não encontrado: {script}")
                return False
        
        if not self.context_path.exists():
            print(f"✗ Contexto JSON não encontrado: {self.context_path}")
            return False
        
        return True
    
    def etapa_1_construir_docx(self):
        """Etapa 1: Construir DOCX candidato"""
        print("\n[1/4] Construindo DOCX candidato...")
        
        docx_candidato = self.workdir / f"{self.nome_peca}_candidata.docx"
        
        cmd = [
            sys.executable,
            str(self.skill_formatar / "scripts" / "construir_peca.py"),
            "--context", str(self.context_path),
            "--output", str(docx_candidato)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"✗ Erro ao construir DOCX: {result.stderr}")
            return None
        
        print(f"✓ DOCX gerado: {docx_candidato.name}")
        return docx_candidato
    
    def etapa_2_publicar(self, docx_candidato):
        """Etapa 2: Publicar (QA + validação)"""
        print("\n[2/4] Publicando (QA + formatação)...")
        
        skill_revisor = Path("C:/Projetos/resolutivo-ai/skills/revisor-rdaa")
        
        docx_final = self.workdir / f"{self.nome_peca}_final.docx"
        qa_json = self.workdir / f"{self.nome_peca}_final.qa.json"
        
        cmd = [
            sys.executable,
            str(skill_revisor / "scripts" / "publicar_docx.py"),
            "--input", str(docx_candidato),
            "--output", str(docx_final),
            "--qa-json", str(qa_json),
            "--context", str(self.context_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"✗ Publicação falhou (QA): {result.stderr}")
            return None
        
        print(f"✓ QA passou: {docx_final.name}")
        return docx_final
    
    def etapa_3_entregar(self, docx_final):
        """Etapa 3: Entregar em Desktop/Produção"""
        print("\n[3/4] Entregando em Desktop/Produção Jurídica...")
        
        cmd = [
            sys.executable,
            str(self.skill_automate / "scripts" / "automatizar_peca.py"),
            "adicionar",
            self.processo,
            self.nome_peca,
            str(docx_final)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"✗ Erro ao entregar: {result.stderr}")
            return False
        
        print(f"✓ Entregue com sucesso")
        print(result.stdout)
        return True
    
    def etapa_4_registrar_cerebro(self):
        """Etapa 4: Registrar no cérebro"""
        print("\n[4/4] Registrando no cérebro...")
        
        # Criar ou atualizar matter_state.json
        matter_dir = self.cerebro / ".rdaa-run" / f"{self.tipo}-{self.processo.split('-')[0]}"
        matter_dir.mkdir(parents=True, exist_ok=True)
        
        matter_state_path = matter_dir / "matter_state.json"
        
        if matter_state_path.exists():
            with open(matter_state_path, 'r', encoding='utf-8') as f:
                matter_state = json.load(f)
        else:
            matter_state = {
                "processo_numero": self.processo,
                "tipo_peca": self.nome_peca,
                "status": "publicado",
                "data_criacao": datetime.now().isoformat(),
                "peca_producao": "Desktop/Produção Jurídica",
                "historico": []
            }
        
        # Atualizar histórico
        evento = {
            "data": datetime.now().isoformat(),
            "acao": "publicar",
            "peca": self.nome_peca,
            "status": "entregue"
        }
        
        if "historico" not in matter_state:
            matter_state["historico"] = []
        
        matter_state["historico"].append(evento)
        matter_state["ultima_atualizacao"] = datetime.now().isoformat()
        
        with open(matter_state_path, 'w', encoding='utf-8') as f:
            json.dump(matter_state, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Registrado: {matter_state_path}")
        return True
    
    def executar(self):
        """Executa o fluxo completo"""
        print("="*70)
        print(f"FORMATAR + ENTREGAR: {self.nome_peca}")
        print("="*70)
        
        if not self.validar_dependencias():
            print("\n✗ Dependências não encontradas")
            sys.exit(1)
        
        # Etapa 1: Construir
        docx_candidato = self.etapa_1_construir_docx()
        if not docx_candidato:
            sys.exit(1)
        
        # Etapa 2: Publicar
        docx_final = self.etapa_2_publicar(docx_candidato)
        if not docx_final:
            sys.exit(1)
        
        # Etapa 3: Entregar
        if not self.etapa_3_entregar(docx_final):
            sys.exit(1)
        
        # Etapa 4: Registrar
        if not self.etapa_4_registrar_cerebro():
            sys.exit(1)
        
        print("\n" + "="*70)
        print("✓ FLUXO COMPLETO")
        print("="*70)
        print(f"\nPeça entregue em:")
        print(f"  Desktop/Produção Jurídica/{datetime.now().strftime('%Y-%m-%d')}/{self.processo}/")
        print(f"\nArquivos:")
        print(f"  • 01. {self.nome_peca}.docx")
        print(f"  • 01. {self.nome_peca}.pdf")
        print(f"\nPróximo passo: Assinar e protocolar no PJe")

def main():
    parser = argparse.ArgumentParser(
        description="Formatar peça RDAA e entregar automaticamente"
    )
    parser.add_argument("--context", required=True, help="Caminho do rdaa_context.json")
    parser.add_argument("--processo", required=True, help="Número do processo (ex: 5012964-89.2023.8.13.0035)")
    parser.add_argument("--nome-peca", required=True, help="Nome da peça (ex: Manifestação)")
    parser.add_argument("--tipo", default="peca", help="Tipo (peca, manifestacao, etc)")
    
    args = parser.parse_args()
    
    publicador = PublicadorComProducao(
        context_json=args.context,
        processo=args.processo,
        nome_peca=args.nome_peca,
        tipo=args.tipo
    )
    
    publicador.executar()

if __name__ == "__main__":
    main()
