"""Testes dos handlers de sistema concretos (orquestracao/system_handlers.py).

Usa monkeypatch para isolar dos servicos reais (services/qa.py,
services/publicacao.py, services/memoria.py).
"""

from pathlib import Path
import pytest
from orquestracao.contracts import ContractError
from orquestracao import system_handlers as sh


def test_find_candidate_artifacts_prioriza_validator(tmp_path):
    w_docx = tmp_path / "writer.docx"
    w_ctx = tmp_path / "writer.json"
    v_docx = tmp_path / "validator.docx"
    v_ctx = tmp_path / "validator.json"

    for f in (w_docx, w_ctx, v_docx, v_ctx):
        f.touch()

    state = {
        "outputs": {
            "writer": {"docx_path": str(w_docx), "context_path": str(w_ctx)},
            "validator": {"docx_path": str(v_docx), "context_path": str(v_ctx)},
        }
    }

    docx_path, context_path = sh._find_candidate_artifacts(state)
    assert docx_path == v_docx
    assert context_path == v_ctx


def test_find_candidate_artifacts_ausente_levanta_contract_error():
    with pytest.raises(ContractError):
        sh._find_candidate_artifacts({"outputs": {}})


def test_find_candidate_artifacts_reconstroi_pacote_validado(tmp_path, monkeypatch):
    state_dir = tmp_path / "state"
    packages = state_dir / "packages"
    packages.mkdir(parents=True)
    (packages / "validator-001.md").write_text("Texto validado.", encoding="utf-8")
    rebuilt_docx = tmp_path / "rebuilt.docx"
    rebuilt_context = tmp_path / "rebuilt.json"
    rebuilt_docx.touch()
    rebuilt_context.touch()

    from orquestracao import production_worker as pw
    monkeypatch.setattr(
        pw,
        "_compile_docx",
        lambda state, role, text: {
            "docx_path": str(rebuilt_docx),
            "context_path": str(rebuilt_context),
        },
    )
    state = {
        "state_dir": str(state_dir),
        "outputs": {"validator": {"docx_path": "ausente.docx", "context_path": "ausente.json"}},
    }

    assert sh._find_candidate_artifacts(state) == (rebuilt_docx, rebuilt_context)


def test_handle_qa_passed_delega_para_servico_qa(tmp_path, monkeypatch):
    docx = tmp_path / "candidate.docx"
    ctx = tmp_path / "context.json"
    docx.touch()
    ctx.touch()

    def fake_run_qa_gate(path, context_path=None):
        assert path == docx
        assert context_path == ctx
        return {"status": "PASS", "checks": []}

    monkeypatch.setattr(sh, "run_qa_gate", fake_run_qa_gate)

    state = {"outputs": {"writer": {"docx_path": str(docx), "context_path": str(ctx)}}}
    result = sh.handle_qa_passed(state)
    assert result["qa_result"]["status"] == "PASS"


def test_handle_qa_passed_reprovado_levanta_erro(tmp_path, monkeypatch):
    docx = tmp_path / "candidate.docx"
    ctx = tmp_path / "context.json"
    docx.touch()
    ctx.touch()

    monkeypatch.setattr(
        sh, "run_qa_gate",
        lambda path, context_path=None: {"status": "FAIL", "errors": ["formatacao"]},
    )

    state = {"outputs": {"writer": {"docx_path": str(docx), "context_path": str(ctx)}}}
    with pytest.raises(ContractError, match="QA reprovado"):
        sh.handle_qa_passed(state)


def test_handle_published_delega_com_target_opcional(tmp_path, monkeypatch):
    docx = tmp_path / "candidate.docx"
    ctx = tmp_path / "context.json"
    docx.touch()
    ctx.touch()

    def fake_publicar_docx(docx_path, output_path, state_dir, context_path, skip_cerebro):
        assert docx_path == docx
        assert context_path == ctx
        assert output_path.name == "peca_123.docx"
        output_path.touch()
        return {"status": "PUBLISHED", "manifesto_path": str(output_path)}

    monkeypatch.setattr(sh, "publicar_docx", fake_publicar_docx)

    state_dir = tmp_path / "state"
    state_dir.mkdir()
    state = {
        "state_dir": str(state_dir),
        "matter_id": "peca_123",
        "outputs": {"writer": {"docx_path": str(docx), "context_path": str(ctx)}},
    }
    result = sh.handle_published(state)
    assert "peca_123.docx" in result["manifesto_path"]
    assert (state_dir / "contexto_peca.json").read_bytes() == ctx.read_bytes()


def test_handle_published_sem_arquivo_final_levanta_contract_error(tmp_path, monkeypatch):
    docx = tmp_path / "candidate.docx"
    ctx = tmp_path / "context.json"
    docx.touch()
    ctx.touch()
    monkeypatch.setattr(sh, "publicar_docx", lambda *args, **kwargs: {"status": "PUBLISHED"})

    state_dir = tmp_path / "state"
    state_dir.mkdir()
    state = {
        "state_dir": str(state_dir),
        "matter_id": "peca_123",
        "outputs": {"writer": {"docx_path": str(docx), "context_path": str(ctx)}},
    }
    with pytest.raises(ContractError, match="não criou o arquivo final"):
        sh.handle_published(state)


def test_handle_vault_registered_delega_com_matter_id(tmp_path, monkeypatch):
    def fake_registrar_cerebro(state_dir, matter, nivel):
        assert matter == "peca_456"
        assert nivel == "B"
        return {"success": True, "referencia_cerebro": "CER-01"}

    monkeypatch.setattr(sh, "registrar_cerebro", fake_registrar_cerebro)

    state = {
        "state_dir": str(tmp_path),
        "matter_id": "peca_456",
        "nivel_peca": "B",
    }
    result = sh.handle_vault_registered(state)
    assert result["referencia_cerebro"] == "CER-01"


def test_handle_vault_registered_rejeita_resultado_sem_sucesso(tmp_path, monkeypatch):
    monkeypatch.setattr(sh, "registrar_cerebro", lambda *args: {"success": False, "error": "offline"})
    state = {"state_dir": str(tmp_path), "matter_id": "peca_456", "nivel_peca": "B"}
    with pytest.raises(ContractError, match="registro no Cérebro-Ricar falhou"):
        sh.handle_vault_registered(state)
