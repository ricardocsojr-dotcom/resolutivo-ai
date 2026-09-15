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
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CEREBRO_PATH = "C:\\Users\\ricar\\cerebro-ricar"
CEREBRO = Path(CEREBRO_PATH)
WIKI_OPERACIONAL = CEREBRO / "wiki" / "operacional"


def _now() -> str:
    """ISO 8601 com Z."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _single_line(value: Any) -> str:
    """Evita que dados de contexto criem campos YAML/Markdown adicionais."""
    return re.sub(r"[\r\n]+", " ", str(value)).strip()


def _partes_estruturadas(ctx: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Aceita partes estruturadas ou o texto usado pelo contexto nativo do DOCX."""
    partes = ctx.get("partes", {})
    if isinstance(partes, dict):
        return partes
    if not isinstance(partes, str):
        return {}

    resultado: dict[str, dict[str, str]] = {}
    restantes: list[str] = []
    for linha in partes.splitlines():
        rotulo, separador, nome = linha.partition(":")
        valor = _single_line(nome if separador else rotulo)
        if not valor:
            continue
        chave = rotulo.strip().casefold()
        if chave in {"autor", "autora", "embargante", "apelante", "agravante", "exequente", "impetrante"}:
            resultado.setdefault("autor", {"nome": valor})
        elif chave in {"réu", "reu", "ré", "embargado", "embargada", "apelado", "apelada", "agravado", "agravada", "executado", "executada", "impetrado", "impetrada"}:
            resultado.setdefault("reu", {"nome": valor})
        else:
            restantes.append(valor)
    if "autor" not in resultado and restantes:
        resultado["autor"] = {"nome": restantes.pop(0)}
    if "reu" not in resultado and restantes:
        resultado["reu"] = {"nome": restantes.pop(0)}
    return resultado


def _extrair_titulo_peca(ctx: dict[str, Any], default: str = "Sem título") -> str:
    """Deriva o título da peça quando ctx não traz 'titulo_peca' explícito.

    O schema padrão de contexto_peca.json (usado por construir_peca.py) nunca
    grava um campo 'titulo_peca' de nível superior — o nome da peça vive dentro
    do bloco 'abertura' como 'nome_peca'. Sem este fallback, toda matéria
    publicada pelo fluxo padrão B/A grava 'Sem título' no Cérebro-Ricar.
    """
    titulo = ctx.get("titulo_peca")
    if titulo:
        return str(titulo)
    for bloco in ctx.get("blocos", []):
        if isinstance(bloco, dict) and bloco.get("tipo") == "abertura":
            nome_peca = bloco.get("nome_peca")
            if nome_peca:
                return str(nome_peca).strip()
    return default


def _extrair_tipo_peca(ctx: dict[str, Any]) -> str:
    """Deriva o tipo da peça a partir do título quando 'tipo_peca' ausente."""
    tipo = ctx.get("tipo_peca")
    if tipo:
        return str(tipo)
    titulo = _extrair_titulo_peca(ctx)
    if titulo and titulo != "Sem título":
        return titulo.title()
    return "Desconhecido"


def normalizar_process_number(num: str) -> str:
    """0130354-80.2018.8.13.0702 → 0130354-80-2018-8-13-0702 (seguro pra filename)."""
    return re.sub(r"[./]", "-", num.strip())


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)[:60]


def _split_party_names(text: str) -> list[str]:
    text = text.strip()
    tokens = [t.strip() for t in re.split(r",|\be\b", text) if t.strip()]
    cleaned = []
    for t in tokens:
        if t.lower() in ("desconhecido", "n/a", "e", "&", ""):
            continue
        t = re.sub(r"^[\s\-:]+|[\s\-:]+$", "", t).strip()
        if len(t) > 2:
            cleaned.append(t)
    return cleaned


def _upsert_entity_file(fpath: Path, nome: str, role: str, matter_link: str) -> None:
    now_str = _now()
    if not fpath.exists():
        content = (
            f"---\n"
            f"type: entity\n"
            f"title: \"{nome}\"\n"
            f"role: {role}\n"
            f"created: {now_str}\n"
            f"updated: {now_str}\n"
            f"---\n\n"
            f"# {nome}\n\n"
            f"**Papel:** {role}\n\n"
            f"## Matérias Relacionadas\n"
            f"{matter_link}\n"
        )
        fpath.write_text(content, encoding="utf-8")
    else:
        existing = fpath.read_text(encoding="utf-8")
        if matter_link not in existing:
            if "## Matérias Relacionadas" in existing:
                existing = existing.replace("## Matérias Relacionadas\n", f"## Matérias Relacionadas\n{matter_link}\n")
            else:
                existing += f"\n## Matérias Relacionadas\n{matter_link}\n"
            existing = re.sub(r"updated:.*", f"updated: {now_str}", existing)
            fpath.write_text(existing, encoding="utf-8")


def _registrar_entidades(ctx: dict[str, Any], matter_id: str, cerebro_root: Path) -> list[str]:
    entities_dir = cerebro_root / "wiki" / "entities"
    entities_dir.mkdir(parents=True, exist_ok=True)
    partes = _partes_estruturadas(ctx)
    normalized_matter = normalizar_process_number(matter_id)
    matter_link = f"- [[matter-{normalized_matter}]]"

    registered = []
    autor_dict = partes.get("autor", {})
    autor_nome = autor_dict.get("nome", "")
    for nome in _split_party_names(autor_nome):
        slug = _slugify(nome)
        if slug:
            _upsert_entity_file(entities_dir / f"{slug}.md", nome, "cliente", matter_link)
            registered.append(slug)

    reu_dict = partes.get("reu", {})
    reu_nome = reu_dict.get("nome", "")
    for nome in _split_party_names(reu_nome):
        slug = _slugify(nome)
        if slug:
            _upsert_entity_file(entities_dir / f"{slug}.md", nome, "adversario", matter_link)
            registered.append(slug)

    return registered


def carregar_contexto(path: Path) -> dict[str, Any]:
    """Lê contexto_peca.json."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"contexto inválido: {path}") from e


def gerar_frontmatter(ctx: dict[str, Any], matter_id: str, level: str) -> str:
    """Monta YAML frontmatter."""
    partes = _partes_estruturadas(ctx)
    cliente = _single_line(partes.get("autor", {}).get("nome", "Desconhecido"))
    titulo = _single_line(_extrair_titulo_peca(ctx))
    matter_id = _single_line(matter_id)
    process_number = _single_line(ctx.get("numero_processo", "N/A"))
    level = _single_line(level)
    
    frontmatter_text = (
        "---\n"
        'type: matter\n'
        f"title: {json.dumps(titulo, ensure_ascii=False)}\n"
        f"matter_id: {json.dumps(matter_id, ensure_ascii=False)}\n"
        f"process_number: {json.dumps(process_number, ensure_ascii=False)}\n"
        f"client: {json.dumps(cliente, ensure_ascii=False)}\n"
        f"level: {json.dumps(level, ensure_ascii=False)}\n"
        f'status: published\n'
        f'created: {_now()}\n'
        f'updated: {_now()}\n'
        "---\n"
    )
    return frontmatter_text


def gerar_conteudo(ctx: dict[str, Any]) -> str:
    """Monta conteúdo do arquivo."""
    titulo = _single_line(_extrair_titulo_peca(ctx, default="Peça sem título"))
    tipo = _single_line(_extrair_tipo_peca(ctx))
    nivel = _single_line(ctx.get("nivel_peca", "?"))
    processo = _single_line(ctx.get("numero_processo", "N/A"))
    
    partes = _partes_estruturadas(ctx)
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
    
    titulo = _extrair_titulo_peca(ctx)
    tipo = _extrair_tipo_peca(ctx)
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


def _registrar_sync_no_manifesto(state_dir: Path, receipt_path: Path) -> dict[str, Any]:
    """Grava o recibo do Cérebro em `vault.syncs[]` do run_manifest.json."""
    manifest_path = state_dir / "run_manifest.json"
    if not manifest_path.is_file():
        return {"success": False, "error": f"manifesto não encontrado: {manifest_path}"}
        
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if "vault" not in manifest or not isinstance(manifest["vault"], dict):
            manifest["vault"] = {"lookups": [], "syncs": []}
        if "syncs" not in manifest["vault"] or not isinstance(manifest["vault"]["syncs"], list):
            manifest["vault"]["syncs"] = []
            
        record = {
            "vault": "cerebro-ricar",
            "direction": "push",
            "artifact_path": str(receipt_path),
        }
        manifest["vault"]["syncs"].append(record)
        
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"success": True, "record": record}
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "error": f"{type(exc).__name__}: {exc}"}


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
    
    # Confirma que o estado determinístico já registrou publicação real.
    manifest_path = state_dir / "run_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return {"success": False, "error": f"manifesto inválido: {manifest_path}", "matter_id": matter_id}
    if manifest.get("phase") != "published":
        return {"success": False, "error": "matéria não está em fase published", "matter_id": matter_id}

    # Carrega contexto tolerando variações de nome de arquivo
    ctx_path = None
    for cand_name in ["contexto_peca.json", "CONTEXTO-PECA.json", "contexto.json", "context.json"]:
        p = state_dir / cand_name
        if p.is_file():
            ctx_path = p
            break
    if ctx_path is None:
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

    # Registra e atualiza entidades envolvidas em wiki/entities
    try:
        _registrar_entidades(ctx, matter_id, CEREBRO)
    except Exception as e:
        print(f"[AVISO] Falha ao registrar entidades no Cérebro: {e}", file=sys.stderr)

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
    
    receipt_path = state_dir / "CEREBRO-RECIBO.json"
    receipt = {
        "vault": "cerebro-ricar",
        "status": "registered",
        "matter_id": matter_id,
        "record_path": str(file_path),
        "registered_at": _now(),
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Grava o recibo NO MANIFESTO, não só em disco.
    #
    # Correção 2026-09-11 (bug real): até aqui o script escrevia
    # CEREBRO-RECIBO.json e devolvia success=True, mas `vault.syncs[]` do
    # manifesto continuava vazio — e é exatamente esse array que o gate
    # `vault_registered` do orquestrador exige. Resultado: matéria publicada
    # e efetivamente registrada no Cérebro ficava travada antes do último
    # estágio para sempre, e o registro do manifesto dependia de alguém
    # lembrar de rodar `register-vault-sync` à mão. Registro obrigatório
    # vira passo do código, nunca instrução em documentação.
    sync_record = _registrar_sync_no_manifesto(state_dir, receipt_path)
    if not sync_record.get("success"):
        return {
            "success": False,
            "cerebro_registered": True,
            "manifest_sync": sync_record,
            "error": "Cérebro-Ricar registrado, mas o recibo não entrou em vault.syncs[] do manifesto",
            "matter_id": matter_id,
            "file": str(file_path),
            "receipt": str(receipt_path),
        }

    return {
        "success": True,
        "matter_id": matter_id,
        "file": str(file_path),
        "receipt": str(receipt_path),
        "manifest_sync": sync_record,
        "level": level,
        "title": _extrair_titulo_peca(ctx),
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
