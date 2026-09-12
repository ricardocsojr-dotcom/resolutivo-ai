import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

O = load('governanca_orq', 'skills/redigir-peca/scripts/orquestrador_rdaa.py')


def test_gate_recusa_autoridade_ia(tmp_path):
    O.inicializar_execucao(tmp_path, 'teste', 'B')
    artifact = tmp_path / 'esqueleto.md'
    artifact.write_text('sintetico', encoding='utf-8')
    with pytest.raises(O.WorkflowStateError, match='ricardo'):
        O.registrar_aprovacao(tmp_path, 'skeleton_approval', artifact, 'IA')
    assert O._read_manifest(tmp_path)['approvals'] == []


def test_segunda_falha_bloqueia_terceira_chamada_e_exige_humano(tmp_path, monkeypatch):
    E = load('governanca_executor', 'skills/redigir-peca/scripts/executar_motor.py')
    O.inicializar_execucao(tmp_path, 'teste', 'A')
    O.avancar_fase(tmp_path, 'intake_ready')
    prompt = tmp_path / 'prompt.md'
    prompt.write_text('sintetico', encoding='utf-8')
    calls = []
    def failed(*args, **kwargs):
        calls.append(1)
        raise TimeoutError('timeout sintetico')
    monkeypatch.setattr(E.subprocess, 'run', failed)
    for _ in range(3):
        with pytest.raises((TimeoutError, ValueError)):
            E.executar('claude', prompt, tmp_path / 'out.md', None, 1,
                       state_dir=tmp_path, role='planner')
    assert len(calls) == 2
    state = O._read_manifest(tmp_path)
    assert state['status'] == 'paused'
    assert state['failures']['intake_ready']['count'] == 2
    with pytest.raises(ValueError):
        O.avancar_fase(tmp_path, 'vault_context_ready')
    with pytest.raises(ValueError):
        O.decidir_disjuntor(tmp_path, 'resume', 'IA', 'continuar')
    with pytest.raises(ValueError):
        O.decidir_disjuntor(tmp_path, 'resume', 'ricardo', '')
    O.decidir_disjuntor(tmp_path, 'resume', 'ricardo', 'Autorizo nova execução')
    with pytest.raises(TimeoutError):
        E.executar('claude', prompt, tmp_path / 'out.md', None, 1,
                   state_dir=tmp_path, role='planner')
    assert len(calls) == 3
    with pytest.raises(TimeoutError):
        E.executar('claude', prompt, tmp_path / 'out.md', None, 1,
                   state_dir=tmp_path, role='planner')
    O.decidir_disjuntor(tmp_path, 'abort', 'ricardo', 'Abortar esta matéria')
    assert O._read_manifest(tmp_path)['status'] == 'aborted'
    with pytest.raises(ValueError):
        E.executar('claude', prompt, tmp_path / 'out.md', None, 1,
                   state_dir=tmp_path, role='planner')
    assert len(calls) == 4


def test_outcome_condicional_e_segunda_rejeicao_pausa(tmp_path):
    O.inicializar_execucao(tmp_path, 'teste', 'C')
    for phase in ('intake_ready', 'drafting', 'draft_ready', 'candidate_ready'):
        O.avancar_fase(tmp_path, phase)
    result = O.avancar_fase(tmp_path, outcome='needs_revision')
    assert result['phase'] == 'drafting'
    assert result['transitions'][-1]['outcome'] == 'needs_revision'
    for phase in ('draft_ready', 'candidate_ready'):
        O.avancar_fase(tmp_path, phase)
    result = O.avancar_fase(tmp_path, outcome='needs_revision')
    assert result['status'] == 'paused'
    assert result['phase'] == 'candidate_ready'
    with pytest.raises(ValueError):
        O.avancar_fase(tmp_path, outcome='ok')


def test_outcome_nao_aprova_gate(tmp_path):
    O.inicializar_execucao(tmp_path, 'teste', 'B')
    state = O._read_manifest(tmp_path)
    state['phase'] = 'awaiting_skeleton_approval'
    O._write_json(tmp_path / 'run_manifest.json', state)
    with pytest.raises(ValueError):
        O.avancar_fase(tmp_path, outcome='approved')
    with pytest.raises(ValueError):
        O.avancar_fase(tmp_path, outcome='ok')
    assert O._read_manifest(tmp_path)['phase'] == 'awaiting_skeleton_approval'
