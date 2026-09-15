import sys
from pathlib import Path
import pytest

# Paths
ROOT = Path(__file__).resolve().parents[1]
GESTAO_DIR = ROOT / "skills" / "gestao-materias" / "scripts"
REVISOR_DIR = ROOT / "skills" / "revisor-rdaa" / "scripts"

sys.path.insert(0, str(GESTAO_DIR))
sys.path.insert(0, str(REVISOR_DIR))

try:
    from gestao_materias import sanitize_id
    from estado_contrato import MatterId
except ImportError:
    pytest.skip("Dependencias de gestao_materias/estado_contrato nao encontradas.", allow_module_level=True)


@pytest.mark.parametrize("entrada", [
    "ação_de_cobrança",
    "  espaços  e  barras/nas/coisas  \n",
    "já-seguro-123",
    "0747080-19.2014.8.13.0024",
    "",
    "!",
    "numero de processo",
    "Ação (2024)",
])
def test_paridade_normalizacao_matter_id(entrada):
    """
    Testa se a implementacao de sanitize_id em gestao-materias
    produz exatamente o mesmo matter_id que MatterId.normalize do rdaa-core.
    Nao as fundimos por pertencerem a skills diferentes sem import cruzado seguro.
    Se isso falhar um dia, decida com um humano qual logica prevalece.
    """
    try:
        res1 = sanitize_id(entrada)
    except Exception:
        res1 = "EXCECAO_GESTAO"
        
    res2 = MatterId.normalize(entrada)
    
    if res1 == "EXCECAO_GESTAO" and res2 == "sem-identificador":
        pass
    else:
        assert res1 == res2, f"Divergencia detectada: '{res1}' != '{res2}' para '{entrada}'"
