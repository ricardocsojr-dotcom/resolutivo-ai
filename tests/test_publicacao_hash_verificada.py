"""Regressão: publicar_docx.py deve comparar confirmed_hash com candidate_hash
e abortar a publicação (revertendo para backup, quando houver) se divergirem,
em vez de só registrar os dois hashes no manifesto sem checá-los."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "formatar-peca" / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "revisor-rdaa" / "scripts"))

import construir_peca  # noqa: E402
import publicar_docx  # noqa: E402

CONTEXT_FIXTURE = ROOT / "tests" / "fixtures" / "context_happy.json"


def test_hash_divergente_pos_copia_aborta_publicacao(monkeypatch, tmp_path, capsys) -> None:
    context = json.loads(CONTEXT_FIXTURE.read_text(encoding="utf-8"))
    context_path = tmp_path / "context.json"
    context_path.write_text(json.dumps(context, ensure_ascii=False), encoding="utf-8")
    candidate = tmp_path / "candidate.docx"
    output = tmp_path / "final.docx"

    construir_peca.construir_peca(context, str(candidate))

    real_sha256 = publicar_docx.file_sha256

    def fake_sha256(path):
        if Path(path) == output:
            return "0" * 64  # hash forjado, nunca bate com o candidato aprovado
        return real_sha256(path)

    monkeypatch.setattr(publicar_docx, "file_sha256", fake_sha256)
    monkeypatch.setattr(
        sys,
        "argv",
        ["publicar_docx.py", "--input", str(candidate), "--output", str(output), "--context", str(context_path)],
    )

    exit_code = publicar_docx.main()

    assert exit_code == 1
    saida = capsys.readouterr().out
    assert "hash do arquivo publicado diverge do candidato aprovado" in saida
