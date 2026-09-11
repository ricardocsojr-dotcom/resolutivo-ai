"""Regressão da escala usando os CSVs reais, sem acesso à rede."""
import csv
import sys
from decimal import Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/calculo-judicial/scripts'))
from calculo_motor import calculate, MotorError
from test_calculo_motor import _write_index, _write_manifest, _approved_definition, _base_input


def test_unidade_mensal_desconhecida_bloqueia(tmp_path):
    _, digest = _write_index(tmp_path, 'mensal', [('2024-01-01', '0.01'), ('2024-02-01', '0.02')])
    definition = _approved_definition('mensal.csv', digest, 'taxa_mensal_percentual', 'meses_calendario_inclusivos')
    definition['unidade'] = 'ambigua'
    manifest = _write_manifest(tmp_path, {'teste': definition})
    with pytest.raises(MotorError) as exc:
        calculate(_base_input('teste', 'meses_calendario_inclusivos'), indices_dir=tmp_path, manifest_path=manifest)
    assert exc.value.code == 'unidade_indice_invalida'

@pytest.mark.parametrize('indice', ['inpc', 'ipca', 'igp-m', 'selic', 'cdi'])
@pytest.mark.parametrize('tratamento', ['aplicar_integralmente', 'piso_zero_no_mes'])
def test_csv_real_multimes_sem_dupla_divisao(indice, tratamento):
    indices = ROOT / 'referencias/indices'
    with (indices / f'{indice}.csv').open(encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if '2026-01-01' <= r['data'] <= '2026-07-01']
    assert len(rows) == 7
    payload = {'principal':'10000', 'indice':indice,
               'data_inicio_correcao':'2026-01-01', 'data_final':'2026-07-31',
               'convencao_indice':'meses_calendario_inclusivos',
               'tratamento_indice_negativo':tratamento, 'modo':'detalhado'}
    result = calculate(payload, indices_dir=indices,
        manifest_path=ROOT / 'skills/calculo-judicial/references/index_manifest.json')
    with localcontext() as ctx:
        ctx.prec = 50
        factor = Decimal(1)
        for raw, detail in zip(rows, result['detalhamento']):
            rate = Decimal(raw['valor'])
            if tratamento == 'piso_zero_no_mes':
                rate = max(Decimal(0), rate)
            factor *= 1 + rate  # CSV já é fração: 0.01 representa 1%.
            expected = format((Decimal(10000)*factor).quantize(Decimal('.01'), rounding=ROUND_HALF_UP), '.2f')
            assert detail['saldo_corrigido'] == expected
        assert result['total'] == expected
        assert result['detalhamento'][-1]['fator_acumulado'] == result['fator_correcao']
