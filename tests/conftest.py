import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

@pytest.fixture
def folder(tmp_path: Path) -> Path:
    """Fixture para prover diretório temporário para testes que utilizam argumento 'folder'."""
    return tmp_path

@pytest.fixture
def source(folder: Path) -> Path:
    """Fixture para prover um arquivo source básico quando solicitado."""
    from tests.test_qa_engineering import build_docx
    return build_docx(folder)
