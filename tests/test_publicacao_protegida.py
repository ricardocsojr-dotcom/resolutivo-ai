#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from test_qa_engineering import (
    FIXTURE,
    GENERATOR,
    mutate_remove_signature_margins,
    rewrite_zip,
)

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = PLUGIN_ROOT / 'skills/revisor-rdaa/scripts/publicar_docx.py'


def mutate_add_colon(data: bytes) -> bytes:
    marker = b'Processo '
    assert marker in data
    return data.replace(marker, b'Processo: ', 1)


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=PLUGIN_ROOT, text=True, capture_output=True)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix='rdaa-publish-') as tmp:
        folder = Path(tmp)
        candidate = folder / 'candidate.docx'
        published = folder / 'published.docx'
        bad = folder / 'bad.docx'
        backup_dir = folder / 'backups'
        qa_json = folder / 'qa.json'
        context = folder / 'context.json'
        data_initial = json.loads(FIXTURE.read_text(encoding='utf-8'))
        data_initial['teses'] = ['Tese explicitamente fornecida no contexto.']
        data_initial['pendencias'] = ['Confirmar documento de suporte.']
        data_initial['blocos'][4]['nota_rodape'] = 'STJ, precedente informado no contexto.'
        context.write_text(json.dumps(data_initial, ensure_ascii=False), encoding='utf-8')

        generated = run([sys.executable, str(GENERATOR), '--context', str(context), '--output', str(candidate)])
        assert generated.returncode == 0, generated.stdout + generated.stderr
        published.write_bytes(b'arquivo-estavel-anterior')

        result = run([
            sys.executable, str(PUBLISHER),
            '--input', str(candidate),
            '--output', str(published),
            '--backup-dir', str(backup_dir),
            '--qa-json', str(qa_json),
            '--context', str(context),
        ])
        assert result.returncode == 0, result.stdout + result.stderr
        assert published.read_bytes() == candidate.read_bytes()
        backups = list(backup_dir.glob('published.docx.*.bak'))
        assert len(backups) == 1
        assert backups[0].read_bytes() == b'arquivo-estavel-anterior'
        assert qa_json.is_file()
        state_dir = folder / '.rdaa-run' / '0000000-00.0000.8.26.0001'
        assert (state_dir / 'matter_state.json').is_file()
        assert (state_dir / 'run_manifest.json').is_file()
        assert (state_dir / 'provenance.jsonl').is_file()
        manifest = json.loads((state_dir / 'run_manifest.json').read_text(encoding='utf-8'))
        assert manifest['status'] == 'PUBLISHED'
        assert manifest['phase'] == 'published'
        state = json.loads((state_dir / 'matter_state.json').read_text(encoding='utf-8'))
        assert state['theses'] == ['Tese explicitamente fornecida no contexto.']
        assert state['pending'] == ['Confirmar documento de suporte.']
        provenance_lines = [json.loads(line) for line in (state_dir / 'provenance.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        assert len(provenance_lines) == 1
        assert provenance_lines[0]['status'] == 'informada'
        assert provenance_lines[0]['origem'] == 'contexto_json'

        rejected_context = folder / 'rejected_context.json'
        rejected_data = json.loads(context.read_text(encoding='utf-8'))
        rejected_data['teses'] = ['Tese que pertence somente ao candidato rejeitado.']
        rejected_data['pendencias'] = ['Pendência exclusiva do candidato rejeitado.']
        rejected_context.write_text(json.dumps(rejected_data, ensure_ascii=False), encoding='utf-8')
        rejected_candidate = folder / 'rejected_candidate.docx'
        rejected_bad = folder / 'rejected_bad.docx'
        generated = run([sys.executable, str(GENERATOR), '--context', str(rejected_context), '--output', str(rejected_candidate)])
        assert generated.returncode == 0, generated.stdout + generated.stderr
        rewrite_zip(rejected_candidate, rejected_bad, 'word/document.xml', mutate_remove_signature_margins)
        confirmed_before_rejection = json.loads((state_dir / 'matter_state.json').read_text(encoding='utf-8'))
        result = run([
            sys.executable, str(PUBLISHER),
            '--input', str(rejected_bad),
            '--output', str(published),
            '--backup-dir', str(backup_dir),
            '--context', str(rejected_context),
        ])
        assert result.returncode != 0, result.stdout + result.stderr
        confirmed_after_rejection = json.loads((state_dir / 'matter_state.json').read_text(encoding='utf-8'))
        assert confirmed_after_rejection['theses'] == confirmed_before_rejection['theses']
        assert confirmed_after_rejection['pending'] == confirmed_before_rejection['pending']
        rejected_state = json.loads((state_dir / 'candidate' / 'matter_state.json').read_text(encoding='utf-8'))
        assert rejected_state['theses'] == ['Tese que pertence somente ao candidato rejeitado.']
        assert rejected_state['pending'] == ['Pendência exclusiva do candidato rejeitado.']
        rejected_manifest = json.loads((state_dir / 'run_manifest.json').read_text(encoding='utf-8'))
        assert rejected_manifest['candidate_status'] == 'REJECTED'
        assert rejected_manifest['confirmed_state_status'] == 'PRESERVED'

        c_context = folder / 'context_c_blocos.json'
        c_data = json.loads(context.read_text(encoding='utf-8'))
        c_data.update({
            'matter_id': 'tipo-c-com-blocos',
            'nivel_peca': 'C',
            'modo_redacao': 'blocos',
            'redacao_por_blocos': True,
        })
        c_context.write_text(json.dumps(c_data, ensure_ascii=False), encoding='utf-8')
        c_candidate = folder / 'c_candidate.docx'
        c_published = folder / 'c_published.docx'
        generated = run([sys.executable, str(GENERATOR), '--context', str(c_context), '--output', str(c_candidate)])
        assert generated.returncode == 0, generated.stdout + generated.stderr
        c_published.write_bytes(b'arquivo-c-estavel')
        result = run([
            sys.executable, str(PUBLISHER),
            '--input', str(c_candidate),
            '--output', str(c_published),
            '--context', str(c_context),
        ])
        assert result.returncode != 0, result.stdout + result.stderr
        assert c_published.read_bytes() == b'arquivo-c-estavel'
        c_state_dir = folder / '.rdaa-run' / 'tipo-c-com-blocos'
        c_manifest = json.loads((c_state_dir / 'run_manifest.json').read_text(encoding='utf-8'))
        assert c_manifest['piece_contract_status'] == 'BLOCK'

        rewrite_zip(candidate, bad, 'word/document.xml', mutate_remove_signature_margins)
        before_failed_publish = published.read_bytes()
        result = run([
            sys.executable, str(PUBLISHER),
            '--input', str(bad),
            '--output', str(published),
            '--backup-dir', str(backup_dir),
            '--context', str(context),
        ])
        assert result.returncode != 0, result.stdout
        assert published.read_bytes() == before_failed_publish
        assert len(list(backup_dir.glob('published.docx.*.bak'))) == 1

        colon_candidate = folder / 'colon_candidate.docx'
        rewrite_zip(candidate, colon_candidate, 'word/document.xml', mutate_add_colon)
        before_style_failed_publish = published.read_bytes()
        result = run([
            sys.executable, str(PUBLISHER),
            '--input', str(colon_candidate),
            '--output', str(published),
            '--backup-dir', str(backup_dir),
            '--context', str(context),
        ])
        assert result.returncode != 0, result.stdout + result.stderr
        assert published.read_bytes() == before_style_failed_publish
        assert len(list(backup_dir.glob('published.docx.*.bak'))) == 1

        context_two = folder / 'context_two.json'
        data = json.loads(context.read_text(encoding='utf-8'))
        data['numero_processo'] = '1111111-11.1111.8.26.0002'
        context_two.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        candidate_two = folder / 'candidate_two.docx'
        published_two = folder / 'published_two.docx'
        generated = run([sys.executable, str(GENERATOR), '--context', str(context_two), '--output', str(candidate_two)])
        assert generated.returncode == 0, generated.stdout + generated.stderr
        result = run([
            sys.executable, str(PUBLISHER),
            '--input', str(candidate_two),
            '--output', str(published_two),
            '--context', str(context_two),
        ])
        assert result.returncode == 0, result.stdout + result.stderr
        state_dir_two = folder / '.rdaa-run' / '1111111-11.1111.8.26.0002'
        assert (state_dir_two / 'matter_state.json').is_file()
        first_state = json.loads((state_dir / 'matter_state.json').read_text(encoding='utf-8'))
        second_state = json.loads((state_dir_two / 'matter_state.json').read_text(encoding='utf-8'))
        assert first_state['matter_id'] != second_state['matter_id']
        assert first_state['facts'] != second_state['facts']

    print('[OK] publicação protegida: sucesso publica, falha preserva e casos ficam isolados')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
