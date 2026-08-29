#!/usr/bin/env python3
"""Motor determinístico local para atualização monetária e juros judiciais.

O módulo não escolhe índice, termo inicial, regime jurídico ou fórmula jurídica.
Ele executa somente o contrato aritmético explicitamente declarado no JSON e no
manifesto local do índice. A série precisa estar aprovada no manifesto.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path
from typing import Any


CENT = Decimal("0.01")
HUNDRED = Decimal("100")
SUPPORTED_MODES = {"resumo", "detalhado"}
SUPPORTED_CONVENTIONS = {
    "registros_com_data_no_intervalo_inclusivo",
    "meses_calendario_inclusivos",
    "aniversario_deposito",
    "dias_corridos_semiaberto",
}
SUPPORTED_INTEREST_TYPES = {"simples_mensal", "simples_mensal_segmentado"}
SUPPORTED_SEGMENT_INTEREST_UNITS = {"percentual_mensal", "percentual_anual"}


class MotorError(ValueError):
    """Erro objetivo e serializável de validação ou execução."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class IndexDefinition:
    name: str
    filename: str
    series_type: str
    unit: str
    status: str
    sha256: str | None
    allowed_conventions: tuple[str, ...]
    notify_coverage: bool = False


@dataclass(frozen=True)
class IndexRow:
    record_date: date
    value: Decimal


@dataclass(frozen=True)
class LoadedIndex:
    definition: IndexDefinition
    rows: tuple[IndexRow, ...]
    sha256: str
    first_date: date
    last_date: date


@dataclass(frozen=True)
class InterestSegment:
    start: date
    end: date
    rate: Decimal
    base: str
    convention: str
    unit: str


def _error(code: str, message: str) -> MotorError:
    return MotorError(code, message)


def _decimal(value: Any, field: str, *, positive: bool = False) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise _error("campo_numerico_invalido", f"{field} deve ser um número decimal explícito.")
    try:
        decimal = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise _error("campo_numerico_invalido", f"{field} não é um número decimal válido.") from exc
    if not decimal.is_finite():
        raise _error("campo_numerico_invalido", f"{field} deve ser finito.")
    if positive and decimal <= 0:
        raise _error("principal_invalido", f"{field} deve ser maior que zero.")
    return decimal


def _iso_date(value: Any, field: str) -> date:
    if not isinstance(value, str) or not value.strip():
        raise _error("data_invalida", f"{field} deve ser uma data ISO explícita no formato AAAA-MM-DD.")
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise _error("data_invalida", f"{field} não é uma data ISO válida: {value!r}.") from exc


def _month_key(value: date) -> tuple[int, int]:
    return value.year, value.month


def _add_calendar_month(value: date, anchor_day: int | None = None) -> date:
    # ponytail: anchor_day preserva o dia original do depósito através de meses
    # curtos — sem isso, Jan/31 -> Fev/28 -> Mar/28 (deveria voltar a Mar/31).
    day = anchor_day if anchor_day is not None else value.day
    year = value.year + value.month // 12
    month = value.month % 12 + 1
    day = min(day, monthrange(year, month)[1])
    return date(year, month, day)


def _month_keys_between(start: date, end: date) -> list[tuple[int, int]]:
    year, month = start.year, start.month
    result: list[tuple[int, int]] = []
    while (year, month) <= (end.year, end.month):
        result.append((year, month))
        month += 1
        if month == 13:
            year += 1
            month = 1
    return result


def _json_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("campo_objeto_invalido", f"{field} deve ser um objeto JSON.")
    return value


def _load_manifest(path: Path) -> dict[str, IndexDefinition]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise _error("manifesto_inexistente", f"Manifesto de índices não encontrado em {path}.") from exc
    except json.JSONDecodeError as exc:
        raise _error("manifesto_invalido", f"Manifesto de índices inválido em {path}: {exc.msg}.") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("indices"), dict):
        raise _error("manifesto_invalido", "Manifesto deve conter o objeto 'indices'.")

    definitions: dict[str, IndexDefinition] = {}
    for name, raw in payload["indices"].items():
        if not isinstance(raw, dict):
            raise _error("manifesto_invalido", f"Definição do índice {name!r} deve ser um objeto.")
        filename = raw.get("arquivo")
        if isinstance(filename, str) and (Path(filename).name != filename or Path(filename).is_absolute()):
            raise _error("manifesto_invalido", f"Arquivo inseguro para o índice {name!r}.")
        series_type = raw.get("tipo_serie")
        unit = raw.get("unidade")
        status = raw.get("status")
        sha256 = raw.get("sha256")
        conventions = raw.get("convencoes", list(SUPPORTED_CONVENTIONS))
        if not all(isinstance(item, str) and item.strip() for item in (filename, series_type, unit, status)):
            raise _error("manifesto_invalido", f"Definição incompleta para o índice {name!r}.")
        if not isinstance(conventions, list) or not all(isinstance(item, str) for item in conventions):
            raise _error("manifesto_invalido", f"Convenções inválidas para o índice {name!r}.")
        definitions[str(name)] = IndexDefinition(
            name=str(name),
            filename=filename,
            series_type=series_type,
            unit=unit,
            status=status,
            sha256=str(sha256) if sha256 else None,
            allowed_conventions=tuple(conventions),
            notify_coverage=bool(raw.get("avisar_cobertura", False)),
        )
    return definitions


def _read_index(path: Path, definition: IndexDefinition) -> LoadedIndex:
    if definition.status != "aprovado":
        raise _error(
            "indice_pendente",
            f"Índice {definition.name!r} está com status {definition.status!r}; exige aprovação explícita.",
        )
    if not definition.sha256:
        raise _error("hash_ausente", f"Índice aprovado {definition.name!r} não possui SHA-256 no manifesto.")
    if not path.is_file():
        raise _error("arquivo_indice_inexistente", f"Arquivo do índice não encontrado em {path}.")

    raw_bytes = path.read_bytes()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    if digest != definition.sha256.lower():
        raise _error(
            "hash_indice_divergente",
            f"SHA-256 divergente para {definition.name!r}. Esperado {definition.sha256}, encontrado {digest}.",
        )

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _error("csv_indice_invalido", f"CSV do índice {definition.name!r} não está em UTF-8.") from exc

    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames != ["data", "valor"]:
        raise _error(
            "cabecalho_indice_invalido",
            f"CSV do índice {definition.name!r} deve ter exatamente o cabeçalho data,valor.",
        )

    rows: list[IndexRow] = []
    previous: date | None = None
    seen: set[date] = set()
    for line_number, raw in enumerate(reader, start=2):
        if set(raw) != {"data", "valor"}:
            raise _error("linha_csv_invalida", f"Linha {line_number} do índice {definition.name!r} contém colunas inesperadas.")
        record_date = _iso_date(raw.get("data"), f"data da linha {line_number}")
        if record_date in seen:
            raise _error("datas_duplicadas", f"Data duplicada no índice {definition.name!r}: {record_date.isoformat()}.")
        if previous is not None and record_date <= previous:
            raise _error("datas_fora_de_ordem", f"Datas fora de ordem no índice {definition.name!r} na linha {line_number}.")
        value = _decimal(raw.get("valor"), f"valor da linha {line_number}")
        rows.append(IndexRow(record_date, value))
        seen.add(record_date)
        previous = record_date
    if not rows:
        raise _error("indice_vazio", f"Índice {definition.name!r} não possui registros.")
    return LoadedIndex(definition, tuple(rows), digest, rows[0].record_date, rows[-1].record_date)


def _select_rows(index: LoadedIndex, start: date, end: date, convention: str) -> list[IndexRow]:
    if convention not in SUPPORTED_CONVENTIONS:
        raise _error("convencao_invalida", f"Convenção não suportada: {convention!r}.")
    if convention == "registros_com_data_no_intervalo_inclusivo":
        coverage_ok = index.first_date <= start and end <= index.last_date
    elif convention == "dias_corridos_semiaberto":
        if end == start:
            coverage_ok = True  # janela [start, end) vazia — nada a cobrir
        else:
            last_needed = end.fromordinal(end.toordinal() - 1)
            coverage_ok = index.first_date <= start and last_needed <= index.last_date
    elif convention == "aniversario_deposito":
        # ponytail: `end` aqui é só o marco final do ciclo, nunca uma linha
        # precificada em si (o último aniversário cobrado é sempre <= 1 mês
        # antes) — exigir cobertura do mês de `end` é forte demais. A checagem
        # precisa (âncora por âncora) já acontece mais abaixo.
        coverage_ok = index.first_date <= start
    else:
        coverage_ok = _month_key(index.first_date) <= _month_key(start) and _month_key(end) <= _month_key(index.last_date)
    if not coverage_ok:
        raise _error(
            "cobertura_insuficiente",
            f"Período solicitado {start.isoformat()} a {end.isoformat()} excede a cobertura "
            f"{index.first_date.isoformat()} a {index.last_date.isoformat()}.",
        )
    if convention not in index.definition.allowed_conventions:
        raise _error(
            "convencao_nao_autorizada",
            f"A convenção {convention!r} não está autorizada para o índice {index.definition.name!r}.",
        )

    if convention == "registros_com_data_no_intervalo_inclusivo":
        selected = [row for row in index.rows if start <= row.record_date <= end]
        if not selected:
            raise _error("periodo_sem_registros", "Nenhum registro do índice está dentro do intervalo informado.")
        if index.definition.series_type == "taxa_diaria_decimal":
            selected_dates = {row.record_date for row in selected}
            missing_dates: list[str] = []
            cursor = start
            while cursor <= end:
                if cursor not in selected_dates:
                    missing_dates.append(cursor.isoformat())
                cursor = cursor.fromordinal(cursor.toordinal() + 1)
            if missing_dates:
                raise _error(
                    "dias_ausentes",
                    f"Dias sem registro no intervalo solicitado: {', '.join(missing_dates[:20])}.",
                )
        return selected

    if convention == "dias_corridos_semiaberto":
        selected = [row for row in index.rows if start <= row.record_date < end]
        selected_dates = {row.record_date for row in selected}
        missing_dates: list[str] = []
        cursor = start
        while cursor < end:
            if cursor not in selected_dates:
                missing_dates.append(cursor.isoformat())
            cursor = cursor.fromordinal(cursor.toordinal() + 1)
        if missing_dates:
            raise _error(
                "dias_ausentes",
                f"Dias sem registro no intervalo solicitado: {', '.join(missing_dates[:20])}.",
            )
        return selected

    if convention == "aniversario_deposito":
        anchors = [start]
        while anchors[-1] < end:
            anchors.append(_add_calendar_month(anchors[-1], anchor_day=start.day))
        if anchors[-1] != end:
            raise _error(
                "aniversario_final_nao_bate",
                f"data_final ({end.isoformat()}) não coincide com um ciclo mensal a partir de "
                f"data_inicio_correcao ({start.isoformat()}); poupança só credita no aniversário do depósito.",
            )
        rows_by_date = {row.record_date: row for row in index.rows}
        missing = [d.isoformat() for d in anchors[:-1] if d not in rows_by_date]
        if missing:
            raise _error("aniversario_ausente", f"Sem registro do índice nas datas de aniversário: {', '.join(missing)}.")
        return [rows_by_date[d] for d in anchors[:-1]]

    month_keys = _month_keys_between(start, end)
    selected_by_month: dict[tuple[int, int], list[IndexRow]] = {}
    for row in index.rows:
        key = _month_key(row.record_date)
        if key in month_keys:
            selected_by_month.setdefault(key, []).append(row)
    missing = [f"{year:04d}-{month:02d}" for year, month in month_keys if (year, month) not in selected_by_month]
    if missing:
        raise _error("meses_ausentes", f"Meses sem registro no intervalo solicitado: {', '.join(missing)}.")
    multiple = [
        f"{year:04d}-{month:02d}"
        for year, month in month_keys
        if len(selected_by_month[(year, month)]) != 1
    ]
    if multiple:
        raise _error("registros_mensais_ambiguous", f"Meses com mais de um registro: {', '.join(multiple)}.")
    return [selected_by_month[key][0] for key in month_keys]


NEGATIVE_TREATMENTS = {"piso_zero_no_mes", "aplicar_integralmente"}


def _factor_for_rows(index: LoadedIndex, rows: list[IndexRow], negative_treatment: str | None = None) -> Decimal:
    if index.definition.series_type == "taxa_mensal_percentual":
        factor = Decimal("1")
        for row in rows:
            monthly = Decimal("1") + row.value / HUNDRED
            if negative_treatment == "piso_zero_no_mes" and monthly < Decimal("1"):
                monthly = Decimal("1")
            factor *= monthly
        return factor
    if index.definition.series_type in ("taxa_diaria_decimal", "taxa_aniversario_percentual"):
        factor = Decimal("1")
        for row in rows:
            factor *= Decimal("1") + row.value
        return factor
    if index.definition.series_type == "taxa_diaria_simples_pro_rata":
        return Decimal("1") + sum((row.value for row in rows), Decimal("0"))
    if index.definition.series_type == "fator_acumulado":
        if len(rows) < 2:
            raise _error("fator_sem_intervalo", "Fator acumulado exige ao menos dois registros no intervalo.")
        if rows[0].value == 0:
            raise _error("fator_inicial_zero", "Fator acumulado não pode começar em zero.")
        return rows[-1].value / rows[0].value
    raise _error("tipo_serie_nao_suportado", f"Tipo de série não suportado: {index.definition.series_type!r}.")


def _round_money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _money_text(value: Decimal) -> str:
    return format(_round_money(value), ".2f")


def _decimal_text(value: Decimal, places: int = 12) -> str:
    normalized = value.quantize(Decimal(1).scaleb(-places))
    return format(normalized, "f").rstrip("0").rstrip(".") or "0"


def _validate_segmented_interest(raw: dict[str, Any], final_date: date, partial_treatment: str | None) -> tuple[InterestSegment, ...]:
    raw_segments = raw.get("segmentos")
    if not isinstance(raw_segments, list) or not raw_segments:
        raise _error("segmentos_juros_ausentes", "Juros segmentados exigem lista não vazia em juros.segmentos.")
    segments: list[InterestSegment] = []
    previous_end: date | None = None
    for index, raw_segment in enumerate(raw_segments):
        segment = _json_object(raw_segment, f"juros.segmentos[{index}]")
        start = _iso_date(segment.get("inicio"), f"juros.segmentos[{index}].inicio")
        end = _iso_date(segment.get("fim"), f"juros.segmentos[{index}].fim")
        if end < start:
            raise _error("segmento_juros_invalido", f"Segmento de juros {index} termina antes de começar.")
        if previous_end is not None:
            expected_start = previous_end.fromordinal(previous_end.toordinal() + 1)
            if start != expected_start:
                raise _error("segmentos_juros_nao_contiguos", "Segmentos de juros devem ser contíguos e sem sobreposição.")
        unit = segment.get("unidade_taxa")
        if not isinstance(unit, str) or unit not in SUPPORTED_SEGMENT_INTEREST_UNITS:
            raise _error("unidade_juros_invalida", "unidade_taxa deve ser percentual_mensal ou percentual_anual.")
        convention = segment.get("convencao")
        if convention != "meses_calendario_inclusivos":
            raise _error("convencao_segmento_juros_invalida", "Segmentos exigem convencao=meses_calendario_inclusivos.")
        if start.day != 1 or end.day != monthrange(end.year, end.month)[1]:
            raise _error("segmento_juros_parcial_nao_implementado", "Segmentos de juros exigem meses completos; pró-rata e mudanças dentro do mês aguardam fórmula aprovada.")
        base = segment.get("base")
        if not isinstance(base, str) or base not in {"principal", "principal_corrigido"}:
            raise _error("base_segmento_juros_invalida", "Base de cada segmento deve ser principal ou principal_corrigido.")
        rate = _decimal(segment.get("taxa"), f"juros.segmentos[{index}].taxa")
        segments.append(InterestSegment(start, end, rate, base, convention, unit))
        previous_end = end
    if segments[-1].end != final_date:
        raise _error("segmentos_juros_incompletos", "O último segmento de juros deve terminar na data_final.")
    return tuple(segments)


def _validate_input(payload: Any) -> dict[str, Any]:
    data = _json_object(payload, "entrada")
    principal = _decimal(data.get("principal"), "principal", positive=True)
    start = _iso_date(data.get("data_inicio_correcao"), "data_inicio_correcao")
    end = _iso_date(data.get("data_final"), "data_final")
    if end < start:
        raise _error("periodo_invalido", "data_final não pode ser anterior a data_inicio_correcao.")
    indice = data.get("indice")
    if not isinstance(indice, str) or not indice.strip():
        raise _error("indice_ausente", "indice deve ser informado explicitamente.")
    convention = data.get("convencao_indice")
    if not isinstance(convention, str) or convention not in SUPPORTED_CONVENTIONS:
        raise _error("convencao_invalida", "convencao_indice deve ser uma convenção suportada e explícita.")
    mode = data.get("modo", "resumo")
    if not isinstance(mode, str) or mode not in SUPPORTED_MODES:
        raise _error("modo_invalido", f"modo deve ser um de {sorted(SUPPORTED_MODES)}.")
    partial_treatment = data.get("tratamento_periodo_parcial")
    if partial_treatment is not None and partial_treatment != "mes_completo_declarado":
        raise _error("tratamento_parcial_invalido", "tratamento_periodo_parcial não é suportado.")
    negative_treatment = data.get("tratamento_indice_negativo")
    if negative_treatment is not None and negative_treatment not in NEGATIVE_TREATMENTS:
        raise _error(
            "tratamento_indice_negativo_invalido",
            f"tratamento_indice_negativo deve ser um de {sorted(NEGATIVE_TREATMENTS)}.",
        )
    if convention == "meses_calendario_inclusivos":
        correction_is_partial = start.day != 1 or end.day != monthrange(end.year, end.month)[1]
        if correction_is_partial and partial_treatment != "mes_completo_declarado":
            raise _error(
                "periodo_parcial_sem_convencao",
                "Datas parciais exigem tratamento_periodo_parcial=mes_completo_declarado explícito.",
            )

    interest_start_raw = data.get("data_inicio_juros")
    interest = data.get("juros")
    interest_segments: tuple[InterestSegment, ...] | None = None
    if interest_start_raw is None and interest in (None, {}, {"tipo": "nenhum"}):
        interest_start = None
        interest_data: dict[str, Any] | None = None
    elif isinstance(interest, dict) and interest.get("tipo") == "simples_mensal_segmentado":
        if interest_start_raw is None:
            raise _error("juros_segmentados_sem_data", "Juros segmentados exigem data_inicio_juros explícita.")
        interest_data = _json_object(interest, "juros")
        interest_segments = _validate_segmented_interest(interest_data, end, partial_treatment)
        interest_start = _iso_date(interest_start_raw, "data_inicio_juros")
        if interest_start != interest_segments[0].start:
            raise _error("inicio_segmentado_divergente", "data_inicio_juros deve coincidir com o início do primeiro segmento.")
    else:
        if interest_start_raw is None:
            raise _error("juros_sem_data", "juros foi informado sem data_inicio_juros.")
        interest_start = _iso_date(interest_start_raw, "data_inicio_juros")
        if interest_start > end:
            raise _error("juros_fora_do_periodo", "data_inicio_juros não pode ser posterior a data_final.")
        interest_data = _json_object(interest, "juros")
        if interest_data.get("tipo") != "simples_mensal":
            raise _error("tipo_juros_nao_suportado", "Somente juros simples mensais ou simples mensais segmentados estão implementados.")
        interest_base = interest_data.get("base")
        if not isinstance(interest_base, str) or interest_base not in {"principal", "principal_corrigido"}:
            raise _error("base_juros_invalida", "base de juros deve ser principal ou principal_corrigido.")
        if interest_data.get("convencao") != "meses_calendario_inclusivos":
            raise _error("convencao_juros_invalida", "Juros simples mensais exigem meses_calendario_inclusivos.")
        if interest_start.day != 1 or end.day != monthrange(end.year, end.month)[1]:
            if partial_treatment != "mes_completo_declarado":
                raise _error(
                    "juros_parciais_sem_convencao",
                    "Datas parciais dos juros exigem tratamento_periodo_parcial=mes_completo_declarado explícito.",
                )
        _decimal(interest_data.get("taxa"), "juros.taxa")
    return {
        "principal": principal,
        "start": start,
        "end": end,
        "indice": indice.strip(),
        "convention": convention,
        "mode": mode,
        "interest_start": interest_start,
        "interest": interest_data,
        "interest_segments": interest_segments,
        "partial_treatment": partial_treatment,
        "negative_treatment": negative_treatment,
    }


def calculate(payload: dict[str, Any], *, indices_dir: Path | str, manifest_path: Path | str) -> dict[str, Any]:
    data = _validate_input(payload)
    definitions = _load_manifest(Path(manifest_path))
    definition = definitions.get(data["indice"])
    if definition is None:
        raise _error("indice_desconhecido", f"Índice não cadastrado no manifesto: {data['indice']!r}.")
    index = _read_index(Path(indices_dir) / definition.filename, definition)
    rows = _select_rows(index, data["start"], data["end"], data["convention"])
    if definition.series_type == "fator_acumulado" and data["convention"] != "meses_calendario_inclusivos":
        raise _error("convencao_fator_invalida", "Fator acumulado exige seleção por meses de calendário explícitos.")

    negative_months = [row for row in rows if row.value < 0] if definition.series_type == "taxa_mensal_percentual" else []
    if negative_months and data["negative_treatment"] is None:
        raise _error(
            "indice_negativo_sem_tratamento",
            "Mês com índice negativo no período selecionado exige tratamento_indice_negativo "
            "explícito ('piso_zero_no_mes' ou 'aplicar_integralmente').",
        )

    with localcontext() as context:
        context.prec = 50
        correction_factor = _factor_for_rows(index, rows, data["negative_treatment"])
        principal_corrected = data["principal"] * correction_factor
        interest_value = Decimal("0")
        interest_months = 0
        interest_segments_result: list[dict[str, str]] = []
        if data["interest_segments"] is not None:
            for segment in data["interest_segments"]:
                if segment.unit != "percentual_mensal":
                    raise _error("unidade_juros_nao_implementada", "Percentual anual segmentado exige caso dourado e fórmula aprovada antes da execução.")
                months = len(_month_keys_between(segment.start, segment.end))
                base = data["principal"] if segment.base == "principal" else principal_corrected
                segment_value = base * (segment.rate / HUNDRED) * Decimal(months)
                interest_value += segment_value
                interest_months += months
                interest_segments_result.append(
                    {
                        "inicio": segment.start.isoformat(),
                        "fim": segment.end.isoformat(),
                        "taxa": _decimal_text(segment.rate),
                        "unidade_taxa": segment.unit,
                        "base": segment.base,
                        "meses": str(months),
                        "juros": _money_text(segment_value),
                    }
                )
        elif data["interest_start"] is not None:
            interest_months = len(_month_keys_between(data["interest_start"], data["end"]))
            rate = _decimal(data["interest"]["taxa"], "juros.taxa") / HUNDRED
            base = data["principal"] if data["interest"]["base"] == "principal" else principal_corrected
            interest_value = base * rate * Decimal(interest_months)
        total = principal_corrected + interest_value

    # Formatação e detalhamento também precisam de precisão >28 dígitos: um fator
    # acumulado de período longo pode gerar mais casas do que o contexto Decimal
    # padrão suporta, e quantize() fora desse contexto levanta InvalidOperation.
    with localcontext() as context:
        context.prec = 50
        result: dict[str, Any] = {
            "status": "ok",
            "indice": data["indice"],
            "tipo_serie": definition.series_type,
            "periodo": {"inicio": data["start"].isoformat(), "fim": data["end"].isoformat()},
            "principal": _money_text(data["principal"]),
            "fator_correcao": _decimal_text(correction_factor),
            "correcao": _money_text(principal_corrected - data["principal"]),
            "juros": _money_text(interest_value),
            "total": _money_text(total),
            "meses_processados": len(_month_keys_between(data["start"], data["end"])) if data["convention"] == "meses_calendario_inclusivos" else None,
            "registros_processados": len(rows),
            "meses_juros": interest_months,
            "segmentos_juros": interest_segments_result,
            "cobertura": {
                "inicio_indice": index.first_date.isoformat(),
                "fim_indice": index.last_date.isoformat(),
                "selecionada_inicio": rows[0].record_date.isoformat() if rows else data["start"].isoformat(),
                "selecionada_fim": rows[-1].record_date.isoformat() if rows else data["start"].isoformat(),
            },
            "avisos": (
                ([] if data["interest_start"] is not None else ["juros_nao_aplicados_sem_data_inicio_juros"])
                + (
                    [f"indice_{data['indice']}_atualizado_ate_{index.last_date.isoformat()}"]
                    if definition.notify_coverage
                    else []
                )
            ),
            "index_sha256": index.sha256,
            "modo": data["mode"],
            "tratamento_periodo_parcial": data.get("partial_treatment"),
            "tratamento_indice_negativo": data.get("negative_treatment"),
            "meses_com_indice_negativo": [row.record_date.isoformat() for row in negative_months],
        }
        if data["mode"] == "detalhado":
            detail: list[dict[str, str]] = []
            running_factor = Decimal("1")
            for row in rows:
                if definition.series_type == "fator_acumulado":
                    running_factor = row.value / rows[0].value
                elif definition.series_type in ("taxa_diaria_decimal", "taxa_aniversario_percentual"):
                    running_factor *= Decimal("1") + row.value
                elif definition.series_type == "taxa_diaria_simples_pro_rata":
                    running_factor += row.value
                else:
                    running_factor *= Decimal("1") + row.value / HUNDRED
                detail.append(
                    {
                        "data": row.record_date.isoformat(),
                        "valor_indice": _decimal_text(row.value),
                        "fator_acumulado": _decimal_text(running_factor),
                        "saldo_corrigido": _money_text(data["principal"] * running_factor),
                    }
                )
            result["detalhamento"] = detail
    return result


def _default_paths() -> tuple[Path, Path]:
    root = Path(__file__).resolve().parents[3]
    return root / "referencias" / "indices", Path(__file__).resolve().parents[1] / "references" / "index_manifest.json"


def main(argv: list[str] | None = None) -> int:
    default_indices, default_manifest = _default_paths()
    parser = argparse.ArgumentParser(description="Motor determinístico local de cálculo judicial")
    parser.add_argument("--input", required=True, type=Path, help="JSON de entrada")
    parser.add_argument("--output", type=Path, help="Arquivo JSON de saída")
    parser.add_argument("--indices-dir", type=Path, default=default_indices)
    parser.add_argument("--manifest", type=Path, default=default_manifest)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = calculate(payload, indices_dir=args.indices_dir, manifest_path=args.manifest)
        exit_code = 0
    except (OSError, json.JSONDecodeError) as exc:
        result = {"status": "erro", "codigo": "entrada_arquivo_invalida", "mensagem": str(exc)}
        exit_code = 1
    except MotorError as exc:
        result = {"status": "erro", "codigo": exc.code, "mensagem": exc.message}
        exit_code = 1
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
