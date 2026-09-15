import json
import os
import sys
import pytest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "skills" / "revisor-rdaa" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from estado_contrato import MatterId, EstadoDirError, validar_state_dir


def test_matter_id_normalize():
    assert MatterId.normalize("12345-67.2023") == "12345-67.2023"
    assert MatterId.normalize("ação de cobrança") == "a-o-de-cobran-a"
    assert MatterId.normalize("  espacos  \n") == "espacos"
    assert MatterId.normalize("") == "sem-identificador"
    assert MatterId.normalize(None) == "sem-identificador"


def test_validar_state_dir_valido(tmp_path):
    d = tmp_path / "normal" / ".rdaa-run" / "123"
    validar_state_dir(d)  # nao deve subir excecao


def test_validar_state_dir_aninhado(tmp_path):
    d = tmp_path / ".rdaa-run" / "x" / ".rdaa-run" / "xyz"
    with pytest.raises(EstadoDirError, match="aninhado"):
        validar_state_dir(d)


def test_validar_state_dir_aninhado_capitalizacao(tmp_path):
    d = tmp_path / ".RDAA-RUN" / "x" / ".rdaa-run" / "xyz"
    with pytest.raises(EstadoDirError, match="aninhado"):
        validar_state_dir(d)


def test_validar_state_dir_symlink(tmp_path, monkeypatch):
    d = tmp_path / "fake_symlink"
    # Mock para devolver True sem precisar de privs de admin no Windows
    monkeypatch.setattr(Path, "is_symlink", lambda self: True)
    with pytest.raises(EstadoDirError, match="symlink"):
        validar_state_dir(d)


def test_validar_state_dir_id_divergente(tmp_path):
    d = tmp_path / "meu_estado"
    d.mkdir()
    manifest_path = d / "run_manifest.json"
    manifest_path.write_text(json.dumps({"matter_id": "123"}))

    # Igual nao falha
    validar_state_dir(d, matter_id="123")

    # Divergente falha
    with pytest.raises(EstadoDirError, match="divergente"):
        validar_state_dir(d, matter_id="999")

    # Se nao passar matter_id, nao checa
    validar_state_dir(d)
