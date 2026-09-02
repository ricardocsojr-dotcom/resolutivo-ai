#!/usr/bin/env python3
"""Consulta read-only do Ementário e prepara recibos para o workflow RDAA.

Este módulo não decide tese nem grava no Ementário. A escrita naquele vault
continua exclusiva do fluxo transacional claude-obsidian executado no WSL.
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

DEFAULT_EMENTARIO_ROOT = Path(r"\\wsl.localhost\Ubuntu\home\ricar\vaults\ementario-resolutivo")
_LINK_PATTERN = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
_DOMAIN_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_LEGACY_MATTER_METADATA = re.compile(r"(?im)^-\s*(?:\*\*)?(?:Arquivo|Matéria|Cliente|Processo) de origem.*$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        Path(temporary_name).replace(path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def _domain_path(vault_root: Path, domain: str) -> Path:
    normalized = str(domain).strip().lower()
    if not _DOMAIN_PATTERN.fullmatch(normalized):
        raise ValueError("domínio do Ementário inválido")
    return vault_root / "wiki" / "domains" / f"{normalized}.md"


def _safe_link_name(value: str) -> str | None:
    candidate = value.strip().lower()
    if not _DOMAIN_PATTERN.fullmatch(candidate):
        return None
    return candidate


def _document(vault_root: Path, path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    if "wiki/sources/" in path.relative_to(vault_root).as_posix():
        content = _LEGACY_MATTER_METADATA.sub("- [REDACTED]", content)
    return {
        "relative_path": path.relative_to(vault_root).as_posix(),
        "sha256": _sha256(path),
        "content": content,
    }


def consultar_ementario(vault_root: Path | str, domain: str, output_path: Path | str) -> dict[str, Any]:
    """Cria um pacote fechado de contexto sem alterar um único arquivo do vault."""
    root = Path(vault_root).resolve()
    manual = root / "CLAUDE.md"
    if not manual.is_file():
        raise FileNotFoundError(f"manual do Ementário ausente: {manual}")
    domain_path = _domain_path(root, domain)
    documents: list[dict[str, str]] = []
    if domain_path.is_file():
        documents.append(_document(root, domain_path))
        captured = {domain_path.relative_to(root).as_posix()}
        direct_links = [_safe_link_name(link) for link in _LINK_PATTERN.findall(domain_path.read_text(encoding="utf-8"))]
        concept_paths: list[Path] = []

        def capture(candidate: Path) -> bool:
            relative_path = candidate.relative_to(root).as_posix()
            if not candidate.is_file() or relative_path in captured:
                return False
            captured.add(relative_path)
            documents.append(_document(root, candidate))
            return True

        for link in direct_links:
            if link is None:
                continue
            candidate = root / "wiki" / "concepts" / f"{link}.md"
            if capture(candidate):
                concept_paths.append(candidate)
        for link in direct_links:
            if link is not None:
                capture(root / "wiki" / "sources" / f"{link}.md")
        for concept_path in concept_paths:
            for link in (_safe_link_name(item) for item in _LINK_PATTERN.findall(concept_path.read_text(encoding="utf-8"))):
                if link is not None:
                    capture(root / "wiki" / "sources" / f"{link}.md")
    package = {
        "schema_version": "1",
        "captured_at": _now(),
        "origin": "ementario-resolutivo",
        "status": "informada",
        "mode": "read_only",
        "vault_root": str(root),
        "vault_manual_sha256": _sha256(manual),
        "domain": str(domain).strip().lower(),
        "domain_found": domain_path.is_file(),
        "documents": documents,
    }
    _write_json(Path(output_path), package)
    return package


def preparar_registro_ementario(
    state_dir: Path | str,
    artifact_path: Path | str,
    output_path: Path | str,
) -> dict[str, Any]:
    """Prepara uma solicitação de ingestão; não simula escrita nem recibo."""
    artifact = Path(artifact_path).resolve()
    if not artifact.is_file():
        raise FileNotFoundError(f"artefato para registro ausente: {artifact}")
    request = {
        "schema_version": "1",
        "created_at": _now(),
        "vault": "ementario-resolutivo",
        "status": "pending_external_ingest",
        "required_runner": "claude-obsidian via WSL",
        "matter_state_dir": str(Path(state_dir).resolve()),
        "artifact_path": str(artifact),
        "artifact_sha256": _sha256(artifact),
    }
    _write_json(Path(output_path), request)
    return request


def main() -> int:
    parser = argparse.ArgumentParser(description="Integração determinística RDAA ↔ Obsidian")
    commands = parser.add_subparsers(dest="command", required=True)

    lookup = commands.add_parser("consultar-ementario", help="gera contexto read-only do Ementário")
    lookup.add_argument("--domain", required=True)
    lookup.add_argument("--output", type=Path, required=True)
    lookup.add_argument("--vault-root", type=Path, default=Path(os.environ.get("RDAA_EMENTARIO_VAULT", DEFAULT_EMENTARIO_ROOT)))

    request = commands.add_parser("preparar-registro-ementario", help="gera solicitação para claude-obsidian")
    request.add_argument("--state-dir", type=Path, required=True)
    request.add_argument("--artifact", type=Path, required=True)
    request.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "consultar-ementario":
        result = consultar_ementario(args.vault_root, args.domain, args.output)
        result = {
            "origin": result["origin"],
            "status": result["status"],
            "mode": result["mode"],
            "domain": result["domain"],
            "domain_found": result["domain_found"],
            "documents_count": len(result["documents"]),
            "output": str(args.output.resolve()),
        }
    else:
        result = preparar_registro_ementario(args.state_dir, args.artifact, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
