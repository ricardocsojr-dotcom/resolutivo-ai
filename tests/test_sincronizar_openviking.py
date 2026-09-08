import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "redigir-peca" / "scripts" / "sincronizar_openviking.py"
SPEC = importlib.util.spec_from_file_location("sincronizar_openviking", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_build_write_command_uses_stable_uri_and_vectors_only(tmp_path):
    cerebro = tmp_path / "cerebro"
    source = cerebro / "wiki" / "operacional" / "matter-teste.md"
    source.parent.mkdir(parents=True)
    source.write_text("# matéria", encoding="utf-8")

    command = MODULE.build_write_command(
        source,
        viking_uri="viking://resources/resolutivo-ai/operacional/matter-teste.md",
        cerebro_root=cerebro,
        processing_mode="vectors_only",
        timeout=120,
        write_mode="create",
    )

    assert command[:2] == ["ov", "write"]
    assert str(source.resolve()) in command
    assert "viking://resources/resolutivo-ai/operacional/matter-teste.md" in command
    assert command[command.index("--mode") + 1] == "create"
    assert command[command.index("--processing-mode") + 1] == "vectors_only"
    assert "--watch-interval" not in command


def test_build_write_command_rejects_path_outside_cerebro(tmp_path):
    cerebro = tmp_path / "cerebro"
    source = tmp_path / "outside.md"
    source.write_text("fora", encoding="utf-8")

    with pytest.raises(ValueError, match="fora da raiz confiável"):
        MODULE.build_write_command(
            source,
            viking_uri="viking://resources/resolutivo-ai/operacional/outside.md",
            cerebro_root=cerebro,
            processing_mode="vectors_only",
            timeout=120,
            write_mode="create",
        )


def test_sync_creates_stable_file_and_receipt(tmp_path):
    cerebro = tmp_path / "cerebro"
    source = cerebro / "wiki" / "operacional"
    source.mkdir(parents=True)
    (source / "matter-teste.md").write_text("# matéria", encoding="utf-8")
    receipt = tmp_path / "OPENVIKING-RECIBO.json"
    calls = []

    def runner(command):
        calls.append(list(command))
        if command[1] == "mkdir":
            return 0, '{"status":"success"}', ""
        return 0, json.dumps({
            "ok": True,
            "result": {
                "uri": "viking://resources/resolutivo-ai/operacional/matter-teste.md",
                "root_uri": "viking://resources/resolutivo-ai/operacional",
                "mode": "create",
                "content_updated": True,
                "vector_status": "complete",
            },
        }), ""

    result = MODULE.sync_path(
        source,
        cerebro_root=cerebro,
        receipt_path=receipt,
        processing_mode="vectors_only",
        runner=runner,
    )

    assert result["success"] is True
    assert result["files_synced"] == 1
    assert result["files_skipped"] == 0
    assert receipt.is_file()
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    assert payload["status"] == "registered"
    assert payload["collection_uri"] == "viking://resources/resolutivo-ai/operacional"
    assert any(command[1] == "write" for command in calls)
    assert json.loads((cerebro / ".openviking-sync-state.json").read_text(encoding="utf-8"))["files"]


def test_sync_recovers_partial_create_by_replacing_same_uri(tmp_path):
    cerebro = tmp_path / "cerebro"
    source = cerebro / "wiki" / "operacional"
    source.mkdir(parents=True)
    (source / "matter-teste.md").write_text("versão", encoding="utf-8")
    calls = []

    def runner(command):
        calls.append(list(command))
        if command[1] == "mkdir":
            return 0, '{"status":"success"}', ""
        if command[command.index("--mode") + 1] == "create":
            return 1, '{"ok":false,"error":{"code":"ALREADY_EXISTS"}}', ""
        return 0, '{"ok":true,"result":{"vector_status":"complete","content_updated":true}}', ""

    result = MODULE.sync_path(source, cerebro_root=cerebro, runner=runner)

    assert result["success"] is True
    write_commands = [command for command in calls if command[1] == "write"]
    assert [command[command.index("--mode") + 1] for command in write_commands] == ["create", "replace"]


def test_sync_replaces_changed_file_without_creating_duplicate(tmp_path):
    cerebro = tmp_path / "cerebro"
    source = cerebro / "wiki" / "operacional"
    source.mkdir(parents=True)
    file_path = source / "matter-teste.md"
    file_path.write_text("versão 1", encoding="utf-8")
    calls = []

    def runner(command):
        calls.append(list(command))
        if command[1] == "mkdir":
            return 0, '{"status":"success"}', ""
        return 0, json.dumps({"ok": True, "result": {"status": "success", "vector_status": "complete"}}), ""

    first = MODULE.sync_path(source, cerebro_root=cerebro, runner=runner)
    assert first["success"] is True
    file_path.write_text("versão 2", encoding="utf-8")
    calls.clear()
    second = MODULE.sync_path(source, cerebro_root=cerebro, runner=runner)

    assert second["success"] is True
    assert second["files_synced"] == 1
    write_commands = [command for command in calls if command[1] == "write"]
    assert write_commands
    assert write_commands[0][write_commands[0].index("--mode") + 1] == "replace"


def test_sync_does_not_write_receipt_on_command_failure(tmp_path):
    cerebro = tmp_path / "cerebro"
    source = cerebro / "wiki" / "operacional"
    source.mkdir(parents=True)
    (source / "matter-teste.md").write_text("# matéria", encoding="utf-8")
    receipt = tmp_path / "OPENVIKING-RECIBO.json"

    def runner(command):
        if command[1] == "mkdir":
            return 0, '{"status":"success"}', ""
        return 2, "", "server unavailable"

    result = MODULE.sync_path(source, cerebro_root=cerebro, receipt_path=receipt, runner=runner)

    assert result["success"] is False
    assert not receipt.exists()
    assert "server unavailable" in result["error"]
