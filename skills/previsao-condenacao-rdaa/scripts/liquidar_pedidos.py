#!/usr/bin/env python3
"""Liquidação determinística de pedidos + provisão ponderada.

Existe para tirar do texto livre do modelo exatamente a conta que fazia a
previsão de condenação dar um valor diferente a cada rodada: soma de
parcelas por período e multiplicação por percentual de risco. Preencha o
JSON com os valores extraídos da petição/contestação (isso continua sendo
leitura e julgamento jurídico) e deixe o script somar (isso é aritmética,
não deveria variar).

Uso:
    python liquidar_pedidos.py pedidos.json

Formato de pedidos.json — lista de objetos:
[
  {
    "pedido": "Repetição de indébito - cobranças jan/2022 a mar/2023",
    "tipo": "material",
    "valor_unitario": 89.90,
    "periodicidade": "mensal",        // "mensal" ou "unico"
    "data_inicio": "2022-01-01",      // obrigatório se mensal (YYYY-MM-DD)
    "data_fim": "2023-03-01",         // obrigatório se mensal (YYYY-MM-DD)
    "risco": "provavel"               // "provavel"|"possivel"|"remoto", ou número 0-1, ou 0-100
  },
  {
    "pedido": "Dano moral - negativação indevida",
    "tipo": "moral",
    "valor_unitario": 8000.00,
    "periodicidade": "unico",
    "risco": 0.5
  }
]
"""
import json
import sys
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENT = Decimal("0.01")
HUNDRED = Decimal("100")

RISCO_LABELS = {
    "provavel": Decimal("1"), "provável": Decimal("1"),
    "possivel": Decimal("0.5"), "possível": Decimal("0.5"),
    "remoto": Decimal("0"),
}


def _decimal(value, field):
    # Decimal(str(value)) em vez de Decimal(value) direto: evita herdar o
    # ruído binário de um float já parseado (str() de float usa a
    # representação mínima que reconstrói o mesmo valor, igual ao literal
    # original). Mesmo padrão usado em calculo_motor.py.
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field} não é um número decimal válido: {value!r}") from exc


def normalizar_risco(risco):
    if isinstance(risco, str):
        chave = risco.strip().lower()
        if chave not in RISCO_LABELS:
            raise ValueError(f"risco textual desconhecido: {risco!r} (use provavel/possivel/remoto)")
        return RISCO_LABELS[chave]
    valor = _decimal(risco, "risco")
    return valor / HUNDRED if valor > 1 else valor


def meses_entre(data_inicio, data_fim):
    ini = date.fromisoformat(data_inicio)
    fim = date.fromisoformat(data_fim)
    if fim < ini:
        raise ValueError(f"data_fim ({data_fim}) anterior a data_inicio ({data_inicio})")
    # conta meses inclusive (jan a mar = 3 meses), pelo dia de calendário, não pró-rata
    return (fim.year - ini.year) * 12 + (fim.month - ini.month) + 1


def liquidar_pedido(p):
    periodicidade = p.get("periodicidade", "unico")
    valor_unitario = _decimal(p["valor_unitario"], "valor_unitario")
    if periodicidade == "mensal":
        n_meses = meses_entre(p["data_inicio"], p["data_fim"])
        valor_base = (valor_unitario * n_meses).quantize(CENT, rounding=ROUND_HALF_UP)
    elif periodicidade == "unico":
        valor_base = valor_unitario.quantize(CENT, rounding=ROUND_HALF_UP)
    else:
        raise ValueError(f"periodicidade inválida: {periodicidade!r} (use mensal/unico)")

    risco_pct = normalizar_risco(p["risco"])
    provisao = (valor_base * risco_pct).quantize(CENT, rounding=ROUND_HALF_UP)
    return valor_base, risco_pct, provisao


def processar(pedidos):
    linhas = []
    total_liquidado = Decimal("0")
    total_provisao = Decimal("0")
    for p in pedidos:
        valor_base, risco_pct, provisao = liquidar_pedido(p)
        linhas.append({
            "pedido": p["pedido"],
            "tipo": p.get("tipo", ""),
            "valor_liquidado": valor_base,
            "risco_pct": risco_pct,
            "provisao_ponderada": provisao,
        })
        total_liquidado += valor_base
        total_provisao += provisao
    return linhas, total_liquidado.quantize(CENT, rounding=ROUND_HALF_UP), total_provisao.quantize(CENT, rounding=ROUND_HALF_UP)


def imprimir(linhas, total_liquidado, total_provisao):
    print(f"{'Pedido':<50} {'Tipo':<10} {'Valor liquidado':>16} {'Risco':>7} {'Provisão':>14}")
    print("-" * 100)
    for l in linhas:
        print(f"{l['pedido'][:50]:<50} {l['tipo']:<10} {l['valor_liquidado']:>16,.2f} "
              f"{l['risco_pct']*100:>6.0f}% {l['provisao_ponderada']:>14,.2f}")
    print("-" * 100)
    print(f"{'TOTAL':<69} {total_liquidado:>16,.2f} {'':>7} {total_provisao:>14,.2f}")


def demo():
    """Self-check: roda com um exemplo fixo e confere o resultado esperado."""
    pedidos = [
        {"pedido": "Repetição de indébito", "tipo": "material", "valor_unitario": 100.0,
         "periodicidade": "mensal", "data_inicio": "2022-01-01", "data_fim": "2022-03-01",
         "risco": "provavel"},
        {"pedido": "Dano moral", "tipo": "moral", "valor_unitario": 8000.0,
         "periodicidade": "unico", "risco": 50},
    ]
    linhas, total_liquidado, total_provisao = processar(pedidos)
    assert linhas[0]["valor_liquidado"] == Decimal("300.00"), linhas[0]  # 3 meses x 100
    assert linhas[0]["provisao_ponderada"] == Decimal("300.00")  # risco 100%
    assert linhas[1]["risco_pct"] == Decimal("0.5")  # "50" normalizado para 0.5
    assert linhas[1]["provisao_ponderada"] == Decimal("4000.00")
    assert total_liquidado == Decimal("8300.00")
    assert total_provisao == Decimal("4300.00")
    # Regressão do bug de float: 3 parcelas de 0.10 deveriam somar exatamente
    # 0.30 em Decimal (em float, 0.1 + 0.1 + 0.1 != 0.3).
    linhas_centavos, total_centavos, _ = processar([
        {"pedido": "Centavos", "tipo": "material", "valor_unitario": 0.10,
         "periodicidade": "mensal", "data_inicio": "2024-01-01", "data_fim": "2024-03-01",
         "risco": "remoto"},
    ])
    assert linhas_centavos[0]["valor_liquidado"] == Decimal("0.30"), linhas_centavos[0]
    print("demo() ok: liquidação e provisão ponderada conferem.")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--demo":
        demo()
        sys.exit(0)
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        pedidos = json.load(f)
    linhas, total_liquidado, total_provisao = processar(pedidos)
    imprimir(linhas, total_liquidado, total_provisao)
