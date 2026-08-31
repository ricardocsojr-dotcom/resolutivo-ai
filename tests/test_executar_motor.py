import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "redigir-peca" / "scripts" / "executar_motor.py"
SPEC = importlib.util.spec_from_file_location("executar_motor", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_motores_usam_entrada_direta_e_so_gravam_no_sucesso(tmp_path):
    prompt = tmp_path / "prompt.md"
    prompt.write_text("analise isto", encoding="utf-8")

    with patch.object(MODULE.subprocess, "run") as run:
        run.return_value.returncode = 0
        run.return_value.stdout = "rascunho\n"
        run.return_value.stderr = ""
        codex_out = tmp_path / "codex.md"
        MODULE.executar("codex", prompt, codex_out, None, 30)
        assert run.call_args.args[0][0:2] == ["codex", "exec"]
        assert run.call_args.kwargs["input"] == "analise isto"
        assert codex_out.read_text(encoding="utf-8") == "rascunho\n"

        run.return_value.stdout = json.dumps(
            {"event": "result", "result": {"status": "SUCCESS", "response": "crítica"}},
            ensure_ascii=False,
        )
        agy_out = tmp_path / "agy.md"
        MODULE.executar("antigravity", prompt, agy_out, None, 30)
        command = run.call_args.args[0]
        assert command[0] == "agy" and "stream-json" in command
        assert "dangerously-skip-permissions" not in " ".join(command)
        assert json.loads(run.call_args.kwargs["input"])["message"]["content"] == "analise isto"
        assert agy_out.read_text(encoding="utf-8") == "crítica\n"
