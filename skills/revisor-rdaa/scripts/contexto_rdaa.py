#!/usr/bin/env python3
"""Contexto compartilhado e provenance de pesquisa do RDAA.

O módulo é deliberadamente determinístico e local. Ele não pesquisa a internet,
não interpreta mérito jurídico e não chama serviços externos. Apenas registra
resultados que a skill de pesquisa declarou como verificados externamente e
projeta o estado completo em um pacote menor para cada agente.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

try:
    from .estado_rdaa import add_provenance, initialize_state
    from .semantica_rdaa import record_agent_event, record_context_metric
except ImportError:  # execução direta pelo caminho do script
    from estado_rdaa import add_provenance, initialize_state
    from semantica_rdaa import record_agent_event, record_context_metric


SCHEMA_VERSION = "1"

TASK_TYPES = {
    "pesquisa",
    "conselho",
    "redator",
    "critico",
    "revisor",
    "formatador",
}

SOURCE_TYPES = {
    "jurisprudencia",
    "lei",
    "sumula",
    "tema_repetitivo",
    "processo",
    "documento",
    "figura",
    "nota_rodape",
    "vault",
    "citacao",
    "outro",
}


class ContextPack(dict[str, Any]):
    """Dicionário serializável que identifica a finalidade do contexto."""

    def __init__(self, *, matter_id: str, task_type: str, **payload: Any) -> None:
        super().__init__(
            schema_version=SCHEMA_VERSION,
            matter_id=matter_id,
            task_type=task_type,
            **payload,
        )

    @property
    def matter_id(self) -> str:
        return str(self["matter_id"])

    @property
    def task_type(self) -> str:
        return str(self["task_type"])

    def to_dict(self) -> dict[str, Any]:
        return dict(self)



def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return dict(default)
    return payload if isinstance(payload, dict) else dict(default)



def _read_provenance(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records



def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    return [value]



def _status_of(item: Any) -> str | None:
    return str(item.get("status")) if isinstance(item, dict) and item.get("status") else None



def _is_approved(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    return _status_of(item) in {"aprovada", "aprovado", "approved", "registrada"}



def _is_source_record(item: dict[str, Any]) -> bool:
    return bool(item.get("tipo") or item.get("fonte") or item.get("trecho"))



def _compact(items: Iterable[Any]) -> list[Any]:
    """Remove apenas duplicatas JSON-exatas, preservando a ordem original."""
    result: list[Any] = []
    seen: set[str] = set()
    for item in items:
        try:
            marker = json.dumps(item, ensure_ascii=False, sort_keys=True)
        except TypeError:
            marker = repr(item)
        if marker in seen:
            continue
        seen.add(marker)
        result.append(item)
    return result



def _select_sources(records: list[dict[str, Any]], task_type: str) -> list[dict[str, Any]]:
    if task_type == "formatador":
        return []
    selected: list[dict[str, Any]] = []
    for record in records:
        if not _is_source_record(record):
            continue
        # Um registro sem fonte não é convertido em fonte utilizável. Ele
        # permanece visível para a pesquisa/crítica/revisão como pendência.
        if task_type == "redator" and record.get("status") == "sem_fonte":
            continue
        selected.append(dict(record))
    return selected



def _select_rules(state: dict[str, Any], task_type: str) -> list[Any]:
    if task_type not in {"redator", "revisor", "formatador"}:
        return []
    return _compact(_as_list(state.get("rules")))



def _select_theses(state: dict[str, Any], task_type: str) -> tuple[list[Any], list[Any], list[Any]]:
    raw_theses = _as_list(state.get("theses"))
    raw_hypotheses = _as_list(state.get("hypotheses"))
    approved = [item for item in raw_theses if _is_approved(item)]

    if task_type == "critico":
        return raw_theses, approved, _compact(raw_hypotheses)
    if task_type == "conselho":
        return raw_theses, approved, _compact(raw_hypotheses)
    if task_type == "redator":
        # Strings legadas e teses sem status são preservadas como explicitamente
        # selecionadas; somente objetos com status aprovado entram em approved.
        return raw_theses, approved, []
    if task_type == "revisor":
        return [], [], []
    return [], [], []



def build_context_pack(state_dir: Path | str, task_type: str) -> ContextPack:
    """Montar somente o contexto relevante para um tipo de agente.

    A função lê um diretório de uma única matéria. Ela não combina diretórios,
    não executa pesquisa e não faz inferências jurídicas.
    """
    task_type = str(task_type).strip().lower()
    if task_type not in TASK_TYPES:
        allowed = ", ".join(sorted(TASK_TYPES))
        raise ValueError(f"task_type inválido: {task_type!r}; use um de: {allowed}")

    state_path = Path(state_dir)
    paths = initialize_state(state_path, matter_id=state_path.name)
    state = _read_json(paths["state"], {"matter_id": state_path.name})
    matter_id = str(state.get("matter_id") or Path(state_dir).name)
    generated_at = state.get("updated_at") or state.get("created_at")
    records = _read_provenance(paths["provenance"])
    facts = _compact(_as_list(state.get("facts")))
    citations = _compact(_as_list(state.get("citations")))
    decisions = _compact(_as_list(state.get("decisions")))
    pending = _compact(_as_list(state.get("pending")))
    requests = _compact(_as_list(state.get("requests")))
    risks = _compact(_as_list(state.get("risks")))
    theses, approved_theses, hypotheses = _select_theses(state, task_type)
    sources = _select_sources(records, task_type)
    confirmed_sources = [
        item for item in sources if item.get("status") == "verificada_externamente"
    ]
    rules = _select_rules(state, task_type)
    semantic_blocks = _compact(_as_list(state.get("semantic_blocks")))
    skeleton = state.get("esqueleto") if isinstance(state.get("esqueleto"), dict) else {}

    if task_type == "pesquisa":
        payload = {
            "facts": facts,
            "sources": sources,
            "confirmed_sources": confirmed_sources,
            "citations": [],
            "theses": [],
            "approved_theses": [],
            "hypotheses": [],
            "decisions": [],
            "pending": pending,
            "requests": [],
            "risks": [],
            "rules": [],
        }
    elif task_type == "conselho":
        payload = {
            "facts": facts,
            "sources": sources,
            "confirmed_sources": confirmed_sources,
            "citations": citations,
            "theses": theses,
            "approved_theses": approved_theses,
            "hypotheses": hypotheses,
            "decisions": decisions,
            "pending": pending,
            "requests": requests,
            "risks": risks,
            "rules": [],
        }
    elif task_type == "redator":
        payload = {
            "facts": facts,
            "sources": sources,
            "confirmed_sources": confirmed_sources,
            "citations": citations,
            "theses": theses,
            "approved_theses": approved_theses,
            "hypotheses": [],
            "decisions": decisions,
            "pending": pending,
            "requests": requests,
            "risks": risks,
            "rules": rules,
            "semantic_blocks": semantic_blocks,
            "esqueleto": skeleton,
        }
    elif task_type == "critico":
        payload = {
            "facts": facts,
            "sources": sources,
            "confirmed_sources": confirmed_sources,
            "citations": [],
            "theses": theses,
            "approved_theses": approved_theses,
            "hypotheses": hypotheses,
            "decisions": [],
            "pending": pending,
            "requests": requests,
            "risks": risks,
            "rules": [],
        }
    elif task_type == "revisor":
        payload = {
            "facts": facts,
            "sources": sources,
            "confirmed_sources": confirmed_sources,
            "citations": citations,
            "theses": [],
            "approved_theses": [],
            "hypotheses": [],
            "decisions": [],
            "pending": pending,
            "requests": requests,
            "risks": risks,
            "rules": rules,
            "semantic_blocks": semantic_blocks,
            "esqueleto": skeleton,
        }
    else:  # formatador
        payload = {
            "facts": facts,
            "sources": [],
            "confirmed_sources": [],
            "citations": [],
            "theses": [],
            "approved_theses": [],
            "hypotheses": [],
            "decisions": [],
            "pending": [],
            "requests": requests,
            "risks": [],
            "rules": rules,
            "semantic_blocks": semantic_blocks,
            "esqueleto": skeleton,
        }

    payload.update(
        {
            "nivel_peca": state.get("nivel_peca"),
            "modo_redacao": state.get("modo_redacao"),
            "redacao_por_blocos": state.get("redacao_por_blocos"),
            "modelo_estrutura": state.get("modelo_estrutura", {}),
            "uf_processo_originario": state.get("uf_processo_originario"),
        }
    )
    pack = ContextPack(
        matter_id=matter_id,
        task_type=task_type,
        generated_at=generated_at,
        **payload,
    )
    measure = record_context_metric(state_path, pack)
    record_agent_event(state_path, task_type, event="context_pack", measure=measure)
    return pack



def _research_items(content: Any) -> list[Any]:
    if isinstance(content, list):
        return list(content)
    if isinstance(content, dict) and isinstance(content.get("results"), list):
        return list(content["results"])
    return [content]



def _text_value(item: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = item.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None



def _research_id(source_type: str, item: dict[str, Any]) -> str:
    explicit = _text_value(item, ("id", "source_id", "identificador"))
    if explicit:
        return explicit
    location = _text_value(item, ("localizacao", "url", "link", "locator")) or ""
    excerpt = _text_value(item, ("trecho", "texto", "excerpt", "content")) or ""
    digest = hashlib.sha1(
        f"{source_type}|{location}|{excerpt}".encode("utf-8")
    ).hexdigest()[:12]
    return f"SRC-{digest}"



def _normalize_research_item(source_type: str, item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        payload = dict(item)
    else:
        payload = {"trecho": str(item)}

    record = {
        "id": _research_id(source_type, payload),
        "tipo": source_type,
        "fonte": _text_value(payload, ("fonte", "source", "provider")),
        "localizacao": _text_value(payload, ("localizacao", "url", "link", "locator")),
        "trecho": _text_value(payload, ("trecho", "texto", "excerpt", "content")),
        # Status externo só é atribuído por esta API explícita de pesquisa.
        "status": "verificada_externamente",
        "origem": _text_value(payload, ("origem", "origin")) or f"pesquisa:{source_type}",
        "usos": payload.get("usos", []) if isinstance(payload.get("usos", []), list) else [],
        "matter_id": payload.get("matter_id"),
    }
    if isinstance(payload.get("conferencia"), dict):
        record["conferencia"] = dict(payload["conferencia"])
    return record



def register_research(
    state_dir: Path | str,
    source_type: str,
    content: Any,
) -> list[dict[str, Any]]:
    """Registrar resultado de pesquisa como fonte explicitamente verificada.

    `content` pode ser um dicionário, uma lista de dicionários ou um texto. O
    status é fixado em `verificada_externamente` porque essa função só deve ser
    chamada depois que a skill de pesquisa declarar que conferiu a fonte.
    """
    source_type = str(source_type).strip().lower()
    if not source_type:
        raise ValueError("source_type não pode ser vazio")
    if source_type not in SOURCE_TYPES:
        source_type = "outro"

    state_path = Path(state_dir)
    paths = initialize_state(state_path, matter_id=state_path.name)
    records = [_normalize_research_item(source_type, item) for item in _research_items(content)]
    for record in records:
        add_provenance(Path(state_dir), record)
    # Força a criação do estado mesmo se a entrada for uma lista vazia e devolve
    # os registros normalizados para permitir auditoria/teste sem reler o JSONL.
    paths["provenance"].touch(exist_ok=True)
    return records



def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Contexto e provenance de pesquisa do RDAA")
    parser.add_argument("state_dir", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)

    pack_parser = commands.add_parser("pack", help="montar pacote para um agente")
    pack_parser.add_argument("task_type", choices=sorted(TASK_TYPES))

    register_parser = commands.add_parser("register", help="registrar pesquisa explicitamente conferida")
    register_parser.add_argument("--source-type", required=True)
    register_parser.add_argument(
        "--content-json",
        required=True,
        type=Path,
        help="arquivo JSON com um resultado, lista de resultados ou objeto com results",
    )

    args = parser.parse_args()
    if args.command == "pack":
        pack = build_context_pack(args.state_dir, args.task_type)
        print(json.dumps(pack, ensure_ascii=False, indent=2))
        return 0

    try:
        content = json.loads(args.content_json.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"[ERRO] JSON de pesquisa não encontrado: {args.content_json}")
        return 2
    except json.JSONDecodeError as exc:
        print(f"[ERRO] JSON de pesquisa inválido: {exc}")
        return 2
    records = register_research(args.state_dir, args.source_type, content)
    print(json.dumps(records, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
