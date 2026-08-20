"""Validação objetiva do esqueleto e das fontes selecionadas.

O módulo não decide pertinência, validade ou mérito jurídico. Ele confere apenas
aprovação explícita, IDs, origem, localização e vínculos declarados.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from .estado_rdaa import initialize_state
except ImportError:
    from estado_rdaa import initialize_state


SOURCE_STATUSES = {"verificada_externamente", "informada", "pendente", "sem_fonte"}
SELECTION_STATUSES = {"selecionadas", "sem_fontes", "pendente"}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _finding(kind: str, message: str, location: str, severity: str = "erro") -> dict[str, Any]:
    return {
        "kind": kind,
        "severity": severity,
        "message": message,
        "location": location,
    }


def _provenance_ids(state_dir: Path | str | None) -> set[str]:
    if state_dir is None:
        return set()
    paths = initialize_state(Path(state_dir), matter_id=Path(state_dir).name)
    ids: set[str] = set()
    if not paths["provenance"].exists():
        return ids
    for line in paths["provenance"].read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and record.get("id"):
            ids.add(str(record["id"]))
    return ids


def validate_skeleton(context: dict[str, Any], state_dir: Path | str | None = None) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    skeleton = context.get("esqueleto", context.get("skeleton"))
    if not isinstance(skeleton, dict):
        return {
            "status": "BLOCK",
            "findings": [_finding("skeleton_missing", "Esqueleto estruturado não foi fornecido.", "contexto.esqueleto")],
        }

    status = str(skeleton.get("status", "")).strip().lower()
    approval = skeleton.get("aprovacao", skeleton.get("approval"))
    approval_status = approval.get("status") if isinstance(approval, dict) else ""
    approval_status = str(approval_status).strip().lower()
    if status != "aprovado" or approval_status != "aprovado":
        findings.append(
            _finding(
                "skeleton_not_approved",
                "O esqueleto precisa de aprovação explícita antes da redação.",
                "contexto.esqueleto.aprovacao",
            )
        )

    source_selection_status = str(
        skeleton.get("fontes_status", skeleton.get("sources_status", ""))
    ).strip().lower()
    if source_selection_status not in SELECTION_STATUSES:
        findings.append(
            _finding(
                "source_selection_status_missing",
                "O esqueleto precisa declarar se as fontes foram selecionadas, não existem ou estão pendentes.",
                "contexto.esqueleto.fontes_status",
            )
        )
    if source_selection_status == "pendente":
        findings.append(
            _finding(
                "source_selection_pending",
                "A seleção de fontes do esqueleto está pendente.",
                "contexto.esqueleto.fontes_status",
            )
        )

    selected = _as_list(skeleton.get("fontes_selecionadas", skeleton.get("selected_sources", [])))
    if source_selection_status == "selecionadas" and not selected:
        findings.append(
            _finding(
                "selected_sources_empty",
                "O esqueleto declarou fontes selecionadas, mas não informou nenhuma fonte.",
                "contexto.esqueleto.fontes_selecionadas",
            )
        )

    context_sources = {}
    for item in _as_list(context.get("sources")) + _as_list(context.get("fontes")):
        if isinstance(item, dict) and item.get("id"):
            context_sources[str(item["id"])] = item
    known_ids = set(context_sources) | _provenance_ids(state_dir)
    selected_ids: set[str] = set()
    for index, item in enumerate(selected, start=1):
        location = f"contexto.esqueleto.fontes_selecionadas[{index}]"
        if not isinstance(item, dict):
            findings.append(_finding("selected_source_not_object", "Cada fonte selecionada deve ser um objeto estruturado.", location))
            continue
        source_id = str(item.get("source_id", item.get("id", ""))).strip()
        if not source_id:
            findings.append(_finding("selected_source_id_missing", "Fonte selecionada sem source_id.", location))
            continue
        if source_id in selected_ids:
            findings.append(_finding("selected_source_duplicate", f"Fonte selecionada repetida: {source_id}.", location))
        selected_ids.add(source_id)
        if known_ids and source_id not in known_ids:
            findings.append(_finding("selected_source_missing", f"Fonte selecionada não existe no provenance da matéria: {source_id}.", location))
        for required in ("uso", "bloco", "origem", "fonte", "localizacao"):
            if not str(item.get(required, "")).strip():
                findings.append(_finding("selected_source_field_missing", f"Campo obrigatório ausente: {required}.", location))
        source_status = str(item.get("status", "")).strip().lower()
        if source_status not in SOURCE_STATUSES:
            findings.append(_finding("selected_source_status_invalid", f"Status de fonte inválido: {source_status or '[vazio]'}.", location))
        if source_status == "verificada_externamente" and item.get("literalidade_confirmada") is not True:
            findings.append(_finding("literal_confirmation_missing", "Fonte externa selecionada precisa declarar literalidade_confirmada como true.", location))

    late_additions = _as_list(skeleton.get("fontes_adicionais", skeleton.get("late_sources", [])))
    allowed_ids = set(selected_ids)
    for index, item in enumerate(late_additions, start=1):
        location = f"contexto.esqueleto.fontes_adicionais[{index}]"
        if not isinstance(item, dict):
            findings.append(_finding("late_source_not_object", "A fonte adicionada depois do esqueleto deve ser um objeto estruturado.", location))
            continue
        source_id = str(item.get("source_id", item.get("id", ""))).strip()
        if not source_id:
            findings.append(_finding("late_source_id_missing", "Fonte posterior sem source_id.", location))
            continue
        allowed_ids.add(source_id)
        if not str(item.get("motivo", "")).strip():
            findings.append(_finding("late_source_reason_missing", "Fonte posterior precisa informar motivo.", location))
        review = item.get("revisao_posterior", item.get("post_review"))
        review_status = review.get("status") if isinstance(review, dict) else ""
        if str(review_status).strip().lower() != "aprovado":
            findings.append(_finding("late_source_not_reviewed", "Fonte posterior precisa de revisão explícita antes da publicação.", location))

    for index, block in enumerate(_as_list(context.get("blocos")), start=1):
        if not isinstance(block, dict):
            continue
        for source_id in _as_list(block.get("source_ids")):
            source_id = str(source_id).strip()
            if source_id and source_id not in allowed_ids:
                findings.append(
                    _finding(
                        "block_source_not_in_skeleton",
                        f"Bloco usa fonte que não foi selecionada ou adicionada com revisão: {source_id}.",
                        f"contexto.blocos[{index}].source_ids",
                    )
                )

    return {
        "status": "BLOCK" if any(item.get("severity") == "erro" for item in findings) else "PASS",
        "findings": findings,
        "selected_source_ids": sorted(selected_ids),
        "late_source_ids": sorted(allowed_ids - selected_ids),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validar esqueleto e fontes selecionadas")
    parser.add_argument("--context", required=True, type=Path)
    parser.add_argument("--state-dir", type=Path, default=None)
    args = parser.parse_args()
    context = json.loads(args.context.read_text(encoding="utf-8"))
    report = validate_skeleton(context, args.state_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
