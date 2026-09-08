#!/usr/bin/env python3
"""Iterador Rápido de Peças RDAA.

Permite aplicar ajustes pontuais de texto, endereçamento ou signatários em uma matéria,
recompilar o DOCX nativo pelo pipeline protegido e atualizar o PDF no Desktop em 2 segundos.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
CONSTRUIR = ROOT / "skills" / "formatar-peca" / "scripts" / "construir_peca.py"
PUBLICAR = ROOT / "skills" / "revisor-rdaa" / "scripts" / "publicar_docx.py"
ENTREGAR = ROOT / "scripts" / "entregar_peca.py"


def iterar(
    state_dir: Path,
    *,
    enderecamento: str | None = None,
    find: str | None = None,
    replace: str | None = None,
    processo: str | None = None,
    nome_peca: str | None = None,
    adicional: bool = False,
) -> int:
    state_dir = Path(state_dir).resolve()
    
    # Localiza o arquivo de contexto
    ctx_path = None
    for cand in [state_dir / "CONTEXTO-PECA.json", state_dir / "contexto_peca.json", state_dir / "contexto.json"]:
        if cand.is_file():
            ctx_path = cand
            break
            
    if not ctx_path:
        print(f"[ERRO] Nenhum arquivo de contexto JSON encontrado em {state_dir}", file=sys.stderr)
        return 1
        
    ctx = json.loads(ctx_path.read_text(encoding="utf-8"))
    
    # 1. Aplica modificações
    modificado = False
    if enderecamento:
        ctx["enderecamento"] = enderecamento.strip()
        modificado = True
        print(f"✓ Endereçamento atualizado: {ctx['enderecamento']}")
        
    if find and replace is not None:
        def _replace_in_obj(obj):
            if isinstance(obj, str):
                return obj.replace(find, replace)
            elif isinstance(obj, list):
                return [_replace_in_obj(x) for x in obj]
            elif isinstance(obj, dict):
                return {k: _replace_in_obj(v) for k, v in obj.items()}
            return obj
            
        ctx = _replace_in_obj(ctx)
        modificado = True
        print(f"✓ Substituído: {find!r} -> {replace!r}")
        
    # Garante fechamento em Uberlândia
    hoje = datetime.now()
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    ctx["data_local"] = f"Uberlândia/MG, {hoje.day} de {meses[hoje.month - 1]} de {hoje.year}."
    
    ctx_path.write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    
    # 2. Gera candidato DOCX
    candidato = state_dir / "CANDIDATA.docx"
    cmd_build = [sys.executable, str(CONSTRUIR), "--context", str(ctx_path), "--output", str(candidato)]
    res_build = subprocess.run(cmd_build, capture_output=True, text=True)
    if res_build.returncode != 0:
        print(f"[ERRO] Falha ao construir DOCX candidato:\n{res_build.stderr or res_build.stdout}", file=sys.stderr)
        return 1
    print(f"✓ Candidato DOCX gerado: {candidato}")
    
    # 3. Publica via publicação protegida
    doc_final = state_dir / f"{ctx.get('matter_id', 'peca')}.docx"
    qa_json = state_dir / f"{ctx.get('matter_id', 'peca')}.qa.json"
    cmd_pub = [
        sys.executable, str(PUBLICAR),
        "--input", str(candidato),
        "--output", str(doc_final),
        "--qa-json", str(qa_json),
        "--state-dir", str(state_dir),
        "--context", str(ctx_path)
    ]
    res_pub = subprocess.run(cmd_pub, capture_output=True, text=True)
    if res_pub.returncode != 0:
        print(f"[ERRO] Falha no QA / Publicação protegida:\n{res_pub.stderr or res_pub.stdout}", file=sys.stderr)
        return 1
    print(f"✓ DOCX publicado após QA: {doc_final}")
    
    # 4. Entrega no Desktop se solicitado ou se número do processo estiver presente
    num_proc = processo or ctx.get("numero_processo")
    if num_proc and nome_peca:
        cmd_entregar = [
            sys.executable, str(ENTREGAR),
            "peca-adicional" if adicional else "peca",
            num_proc,
            nome_peca,
            str(doc_final)
        ]
        res_entregar = subprocess.run(cmd_entregar, capture_output=True, text=True)
        if res_entregar.returncode == 0:
            print(f"✓ DOCX e PDF sincronizados no Desktop para {num_proc}")
            print(res_entregar.stdout.strip())
        else:
            print(f"⚠ Aviso na entrega ao Desktop:\n{res_entregar.stderr or res_entregar.stdout}")
            
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Iterador Rápido de Peças RDAA")
    parser.add_argument("state_dir", type=Path, help="Pasta .rdaa-run/<matter_id>")
    parser.add_argument("--set-enderecamento", help="Novo texto de endereçamento")
    parser.add_argument("--find", help="Texto a buscar")
    parser.add_argument("--replace", help="Texto de substituição")
    parser.add_argument("--processo", help="Número do processo para entrega no Desktop")
    parser.add_argument("--nome-peca", help="Nome da peça para entrega (ex: 'Pedido de Esclarecimentos')")
    parser.add_argument("--adicional", action="store_true", help="Usa peca-adicional em vez de 01. peca")
    
    args = parser.parse_args()
    return iterar(
        args.state_dir,
        enderecamento=args.set_enderecamento,
        find=args.find,
        replace=args.replace,
        processo=args.processo,
        nome_peca=args.nome_peca,
        adicional=args.adicional,
    )


if __name__ == "__main__":
    raise SystemExit(main())
