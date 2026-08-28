"""Testes determinísticos do motor Python de cálculo judicial."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "calculo-judicial" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from calculo_motor import MotorError, calculate  # noqa: E402


def _write_index(root: Path, name: str, rows: list[tuple[str, str]]) -> tuple[Path, str]:
    path = root / f"{name}.csv"
    content = "data,valor\n" + "\n".join(f"{record_date},{value}" for record_date, value in rows) + "\n"
    path.write_text(content, encoding="utf-8", newline="\n")
    return path, hashlib.sha256(content.encode("utf-8")).hexdigest()


def _write_manifest(root: Path, definitions: dict[str, dict]) -> Path:
    path = root / "manifest.json"
    path.write_text(json.dumps({"schema_version": "1", "indices": definitions}), encoding="utf-8")
    return path


def _approved_definition(filename: str, digest: str, series_type: str, convention: str) -> dict:
    return {
        "arquivo": filename,
        "tipo_serie": series_type,
        "unidade": "teste",
        "status": "aprovado",
        "sha256": digest,
        "convencoes": [convention],
    }


def _base_input(indice: str, convention: str, *, mode: str = "resumo") -> dict:
    return {
        "principal": "100.00",
        "data_inicio_correcao": "2024-01-01",
        "data_final": "2024-02-29",
        "indice": indice,
        "convencao_indice": convention,
        "modo": mode,
    }


def test_repository_manifest_has_all_real_indices_approved() -> None:
    # Todos os 10 índices reais (inpc/ipca/inpc/igp-m/selic/cdi/tjmg-nao-expurgada/
    # tjsp-tabela-pratica/tjrj/poupanca-nova/taxa-legal) foram aprovados com caso
    # dourado real em 2026-08-27 (ver index_manifest.json). tjsp simples e
    # tjmg-fator-atualizacao foram removidos por duplicação, não ficam pendentes.
    manifest = json.loads(
        (ROOT / "skills" / "calculo-judicial" / "references" / "index_manifest.json").read_text(encoding="utf-8")
    )
    statuses = {name: definition["status"] for name, definition in manifest["indices"].items()}
    assert statuses == {name: "aprovado" for name in statuses}


def test_monthly_percentage_and_simple_interest() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-mensal", [("2024-01-01", "10"), ("2024-02-01", "5")])
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-mensal.csv", digest, "taxa_mensal_percentual", "meses_calendario_inclusivos"
                )
            },
        )
        payload = _base_input("teste", "meses_calendario_inclusivos")
        payload.update(
            {
                "data_inicio_juros": "2024-01-01",
                "juros": {
                    "tipo": "simples_mensal",
                    "taxa": "1.00",
                    "base": "principal_corrigido",
                    "convencao": "meses_calendario_inclusivos",
                },
            }
        )
        result = calculate(payload, indices_dir=root, manifest_path=manifest)

    assert result["status"] == "ok"
    assert result["fator_correcao"] == "1.155"
    assert result["correcao"] == "15.50"
    assert result["juros"] == "2.31"
    assert result["total"] == "117.81"


def test_coverage_notice_when_flagged_in_manifest() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-cobertura", [("2024-01-01", "10"), ("2024-02-01", "5")])
        definition = _approved_definition("teste-cobertura.csv", digest, "taxa_mensal_percentual", "meses_calendario_inclusivos")
        definition["avisar_cobertura"] = True
        manifest = _write_manifest(root, {"teste": definition})
        payload = _base_input("teste", "meses_calendario_inclusivos")
        result = calculate(payload, indices_dir=root, manifest_path=manifest)
    assert "indice_teste_atualizado_ate_2024-02-01" in result["avisos"]


def test_negative_month_requires_explicit_treatment() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-negativo", [("2024-01-01", "10"), ("2024-02-01", "-5")])
        manifest = _write_manifest(
            root,
            {"teste": _approved_definition("teste-negativo.csv", digest, "taxa_mensal_percentual", "meses_calendario_inclusivos")},
        )
        payload = _base_input("teste", "meses_calendario_inclusivos")
        try:
            calculate(payload, indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "indice_negativo_sem_tratamento"
        else:
            raise AssertionError("mês negativo sem tratamento explícito deveria bloquear")


def test_negative_month_piso_zero_no_mes() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-negativo", [("2024-01-01", "10"), ("2024-02-01", "-5")])
        manifest = _write_manifest(
            root,
            {"teste": _approved_definition("teste-negativo.csv", digest, "taxa_mensal_percentual", "meses_calendario_inclusivos")},
        )
        payload = _base_input("teste", "meses_calendario_inclusivos")
        payload["tratamento_indice_negativo"] = "piso_zero_no_mes"
        result = calculate(payload, indices_dir=root, manifest_path=manifest)
    # fevereiro negativo não reduz: fator = 1.10 (janeiro) * 1 (fevereiro sem correção)
    assert result["fator_correcao"] == "1.1"
    assert result["correcao"] == "10.00"
    assert result["meses_com_indice_negativo"] == ["2024-02-01"]


def test_negative_month_aplicar_integralmente() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-negativo", [("2024-01-01", "10"), ("2024-02-01", "-5")])
        manifest = _write_manifest(
            root,
            {"teste": _approved_definition("teste-negativo.csv", digest, "taxa_mensal_percentual", "meses_calendario_inclusivos")},
        )
        payload = _base_input("teste", "meses_calendario_inclusivos")
        payload["tratamento_indice_negativo"] = "aplicar_integralmente"
        result = calculate(payload, indices_dir=root, manifest_path=manifest)
    # fator = 1.10 * 0.95 = 1.045 (deflação reduz, comportamento legado)
    assert result["fator_correcao"] == "1.045"
    assert result["correcao"] == "4.50"
    assert result["registros_processados"] == 2
    assert result["index_sha256"] == digest


def test_accumulated_factor_uses_first_and_last_factors() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(
            root,
            "teste-fator",
            [("2024-01-01", "100"), ("2024-02-01", "110"), ("2024-03-01", "121")],
        )
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-fator.csv", digest, "fator_acumulado", "meses_calendario_inclusivos"
                )
            },
        )
        payload = _base_input("teste", "meses_calendario_inclusivos", mode="detalhado")
        payload["data_final"] = "2024-03-31"
        result = calculate(payload, indices_dir=root, manifest_path=manifest)

    assert result["fator_correcao"] == "1.21"
    assert result["correcao"] == "21.00"
    assert result["total"] == "121.00"
    assert result["avisos"] == ["juros_nao_aplicados_sem_data_inicio_juros"]
    assert len(result["detalhamento"]) == 3
    assert result["detalhamento"][-1]["fator_acumulado"] == "1.21"


def test_daily_decimal_series_is_inclusive() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-diario", [("2024-01-01", "0.01"), ("2024-01-02", "0.02")])
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-diario.csv", digest, "taxa_diaria_decimal", "registros_com_data_no_intervalo_inclusivo"
                )
            },
        )
        payload = {
            "principal": "100.00",
            "data_inicio_correcao": "2024-01-01",
            "data_final": "2024-01-02",
            "indice": "teste",
            "convencao_indice": "registros_com_data_no_intervalo_inclusivo",
            "modo": "resumo",
        }
        result = calculate(payload, indices_dir=root, manifest_path=manifest)

    assert result["fator_correcao"] == "1.0302"
    assert result["correcao"] == "3.02"
    assert result["total"] == "103.02"
    assert result["registros_processados"] == 2


def test_daily_gap_is_blocked() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-diario-lacuna", [("2024-01-01", "0.01"), ("2024-01-03", "0.01")])
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-diario-lacuna.csv", digest, "taxa_diaria_decimal", "registros_com_data_no_intervalo_inclusivo"
                )
            },
        )
        payload = {
            "principal": "100.00",
            "data_inicio_correcao": "2024-01-01",
            "data_final": "2024-01-03",
            "indice": "teste",
            "convencao_indice": "registros_com_data_no_intervalo_inclusivo",
        }
        try:
            calculate(payload, indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "dias_ausentes"
        else:
            raise AssertionError("dia ausente não poderia ser completado")


def test_anniversary_series_matches_bcb_calculator() -> None:
    # Caso dourado poupança: R$10.000,00 de 01/01/2026 a 01/07/2026, regra nova,
    # verificado na calculadora do cidadão do BCB (www3.bcb.gov.br/CALCIDADAO) em
    # 27/08/2026 -> fator 1,04044920, valor corrigido R$10.404,49.
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(
            root,
            "teste-poupanca",
            [
                ("2026-01-01", "0.006727"),
                ("2026-02-01", "0.006213"),
                ("2026-03-01", "0.006744"),
                ("2026-04-01", "0.006687"),
                ("2026-05-01", "0.006695"),
                ("2026-06-01", "0.006718"),
                ("2026-07-01", "0.006738"),
            ],
        )
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-poupanca.csv", digest, "taxa_aniversario_percentual", "aniversario_deposito"
                )
            },
        )
        payload = {
            "principal": "10000.00",
            "data_inicio_correcao": "2026-01-01",
            "data_final": "2026-07-01",
            "indice": "teste",
            "convencao_indice": "aniversario_deposito",
        }
        result = calculate(payload, indices_dir=root, manifest_path=manifest)

    assert result["total"] == "10404.49"
    assert result["registros_processados"] == 6


def test_anniversary_series_requires_aligned_final_date() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-poupanca", [("2026-01-01", "0.006727"), ("2026-02-01", "0.006213")])
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-poupanca.csv", digest, "taxa_aniversario_percentual", "aniversario_deposito"
                )
            },
        )
        payload = {
            "principal": "100.00",
            "data_inicio_correcao": "2026-01-01",
            "data_final": "2026-01-15",
            "indice": "teste",
            "convencao_indice": "aniversario_deposito",
        }
        try:
            calculate(payload, indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "aniversario_final_nao_bate"
        else:
            raise AssertionError("data_final fora do ciclo de aniversário não poderia ser aceita")


def test_anniversary_series_blocks_missing_anchor() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(
            root, "teste-poupanca", [("2026-01-01", "0.006727"), ("2026-03-01", "0.006744")]
        )
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-poupanca.csv", digest, "taxa_aniversario_percentual", "aniversario_deposito"
                )
            },
        )
        payload = {
            "principal": "100.00",
            "data_inicio_correcao": "2026-01-01",
            "data_final": "2026-03-01",
            "indice": "teste",
            "convencao_indice": "aniversario_deposito",
        }
        try:
            calculate(payload, indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "aniversario_ausente"
        else:
            raise AssertionError("aniversário sem registro no índice não poderia ser completado")


def test_simple_prorata_daily_series_matches_bcb_examples() -> None:
    # Caso dourado taxa legal (Lei 14.905/2024): a metodologia do BCB é juros
    # simples com acumulação aditiva e intervalo semiaberto [inicio, fim) — o dia
    # final não entra na soma. Verificado em 27/08/2026 contra a própria
    # Calculadora do Cidadão do BCB (www3.bcb.gov.br/CALCIDADAO), aba Taxa Legal.
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(
            root, "teste-taxa-legal", [("2024-08-30", "0.00019526"), ("2024-08-31", "0.00019526")]
        )
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-taxa-legal.csv", digest, "taxa_diaria_simples_pro_rata", "dias_corridos_semiaberto"
                )
            },
        )
        # Exemplo da metodologia do BCB: 30/08/2024 a 31/08/2024, R$1.000,00 -> R$1.000,20
        payload = {
            "principal": "1000.00",
            "data_inicio_correcao": "2024-08-30",
            "data_final": "2024-08-31",
            "indice": "teste",
            "convencao_indice": "dias_corridos_semiaberto",
        }
        result = calculate(payload, indices_dir=root, manifest_path=manifest)
        assert result["total"] == "1000.20"
        assert result["registros_processados"] == 1  # dia 31 (fim) não entra na soma


def test_simple_prorata_daily_series_blocks_missing_day_before_end() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(
            root, "teste-taxa-legal-lacuna", [("2024-08-30", "0.0002"), ("2024-09-01", "0.0002")]
        )
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-taxa-legal-lacuna.csv", digest, "taxa_diaria_simples_pro_rata", "dias_corridos_semiaberto"
                )
            },
        )
        payload = {
            "principal": "100.00",
            "data_inicio_correcao": "2024-08-30",
            "data_final": "2024-09-01",
            "indice": "teste",
            "convencao_indice": "dias_corridos_semiaberto",
        }
        try:
            calculate(payload, indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "dias_ausentes"
        else:
            raise AssertionError("dia sem registro antes do fim não poderia ser completado")


def test_coverage_outside_index_is_blocked() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-cobertura", [("2024-02-01", "1"), ("2024-03-01", "1")])
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-cobertura.csv", digest, "taxa_mensal_percentual", "meses_calendario_inclusivos"
                )
            },
        )
        payload = _base_input("teste", "meses_calendario_inclusivos")
        try:
            calculate(payload, indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "cobertura_insuficiente"
        else:
            raise AssertionError("período fora da cobertura não poderia ser aceito")


def test_partial_month_requires_explicit_treatment() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-parcial", [("2024-01-01", "1"), ("2024-02-01", "1")])
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-parcial.csv", digest, "taxa_mensal_percentual", "meses_calendario_inclusivos"
                )
            },
        )
        payload = {
            "principal": "100.00",
            "data_inicio_correcao": "2024-01-15",
            "data_final": "2024-02-20",
            "indice": "teste",
            "convencao_indice": "meses_calendario_inclusivos",
        }
        try:
            calculate(payload, indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "periodo_parcial_sem_convencao"
        else:
            raise AssertionError("período parcial não poderia ser aceito sem declaração")

        payload["tratamento_periodo_parcial"] = "mes_completo_declarado"
        result = calculate(payload, indices_dir=root, manifest_path=manifest)
        assert result["tratamento_periodo_parcial"] == "mes_completo_declarado"


def test_invalid_input_and_incomplete_interest_are_blocked() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-entrada", [("2024-01-01", "1"), ("2024-02-01", "1")])
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-entrada.csv", digest, "taxa_mensal_percentual", "meses_calendario_inclusivos"
                )
            },
        )
        cases = [
            ({"principal": "0"}, "principal_invalido"),
            ({"principal": "100", "data_final": "2023-12-31"}, "periodo_invalido"),
        ]
        for overrides, expected_code in cases:
            payload = _base_input("teste", "meses_calendario_inclusivos")
            payload.update(overrides)
            try:
                calculate(payload, indices_dir=root, manifest_path=manifest)
            except MotorError as exc:
                assert exc.code == expected_code
            else:
                raise AssertionError(f"entrada inválida deveria gerar {expected_code}")

        payload = _base_input("teste", "meses_calendario_inclusivos")
        payload.update({"data_inicio_juros": "2024-01-01", "juros": {}})
        try:
            calculate(payload, indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "tipo_juros_nao_suportado"
        else:
            raise AssertionError("juros sem parâmetros não poderiam ser aceitos")


def test_pending_index_is_blocked_before_arithmetic() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-pendente", [("2024-01-01", "1")])
        manifest = _write_manifest(
            root,
            {
                "teste": {
                    **_approved_definition(
                        "teste-pendente.csv", digest, "taxa_mensal_percentual", "meses_calendario_inclusivos"
                    ),
                    "status": "pendente_validacao",
                }
            },
        )
        try:
            calculate(_base_input("teste", "meses_calendario_inclusivos"), indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "indice_pendente"
        else:
            raise AssertionError("índice pendente não poderia ser executado")


def test_hash_mismatch_is_blocked() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _write_index(root, "teste-hash", [("2024-01-01", "1"), ("2024-02-01", "1")])
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-hash.csv", "0" * 64, "taxa_mensal_percentual", "meses_calendario_inclusivos"
                )
            },
        )
        try:
            calculate(_base_input("teste", "meses_calendario_inclusivos"), indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "hash_indice_divergente"
        else:
            raise AssertionError("hash divergente não poderia ser aceito")


def test_missing_month_and_missing_index_are_blocked() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-lacuna", [("2024-01-01", "1"), ("2024-03-01", "1")])
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-lacuna.csv", digest, "taxa_mensal_percentual", "meses_calendario_inclusivos"
                )
            },
        )
        payload = _base_input("teste", "meses_calendario_inclusivos")
        payload["data_final"] = "2024-03-31"
        try:
            calculate(payload, indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "meses_ausentes"
        else:
            raise AssertionError("mês ausente não poderia ser interpolado")

        try:
            calculate(_base_input("nao-cadastrado", "meses_calendario_inclusivos"), indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "indice_desconhecido"
        else:
            raise AssertionError("índice desconhecido não poderia ser executado")


def test_segmented_monthly_interest_requires_complete_contiguous_months() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        _, digest = _write_index(root, "teste-segmentado", [("2024-01-01", "0"), ("2024-02-01", "0")])
        manifest = _write_manifest(
            root,
            {
                "teste": _approved_definition(
                    "teste-segmentado.csv", digest, "taxa_mensal_percentual", "meses_calendario_inclusivos"
                )
            },
        )
        payload = _base_input("teste", "meses_calendario_inclusivos")
        payload["data_inicio_juros"] = "2024-01-01"
        payload["juros"] = {
            "tipo": "simples_mensal_segmentado",
            "segmentos": [
                {
                    "inicio": "2024-01-01",
                    "fim": "2024-01-31",
                    "taxa": "1.00",
                    "unidade_taxa": "percentual_mensal",
                    "base": "principal",
                    "convencao": "meses_calendario_inclusivos",
                },
                {
                    "inicio": "2024-02-01",
                    "fim": "2024-02-29",
                    "taxa": "2.00",
                    "unidade_taxa": "percentual_mensal",
                    "base": "principal",
                    "convencao": "meses_calendario_inclusivos",
                },
            ],
        }
        result = calculate(payload, indices_dir=root, manifest_path=manifest)
        assert result["juros"] == "3.00"
        assert result["total"] == "103.00"
        assert len(result["segmentos_juros"]) == 2

        missing_start = dict(payload)
        missing_start.pop("data_inicio_juros")
        try:
            calculate(missing_start, indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "juros_segmentados_sem_data"
        else:
            raise AssertionError("juros segmentados não poderiam inferir o termo inicial")

        payload["juros"]["segmentos"][1]["inicio"] = "2024-02-02"
        try:
            calculate(payload, indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "segmentos_juros_nao_contiguos"
        else:
            raise AssertionError("segmento não contíguo não poderia ser interpretado por aproximação")

        payload["juros"]["segmentos"][1]["inicio"] = "2024-02-01"
        payload["juros"]["segmentos"][1]["unidade_taxa"] = "percentual_anual"
        try:
            calculate(payload, indices_dir=root, manifest_path=manifest)
        except MotorError as exc:
            assert exc.code == "unidade_juros_nao_implementada"
        else:
            raise AssertionError("taxa anual segmentada não poderia ser executada sem homologação")


def main() -> None:
    test_repository_manifest_has_all_real_indices_approved()
    test_monthly_percentage_and_simple_interest()
    test_coverage_notice_when_flagged_in_manifest()
    test_negative_month_requires_explicit_treatment()
    test_negative_month_piso_zero_no_mes()
    test_negative_month_aplicar_integralmente()
    test_accumulated_factor_uses_first_and_last_factors()
    test_daily_decimal_series_is_inclusive()
    test_daily_gap_is_blocked()
    test_anniversary_series_matches_bcb_calculator()
    test_anniversary_series_requires_aligned_final_date()
    test_anniversary_series_blocks_missing_anchor()
    test_simple_prorata_daily_series_matches_bcb_examples()
    test_simple_prorata_daily_series_blocks_missing_day_before_end()
    test_coverage_outside_index_is_blocked()
    test_partial_month_requires_explicit_treatment()
    test_invalid_input_and_incomplete_interest_are_blocked()
    test_pending_index_is_blocked_before_arithmetic()
    test_hash_mismatch_is_blocked()
    test_missing_month_and_missing_index_are_blocked()
    test_segmented_monthly_interest_requires_complete_contiguous_months()
    print("PASS test_calculo_motor")


if __name__ == "__main__":
    main()
