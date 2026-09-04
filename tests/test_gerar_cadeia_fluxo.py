import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "legal-design-rdaa" / "scripts" / "gerar_cadeia_fluxo.py"
SPEC = importlib.util.spec_from_file_location("gerar_cadeia_fluxo", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _spec() -> dict:
    return {
        "titulo": "Fluxo",
        "etapas": [
            {"numero": 1, "titulo": "Etapa 1", "ator": "Autor", "descricao": "Fato", "prova": "Doc"},
            {"numero": 2, "titulo": "Etapa 2", "ator": "Réu", "descricao": "Resposta", "prova": "Evento"},
        ],
    }


def test_gerador_escapa_markup_controlado_pelo_spec(tmp_path):
    spec = _spec()
    spec["titulo"] = "</text><script>alert(1)</script><text>"
    spec_path = tmp_path / "spec.json"
    output_path = tmp_path / "fluxo.svg"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")

    MODULE.gerar_cadeia_unica(str(spec_path), str(output_path))

    svg = output_path.read_text(encoding="utf-8")
    assert "<script>" not in svg
    assert "&lt;/text&gt;&lt;script&gt;alert(1)&lt;/script&gt;&lt;text&gt;" in svg


def test_gerador_usa_extensao_svg_sem_sobrescrever_spec(tmp_path):
    spec_path = tmp_path / "spec.JSON"
    original = json.dumps(_spec())
    spec_path.write_text(original, encoding="utf-8")

    output = MODULE.gerar_cadeia_unica(str(spec_path))

    assert Path(output) == tmp_path / "spec.svg"
    assert spec_path.read_text(encoding="utf-8") == original
