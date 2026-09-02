#!/usr/bin/env python3
"""Executa workers de IA diretamente, sem agente-wrapper."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ponytail: mesmo fix de construir_peca.py/verificar_formatacao.py/qa_gate.py
# — sem isso, mensagem de erro com acento sai como mojibake no Windows.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
MAX_OUTPUT_BYTES = 16 * 1024 * 1024


def _executavel(name: str) -> str:
    """Resolve wrappers .EXE/.CMD no Windows antes do subprocesso."""
    return shutil.which(name) or name


def executar(
    motor: str,
    prompt_path: Path,
    output_path: Path,
    schema: Path | None,
    timeout: int,
    effort: str = "medium",
    *,
    state_dir: Path | None = None,
    role: str | None = None,
    max_budget_usd: float | None = 1.0,
) -> dict[str, object]:
    """Executa um trabalhador isolado e devolve metadados para o manifesto."""
    if (state_dir is None) != (role is None):
        raise ValueError("state_dir e role devem ser informados juntos")
    if state_dir is not None and role is not None:
        _validar_no_manifesto(state_dir, role, motor)
    prompt = prompt_path.read_text(encoding="utf-8")
    if not prompt.strip():
        raise ValueError("prompt vazio")

    if motor == "codex":
        cmd = [
            _executavel("codex"), "exec", "--ephemeral", "--sandbox", "read-only",
            "--color", "never", "-C", str(ROOT), "-",
        ]
        stdin = prompt
    elif motor == "antigravity":
        cmd = [
            _executavel("agy"), "--sandbox", "--input-format", "stream-json", "--output-format", "stream-json",
            "--effort", effort,
        ]
        if schema:
            cmd += ["--json-schema", str(schema)]
        stdin = json.dumps({"event": "user", "message": {"content": prompt}}, ensure_ascii=False) + "\n"
    elif motor == "claude":
        cmd = [
            _executavel("claude"), "-p", "Use integralmente o pacote anexado pela entrada padrão e responda somente com o resultado solicitado.",
            "--output-format", "json", "--no-session-persistence", "--tools", "", "--max-turns", "1",
        ]
        if max_budget_usd is not None:
            cmd += ["--max-budget-usd", str(max_budget_usd)]
        if schema:
            cmd += ["--json-schema", schema.read_text(encoding="utf-8")]
        stdin = prompt
    else:
        raise ValueError(f"motor não suportado: {motor}")

    started = time.monotonic()
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    duration_ms = round((time.monotonic() - started) * 1000)
    if result.returncode:
        diagnostic = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(diagnostic or f"{motor} encerrou com código {result.returncode}")
    if len(result.stdout.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise RuntimeError(f"{motor} excedeu o limite de saída de 16 MiB")

    session_id = None
    model_ids: list[str] = []
    usage: dict[str, object] = {}
    if motor == "codex":
        content = result.stdout.strip()
    elif motor == "antigravity":
        content = _resultado_antigravity(result.stdout, bool(schema))
    else:
        content, session_id, model_ids, usage = _resultado_claude(result.stdout, bool(schema))
    if not content:
        raise RuntimeError(f"{motor} não devolveu conteúdo")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content + "\n", encoding="utf-8")
    metadata: dict[str, object] = {
        "motor": motor,
        "output_path": str(output_path),
        "duration_ms": duration_ms,
        "session_id": session_id,
        "model_ids": model_ids,
        "usage": usage,
    }
    if state_dir is not None and role is not None:
        metadata["manifest_record"] = _registrar_no_manifesto(
            state_dir, role, motor, prompt_path, output_path, metadata
        )
    return metadata


def _validar_no_manifesto(state_dir: Path, role: str, motor: str) -> None:
    path = Path(__file__).with_name("orquestrador_rdaa.py")
    spec = importlib.util.spec_from_file_location("orquestrador_rdaa", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    module.validar_inicio_worker(state_dir, role, motor)


def _registrar_no_manifesto(
    state_dir: Path, role: str, motor: str, prompt_path: Path, output_path: Path, metadata: dict[str, object]
) -> dict[str, object]:
    path = Path(__file__).with_name("orquestrador_rdaa.py")
    spec = importlib.util.spec_from_file_location("orquestrador_rdaa", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.registrar_execucao(
        state_dir,
        role=role,
        motor=motor,
        prompt_path=prompt_path,
        output_path=output_path,
        metadata=metadata,
    )


def _resultado_antigravity(stdout: str, structured: bool) -> str:
    events = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    event = next((item for item in reversed(events) if item.get("event") == "result"), None)
    final = event.get("result") if event else None
    if not final or final.get("status") != "SUCCESS":
        raise RuntimeError("Antigravity não devolveu um resultado válido")
    value = final.get("structured_output") if structured else final.get("response")
    if value is None:
        raise RuntimeError("Antigravity não devolveu um resultado válido")
    return json.dumps(value, ensure_ascii=False, indent=2) if structured else str(value or "")


def _resultado_claude(stdout: str, structured: bool) -> tuple[str, str | None, list[str], dict[str, object]]:
    try:
        result = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Claude não devolveu JSON válido") from exc
    if result.get("type") != "result" or result.get("subtype") != "success":
        raise RuntimeError("Claude não devolveu um resultado válido")
    value = result.get("structured_output") if structured else result.get("result")
    if value is None:
        raise RuntimeError("Claude não devolveu um resultado válido")
    content = json.dumps(value, ensure_ascii=False, indent=2) if structured else str(value or "")
    model_usage = result.get("modelUsage") or {}
    model_ids = sorted(str(model_id) for model_id in model_usage if model_id)
    usage = {
        key: result[key]
        for key in ("usage", "total_cost_usd", "duration_ms", "num_turns")
        if key in result
    }
    return content, result.get("session_id"), model_ids, usage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("motor", choices=("codex", "antigravity", "claude"))
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--effort", choices=("low", "medium", "high"), default="medium")
    parser.add_argument("--max-budget-usd", type=float, default=1.0, help="limite por chamada Claude; use valor negativo para desativar")
    parser.add_argument("--state-dir", type=Path)
    parser.add_argument("--role", choices=("planner", "writer", "critic", "validator"))
    args = parser.parse_args()
    executar(
        args.motor,
        args.prompt,
        args.output,
        args.schema,
        args.timeout,
        args.effort,
        state_dir=args.state_dir,
        role=args.role,
        max_budget_usd=None if args.max_budget_usd < 0 else args.max_budget_usd,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
