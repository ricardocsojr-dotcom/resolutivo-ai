#!/usr/bin/env python3
"""Preparar uma fonte local de índice usando perfil técnico explícito.

O script apenas coordena o normalizador local. Não baixa fontes, não executa
macros, não promove índice e não altera o manifesto.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
NORMALIZER_PATH = Path(__file__).with_name("normalizar_indice_candidato.py")
PROFILES_PATH = ROOT / "references" / "normalization_profiles.json"


class PrepareError(ValueError):
    pass


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("normalizar_indice_candidato", NORMALIZER_PATH)
    if spec is None or spec.loader is None:
        raise PrepareError("não foi possível carregar o normalizador")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_profiles() -> dict[str, Any]:
    try:
        payload = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PrepareError(f"perfis inválidos: {exc}") from exc
    profiles = payload.get("profiles")
    if not isinstance(profiles, dict):
        raise PrepareError("normalization_profiles.json deve conter profiles")
    return profiles


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Preparar fonte local de índice como candidato")
    result.add_argument("--profile", required=True, help="ID em normalization_profiles.json")
    result.add_argument("--source", required=True, type=Path)
    result.add_argument("--indice", required=True)
    result.add_argument("--output-dir", required=True, type=Path)
    result.add_argument("--url")
    result.add_argument("--data-coleta", required=True)
    result.add_argument("--observacao", default="")
    result.add_argument("--allow-legacy-xls", action="store_true")
    result.add_argument("--decimal-comma", action="store_true")
    result.add_argument("--pdf-regex")
    result.add_argument("--pdf-date-format", default="%d/%m/%Y")
    return result


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    profiles = load_profiles()
    profile = profiles.get(args.profile)
    if not isinstance(profile, dict):
        raise PrepareError(f"perfil não encontrado: {args.profile}")
    source_format = profile.get("formato")
    if source_format == "xls" and not args.allow_legacy_xls:
        raise PrepareError("perfil XLS exige --allow-legacy-xls")
    url = args.url or profile.get("url")
    if not isinstance(url, str) or not url.strip():
        raise PrepareError("URL ou localização da fonte deve ser declarada")
    conventions = profile.get("convencao")
    if not isinstance(conventions, str) or not conventions.strip():
        raise PrepareError("perfil deve declarar convencao")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    normalizer = load_module()
    normalizer_args = argparse.Namespace(
        source=args.source,
        indice=args.indice,
        tipo_serie=profile["tipo_serie"],
        unidade=profile["unidade"],
        frequencia=profile["frequencia"],
        convencao=[conventions],
        autoridade=profile["autoridade"],
        url=url,
        codigo_serie=profile.get("codigo_serie", ""),
        data_coleta=args.data_coleta,
        observacao=args.observacao or profile.get("observacao", ""),
        output_csv=args.output_dir / f"{args.indice}.csv",
        output_json=args.output_dir / f"{args.indice}.candidate.json",
        sheet=profile.get("aba"),
        date_column=profile.get("coluna_data"),
        year_column=profile.get("coluna_ano"),
        month_column=profile.get("coluna_mes"),
        month_language=profile.get("idioma_mes", "pt-BR"),
        value_column=profile.get("coluna_valor"),
        start_row=profile.get("linha_inicial"),
        end_row=profile.get("linha_final"),
        allow_legacy_xls=args.allow_legacy_xls,
        decimal_comma=args.decimal_comma,
        pdf_regex=args.pdf_regex,
        pdf_date_format=args.pdf_date_format,
    )
    candidate = normalizer.build_candidate(normalizer_args)
    normalizer_args.output_json.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return candidate


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        candidate = prepare(args)
        print(json.dumps({"status": "ok", "indice": candidate["indice"], "saida": str(args.output_dir), "sha256_csv": candidate["integridade"]["sha256_csv_normalizado"]}, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "erro", "mensagem": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
