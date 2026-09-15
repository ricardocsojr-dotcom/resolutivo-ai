"""Contract tests for direct, tool-free RDAA worker execution."""

from __future__ import annotations

import json
import subprocess

from orquestracao.contracts import Packet
from orquestracao import direct_workers
from orquestracao.direct_workers import DirectWorkerClient


def _packet() -> Packet:
    return Packet(
        role="planner",
        combo="claude-sonnet-5",
        system_prompt="Produza somente o esqueleto solicitado.",
        user_prompt="Fatos mínimos.",
        matter_id="TESTE-001",
        phase="sources_ready",
    )


def test_claude_worker_isolated_from_tools_memory_and_project_context(monkeypatch):
    captured = {}
    response = {
        "type": "result",
        "subtype": "success",
        "result": "# Esqueleto\n\n1. Fatos",
        "modelUsage": {"claude-sonnet-5": {}},
    }

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(cmd, 0, json.dumps(response), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    content, execution = DirectWorkerClient().send("claude", _packet())

    assert content == "# Esqueleto\n\n1. Fatos"
    assert execution["engine"] == "claude"
    assert execution["requested_model"] == "claude-sonnet-5"
    assert "--tools" in captured["cmd"]
    assert captured["cmd"][captured["cmd"].index("--tools") + 1] == ""
    assert "--no-session-persistence" in captured["cmd"]
    assert "--disable-slash-commands" in captured["cmd"]
    assert "--mcp-config" not in captured["cmd"]
    assert "rdaa-worker-" in captured["kwargs"]["cwd"]
    assert captured["cmd"][captured["cmd"].index("-p") + 1] == "Use o pacote recebido por stdin e responda somente com o artefato solicitado."
    assert "Fatos mínimos." in captured["kwargs"]["input"]


def test_claude_worker_repassa_effort_do_packet(monkeypatch):
    captured = {}
    response = {"type": "result", "subtype": "success", "result": "OK"}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0, json.dumps(response), "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    packet = Packet(
        role="planner",
        combo="claude-sonnet-5",
        system_prompt="Planeje.",
        user_prompt="Fatos.",
        matter_id="TESTE-001",
        phase="sources_ready",
        effort="high",
    )

    DirectWorkerClient().send("claude", packet)

    assert captured["cmd"][captured["cmd"].index("--effort") + 1] == "high"


def test_codex_worker_repassa_effort_do_packet(monkeypatch):
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0, "resposta", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    packet = Packet(
        role="writer",
        combo="gpt-6-astra",
        system_prompt="Redija.",
        user_prompt="Esqueleto.",
        matter_id="TESTE-001",
        phase="drafting",
        effort="high",
    )

    DirectWorkerClient().send("codex", packet)

    assert captured["cmd"][captured["cmd"].index("-c") + 1] == 'model_reasoning_effort="high"'


def test_antigravity_worker_usa_effort_do_packet_nao_hardcoded():
    packet = Packet(
        role="critic",
        combo="gemini-3.7-flash",
        system_prompt="Critique.",
        user_prompt="Rascunho.",
        matter_id="TESTE-001",
        phase="criticizing",
        effort="low",
    )

    command, _ = DirectWorkerClient._command("antigravity", packet)

    assert command[command.index("--effort") + 1] == "low"


def test_worker_ignora_limpeza_temporaria_bloqueada_por_cli(monkeypatch):
    temporary_directory = {}
    response = {"type": "result", "subtype": "success", "result": "OK"}

    class TemporaryDirectory:
        def __init__(self, *args, **kwargs):
            temporary_directory["kwargs"] = kwargs

        def __enter__(self):
            return "C:/temp/rdaa-worker-isolated"

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(direct_workers.tempfile, "TemporaryDirectory", TemporaryDirectory)
    monkeypatch.setattr(
        direct_workers.subprocess,
        "run",
        lambda cmd, **kwargs: subprocess.CompletedProcess(cmd, 0, json.dumps(response), ""),
    )

    content, _ = DirectWorkerClient().send("claude", _packet())

    assert content == "OK"
    assert temporary_directory["kwargs"]["ignore_cleanup_errors"] is True


def test_antigravity_worker_usa_effort_padrao_quando_nao_especificado():
    packet = Packet(
        role="critic",
        combo="gemini-3.7-flash",
        system_prompt="Critique.",
        user_prompt="Rascunho.",
        matter_id="TESTE-001",
        phase="criticizing",
    )

    command, _ = DirectWorkerClient._command("antigravity", packet)

    assert command[command.index("--effort") + 1] == "medium"
