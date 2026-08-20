#!/usr/bin/env python3
"""Promove um índice candidato para uma cópia do manifesto após homologação.

A promoção exige proveniência completa, hash do CSV normalizado, caso dourado
aprovado, tolerância explícita e responsável pela aprovação. O manifesto de
origem nunca é sobrescrito pelo script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


class PromotionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def error(code: str, message: str) -> PromotionError:
    return PromotionError(code, message)


def obj(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise error("objeto_invalido", f"{field} deve ser objeto JSON.")
    return value


def required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise error("campo_obrigatorio_ausente", f"{field} é obrigatório.")
    return value.strip()


def decimal(value: Any, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise error("decimal_invalido", f"{field} deve ser decimal explícito.") from exc
    if not result.is_finite() or result < 0:
        raise error("decimal_invalido", f"{field} deve ser decimal finito não negativo.")
    return result


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise error("json_invalido", f"{label} inválido: {exc}.") from exc
    return obj(payload, label)


def promote(*, manifest_path: Path, candidate_path: Path, normalized_csv: Path, golden_path: Path, output_manifest: Path) -> None:
    candidate = load_json(candidate_path, "candidate")
    golden = load_json(golden_path, "caso_dourado")
    manifest = load_json(manifest_path, "manifesto")
    if candidate.get("status") != "candidato":
        raise error("candidato_status_invalido", "O pacote precisa estar com status candidato.")
    if golden.get("status") != "aprovado":
        raise error("caso_dourado_nao_aprovado", "O caso dourado precisa estar com status aprovado.")
    approved_by = required_text(golden.get("aprovado_por"), "caso_dourado.aprovado_por")
    required_text(golden.get("formula_referencia"), "caso_dourado.formula_referencia")
    required_text(golden.get("convencao_declarada"), "caso_dourado.convencao_declarada")
    expected = decimal(golden.get("resultado_esperado"), "caso_dourado.resultado_esperado")
    observed = decimal(golden.get("resultado_observado"), "caso_dourado.resultado_observado")
    tolerance = decimal(golden.get("tolerancia"), "caso_dourado.tolerancia")
    if abs(expected - observed) > tolerance:
        raise error("caso_dourado_divergente", "Resultado observado excede a tolerância aprovada.")

    index_name = required_text(candidate.get("indice"), "candidate.indice")
    definition = obj(candidate.get("definicao_proposta"), "candidate.definicao_proposta")
    provenance = obj(candidate.get("proveniencia"), "candidate.proveniencia")
    integrity = obj(candidate.get("integridade"), "candidate.integridade")
    for field in ("autoridade_primaria", "url_ou_localizacao", "codigo_serie", "data_coleta", "arquivo_bruto", "sha256_arquivo_bruto"):
        required_text(provenance.get(field), f"candidate.proveniencia.{field}")
    for field in ("arquivo", "tipo_serie", "unidade", "frequencia"):
        required_text(definition.get(field), f"candidate.definicao_proposta.{field}")
    normalized_hash = required_text(integrity.get("sha256_csv_normalizado"), "candidate.integridade.sha256_csv_normalizado").lower()
    if not normalized_csv.is_file():
        raise error("csv_normalizado_inexistente", f"CSV normalizado não encontrado: {normalized_csv}.")
    actual_hash = hashlib.sha256(normalized_csv.read_bytes()).hexdigest()
    if actual_hash != normalized_hash:
        raise error("hash_csv_divergente", f"SHA-256 do CSV diverge. Esperado {normalized_hash}, encontrado {actual_hash}.")

    indices = manifest.get("indices")
    if not isinstance(indices, dict):
        raise error("manifesto_invalido", "Manifesto deve conter objeto indices.")
    existing = indices.get(index_name)
    if isinstance(existing, dict) and existing.get("status") == "aprovado":
        raise error("indice_ja_aprovado", f"Índice {index_name!r} já está aprovado e não será substituído automaticamente.")
    conventions = definition.get("convencoes")
    if not isinstance(conventions, list) or not conventions or not all(isinstance(item, str) and item.strip() for item in conventions):
        raise error("convencoes_ausentes", "candidate.definicao_proposta.convencoes deve ser lista explícita.")

    indices[index_name] = {
        "arquivo": Path(definition["arquivo"]).name,
        "tipo_serie": definition["tipo_serie"],
        "unidade": definition["unidade"],
        "status": "aprovado",
        "sha256": normalized_hash,
        "convencoes": conventions,
        "proveniencia": provenance,
        "homologacao": {
            "caso": required_text(golden.get("caso"), "caso_dourado.caso"),
            "resultado_esperado": format(expected, "f"),
            "resultado_observado": format(observed, "f"),
            "tolerancia": format(tolerance, "f"),
            "formula_referencia": golden["formula_referencia"],
            "convencao_declarada": golden["convencao_declarada"],
            "aprovado_por": approved_by,
            "data_aprovacao": required_text(golden.get("data_aprovacao"), "caso_dourado.data_aprovacao"),
        },
    }
    output_manifest.parent.mkdir(parents=True, exist_ok=True)
    output_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Promover índice candidato para cópia do manifesto")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--normalized-csv", required=True, type=Path)
    parser.add_argument("--golden", required=True, type=Path)
    parser.add_argument("--output-manifest", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        promote(manifest_path=args.manifest, candidate_path=args.candidate, normalized_csv=args.normalized_csv, golden_path=args.golden, output_manifest=args.output_manifest)
        print(json.dumps({"status": "ok", "saida_manifesto": str(args.output_manifest)}, ensure_ascii=False))
        return 0
    except PromotionError as exc:
        print(json.dumps({"status": "erro", "codigo": exc.code, "mensagem": exc.message}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
