from pathlib import Path
import sys
import tempfile
import subprocess
import json

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = PLUGIN_ROOT / "skills" / "revisor-rdaa" / "scripts" / "publicar_docx.py"

def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PLUGIN_ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )

def test_publicar_sem_contexto_cria_subpasta_matter_id():
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        
        c1 = folder / "peca1.docx"
        c2 = folder / "peca2_com_espacos.docx"
        
        from test_qa_engineering import GENERATOR
        from test_qa_engineering import FIXTURE
        
        # O gerador exige um contexto, mas vamos rodar o PUBLICADOR sem contexto.
        gen1 = run([sys.executable, str(GENERATOR), "--context", str(FIXTURE), "--output", str(c1)])
        gen2 = run([sys.executable, str(GENERATOR), "--context", str(FIXTURE), "--output", str(c2)])
        
        assert gen1.returncode == 0
        assert gen2.returncode == 0
        
        res1 = run([sys.executable, str(PUBLISHER), "--input", str(c1), "--output", str(c1)])
        res2 = run([sys.executable, str(PUBLISHER), "--input", str(c2), "--output", str(c2)])
        
        assert res1.returncode == 0, res1.stderr
        assert res2.returncode == 0, res2.stderr
        
        # Check folders
        dir1 = folder / ".rdaa-run" / "peca1"
        dir2 = folder / ".rdaa-run" / "peca2_com_espacos"
        
        assert (dir1 / "run_manifest.json").exists()
        assert (dir2 / "run_manifest.json").exists()
        
        m1 = json.loads((dir1 / "run_manifest.json").read_text())
        m2 = json.loads((dir2 / "run_manifest.json").read_text())
        
        assert m1["matter_id"] == "peca1"
        assert m2["matter_id"] == "peca2_com_espacos"
