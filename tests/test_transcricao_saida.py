import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "transcricao-audio" / "scripts" / "transcrever.py"
SPEC = importlib.util.spec_from_file_location("transcrever_saida_test", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_gravacao_de_transcricao_substitui_destino_sem_arquivo_parcial(tmp_path):
    destino = tmp_path / "transcricao.txt"
    destino.write_text("conteúdo anterior", encoding="utf-8")

    MODULE._gravar_saida_atomica(destino, "conteúdo novo")

    assert destino.read_text(encoding="utf-8") == "conteúdo novo"
    assert not list(tmp_path.glob(".transcricao.txt.*.tmp"))


def test_falha_na_substituicao_preserva_transcricao_anterior(tmp_path, monkeypatch):
    destino = tmp_path / "transcricao.txt"
    destino.write_text("conteúdo anterior", encoding="utf-8")

    def fail_replace(*_args):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(MODULE.os, "replace", fail_replace)
    with pytest.raises(OSError, match="simulated"):
        MODULE._gravar_saida_atomica(destino, "conteúdo novo")

    assert destino.read_text(encoding="utf-8") == "conteúdo anterior"
    assert not list(tmp_path.glob(".transcricao.txt.*.tmp"))
