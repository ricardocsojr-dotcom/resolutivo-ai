#!/usr/bin/env python3
"""Estado local e provenance mínima do RDAA.

Os arquivos são criados automaticamente pelo fluxo de publicação. O usuário
não precisa editá-los. O módulo usa somente a biblioteca padrão e mantém fatos,
decisões e citações separados por execução/caso.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "3"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        Path(temp_name).replace(path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def file_sha256(path: Path | str) -> str | None:
    path = Path(path)
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy_file_atomic(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    try:
        with source.open("rb") as source_handle, os.fdopen(fd, "wb") as destination_handle:
            for chunk in iter(lambda: source_handle.read(1024 * 1024), b""):
                destination_handle.write(chunk)
        Path(temp_name).replace(destination)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise


def promote_candidate_state(candidate_state_dir: Path | str, state_dir: Path | str) -> list[str]:
    """Promover somente os arquivos de estado após o DOCX ter sido publicado."""
    candidate_state_dir = Path(candidate_state_dir)
    state_dir = Path(state_dir)
    promoted: list[str] = []
    for name in ("matter_state.json", "provenance.jsonl"):
        source = candidate_state_dir / name
        if not source.is_file():
            raise FileNotFoundError(f"estado candidato incompleto: {source}")
        _copy_file_atomic(source, state_dir / name)
        promoted.append(name)
    return promoted


def _safe_matter_id(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return value.strip("-") or "sem-identificador"


def initialize_state(state_dir: Path, matter_id: str | None = None, output: Path | str | None = None) -> dict[str, Path]:
    state_dir = Path(state_dir)
    output_path = Path(output) if output is not None else None
    state_dir.mkdir(parents=True, exist_ok=True)
    matter_id = _safe_matter_id(matter_id or (output_path.stem if output_path else "execucao-rdaa"))
    state_path = state_dir / "matter_state.json"
    manifest_path = state_dir / "run_manifest.json"
    provenance_path = state_dir / "provenance.jsonl"

    if not state_path.exists():
        _write_json(
            state_path,
            {
                "schema_version": SCHEMA_VERSION,
                "matter_id": matter_id,
                "created_at": _now(),
                "facts": [],
                "theses": [],
                "citations": [],
                "decisions": [],
                "pending": [],
                "hypotheses": [],
                "requests": [],
                "risks": [],
                "rules": [],
                "semantic_reviews": [],
                "metrics": {},
                "semantic_blocks": [],
                "esqueleto": {},
                "nivel_peca": None,
                "modo_redacao": None,
                "redacao_por_blocos": None,
                "modelo_estrutura": {},
                "uf_processo_originario": None,
            },
        )
    if not manifest_path.exists():
        _write_json(
            manifest_path,
            {
                "schema_version": SCHEMA_VERSION,
                "matter_id": matter_id,
                "created_at": _now(),
                "phase": "initialized",
                "status": "initialized",
                "attempt": 0,
            },
        )
    provenance_path.touch(exist_ok=True)
    return {
        "state": state_path,
        "manifest": manifest_path,
        "provenance": provenance_path,
    }


def update_manifest(state_dir: Path, **updates: Any) -> Path:
    paths = initialize_state(state_dir, updates.get("matter_id"), updates.get("output"))
    path = paths["manifest"]
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.update({key: value for key, value in updates.items() if value is not None})
    payload["updated_at"] = _now()
    payload["attempt"] = int(payload.get("attempt", 0)) + 1
    _write_json(path, payload)
    return path


def add_provenance(state_dir: Path, record: dict[str, Any]) -> Path:
    paths = initialize_state(state_dir, record.get("matter_id"))
    normalized = {
        "schema_version": SCHEMA_VERSION,
        "recorded_at": _now(),
        "id": record.get("id"),
        "tipo": record.get("tipo", "desconhecido"),
        "fonte": record.get("fonte"),
        "localizacao": record.get("localizacao"),
        "trecho": record.get("trecho"),
        "status": record.get("status", "pendente"),
        "origem": record.get("origem", "contexto_json"),
        "usos": record.get("usos", []),
    }
    if isinstance(record.get("conferencia"), dict):
        normalized["conferencia"] = dict(record["conferencia"])
    existing_ids = set()
    if paths["provenance"].exists():
        for line in paths["provenance"].read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    old = json.loads(line)
                    if old.get("id"):
                        existing_ids.add(old["id"])
                except json.JSONDecodeError:
                    continue
    if normalized["id"] not in existing_ids:
        with paths["provenance"].open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(normalized, ensure_ascii=False) + "\n")
    return paths["provenance"]


def matter_id_from_context(context: dict[str, Any], output: Path | str | None = None) -> str:
    explicit = context.get("matter_id")
    process = context.get("numero_processo")
    if explicit:
        return _safe_matter_id(str(explicit))
    if process:
        return _safe_matter_id(str(process))
    return _safe_matter_id(Path(output).stem if output is not None else "execucao-rdaa")


def _stable_id(prefix: str, location: str, value: str) -> str:
    digest = hashlib.sha1(f"{location}|{value}".encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{digest}"


def _structured_records(
    value: Any,
    *,
    kind: str,
    text_keys: tuple[str, ...],
    location: str,
) -> list[dict[str, Any]]:
    """Normaliza registros explícitos sem preencher conclusões jurídicas."""
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    records: list[dict[str, Any]] = []
    for index, item in enumerate(items, start=1):
        if isinstance(item, dict):
            record = dict(item)
            text = next(
                (str(record[key]).strip() for key in text_keys if record.get(key)),
                "",
            )
        else:
            text = str(item).strip()
            record = {"texto": text}
        if not text and not record:
            continue
        marker = text or json.dumps(record, ensure_ascii=False, sort_keys=True)
        record.setdefault("id", _stable_id(kind.upper(), f"{location}[{index}]", marker))
        record.setdefault("tipo", kind)
        record.setdefault("origem", "contexto_json")
        records.append(record)
    return records


def _id_list(value: Any) -> list[str]:
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    return [str(item).strip() for item in values if str(item).strip()]


def _semantic_block_records(context: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, block in enumerate(context.get("blocos", []), start=1):
        if not isinstance(block, dict):
            continue
        location = f"contexto.blocos[{index}]"
        ids: list[str] = []
        for key in ("id", "semantic_ids", "fact_ids", "thesis_ids", "request_ids", "source_ids", "risk_ids"):
            ids.extend(_id_list(block.get(key)))
        ids = list(dict.fromkeys(ids))
        if not ids:
            continue
        block_id = str(block.get("id") or _stable_id("B", location, json.dumps(ids, ensure_ascii=False)))
        record: dict[str, Any] = {
            "id": block_id,
            "tipo": block.get("tipo", "desconhecido"),
            "semantic_ids": ids,
            "localizacao": location,
            "origem": "contexto_json",
        }
        for key in ("fact_ids", "thesis_ids", "request_ids", "source_ids", "risk_ids"):
            values = _id_list(block.get(key))
            if values:
                record[key] = list(dict.fromkeys(values))
        for key in ("visual_tipo", "funcao_visual", "texto_pesquisavel", "source_path", "source_sha256", "annotation_manifest", "source_kind"):
            value = block.get(key)
            if value is not None and str(value).strip():
                record[key] = str(value).strip()
        page_value = block.get("page", block.get("pagina"))
        if page_value is not None:
            record["page"] = page_value
        if isinstance(block.get("rectangle_ids"), list):
            record["rectangle_ids"] = _id_list(block.get("rectangle_ids"))
        records.append(record)
    return records


def derive_from_context(context: dict[str, Any]) -> dict[str, Any]:
    """Deriva somente campos explícitos do contexto, sem interpretação jurídica."""
    facts = []
    for field in ("enderecamento", "numero_processo", "partes", "data_local"):
        value = context.get(field)
        if not value:
            continue
        values = str(value).splitlines() if field == "partes" else [str(value)]
        for line_index, item in enumerate(values, start=1):
            item = item.strip()
            if not item:
                continue
            location = f"contexto.{field}" + (f"[{line_index}]" if field == "partes" else "")
            facts.append({
                "id": _stable_id("F", location, item),
                "campo": field,
                "valor": item,
                "origem": "contexto_json",
                "localizacao": location,
                "status": "informado",
            })

    theses = context.get("teses", context.get("hipoteses", []))
    if not isinstance(theses, list):
        theses = []
    hypotheses = context.get("hipoteses", [])
    if not isinstance(hypotheses, list):
        hypotheses = []
    pending = context.get("pendencias", context.get("pending", []))
    if not isinstance(pending, list):
        pending = []

    theses_structured = _structured_records(
        theses,
        kind="tese",
        text_keys=("texto", "tese", "descricao"),
        location="contexto.teses",
    )
    hypotheses_structured = _structured_records(
        hypotheses,
        kind="hipotese",
        text_keys=("texto", "hipotese", "descricao"),
        location="contexto.hipoteses",
    )
    requests_key = "pedidos" if "pedidos" in context else "requests"
    risks_key = "riscos" if "riscos" in context else "risks"
    decisions_key = "decisoes" if "decisoes" in context else "decisions"
    rules_key = "regras" if "regras" in context else "rules"
    requests = _structured_records(
        context.get(requests_key),
        kind="pedido",
        text_keys=("texto", "pedido", "descricao"),
        location=f"contexto.{requests_key}",
    )
    risks = _structured_records(
        context.get(risks_key),
        kind="risco",
        text_keys=("descricao", "texto", "risco"),
        location=f"contexto.{risks_key}",
    )
    decisions = _structured_records(
        context.get(decisions_key),
        kind="decisao",
        text_keys=("texto", "veredito", "decisao", "descricao"),
        location=f"contexto.{decisions_key}",
    )
    rules = _structured_records(
        context.get(rules_key),
        kind="regra",
        text_keys=("texto", "regra", "descricao"),
        location=f"contexto.{rules_key}",
    )

    semantic_blocks = _semantic_block_records(context)
    provenance = []
    explicit_source_items: list[Any] = []
    for key in ("sources", "fontes"):
        value = context.get(key, [])
        explicit_source_items.extend(value if isinstance(value, list) else [value])
    skeleton_value = context.get("esqueleto", context.get("skeleton"))
    if isinstance(skeleton_value, dict):
        selected_sources = skeleton_value.get("fontes_selecionadas", skeleton_value.get("selected_sources", []))
        explicit_source_items.extend(selected_sources if isinstance(selected_sources, list) else [selected_sources])
    seen_source_ids: set[str] = set()
    for index, source in enumerate(explicit_source_items, start=1):
        if not isinstance(source, dict):
            continue
        source_id = str(source.get("source_id", source.get("id", ""))).strip()
        if not source_id or source_id in seen_source_ids:
            continue
        seen_source_ids.add(source_id)
        provenance.append({
            "id": source_id,
            "tipo": source.get("tipo", "fonte_selecionada"),
            "fonte": source.get("fonte") or source.get("source"),
            "localizacao": source.get("localizacao") or f"contexto.fontes[{index}]",
            "trecho": source.get("trecho") or source.get("texto"),
            "status": source.get("status", "informada"),
            "origem": source.get("origem", "contexto_json"),
            "usos": [source.get("uso")] if source.get("uso") else [],
        })
    for index, block in enumerate(context.get("blocos", []), start=1):
        if not isinstance(block, dict):
            continue
        location = f"contexto.blocos[{index}]"
        note = block.get("nota_rodape")
        if note:
            note = str(note).strip()
            provenance.append({
                "id": _stable_id("P", f"{location}.nota_rodape", note),
                "tipo": "nota_rodape",
                "fonte": note,
                "localizacao": f"{location}.nota_rodape",
                "trecho": note,
                "status": "informada",
                "origem": "contexto_json",
            })
        if block.get("tipo") in ("citacao", "documento", "figura", "decisao_anotada"):
            excerpt = str(block.get("texto") or block.get("texto_pesquisavel") or block.get("legenda") or "").strip()
            source = block.get("fonte") or block.get("source") or block.get("source_path")
            if excerpt or source:
                provenance.append({
                    "id": _stable_id("P", location, excerpt or str(source)),
                    "tipo": block.get("tipo"),
                    "fonte": str(source).strip() if source else None,
                    "localizacao": location,
                    "trecho": excerpt or None,
                    "status": "informada" if source else "sem_fonte",
                    "origem": "contexto_json",
                })

    return {
        "facts": facts,
        "theses": theses,
        "theses_structured": theses_structured,
        "hypotheses": hypotheses,
        "hypotheses_structured": hypotheses_structured,
        "pending": pending,
        "requests": requests,
        "risks": risks,
        "decisions": decisions,
        "rules": rules,
        "has_hypotheses": "hipoteses" in context,
        "has_requests": requests_key in context,
        "has_risks": risks_key in context,
        "has_decisions": decisions_key in context,
        "has_rules": rules_key in context,
        "has_theses": "teses" in context or "hipoteses" in context,
        "has_semantic_blocks": bool(semantic_blocks),
        "semantic_blocks": semantic_blocks,
        "provenance": provenance,
    }


def persist_context(state_dir: Path, context: dict[str, Any], output: Path | str | None = None) -> dict[str, Any]:
    matter_id = matter_id_from_context(context, output)
    paths = initialize_state(state_dir, matter_id=matter_id, output=output)
    derived = derive_from_context(context)
    state = json.loads(paths["state"].read_text(encoding="utf-8"))
    state.update({
        "schema_version": SCHEMA_VERSION,
        "matter_id": matter_id,
        "facts": derived["facts"],
        "theses": derived["theses"],
        "pending": derived["pending"],
        "updated_at": _now(),
    })
    if derived["has_hypotheses"]:
        state["hypotheses"] = derived["hypotheses"]
        state["hypotheses_structured"] = derived["hypotheses_structured"]
    if derived["has_theses"]:
        state["theses_structured"] = derived["theses_structured"]
    if derived["has_requests"]:
        state["requests"] = derived["requests"]
    if derived["has_risks"]:
        state["risks"] = derived["risks"]
    if derived["has_decisions"]:
        state["decisions"] = derived["decisions"]
    if derived["has_rules"]:
        state["rules"] = derived["rules"]
    if derived["has_semantic_blocks"]:
        state["semantic_blocks"] = derived["semantic_blocks"]
    skeleton = context.get("esqueleto", context.get("skeleton"))
    if isinstance(skeleton, dict):
        state["esqueleto"] = skeleton
    explicit_risk_level = context.get("nivel_risco", context.get("risk_level"))
    if explicit_risk_level is not None and str(explicit_risk_level).strip():
        state["declared_risk_level"] = str(explicit_risk_level).strip()
    explicit_piece_level = context.get("nivel_peca")
    if explicit_piece_level is not None and str(explicit_piece_level).strip():
        state["nivel_peca"] = str(explicit_piece_level).strip().upper()
    explicit_mode = context.get("modo_redacao")
    if explicit_mode is not None and str(explicit_mode).strip():
        state["modo_redacao"] = str(explicit_mode).strip().lower()
    if "redacao_por_blocos" in context:
        state["redacao_por_blocos"] = bool(context["redacao_por_blocos"])
    selected_model = context.get("modelo_estrutura")
    if isinstance(selected_model, dict):
        state["modelo_estrutura"] = dict(selected_model)
    explicit_uf = context.get("uf_processo_originario", context.get("estado_processo_originario"))
    if explicit_uf is not None and str(explicit_uf).strip():
        state["uf_processo_originario"] = str(explicit_uf).strip()
    _write_json(paths["state"], state)
    for record in derived["provenance"]:
        record["matter_id"] = matter_id
        add_provenance(state_dir, record)
    return {"matter_id": matter_id, "paths": paths, "derived": derived}


def main() -> int:
    parser = argparse.ArgumentParser(description="Estado local e provenance do RDAA")
    parser.add_argument("state_dir", type=Path)
    parser.add_argument("--matter-id", default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    paths = initialize_state(args.state_dir, args.matter_id, args.output)
    print(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
