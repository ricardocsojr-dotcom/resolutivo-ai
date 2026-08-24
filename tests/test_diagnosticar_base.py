"""Regressão da guarda de merge many-to-one em diagnosticar_base.py."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "correcao-base-rdaa" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from diagnosticar_base import carregar_e_analisar  # noqa: E402

COLUNAS = [
    "Cliente", "Número do processo", "Ação", "Autor", "Réu", "Fase Processual",
    "Risco", "Situação atual", "Resumo/Assunto", "Advogado Responsável",
    "Ficha", "Arquivo Ficha Incidente", "Instância", "Localizador",
]


def _linha(ficha, incidente, acao="Apelação", fase="EM ANDAMENTO", localizador="ATIVO"):
    return {
        "Cliente": "Cliente Teste", "Número do processo": "0000000-00.2024.8.13.0000",
        "Ação": acao, "Autor": "Cliente Teste", "Réu": "Parte Contraria",
        "Fase Processual": fase, "Risco": "Possível", "Situação atual": "Em andamento",
        "Resumo/Assunto": "Resumo com conteudo suficiente para nao ser sinalizado como vazio",
        "Advogado Responsável": "Fulano", "Ficha": ficha,
        "Arquivo Ficha Incidente": incidente, "Instância": "2", "Localizador": localizador,
    }


def _escrever_xlsx(linhas) -> Path:
    df = pd.DataFrame(linhas, columns=COLUNAS)
    tmp = Path(tempfile.mkdtemp()) / "base.xlsx"
    df.to_excel(tmp, index=False, sheet_name="Resolutivo")
    return tmp


def test_ficha_com_origem_unica_nao_levanta_erro() -> None:
    caminho = _escrever_xlsx([
        _linha("F1", "F1.00", acao="Ação Ordinária", fase="ARQUIVADO"),
        _linha("F1", "F1.01", acao="Apelação"),
    ])
    resultado = carregar_e_analisar(caminho)
    assert resultado is not None


def test_ficha_com_origem_duplicada_levanta_erro_claro() -> None:
    caminho = _escrever_xlsx([
        _linha("F2", "F2.00", acao="Ação Ordinária", fase="ARQUIVADO"),
        _linha("F2", "F2.00", acao="Ação Ordinária", fase="ATIVO"),  # duplicidade de cadastro
        _linha("F2", "F2.01", acao="Apelação"),
    ])
    with pytest.raises(ValueError, match="mais de uma linha de origem"):
        carregar_e_analisar(caminho)


if __name__ == "__main__":
    test_ficha_com_origem_unica_nao_levanta_erro()
    test_ficha_com_origem_duplicada_levanta_erro_claro()
    print("[OK] guarda de merge many-to-one em diagnosticar_base.py")
