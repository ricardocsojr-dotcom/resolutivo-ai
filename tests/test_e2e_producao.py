"""Integração do fluxo produtivo C, sem rede nem escrita no vault real."""

from pathlib import Path
import shutil

from orquestracao import cli
from orquestracao.contracts import ContractError
from orquestracao import system_handlers as sh


class Args:
    def __init__(self, **values):
        self.__dict__.update(values)


def json_result(payload, exit_code):
    return {"payload": payload, "exit_code": exit_code}


def start_args(tmp_path: Path) -> Args:
    return Args(state_dir=str(tmp_path), level="C", matter_id="MAT-01", route=None)


def resume_args(tmp_path: Path) -> Args:
    return Args(state_dir=str(tmp_path), authority="ricardo", reason="artefato manual salvo")


def prepare_writer_input(tmp_path: Path) -> None:
    packages = tmp_path / "packages"
    packages.mkdir(exist_ok=True)
    (packages / "writer-input.md").write_text("# Manifestação\n\nTexto da peça.", encoding="utf-8")


def test_e2e_producao_fluxo_feliz(monkeypatch, tmp_path):
    qa_calls = []
    publication_calls = []
    vault_calls = []

    def fake_qa(docx, context):
        qa_calls.append((docx, context))
        assert docx.is_file()
        assert context.is_file()
        return {"status": "PASS"}

    def fake_publish(candidate, output, *, context_path, **kwargs):
        publication_calls.append((candidate, output, context_path))
        assert candidate.is_file()
        assert context_path.is_file()
        shutil.copyfile(candidate, output)
        return {"status": "PUBLISHED", "output_path": str(output)}

    def fake_vault(state_dir, matter_id, level):
        vault_calls.append((state_dir, matter_id, level))
        assert (state_dir / "contexto_peca.json").is_file()
        return {"success": True, "receipt": str(state_dir / "CEREBRO-RECIBO.json")}

    monkeypatch.setattr(cli, "_json_out", json_result)
    monkeypatch.setattr(sh, "run_qa_gate", fake_qa)
    monkeypatch.setattr(sh, "publicar_docx", fake_publish)
    monkeypatch.setattr(sh, "registrar_cerebro", fake_vault)

    blocked = cli.cmd_start(start_args(tmp_path))
    assert blocked["exit_code"] == 1
    assert blocked["payload"]["status"] == "failed"
    assert "writer-input.md" in blocked["payload"]["_worker_error"]

    prepare_writer_input(tmp_path)
    completed = cli.cmd_resume(resume_args(tmp_path))

    assert completed["exit_code"] == 0
    assert completed["payload"]["status"] == "vault_registered"
    assert qa_calls and publication_calls and vault_calls
    candidate, published, context = publication_calls[0]
    assert candidate == qa_calls[0][0]
    assert context == qa_calls[0][1]
    assert published.is_file()


def test_qa_fail_impede_publicacao_e_vault(monkeypatch, tmp_path):
    publication_called = False
    vault_called = False

    def fail_qa(*args):
        return {"status": "FAIL", "errors": ["formatação"]}

    def publish(*args, **kwargs):
        nonlocal publication_called
        publication_called = True

    def vault(*args):
        nonlocal vault_called
        vault_called = True

    monkeypatch.setattr(cli, "_json_out", json_result)
    monkeypatch.setattr(sh, "run_qa_gate", fail_qa)
    monkeypatch.setattr(sh, "publicar_docx", publish)
    monkeypatch.setattr(sh, "registrar_cerebro", vault)

    cli.cmd_start(start_args(tmp_path))
    prepare_writer_input(tmp_path)
    result = cli.cmd_resume(resume_args(tmp_path))

    assert result["exit_code"] == 1
    assert result["payload"]["status"] == "failed"
    assert "QA reprovado" in result["payload"]["_worker_error"]
    assert not publication_called
    assert not vault_called


def test_publicacao_falha_impede_vault(monkeypatch, tmp_path):
    vault_called = False

    def pass_qa(*args):
        return {"status": "PASS"}

    def fail_publish(*args, **kwargs):
        raise ContractError("falha de publicação")

    def vault(*args):
        nonlocal vault_called
        vault_called = True

    monkeypatch.setattr(cli, "_json_out", json_result)
    monkeypatch.setattr(sh, "run_qa_gate", pass_qa)
    monkeypatch.setattr(sh, "publicar_docx", fail_publish)
    monkeypatch.setattr(sh, "registrar_cerebro", vault)

    cli.cmd_start(start_args(tmp_path))
    prepare_writer_input(tmp_path)
    result = cli.cmd_resume(resume_args(tmp_path))

    assert result["exit_code"] == 1
    assert result["payload"]["status"] == "failed"
    assert "falha de publicação" in result["payload"]["_worker_error"]
    assert not vault_called
