import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "redigir-peca" / "scripts" / "integracao_obsidian.py"
SPEC = importlib.util.spec_from_file_location("integracao_obsidian", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _vault(tmp_path: Path) -> Path:
    vault = tmp_path / "ementario"
    (vault / "wiki" / "domains").mkdir(parents=True)
    (vault / "wiki" / "concepts").mkdir()
    (vault / "wiki" / "sources").mkdir()
    (vault / "CLAUDE.md").write_text("# Ementário\n", encoding="utf-8")
    (vault / "wiki" / "domains" / "dano-moral.md").write_text(
        "# Dano moral\n\n[[tese-exemplo]]\n", encoding="utf-8"
    )
    (vault / "wiki" / "concepts" / "tese-exemplo.md").write_text(
        "Tese informada. [[PREC-001]] [[tese-associada]]", encoding="utf-8"
    )
    (vault / "wiki" / "concepts" / "tese-associada.md").write_text("Não deve entrar no pacote.", encoding="utf-8")
    (vault / "wiki" / "sources" / "prec-001.md").write_text(
        "Ementa literal.\n- Cliente de origem: Cliente histórico\n- Processo de origem: 0000000-00.0000.0.00.0000",
        encoding="utf-8",
    )
    return vault


def test_consulta_ementario_cria_pacote_somente_leitura_com_proveniencia(tmp_path):
    vault = _vault(tmp_path)
    output = tmp_path / "EMENTARIO-CONTEXTO.json"
    before = {path.relative_to(vault): path.read_bytes() for path in vault.rglob("*") if path.is_file()}

    package = MODULE.consultar_ementario(vault, "dano-moral", output)

    saved = json.loads(output.read_text(encoding="utf-8"))
    after = {path.relative_to(vault): path.read_bytes() for path in vault.rglob("*") if path.is_file()}
    assert package == saved
    assert after == before
    assert saved["origin"] == "cerebro-ricar"
    assert saved["status"] == "informada"
    assert saved["mode"] == "read_only"
    assert [item["relative_path"] for item in saved["documents"]] == [
        "wiki/domains/dano-moral.md",
        "wiki/concepts/tese-exemplo.md",
        "wiki/sources/prec-001.md",
    ]
    assert all(item["sha256"] for item in saved["documents"])
    source_content = saved["documents"][-1]["content"]
    assert "Cliente histórico" not in source_content
    assert "0000000-00.0000.0.00.0000" not in source_content
    assert "Cliente de origem" not in source_content
    assert "[REDACTED]" in source_content


def test_consulta_ementario_rejeita_identificador_de_dominio_inseguro(tmp_path):
    with pytest.raises(ValueError, match="domínio"):
        MODULE.consultar_ementario(_vault(tmp_path), "../segredo", tmp_path / "resultado.json")


def test_cli_de_consulta_nao_expoe_conteudo_do_vault(tmp_path, monkeypatch, capsys):
    vault = _vault(tmp_path)
    output = tmp_path / "EMENTARIO-CONTEXTO.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "integracao_obsidian.py",
            "consultar-ementario",
            "--vault-root",
            str(vault),
            "--domain",
            "dano-moral",
            "--output",
            str(output),
        ],
    )

    assert MODULE.main() == 0

    stdout = capsys.readouterr().out
    assert "Cliente histórico" not in stdout
    assert "Ementa literal" not in stdout
    assert '"documents_count": 3' in stdout


def test_caminho_resolvido_fora_do_cerebro_e_rejeitado(tmp_path):
    vault = _vault(tmp_path)
    external = tmp_path / "segredo.txt"
    external.write_text("conteúdo externo", encoding="utf-8")

    with pytest.raises(ValueError, match="fora do Cérebro"):
        MODULE._require_within_root(vault, external)


def test_consulta_ementario_rejeita_link_simbolico_para_arquivo_externo(tmp_path):
    vault = _vault(tmp_path)
    external = tmp_path / "segredo.txt"
    external.write_text("conteúdo externo", encoding="utf-8")
    linked_source = vault / "wiki" / "sources" / "prec-001.md"
    linked_source.unlink()
    try:
        linked_source.symlink_to(external)
    except OSError as exc:
        pytest.skip(f"symlink indisponível neste ambiente: {exc}")

    with pytest.raises(ValueError, match="fora do Cérebro"):
        MODULE.consultar_ementario(vault, "dano-moral", tmp_path / "resultado.json")