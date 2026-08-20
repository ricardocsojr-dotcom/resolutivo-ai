"""Regressões do contrato documental de candidato temporário."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_formatar_requires_candidate_before_publish() -> None:
    text = (ROOT / "skills" / "formatar-peca" / "SKILL.md").read_text(encoding="utf-8")
    assert "gerar o candidato temporário" in text
    assert "Nunca use o caminho final como `--output` de `construir_peca.py`" in text
    assert "publicar_docx.py" in text
    assert "--output /tmp/rdaa-candidatos/peca_candidata.docx" in text


def test_redigir_requires_candidate_and_protected_publication() -> None:
    text = (ROOT / "skills" / "redigir-peca" / "SKILL.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "Gere o `.docx` **candidato**" in normalized
    assert "nunca grave diretamente no caminho final" in normalized
    assert "Só entregue o documento final depois que o publicador" in normalized


if __name__ == "__main__":
    test_formatar_requires_candidate_before_publish()
    test_redigir_requires_candidate_and_protected_publication()
    print("[OK] contrato documental de candidato temporário passou")
