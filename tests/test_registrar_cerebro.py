import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "redigir-peca" / "scripts" / "registrar_cerebro.py"
SPEC = importlib.util.spec_from_file_location("registrar_cerebro", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _cerebro(tmp_path: Path) -> Path:
    cerebro = tmp_path / "cerebro"
    for directory in ("domains", "concepts", "sources", "entities", "operacional", "pessoal"):
        (cerebro / "wiki" / directory).mkdir(parents=True, exist_ok=True)
    return cerebro


def test_registrar_recusa_materia_ainda_nao_publicada(tmp_path, monkeypatch):
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)
    monkeypatch.setattr(MODULE, "WIKI_OPERACIONAL", cerebro / "wiki" / "operacional")
    (tmp_path / "contexto_peca.json").write_text(
        json.dumps({"titulo_peca": "Manifestação", "partes": {"autor": {"nome": "Cliente"}}}),
        encoding="utf-8",
    )
    (tmp_path / "run_manifest.json").write_text(json.dumps({"phase": "drafting"}), encoding="utf-8")

    result = MODULE.registrar(tmp_path, "caso-123", "B")

    assert result["success"] is False
    assert "published" in result["error"]
    assert not list((cerebro / "wiki" / "operacional").glob("*.md"))


def test_registrar_publicado_emite_recibo_para_vault_registered(tmp_path, monkeypatch):
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)
    monkeypatch.setattr(MODULE, "WIKI_OPERACIONAL", cerebro / "wiki" / "operacional")
    (tmp_path / "contexto_peca.json").write_text(
        json.dumps({"titulo_peca": "Manifestação", "partes": {"autor": {"nome": "Cliente"}}}),
        encoding="utf-8",
    )
    (tmp_path / "run_manifest.json").write_text(json.dumps({"phase": "published"}), encoding="utf-8")
    monkeypatch.setattr(MODULE, "_sincronizar_openviking", lambda *args, **kwargs: {"success": True})

    result = MODULE.registrar(tmp_path, "caso-123", "B")

    receipt = json.loads((tmp_path / "CEREBRO-RECIBO.json").read_text(encoding="utf-8"))
    assert result["success"] is True
    assert receipt["vault"] == "cerebro-ricar"
    assert receipt["status"] == "registered"


def test_registrar_grava_recibo_em_vault_syncs_do_manifesto(tmp_path, monkeypatch):
    """Regressão 2026-09-11: o script emitia CEREBRO-RECIBO.json e devolvia
    success=True, mas nunca escrevia em `vault.syncs[]` do manifesto — que é
    o array exigido pelo gate `vault_registered` do orquestrador. Matéria
    publicada e registrada de verdade ficava travada antes do último estágio,
    e fechar o manifesto dependia de alguém lembrar de rodar
    `register-vault-sync` à mão. Emitir o recibo em disco NÃO basta."""
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)
    monkeypatch.setattr(MODULE, "WIKI_OPERACIONAL", cerebro / "wiki" / "operacional")
    (tmp_path / "contexto_peca.json").write_text(
        json.dumps({"titulo_peca": "Manifestação", "partes": {"autor": {"nome": "Cliente"}}}),
        encoding="utf-8",
    )
    (tmp_path / "run_manifest.json").write_text(json.dumps({"phase": "published"}), encoding="utf-8")
    monkeypatch.setattr(MODULE, "_sincronizar_openviking", lambda *args, **kwargs: {"success": True})

    result = MODULE.registrar(tmp_path, "caso-123", "B")
    assert result["success"] is True

    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    syncs = manifest.get("vault", {}).get("syncs", [])
    registrados = [s for s in syncs if s.get("vault") == "cerebro-ricar" and s.get("status") == "registered"]
    assert len(registrados) == 1, manifest
    assert Path(registrados[0]["artifact_path"]).name == "CEREBRO-RECIBO.json"
    assert registrados[0]["artifact_sha256"]


def test_registrar_falha_se_o_manifesto_nao_aceitar_o_recibo(tmp_path, monkeypatch):
    """Falha fechada: se o recibo não entra no manifesto, a matéria NÃO pode
    ser reportada como registrada — senão o gate seguinte trava sem que
    ninguém saiba por quê."""
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)
    monkeypatch.setattr(MODULE, "WIKI_OPERACIONAL", cerebro / "wiki" / "operacional")
    (tmp_path / "contexto_peca.json").write_text(
        json.dumps({"titulo_peca": "Manifestação", "partes": {"autor": {"nome": "Cliente"}}}),
        encoding="utf-8",
    )
    (tmp_path / "run_manifest.json").write_text(json.dumps({"phase": "published"}), encoding="utf-8")
    monkeypatch.setattr(MODULE, "_sincronizar_openviking", lambda *args, **kwargs: {"success": True})
    monkeypatch.setattr(
        MODULE,
        "_registrar_sync_no_manifesto",
        lambda *args, **kwargs: {"success": False, "error": "WorkflowStateError: simulado"},
    )

    result = MODULE.registrar(tmp_path, "caso-123", "B")

    assert result["success"] is False
    assert result["cerebro_registered"] is True
    assert "vault.syncs" in result["error"]


def test_registrar_normaliza_campos_para_nao_forjar_frontmatter(tmp_path, monkeypatch):
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)
    monkeypatch.setattr(MODULE, "WIKI_OPERACIONAL", cerebro / "wiki" / "operacional")
    (tmp_path / "contexto_peca.json").write_text(
        json.dumps({"titulo_peca": "Título\nstatus: forjado", "partes": {"autor": {"nome": "Cliente\n---"}}}),
        encoding="utf-8",
    )
    (tmp_path / "run_manifest.json").write_text(json.dumps({"phase": "published"}), encoding="utf-8")
    monkeypatch.setattr(MODULE, "_sincronizar_openviking", lambda *args, **kwargs: {"success": True})

    result = MODULE.registrar(tmp_path, "caso-123", "B")

    content = Path(result["file"]).read_text(encoding="utf-8")
    assert "\nstatus: forjado\n" not in content
    assert 'title: "Título status: forjado"' in content
    assert content.count("---\n") == 2


def test_registrar_aceita_partes_textuais_do_contexto_docx(tmp_path, monkeypatch):
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)
    monkeypatch.setattr(MODULE, "WIKI_OPERACIONAL", cerebro / "wiki" / "operacional")
    (tmp_path / "contexto_peca.json").write_text(
        json.dumps(
            {
                "titulo_peca": "Desistência",
                "partes": "Embargante: Cooperativa Agropecuária Ltda.\nEmbargado: Escritório Credor",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "run_manifest.json").write_text(json.dumps({"phase": "published"}), encoding="utf-8")
    monkeypatch.setattr(MODULE, "_sincronizar_openviking", lambda *args, **kwargs: {"success": True})

    result = MODULE.registrar(tmp_path, "caso-123", "C")

    assert result["success"] is True
    content = Path(result["file"]).read_text(encoding="utf-8")
    assert 'client: "Cooperativa Agropecuária Ltda."' in content
    assert "- **Autor:** Cooperativa Agropecuária Ltda." in content


def test_registrar_publicado_dispara_sincronizacao_openviking(tmp_path, monkeypatch):
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)
    monkeypatch.setattr(MODULE, "WIKI_OPERACIONAL", cerebro / "wiki" / "operacional")
    (tmp_path / "contexto_peca.json").write_text(
        json.dumps({"titulo_peca": "Manifestação", "partes": {"autor": {"nome": "Cliente"}}}),
        encoding="utf-8",
    )
    (tmp_path / "run_manifest.json").write_text(json.dumps({"phase": "published"}), encoding="utf-8")
    calls = []

    def fake_sync(*args, **kwargs):
        calls.append((args, kwargs))
        return {"success": True, "receipt": str(tmp_path / "OPENVIKING-RECIBO.json")}

    monkeypatch.setattr(MODULE, "_sincronizar_openviking", fake_sync)

    result = MODULE.registrar(tmp_path, "caso-123", "B")

    assert result["success"] is True
    assert result["openviking_sync"]["success"] is True
    assert calls
    assert calls[0][0][0] == cerebro / "wiki" / "operacional"
    assert calls[0][1]["processing_mode"] == "vectors_only"
    assert calls[0][1]["receipt_path"] == tmp_path / "OPENVIKING-RECIBO.json"


def test_registrar_cria_e_atualiza_entidades_automaticamente(tmp_path, monkeypatch):
    cerebro = _cerebro(tmp_path)
    monkeypatch.setattr(MODULE, "CEREBRO", cerebro)
    monkeypatch.setattr(MODULE, "WIKI_OPERACIONAL", cerebro / "wiki" / "operacional")
    (tmp_path / "contexto_peca.json").write_text(
        json.dumps({
            "titulo_peca": "Ação de Cobrança",
            "partes": "Autor: Empresa Alpha Ltda.\nRéu: Banco Beta S.A.",
        }),
        encoding="utf-8",
    )
    (tmp_path / "run_manifest.json").write_text(json.dumps({"phase": "published"}), encoding="utf-8")
    monkeypatch.setattr(MODULE, "_sincronizar_openviking", lambda *args, **kwargs: {"success": True})

    result = MODULE.registrar(tmp_path, "cobranca-456", "B")
    assert result["success"] is True

    ent_dir = cerebro / "wiki" / "entities"
    alpha_file = ent_dir / "empresa-alpha-ltda.md"
    beta_file = ent_dir / "banco-beta-sa.md"

    assert alpha_file.exists()
    assert beta_file.exists()

    alpha_content = alpha_file.read_text(encoding="utf-8")
    assert "role: cliente" in alpha_content
    assert "- [[matter-cobranca-456]]" in alpha_content

    beta_content = beta_file.read_text(encoding="utf-8")
    assert "role: adversario" in beta_content
    assert "- [[matter-cobranca-456]]" in beta_content
