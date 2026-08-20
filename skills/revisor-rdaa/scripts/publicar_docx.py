"""Publicação protegida de DOCX RDAA.

O arquivo candidato é validado em estado separado antes de tocar no destino final.
Em caso de falha, o estado confirmado e o destino anterior permanecem intactos.
Em caso de aprovação, a versão anterior é copiada para backup, o novo arquivo é
substituído atomicamente e o estado candidato é promovido.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from qa_gate import run_gate  # noqa: E402
from seguro import substituir_com_backup  # noqa: E402
from estado_rdaa import (  # noqa: E402
    file_sha256,
    matter_id_from_context,
    persist_context,
    promote_candidate_state,
    update_manifest,
)
from semantica_rdaa import (  # noqa: E402
    persist_route,
    persist_semantic_review,
    record_publish_event,
    review_state,
)  # noqa: E402
from verificar_semantica_docx import verify_docx_semantics  # noqa: E402
from verificar_visual_law import verify_visual_law  # noqa: E402
from validar_esqueleto import validate_skeleton  # noqa: E402
from classificacao_peca import validate_piece_contract  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Publicação protegida de DOCX RDAA")
    parser.add_argument("--input", required=True, type=Path, help="DOCX candidato")
    parser.add_argument("--output", required=True, type=Path, help="DOCX final publicado")
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="pasta de backups; por padrão, .rdaa-backups ao lado do destino",
    )
    parser.add_argument("--qa-json", type=Path, default=None, help="resultado estruturado do gate")
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=None,
        help="pasta de estado; por padrão, .rdaa-run ao lado do destino",
    )
    parser.add_argument(
        "--context",
        type=Path,
        default=None,
        help="JSON de contexto opcional para preencher facts/provenance automaticamente",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"[ERRO] candidato não encontrado: {args.input}", file=sys.stderr)
        return 2

    context = None
    if args.context:
        if not args.context.is_file():
            print(f"[ERRO] contexto não encontrado: {args.context}", file=sys.stderr)
            return 2
        try:
            context = json.loads(args.context.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"[ERRO] contexto JSON inválido: {exc}", file=sys.stderr)
            return 2

    matter_id = matter_id_from_context(context, args.output) if context else args.output.stem
    state_dir = args.state_dir or (
        args.output.parent / ".rdaa-run" / matter_id
        if context is not None
        else args.output.parent / ".rdaa-run"
    )
    candidate_state_dir = None
    evaluation_state_dir = state_dir
    if context is not None:
        candidate_state_dir = state_dir / "candidate"
        if candidate_state_dir.exists():
            shutil.rmtree(candidate_state_dir)
        evaluation_state_dir = candidate_state_dir

    result = run_gate(args.input)
    semantic_report = None
    route = None
    visual_report = None
    skeleton_report = None
    piece_report = None
    if context is not None:
        piece_report = validate_piece_contract(context)
        if piece_report["status"] == "BLOCK":
            result["status"] = "FAIL"
            result.setdefault("errors", []).append("contrato_peca_rdaa")
        persist_context(evaluation_state_dir, context, output=args.output)
        if context.get("exigir_esqueleto") is True:
            skeleton_report = validate_skeleton(context, evaluation_state_dir)
            if skeleton_report["status"] == "BLOCK":
                result["status"] = "FAIL"
                result.setdefault("errors", []).append("esqueleto_rdaa")
        route = persist_route(evaluation_state_dir)
        state_report = review_state(evaluation_state_dir)
        docx_report = verify_docx_semantics(args.input, context)
        visual_report = verify_visual_law(args.input, context)
        findings = (
            state_report.get("findings", [])
            + docx_report.get("findings", [])
            + visual_report.get("findings", [])
            + (skeleton_report.get("findings", []) if skeleton_report else [])
            + (piece_report.get("findings", []) if piece_report else [])
        )
        blocking = [item for item in findings if item.get("severity") == "erro"]
        semantic_report = {
            **state_report,
            "status": "BLOCK" if blocking else "PASS",
            "findings": findings,
            "docx": docx_report,
            "visual_law": visual_report,
            "esqueleto": skeleton_report,
            "contrato_peca": piece_report,
            "counts": {
                "total": len(findings),
                "blocking": len(blocking),
                "alerts": sum(1 for item in findings if item.get("severity") == "alerta"),
            },
        }
        persist_semantic_review(evaluation_state_dir, semantic_report)
        if semantic_report["status"] == "BLOCK":
            result["status"] = "FAIL"
            result.setdefault("errors", []).append("semantica_rdaa")

    blocked = result["status"] != "PASS"
    record_publish_event(state_dir, blocked=blocked)
    candidate_hash = file_sha256(args.input)
    candidate_status = "REJECTED" if blocked else "APPROVED"
    candidate_manifest_updates = {
        "matter_id": matter_id,
        "output": str(args.output),
        "candidate": str(args.input),
        "phase": "candidate_rejected" if blocked else "candidate_approved",
        "status": candidate_status,
        "candidate_status": candidate_status,
        "candidate_hash": candidate_hash,
        "errors": result["errors"],
        "semantic_status": semantic_report["status"] if semantic_report else "SKIPPED",
        "semantic_findings": semantic_report["counts"] if semantic_report else None,
        "visual_law_status": visual_report["status"] if visual_report else "SKIPPED",
        "skeleton_status": skeleton_report["status"] if skeleton_report else "SKIPPED",
        "piece_contract_status": piece_report["status"] if piece_report else "SKIPPED",
        "nivel_peca": piece_report.get("nivel_peca") if piece_report else None,
        "modo_redacao": piece_report.get("modo_redacao") if piece_report else None,
        "route": route,
        "state_role": "candidate",
    }
    if candidate_state_dir is not None:
        update_manifest(evaluation_state_dir, **candidate_manifest_updates)

    update_manifest(
        state_dir,
        matter_id=matter_id,
        output=str(args.output),
        candidate=str(args.input),
        phase="candidate_rejected" if blocked else "candidate_ready",
        status="REJECTED" if blocked else "QA_PASSED",
        candidate_status=candidate_status,
        candidate_state=str(candidate_state_dir) if candidate_state_dir else None,
        candidate_hash=candidate_hash,
        confirmed_state_status="PRESERVED" if blocked else "PENDING_PROMOTION",
        errors=result["errors"],
        semantic_status=semantic_report["status"] if semantic_report else "SKIPPED",
        semantic_findings=semantic_report["counts"] if semantic_report else None,
        visual_law_status=visual_report["status"] if visual_report else "SKIPPED",
        skeleton_status=skeleton_report["status"] if skeleton_report else "SKIPPED",
        piece_contract_status=piece_report["status"] if piece_report else "SKIPPED",
        nivel_peca=piece_report.get("nivel_peca") if piece_report else None,
        modo_redacao=piece_report.get("modo_redacao") if piece_report else None,
        route=route,
    )
    if args.qa_json:
        args.qa_json.parent.mkdir(parents=True, exist_ok=True)
        args.qa_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if blocked:
        print("[ERRO] publicação bloqueada: o candidato não passou no gate RDAA")
        for name in result["errors"]:
            print(f"  - {name}")
        if semantic_report and semantic_report["status"] == "BLOCK":
            print("[INFO] revisão semântica: inconsistência estrutural objetiva encontrada")
        return 1

    backup_dir = args.backup_dir or args.output.parent / ".rdaa-backups"
    backup = substituir_com_backup(args.input, args.output, backup_dir)
    promoted_files = []
    if candidate_state_dir is not None:
        promoted_files = promote_candidate_state(candidate_state_dir, state_dir)
    confirmed_hash = file_sha256(args.output)
    update_manifest(
        state_dir,
        matter_id=matter_id,
        output=str(args.output),
        candidate=str(args.input),
        phase="published",
        status="PUBLISHED",
        candidate_status="APPROVED",
        candidate_state=str(candidate_state_dir) if candidate_state_dir else None,
        candidate_hash=candidate_hash,
        confirmed_state_status="CONFIRMED",
        confirmed_state_promoted=bool(promoted_files) if candidate_state_dir is not None else True,
        confirmed_hash=confirmed_hash,
        backup=str(backup) if backup else None,
        promoted_state_files=promoted_files,
        route=route,
    )
    print(f"[OK] DOCX publicado após QA: {args.output}")
    print(f"[INFO] backup anterior: {backup or 'não havia arquivo anterior'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
