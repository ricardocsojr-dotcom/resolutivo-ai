"""Adaptadores diretos e isolados para workers cognitivos do RDAA.

Esta camada executa CLIs locais sem OmniRoute, Combos, memória, MCP ou
contexto do projeto. O único contexto do worker é o ``Packet`` recebido.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from orquestracao.contracts import ContractError, Packet

MAX_OUTPUT_BYTES = 16 * 1024 * 1024
SUPPORTED_ENGINES = frozenset({"claude", "codex", "antigravity"})


def _executable(name: str) -> str:
    return shutil.which(name) or name


def _prompt(packet: Packet) -> str:
    return (
        "## Instruções da etapa\n"
        f"{packet.system_prompt}\n\n"
        "## Pacote autorizado\n"
        f"{packet.user_prompt}\n\n"
        "Entregue somente o artefato previsto para esta etapa. "
        "Não use memória, ferramentas, arquivos, MCPs ou contexto externo."
    )


class DirectWorkerClient:
    """Executa o motor declarado em ambiente temporário e sem ferramentas."""

    def send(self, engine: str, packet: Packet) -> tuple[str, dict[str, Any]]:
        if engine not in SUPPORTED_ENGINES:
            raise ContractError(f"engine direto não suportado: {engine}")

        command, stdin = self._command(engine, packet)
        started = time.monotonic()
        with tempfile.TemporaryDirectory(
            prefix="rdaa-worker-", ignore_cleanup_errors=True
        ) as isolated_cwd:
            result = subprocess.run(
                command,
                cwd=isolated_cwd,
                input=stdin,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=packet.timeout_seconds,
                check=False,
            )
        duration_ms = round((time.monotonic() - started) * 1000)

        if result.returncode:
            diagnostic = result.stderr.strip() or result.stdout.strip()
            raise ContractError(diagnostic or f"{engine} encerrou com código {result.returncode}")
        if len(result.stdout.encode("utf-8")) > MAX_OUTPUT_BYTES:
            raise ContractError(f"{engine} excedeu o limite de saída de 16 MiB")

        content = self._extract_content(engine, result.stdout)
        if not content:
            raise ContractError(f"{engine} não devolveu conteúdo final")
        return content, {
            "engine": engine,
            "requested_model": packet.combo,
            "duration_ms": duration_ms,
            "transport": "direct_cli_isolated",
        }

    @staticmethod
    def _command(engine: str, packet: Packet) -> tuple[list[str], str]:
        prompt = _prompt(packet)
        if engine == "claude":
            return [
                _executable("claude"),
                "-p", "Use o pacote recebido por stdin e responda somente com o artefato solicitado.",
                "--model", packet.combo,
                "--system-prompt", "Você é um worker isolado do RDAA.",
                "--output-format", "json",
                "--no-session-persistence",
                "--disable-slash-commands",
                "--tools", "",
                "--max-turns", "1",
                "--effort", packet.effort,
            ], prompt
        if engine == "codex":
            return [
                _executable("codex"), "exec",
                "--ephemeral",
                "--ignore-user-config",
                "--ignore-rules",
                "--skip-git-repo-check",
                "--sandbox", "read-only",
                "--color", "never",
                "--model", packet.combo,
                "-c", f'model_reasoning_effort="{packet.effort}"',
                "-",
            ], prompt
        return [
            _executable("agy"),
            "--print", prompt,
            "--model", packet.combo,
            "--effort", packet.effort,
            "--sandbox",
            "--disable-slash-commands",
            "--print-timeout", f"{packet.timeout_seconds}s",
        ], ""

    @staticmethod
    def _extract_content(engine: str, stdout: str) -> str:
        if engine == "codex":
            return stdout.strip()
        if engine == "claude":
            try:
                payload = json.loads(stdout)
            except json.JSONDecodeError as exc:
                raise ContractError("Claude não devolveu JSON válido") from exc
            if payload.get("type") != "result" or payload.get("subtype") != "success":
                raise ContractError("Claude não devolveu um resultado válido")
            return str(payload.get("result") or "").strip()
        return stdout.strip()
