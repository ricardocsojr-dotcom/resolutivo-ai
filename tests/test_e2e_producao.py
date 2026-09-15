"""Integração do fluxo produtivo C, sem rede nem escrita no vault real."""

from pathlib import Path
import shutil
import json
import pytest

from orquestracao import cli
from orquestracao.contracts import ContractError, Packet
from orquestracao import production_worker as pw
from orquestracao import system_handlers as sh


class Args:
    def __init__(self, **values):
        self.__dict__.update(values)


def json_result(payload, exit_code):
    return {"payload": payload, "exit_code": exit_code}


def start_args(tmp_path: Path) -> Args:
    # Nível C usa engine="chat": o Codex grava o texto redigido em
    # packages/writer-input.md ANTES de `cli start` (ver production_worker.py).
    packages = tmp_path / "packages"
    packages.mkdir(parents=True, exist_ok=True)
    writer_input = packages / "writer-input.md"
    if not writer_input.is_file():
        writer_input.write_text("# Manifestação\n\nTexto da peça.", encoding="utf-8")
    return Args(state_dir=str(tmp_path), level="C", matter_id="MAT-01", route=None)


def fake_direct_worker(monkeypatch) -> None:
    class Client:
        def send(self, engine, packet):
            return "# Manifestação\n\nTexto da peça.", {"engine": engine}

    monkeypatch.setattr(pw, "DirectWorkerClient", Client)


def test_worker_injeta_intake_cerebro_e_nucleo_rdaa(monkeypatch, tmp_path):
    packages = tmp_path / "packages"
    packages.mkdir()
    (packages / "intake.md").write_text("Fatos do teste.", encoding="utf-8")
    (packages / "planner-input.md").write_text("Recorte para planejamento.", encoding="utf-8")
    (packages / "cerebro-contexto.json").write_text("Contexto do Cérebro.", encoding="utf-8")
    captured = {}

    def builder(state, **kwargs):
        captured[state["role"]] = kwargs
        return object()

    class Client:
        def send(self, engine, packet):
            return "resultado", {"engine": engine}

    monkeypatch.setattr(pw, "DirectWorkerClient", Client)
    monkeypatch.setattr(pw, "_is_doc_producer_role", lambda *args: False)
    state = {
        "state_dir": str(tmp_path),
        "matter_id": "teste",
        "nivel_peca": "B",
        "route": {"workers": {
            "planner": {"engine": "claude"},
            "writer": {"engine": "codex"},
            "validator": {"engine": "claude"},
        }},
    }
    for role in ("planner", "writer", "validator"):
        state["role"] = role
        monkeypatch.setitem(pw._PACKET_BUILDERS, role, builder)
        pw.production_worker(role, state)

    assert captured["planner"] == {
        "facts": "Recorte para planejamento.",
        "vault_context": "Contexto do Cérebro.",
    }
    assert captured["writer"]["facts"] == "Fatos do teste."
    assert captured["writer"]["sources"] == "Contexto do Cérebro."
    assert "Fatos do teste." in captured["validator"]["sources"]
    assert "Contexto do Cérebro." in captured["validator"]["sources"]
    assert "Dois-pontos | Proibido" in captured["writer"]["style_guide"]
    assert "Dois-pontos | Proibido" in captured["validator"]["checklist"]


def test_worker_claude_usa_adapter_direto_nunca_omniroute(monkeypatch, tmp_path):
    packages = tmp_path / "packages"
    packages.mkdir()
    (packages / "intake.md").write_text("Fatos mínimos.", encoding="utf-8")
    (packages / "planner-input.md").write_text("Recorte mínimo.", encoding="utf-8")
    captured = {}

    class DirectClient:
        def send(self, engine, packet):
            captured["engine"] = engine
            captured["model"] = packet.combo
            return "# Esqueleto\n\n1. Fatos", {"engine": engine}

    def builder(state, **kwargs):
        return Packet(
            role="planner",
            combo="claude-sonnet-5",
            system_prompt="Planeje.",
            user_prompt=kwargs["facts"],
            matter_id="teste",
            phase="sources_ready",
        )

    monkeypatch.setattr(pw, "DirectWorkerClient", DirectClient, raising=False)
    monkeypatch.setitem(pw._PACKET_BUILDERS, "planner", builder)
    monkeypatch.setattr(pw, "_is_doc_producer_role", lambda *args: False)

    result = pw.production_worker("planner", {
        "state_dir": str(tmp_path),
        "matter_id": "teste",
        "nivel_peca": "B",
        "route": {"workers": {"planner": {
            "engine": "claude", "model": "claude-sonnet-5",
        }}},
    })

    assert result["content"].startswith("# Esqueleto")
    assert captured == {"engine": "claude", "model": "claude-sonnet-5"}
    assert not hasattr(pw, "OmniRouteClient")


def test_planner_recusa_intake_bruto_sem_pacote_minimo(monkeypatch, tmp_path):
    packages = tmp_path / "packages"
    packages.mkdir()
    (packages / "intake.md").write_text("fonte bruta\n" * 20_000, encoding="utf-8")

    with pytest.raises(ContractError, match="planner-input.md"):
        pw.production_worker("planner", {
            "state_dir": str(tmp_path),
            "matter_id": "teste",
            "nivel_peca": "B",
            "route": {"workers": {"planner": {
                "engine": "claude", "model": "claude-sonnet-5",
            }}},
        })


def test_candidato_final_fica_fora_do_state_dir(monkeypatch, tmp_path):
    state_dir = tmp_path / ".rdaa-run" / "materia"
    state_dir.mkdir(parents=True)
    monkeypatch.setattr(pw, "MD2RDAA_SCRIPT", Path(__file__))
    monkeypatch.setattr(pw, "CONSTRUIR_SCRIPT", Path(__file__))

    class Md2:
        @staticmethod
        def compilar_markdown_para_contexto(*args, **kwargs):
            return {}

    class Construir:
        @staticmethod
        def construir_peca(contexto, output):
            Path(output).write_bytes(b"docx")

    modules = iter((Md2, Construir))
    monkeypatch.setattr(pw, "_load_module", lambda *args: next(modules))
    result = pw._compile_docx(
        {"state_dir": str(state_dir), "matter_id": "materia", "nivel_peca": "B"},
        "validator",
        "texto",
    )

    assert state_dir.resolve() not in Path(result["docx_path"]).parents
    assert "rdaa-candidatos" in Path(result["docx_path"]).parts


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
    fake_direct_worker(monkeypatch)
    monkeypatch.setattr(sh, "run_qa_gate", fake_qa)
    monkeypatch.setattr(sh, "publicar_docx", fake_publish)
    monkeypatch.setattr(sh, "registrar_cerebro", fake_vault)

    completed = cli.cmd_start(start_args(tmp_path))

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
    fake_direct_worker(monkeypatch)
    monkeypatch.setattr(sh, "run_qa_gate", fail_qa)
    monkeypatch.setattr(sh, "publicar_docx", publish)
    monkeypatch.setattr(sh, "registrar_cerebro", vault)

    result = cli.cmd_start(start_args(tmp_path))

    assert result["exit_code"] == 1
    assert result["payload"]["status"] == "failed"
    assert "QA reprovado" in result["payload"]["error"]
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
    fake_direct_worker(monkeypatch)
    monkeypatch.setattr(sh, "run_qa_gate", pass_qa)
    monkeypatch.setattr(sh, "publicar_docx", fail_publish)
    monkeypatch.setattr(sh, "registrar_cerebro", vault)

    result = cli.cmd_start(start_args(tmp_path))

    assert result["exit_code"] == 1
    assert result["payload"]["status"] == "failed"
    assert "falha de publicação" in result["payload"]["error"]
    assert not vault_called


def test_cli_resume_curto_e_detalhes_em_arquivo(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "_json_out", json_result)
    result = cli._format_action_result(
        "STARTED",
        {
            "phase": "skeleton_ready",
            "status": "executing",
            "history": ["intake_ready", "skeleton_ready"],
            "route": {"stages": ["skeleton_ready", "awaiting_skeleton_approval"]},
            "state_dir": str(tmp_path),
            "outputs": {"planner": {"content": "conteúdo extenso"}},
        },
    )
    assert "history" not in result["payload"]
    assert result["payload"]["required_gate"] == "skeleton_approval"
    assert Path(result["payload"]["details"]).is_file()


def test_bloqueia_tentativa_duplicada(monkeypatch, tmp_path):
    """Se um state_dir irmão já pausou com disjuntor estourado e mesmo
    writer-input.md hash, o motor bloqueia com ContractError ao criar novo dir."""
    from orquestracao.engine import RDAAEngine, MAX_CONSECUTIVE_FAILURES
    from orquestracao.contracts import ContractError

    writer_text = "# Peça duplicada\n\nTexto teste.\n\nI. PEDIDO.\n\nDiante do exposto, requer-se."

    d1 = tmp_path / "MAT-DUP-01"
    d1.mkdir()
    (d1 / "packages").mkdir()
    (d1 / "packages" / "writer-input.md").write_text(writer_text, encoding="utf-8")
    (d1 / "matter_state.json").write_text(json.dumps({
        "matter_id": "MAT-DUP-01",
        "status": "paused",
        "phase": "qa_passed",
        "consecutive_failures": MAX_CONSECUTIVE_FAILURES,
    }), encoding="utf-8")

    d2 = tmp_path / "MAT-DUP-01-v2"
    d2.mkdir()
    (d2 / "packages").mkdir()
    (d2 / "packages" / "writer-input.md").write_text(writer_text, encoding="utf-8")

    engine = RDAAEngine(state_dir=str(d2), nivel_peca="C")

    with pytest.raises(ContractError, match="tentativa duplicada bloqueada"):
        engine.initialize("MAT-DUP-01")


def test_bloqueia_nao_ativa_sem_disjuntor(monkeypatch, tmp_path):
    """Se o state_dir irmão pausou mas o disjuntor NÃO estourou, NÃO bloqueia
    (é um caso legítimo de reexecução autorizada)."""
    from orquestracao.engine import RDAAEngine, MAX_CONSECUTIVE_FAILURES

    writer_text = "# Peça OK\n\nTexto teste.\n\nI. PEDIDO.\n\nDiante do exposto, requer-se."

    d1 = tmp_path / "MAT-DUP-02"
    d1.mkdir()
    (d1 / "packages").mkdir()
    (d1 / "packages" / "writer-input.md").write_text(writer_text, encoding="utf-8")
    (d1 / "matter_state.json").write_text(json.dumps({
        "matter_id": "MAT-DUP-02",
        "status": "paused",
        "phase": "qa_passed",
        "consecutive_failures": 1,
    }), encoding="utf-8")

    d2 = tmp_path / "MAT-DUP-02-v2"
    d2.mkdir()
    (d2 / "packages").mkdir()
    (d2 / "packages" / "writer-input.md").write_text(writer_text, encoding="utf-8")

    engine = RDAAEngine(state_dir=str(d2), nivel_peca="C")

    try:
        engine.initialize("MAT-DUP-02")
    except ContractError as exc:
        assert "tentativa duplicada" not in str(exc)
