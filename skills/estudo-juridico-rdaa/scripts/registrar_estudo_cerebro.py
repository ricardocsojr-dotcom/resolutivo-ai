#!/usr/bin/env python3
"""Grava automaticamente estudo jurídico no cérebro-ricar.

Executado ao final de um estudo publicado via `estudo-juridico-rdaa`.
Cria/atualiza concepts, sources, linkagem a domains, e atualiza índices.
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


def _now() -> str:
    """ISO 8601 com Z."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


_DOMAIN_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_SOURCE_ID_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*")


def kebab_case(text: str) -> str:
    """Converte para kebab-case."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    result = text.strip("-")
    if not result:
        raise ValueError("título de conceito inválido")
    return result


def _safe_identifier(value: str, pattern: re.Pattern[str], label: str) -> str:
    normalized = str(value).strip()
    if not pattern.fullmatch(normalized):
        raise ValueError(f"{label} inválido")
    return normalized


def criar_concept(title: str, domain: str, artifact_url: str, content: str) -> Path:
    """Cria/atualiza arquivo de conceito."""
    filename = f"{kebab_case(title)}.md"
    path = CEREBRO / "wiki" / "concepts" / filename
    
    frontmatter = (
        "---\n"
        "type: concept\n"
        f"title: \"{title}\"\n"
        f"domain: {domain}\n"
        "status: aprovada\n"
        f"created: {_now()}\n"
        f"artifact: {artifact_url}\n"
        "---\n"
    )
    
    conteudo = f"{frontmatter}\n{content}\n\n*Estudo publicado: [[{artifact_url}]]*\n"
    path.write_text(conteudo, encoding="utf-8")
    return path


def criar_source(source_id: str, ementa: str, court: str, date_str: str) -> Path:
    """Cria/atualiza arquivo de fonte."""
    safe_source_id = _safe_identifier(source_id, _SOURCE_ID_PATTERN, "fonte")
    path = CEREBRO / "wiki" / "sources" / f"{safe_source_id}.md"
    
    frontmatter = (
        "---\n"
        "type: source\n"
        f"title: \"{source_id}\"\n"
        f"court: {court}\n"
        f"date: {date_str}\n"
        "origin: estudo-juridico\n"
        f"created: {_now()}\n"
        "---\n"
    )
    
    conteudo = f"{frontmatter}\n{ementa}\n"
    path.write_text(conteudo, encoding="utf-8")
    return path


def atualizar_domain(domain: str, concept_names: list[str], source_names: list[str]) -> None:
    """Linkeia conceitos e fontes ao domínio."""
    safe_domain = _safe_identifier(domain, _DOMAIN_PATTERN, "domínio")
    domain_file = CEREBRO / "wiki" / "domains" / f"{safe_domain}.md"
    
    if not domain_file.exists():
        # Cria domain básico
        frontmatter = (
            "---\n"
            "type: domain\n"
            f"title: {domain.replace('-', ' ').title()}\n"
            f"created: {_now()}\n"
            "---\n"
        )
        conteudo = frontmatter + "\n"
    else:
        conteudo = domain_file.read_text(encoding="utf-8")
    
    # Adiciona links se ainda não estiverem
    for concept in concept_names:
        link = f"[[{kebab_case(concept)}]]"
        if link not in conteudo:
            conteudo += f"\n- {link} (conceito)"
    
    for source in source_names:
        link = f"[[{source}]]"
        if link not in conteudo:
            conteudo += f"\n- {link} (fonte)"
    
    domain_file.write_text(conteudo, encoding="utf-8")


def atualizar_indices() -> None:
    """Recount index.json."""
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
        "last_updated": _now()
    }
    
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def atualizar_hot(theme: str, artifact_url: str) -> None:
    """Adiciona estudo novo ao hot.md."""
    hot_path = CEREBRO / "hot.md"
    
    if hot_path.exists():
        conteudo = hot_path.read_text(encoding="utf-8")
    else:
        conteudo = "# Hot — Últimas 48h\n\n"
    
    # Adiciona linha do estudo novo
    nova_linha = f"- **Estudo:** {theme} — [{artifact_url}]({artifact_url})\n"
    
    if "## Estudos Novos" not in conteudo:
        conteudo = conteudo.replace(
            "# Hot — Últimas 48h\n",
            f"# Hot — Últimas 48h\n\n## Estudos Novos\n{nova_linha}\n"
        )
    else:
        conteudo = conteudo.replace(
            "## Estudos Novos\n",
            f"## Estudos Novos\n{nova_linha}"
        )
    
    hot_path.write_text(conteudo, encoding="utf-8")


def registrar(theme: str, artifact_url: str, concepts: list[str], sources: list[str], domain: str) -> dict[str, Any]:
    """Registra estudo no cérebro.
    
    Args:
        theme: Tema do estudo
        artifact_url: URL do artifact publicado
        concepts: Lista de nomes de conceitos a criar
        sources: Lista de source IDs (ex: PREC-001)
        domain: Domínio (ex: direito-contratual)
    
    Returns:
        {"success": bool, ...}
    """
    
    if not CEREBRO.exists():
        return {
            "success": False,
            "error": f"Cérebro não encontrado em {CEREBRO}",
            "theme": theme
        }
    
    try:
        # Cria conceitos
        concept_files = []
        for concept in concepts:
            path = criar_concept(concept, domain, artifact_url, f"Vide estudo: {artifact_url}")
            concept_files.append(str(path))
        
        # Fontes precisam existir com ementa literal já verificada; nunca crie placeholders.
        source_files = []
        for source in sources:
            safe_source = _safe_identifier(source, _SOURCE_ID_PATTERN, "fonte")
            path = CEREBRO / "wiki" / "sources" / f"{safe_source}.md"
            if not path.is_file():
                raise ValueError(f"fonte sem ementa literal verificada: {safe_source}")
            source_files.append(str(path))
        
        # Linkeia ao domain
        atualizar_domain(domain, concepts, sources)
        
        # Atualiza índices
        atualizar_indices()
        atualizar_hot(theme, artifact_url)
        
        return {
            "success": True,
            "theme": theme,
            "artifact_url": artifact_url,
            "concepts_created": len(concept_files),
            "sources_created": len(source_files),
            "domain": domain,
            "timestamp": _now()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "theme": theme
        }


def main():
    parser = argparse.ArgumentParser(
        description="Registra estudo jurídico no cérebro após publicação"
    )
    parser.add_argument("--theme", required=True, help="Tema do estudo")
    parser.add_argument("--artifact-url", required=True, help="URL do artifact publicado")
    parser.add_argument("--concepts", nargs="+", default=[], help="Nomes de conceitos")
    parser.add_argument("--sources", nargs="+", default=[], help="Source IDs (PREC-001, etc)")
    parser.add_argument("--domain", required=True, help="Domínio (ex: direito-contratual)")
    
    args = parser.parse_args()
    
    result = registrar(
        theme=args.theme,
        artifact_url=args.artifact_url,
        concepts=args.concepts,
        sources=args.sources,
        domain=args.domain
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    exit(main())
