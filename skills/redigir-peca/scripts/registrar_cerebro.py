#!/usr/bin/env python3
"""Grava automaticamente matéria no cérebro-ricar após publicação.

Executado pelo orquestrador após `publicar_docx.py` retornar [OK].
Lê contexto_peca.json, cria/atualiza wiki/operacional/matter-XXX.md,
atualiza index.json e hot.md.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CEREBRO_PATH = "C:\\Users\\ricar\\cerebro-ricar"
CEREBRO = Path(CEREBRO_PATH)
WIKI_OPERACIONAL = CEREBRO / "wiki" / "operacional"


def _now() -> str:
    """ISO 8601 com Z."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalizar_process_number(num: str) -> str:
    """0130354-80.2018.8.13.0702 → 0130354-80-2018-8-13-0702 (seguro pra filename)."""
    return re.sub(r"[./]", "-", num.strip())


def carregar_contexto(path: Path) -> dict[str, Any]:
    """Lê contexto_peca.json."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"contexto inválido: {path}") from e


def gerar_frontmatter(ctx: dict[str, Any], matter_id: str, level: str) -> str:
    """Monta YAML frontmatter."""
    partes = ctx.get("partes", {})
    cliente = partes.get("autor", {}).get("nome", "Desconhecido")
    titulo = ctx.get("titulo_peca", "Sem título").replace('"', '\\"')
    
    frontmatter_text = (
        "---\n"
        'type: matter\n'
        f'title: "{titulo}"\n'
        f'matter_id: {matter_id}\n'
        f'process_number: {ctx.get("numero_processo", "N/A")}\n'
        f'client: {cliente}\n'
        f'level: {level}\n'
        f'status: published\n'
        f'created: {_now()}\n'
        f'updated: {_now()}\n'
        "---\n"
    )
    return frontmatter_text


def gerar_conteudo(ctx: dict[str, Any]) -> str:
    """Monta conteúdo do arquivo."""
    titulo = ctx.get("titulo_peca", "Peça sem título")
    tipo = ctx.get("tipo_peca", "Desconhecido")
    nivel = ctx.get("nivel_peca", "?")
    processo = ctx.get("numero_processo", "N/A")
    
    partes = ctx.get("partes", {})
    autor = partes.get("autor", {})
    reu = partes.get("reu", {})
    
    linhas = [
        f"## {titulo}",
        "",
        f"**Tipo:** {tipo} | **Nível:** {nivel} | **Processo:** {processo}",
        "",
        "### Partes",
        f"- **Autor:** {autor.get('nome', 'Desconhecido')} ({autor.get('qualificacao', 'N/A')})",
        f"- **Réu:** {reu.get('nome', 'Desconhecido')} ({reu.get('qualificacao', 'N/A')})",
        "",
        "### Pedidos",
    ]
    
    pedidos = ctx.get("pedidos", {})
    if isinstance(pedidos, dict):
        for tipo_pedido, desc in pedidos.items():
            linhas.append(f"- {tipo_pedido}: {desc}")
    elif isinstance(pedidos, list):
        for p in pedidos:
            linhas.append(f"- {p}")
    
    linhas.extend([
        "",
        "### Fundamentos",
        "- (vide documento publicado)",
        "",
        "### Status",
        f"- Publicado em: {_now()}",
        "- Estado: Aguardando registro no vault operacional",
        "",
        "*Criado automaticamente pelo Hermes após publicação.*"
    ])
    
    return "\n".join(linhas)


def atualizar_index(matter_id: str) -> None:
    """Recount e atualiza index.json."""
    index_path = CEREBRO / "index.json"
    
    stats = {}
    for tipo in ["domains", "concepts", "sources", "entities", "operacional", "pessoal"]:
        pasta = CEREBRO / "wiki" / tipo
        if pasta.exists():
            count = len([f for f in pasta.glob("*.md") if f.name != "_index.md"])
            stats[tipo] = count
    
    index = {
        "generated_at": _now(),
        "cerebro_path": CEREBRO_PATH,
        "stats": {
            "domains": stats.get("domains", 0),
            "concepts": stats.get("concepts", 0),
            "sources": stats.get("sources", 0),
            "entities": stats.get("entities", 0),
            "matters": stats.get("operacional", 0),
            "personal": stats.get("pessoal", 0),
            "total": sum(stats.values())
        },
        "last_matter_updated": matter_id,
        "last_updated": _now()
    }
    
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def atualizar_hot(ctx: dict[str, Any], matter_id: str) -> None:
    """Atualiza hot.md com a matéria nova."""
    hot_path = CEREBRO / "hot.md"
    
    titulo = ctx.get("titulo_peca", "Sem título")
    tipo = ctx.get("tipo_peca", "Desconhecido")
    processo = ctx.get("numero_processo", "N/A")
    normalized = normalizar_process_number(matter_id)
    
    conteudo = (
        "# Hot — Últimas 48h\n\n"
        f"**Última atualização:** {_now()}\n\n"
        "## Matérias Publicadas\n"
        f"- **[[matter-{normalized}]]** — {titulo} ({tipo}, Processo {processo})\n\n"
        "## Prazos Próximos (7 dias)\n"
        "(nenhum registrado)\n\n"
        "## Pendências Abertas\n"
        "- Registrar nova matéria no vault operacional\n\n"
        "## Reflexões Recentes\n"
        "(nenhuma)\n\n"
        "---\n"
        "*Atualizado automaticamente após cada publicação.*\n"
    )
    
    hot_path.write_text(conteudo, encoding="utf-8")


def registrar(state_dir: Path | str, matter_id: str, level: str) -> dict[str, Any]:
    """Registra matéria no cérebro após publicação.
    
    Args:
        state_dir: .rdaa-run/<matter_id>/
        matter_id: identificador (processo ou nome)
        level: C/B/A
    
    Returns:
        {"success": bool, "file": str, "matter_id": str, ...}
    """
    state_dir = Path(state_dir).resolve()
    
    if not CEREBRO.exists():
        return {
            "success": False,
            "error": f"Cérebro não encontrado em {CEREBRO}",
            "matter_id": matter_id
        }
    
    WIKI_OPERACIONAL.mkdir(parents=True, exist_ok=True)
    
    # Carrega contexto
    ctx_path = state_dir / "contexto_peca.json"
    try:
        ctx = carregar_contexto(ctx_path)
    except ValueError as e:
        return {"success": False, "error": str(e), "matter_id": matter_id}
    
    # Normaliza nome do arquivo
    filename = f"matter-{normalizar_process_number(matter_id)}.md"
    file_path = WIKI_OPERACIONAL / filename
    
    # Monta conteúdo
    frontmatter = gerar_frontmatter(ctx, matter_id, level)
    conteudo = gerar_conteudo(ctx)
    
    # Escreve
    full_text = frontmatter + conteudo
    file_path.write_text(full_text, encoding="utf-8")
    
    # Atualiza índices
    try:
        atualizar_index(matter_id)
        atualizar_hot(ctx, matter_id)
    except Exception as e:
        return {
            "success": False,
            "error": f"Falha ao atualizar índices: {e}",
            "file": str(file_path),
            "matter_id": matter_id
        }
    
    return {
        "success": True,
        "matter_id": matter_id,
        "file": str(file_path),
        "level": level,
        "title": ctx.get("titulo_peca", "Sem título"),
        "process_number": ctx.get("numero_processo", "N/A"),
        "timestamp": _now()
    }


def main():
    parser = argparse.ArgumentParser(
        description="Registra matéria no cérebro após publicação RDAA"
    )
    parser.add_argument("state_dir", type=Path, help=".rdaa-run/<matter_id>/")
    parser.add_argument("--matter-id", required=True, help="Identificador da matéria")
    parser.add_argument("--level", required=True, choices=["C", "B", "A"])
    
    args = parser.parse_args()
    
    result = registrar(args.state_dir, args.matter_id, args.level)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    exit(main())
