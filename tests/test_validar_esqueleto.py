from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills' / 'revisor-rdaa' / 'scripts' / 'validar_esqueleto.py'


def run(context: dict, state_dir: Path) -> tuple[int, dict]:
    context_path = state_dir / 'context.json'
    context_path.write_text(json.dumps(context, ensure_ascii=False), encoding='utf-8')
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--context', str(context_path), '--state-dir', str(state_dir)],
        capture_output=True,
        text=True,
    )
    return result.returncode, json.loads(result.stdout)


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        state_dir = Path(temp) / 'matter'
        state_dir.mkdir()
        provenance = state_dir / 'provenance.jsonl'
        provenance.write_text(
            json.dumps({
                'id': 'SRC-1',
                'tipo': 'jurisprudencia',
                'fonte': 'Jusbrasil',
                'localizacao': 'https://example.test/acordao',
                'trecho': 'EMENTA LITERAL',
                'status': 'verificada_externamente',
                'origem': 'buscar-jurisprudencia',
            }) + '\n',
            encoding='utf-8',
        )
        valid = {
            'esqueleto': {
                'status': 'aprovado',
                'aprovacao': {'status': 'aprovado', 'por': 'Ricardo'},
                'fontes_status': 'selecionadas',
                'fontes_selecionadas': [{
                    'source_id': 'SRC-1',
                    'uso': 'fundamentacao.tese-1',
                    'bloco': 'fundamentos',
                    'status': 'verificada_externamente',
                    'origem': 'buscar-jurisprudencia',
                    'fonte': 'Jusbrasil',
                    'localizacao': 'https://example.test/acordao',
                    'literalidade_confirmada': True,
                }],
            },
            'blocos': [{'id': 'fundamentos', 'source_ids': ['SRC-1']}],
        }
        code, report = run(valid, state_dir)
        assert code == 0, report
        assert report['status'] == 'PASS', report

        blocked = json.loads(json.dumps(valid))
        blocked['esqueleto']['aprovacao']['status'] = 'pendente'
        code, report = run(blocked, state_dir)
        assert code == 1, report
        assert any(item['kind'] == 'skeleton_not_approved' for item in report['findings']), report

        late = json.loads(json.dumps(valid))
        late['esqueleto']['fontes_adicionais'] = [{'source_id': 'SRC-2', 'motivo': 'fonte encontrada após aprovação', 'revisao_posterior': {'status': 'aprovado'}}]
        late['blocos'].append({'id': 'fundamentos-2', 'source_ids': ['SRC-2']})
        code, report = run(late, state_dir)
        assert code == 0, report
        assert report['late_source_ids'] == ['SRC-2'], report

    print('[OK] validação do esqueleto e das fontes passou')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
