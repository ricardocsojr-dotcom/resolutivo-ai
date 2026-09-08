#!/usr/bin/env python3
"""Sincroniza o Cérebro-Ricar com um namespace estável do OpenViking.

O Cérebro-Ricar permanece como fonte de verdade. Cada Markdown recebe uma URI
previsível em ``viking://resources/resolutivo-ai/<coleção>/``. Arquivos novos
usam ``ov write --mode create``; arquivos alterados usam ``--mode replace``.
O embedding padrão é local (``vectors_only``), sem envio ao VLM externo.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence
from urllib.parse import quote

CEREBRO_PATH = Path(r"C:\Users\ricar\cerebro-ricar")
DEFAULT_NAMESPACE = "viking://resources/resolutivo-ai"
DEFAULT_PROCESSING_MODE = "vectors_only"
DEFAULT_TIMEOUT = 300
STATE_FILENAME = ".openviking-sync-state.json"
VALID_COLLECTIONS = {"concepts", "sources", "domains", "operacional", "entities", "pessoal"}
_VALID_MODES = {"vectors_only", "semantic_and_vectors"}
Runner = Callable[[Sequence[str]], tuple[int, str, str]]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _resolve_under_root(path: Path | str, root: Path | str) -> Path:
    trusted_root = Path(root).expanduser().resolve()
    candidate = Path(path).expanduser().resolve()
    try:
        candidate.relative_to(trusted_root)
    except ValueError as exc:
        raise ValueError(f"caminho fora da raiz confiável: {candidate}") from exc
    return candidate


def _collection_for(source: Path, root: Path) -> tuple[str, Path]:
    wiki_root = _resolve_under_root(root / "wiki", root)
    try:
        relative = source.relative_to(wiki_root)
    except ValueError as exc:
        raise ValueError("fonte deve estar dentro de Cérebro-Ricar/wiki") from exc
    collection = relative.parts[0] if relative.parts else ""
    if collection not in VALID_COLLECTIONS:
        raise ValueError(f"coleção não permitida: {collection}")
    collection_root = wiki_root / collection
    if source.is_file():
        source_root = collection_root
    else:
        source_root = source
    return collection, source_root


def _markdown_inventory(source: Path, root: Path) -> list[Path]:
    candidates = [source] if source.is_file() else sorted(source.rglob("*.md"))
    files: list[Path] = []
    for candidate in candidates:
        resolved = _resolve_under_root(candidate, root)
        if resolved.suffix.lower() == ".md":
            files.append(resolved)
    return files


def _uri_segment(segment: str) -> str:
    return quote(segment, safe=".-_")


def _stable_uri(file_path: Path, root: Path) -> str:
    relative = file_path.relative_to(root / "wiki")
    return "/".join(
        [DEFAULT_NAMESPACE.rstrip("/"), *(_uri_segment(part) for part in relative.parts)]
    )


def build_write_command(
    source: Path | str,
    *,
    viking_uri: str,
    cerebro_root: Path | str = CEREBRO_PATH,
    processing_mode: str = DEFAULT_PROCESSING_MODE,
    timeout: int = DEFAULT_TIMEOUT,
    write_mode: str = "create",
) -> list[str]:
    """Build a shell-free command for one stable OpenViking resource."""
    root = Path(cerebro_root).expanduser().resolve()
    source_path = _resolve_under_root(source, root)
    if not source_path.is_file():
        raise ValueError(f"arquivo Markdown inexistente: {source_path}")
    if processing_mode not in _VALID_MODES:
        raise ValueError(f"modo de processamento inválido: {processing_mode}")
    if write_mode not in {"create", "replace"}:
        raise ValueError(f"modo de escrita inválido: {write_mode}")
    if not viking_uri.startswith(DEFAULT_NAMESPACE + "/"):
        raise ValueError("URI OpenViking fora do namespace do Resolutivo")
    if timeout <= 0:
        raise ValueError("timeout deve ser positivo")
    return [
        "ov",
        "write",
        viking_uri,
        "--from-file",
        str(source_path),
        "--mode",
        write_mode,
        "--processing-mode",
        processing_mode,
        "--wait",
        "--timeout",
        str(timeout),
        "-o",
        "json",
    ]


def _default_runner(command: Sequence[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        list(command),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def _parse_result(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        raise ValueError("OpenViking não retornou JSON")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("resposta do OpenViking não contém JSON válido")
        payload = json.loads(text[start : end + 1])
    if isinstance(payload.get("result"), dict):
        return payload["result"]
    return payload


def _run_command(command: Sequence[str], runner: Runner) -> dict[str, Any]:
    returncode, stdout, stderr = runner(command)
    if returncode != 0:
        detail = (stderr or stdout).strip() or f"ov terminou com código {returncode}"
        raise RuntimeError(detail)
    result = _parse_result(stdout)
    confirmed = result.get("status") in {"success", "ok", "completed"}
    confirmed = confirmed or result.get("vector_status") == "complete"
    confirmed = confirmed or result.get("content_updated") is True
    if not confirmed:
        raise RuntimeError(f"OpenViking não confirmou sucesso: {result}")
    return result


def _ensure_collection(collection_uri: str, runner: Runner) -> None:
    command = ["ov", "mkdir", collection_uri, "-o", "json"]
    returncode, stdout, stderr = runner(command)
    if returncode == 0:
        return
    # mkdir é idempotente para o sincronizador: se já existe, confirme por ls.
    ls_code, ls_stdout, ls_stderr = runner(["ov", "ls", collection_uri, "-o", "json"])
    if ls_code != 0:
        detail = (stderr or stdout or ls_stderr or ls_stdout).strip()
        raise RuntimeError(detail or "não foi possível criar/verificar coleção OpenViking")


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "files": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"estado OpenViking inválido: {path}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("files", {}), dict):
        raise ValueError(f"estado OpenViking inválido: {path}")
    return payload


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def sync_path(
    source: Path | str,
    *,
    cerebro_root: Path | str = CEREBRO_PATH,
    receipt_path: Path | str | None = None,
    processing_mode: str = DEFAULT_PROCESSING_MODE,
    timeout: int = DEFAULT_TIMEOUT,
    runner: Runner = _default_runner,
) -> dict[str, Any]:
    """Synchronize a file/collection and optionally emit a verifiable receipt."""
    try:
        root = Path(cerebro_root).expanduser().resolve()
        source_path = _resolve_under_root(source, root)
        collection, source_root = _collection_for(source_path, root)
        files = _markdown_inventory(source_path, root)
        collection_uri = f"{DEFAULT_NAMESPACE}/{_uri_segment(collection)}"
        state_path = root / STATE_FILENAME
        state = _load_state(state_path)
        prior_files = dict(state.get("files", {}))
        next_files = dict(prior_files)
        _ensure_collection(collection_uri, runner)

        synced = 0
        skipped = 0
        file_results: list[dict[str, Any]] = []
        for file_path in files:
            relative_key = file_path.relative_to(root).as_posix()
            digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
            uri = _stable_uri(file_path, root)
            previous = prior_files.get(relative_key, {})
            if previous.get("sha256") == digest and previous.get("uri") == uri:
                skipped += 1
                continue
            write_mode = "replace" if previous.get("uri") == uri else "create"
            try:
                remote = _run_command(
                    build_write_command(
                        file_path,
                        viking_uri=uri,
                        cerebro_root=root,
                        processing_mode=processing_mode,
                        timeout=timeout,
                        write_mode=write_mode,
                    ),
                    runner,
                )
            except RuntimeError as exc:
                if write_mode != "create" or "ALREADY_EXISTS" not in str(exc):
                    raise
                write_mode = "replace"
                remote = _run_command(
                    build_write_command(
                        file_path,
                        viking_uri=uri,
                        cerebro_root=root,
                        processing_mode=processing_mode,
                        timeout=timeout,
                        write_mode=write_mode,
                    ),
                    runner,
                )
            next_files[relative_key] = {"sha256": digest, "uri": uri}
            synced += 1
            file_results.append({"path": relative_key, "uri": uri, "mode": write_mode, "remote": remote})

        state_payload = {"version": 1, "updated_at": _now(), "files": next_files}
        _atomic_write_json(state_path, state_payload)
        result: dict[str, Any] = {
            "success": True,
            "vault": "openviking",
            "status": "registered",
            "source_path": str(source_path),
            "collection_uri": collection_uri,
            "processing_mode": processing_mode,
            "files_synced": synced,
            "files_skipped": skipped,
            "files": file_results,
            "state_path": str(state_path),
            "synced_at": _now(),
        }
        if receipt_path is not None:
            receipt = Path(receipt_path).expanduser().resolve()
            _atomic_write_json(receipt, result)
            result["receipt"] = str(receipt)
        return result
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        return {"success": False, "error": str(exc), "source_path": str(source)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza o Cérebro-Ricar com OpenViking")
    parser.add_argument("--path", required=True, type=Path)
    parser.add_argument("--cerebro-root", type=Path, default=CEREBRO_PATH)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--processing-mode", choices=sorted(_VALID_MODES), default=DEFAULT_PROCESSING_MODE)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument(
        "--watch-interval",
        type=int,
        default=0,
        help="mantido por compatibilidade; caminhos locais não aceitam watch",
    )
    args = parser.parse_args()
    if args.watch_interval:
        result = {"success": False, "error": "caminho local não pode usar watch-interval; use sincronização explícita"}
    else:
        result = sync_path(
            args.path,
            cerebro_root=args.cerebro_root,
            receipt_path=args.receipt,
            processing_mode=args.processing_mode,
            timeout=args.timeout,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
