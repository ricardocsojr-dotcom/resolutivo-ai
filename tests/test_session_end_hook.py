import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "scripts" / "session-end.mjs"


def _run(cwd: Path):
    return subprocess.run(["node", str(HOOK)], cwd=cwd, capture_output=True, text=True)


def _matter(tmp_path: Path, name: str, manifest: dict) -> Path:
    matter = tmp_path / ".rdaa-run" / name
    matter.mkdir(parents=True)
    (matter / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return matter


def _pending(tmp_path: Path):
    path = tmp_path / ".rdaa-run" / ".pending_vault_sync.json"
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8"))["pending"]


def test_publicada_sem_recibo_vira_pendencia(tmp_path):
    """Publicação sem recibo no Cérebro é exatamente o caso que a rede de
    segurança existe para pegar."""
    if not shutil.which("node"):
        return
    _matter(
        tmp_path,
        "caso-publicado",
        {"phase": "published", "status": "PUBLISHED", "output": "peca.docx", "vault": {"syncs": []}},
    )
    result = _run(tmp_path)
    assert result.returncode == 0
    assert _pending(tmp_path) == [
        {
            "matter_id": "caso-publicado",
            "phase": "published",
            "status": "PUBLISHED",
            "output": "peca.docx",
        }
    ]


def test_recibo_registrado_encerra_a_pendencia(tmp_path):
    """Regressão 2026-09-11: o critério antigo era `manifest.vault_synced_at`,
    campo que nenhum script do repo grava — registrar_cerebro.py e o
    orquestrador escrevem o recibo em `vault.syncs[]`. Matéria sincronizada
    ficava pendente para sempre e o aviso virou ruído ignorado. O critério
    tem de ser o MESMO do gate `vault_registered`."""
    if not shutil.which("node"):
        return
    _matter(
        tmp_path,
        "caso-sincronizado",
        {
            "phase": "published",
            "status": "PUBLISHED",
            "vault": {
                "syncs": [
                    {"vault": "cerebro-ricar", "status": "registered", "artifact_path": "recibo.json"}
                ]
            },
        },
    )
    result = _run(tmp_path)
    assert result.returncode == 0
    assert _pending(tmp_path) == []


def test_materia_nao_publicada_nao_e_pendencia(tmp_path):
    """Antes de publicar não existe nada a registrar no Cérebro; listar
    rascunho como pendente é falso positivo por construção."""
    if not shutil.which("node"):
        return
    _matter(tmp_path, "caso-rascunho", {"phase": "drafting", "status": "active"})
    result = _run(tmp_path)
    assert result.returncode == 0
    assert _pending(tmp_path) == []


def test_pendencia_antiga_e_removida_quando_zera(tmp_path):
    if not shutil.which("node"):
        return
    run_dir = tmp_path / ".rdaa-run"
    _matter(tmp_path, "caso-rascunho", {"phase": "drafting", "status": "active"})
    stale = run_dir / ".pending_vault_sync.json"
    stale.write_text(json.dumps({"pending": [{"matter_id": "antigo"}]}), encoding="utf-8")
    result = _run(tmp_path)
    assert result.returncode == 0
    assert not stale.exists()
