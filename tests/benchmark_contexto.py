#!/usr/bin/env python3
"""Benchmark local de contexto e roteamento com fixtures anonimizadas."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "revisor-rdaa" / "scripts"
import sys

sys.path.insert(0, str(SCRIPT_DIR))

from contexto_rdaa import TASK_TYPES, build_context_pack  # noqa: E402
from estado_rdaa import persist_context  # noqa: E402
from semantica_rdaa import measure_context_pack, route_for_matter  # noqa: E402



def _load_context(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))



def _variant(base: dict[str, Any], name: str) -> dict[str, Any]:
    context = json.loads(json.dumps(base, ensure_ascii=False))
    context["matter_id"] = f"benchmark-{name}"
    if name == "medio":
        context["nivel_risco"] = "medio"
        context["teses"] = [{"id": "T-M-1", "texto": "Tese declarada para benchmark", "status": "proposta"}]
        context["pedidos"] = [{"id": "REQ-M-1", "texto": "Pedido declarado"}]
    elif name == "alto":
        context["nivel_risco"] = "alto"
        context["teses"] = [
            {"id": "T-A-1", "texto": "Tese principal declarada", "status": "aprovada"},
            {"id": "T-A-2", "texto": "Tese alternativa declarada", "status": "proposta"},
        ]
        context["pedidos"] = [
            {"id": "REQ-A-1", "texto": "Pedido principal"},
            {"id": "REQ-A-2", "texto": "Pedido subsidiário"},
        ]
        context["riscos"] = [{"id": "R-A-1", "descricao": "Risco explicitamente declarado", "nivel": "alto", "origem": "usuario"}]
        context["regras"] = [{"id": "RULE-A-1", "texto": "Regra explicitamente fornecida"}]
    return context



def _state_bytes(state_dir: Path) -> int:
    total = 0
    for name in ("matter_state.json", "provenance.jsonl", "run_manifest.json"):
        path = state_dir / name
        if path.exists():
            total += path.stat().st_size
    return total



def run_benchmark(fixture: Path) -> dict[str, Any]:
    base = _load_context(fixture)
    cases: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="rdaa-benchmark-") as temp:
        root = Path(temp)
        for name in ("sem-nivel", "medio", "alto"):
            context = _variant(base, name)
            state_dir = root / name
            persist_context(state_dir, context)
            route = route_for_matter(state_dir)
            rows: list[dict[str, Any]] = []
            full_state = _state_bytes(state_dir)
            for task_type in sorted(TASK_TYPES):
                pack = build_context_pack(state_dir, task_type)
                measure = measure_context_pack(pack)
                rows.append(
                    {
                        "task_type": task_type,
                        **measure,
                        "full_state_bytes": full_state,
                        "pack_to_state_ratio": round(measure["bytes"] / full_state, 4) if full_state else None,
                    }
                )
            cases.append(
                {
                    "case": name,
                    "risk_level": route["risk_level"],
                    "risk_source": route["risk_source"],
                    "required": route["required"],
                    "recommended": route["recommended"],
                    "rows": rows,
                }
            )
    return {
        "fixture": str(fixture),
        "measurement_note": "Proxies locais de tamanho; não equivalem diretamente a créditos do Claude Code.",
        "task_types": sorted(TASK_TYPES),
        "cases": cases,
    }



def markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# Benchmark local de contexto RDAA",
        "",
        "> Medidas de bytes, caracteres e itens são proxies de engenharia. Elas não são uma medição direta de créditos do Claude Code.",
        "",
        "| Caso | Nível explícito | Agentes recomendados | Tarefa | Bytes do pacote | Bytes do estado | Razão pacote/estado |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for case in result["cases"]:
        recommended = ", ".join(case["recommended"]) or "nenhum"
        for row in case["rows"]:
            lines.append(
                f"| {case['case']} | {case['risk_level'] or 'nenhum'} | {recommended} | "
                f"{row['task_type']} | {row['bytes']} | {row['full_state_bytes']} | {row['pack_to_state_ratio']} |"
            )
    lines.extend(
        [
            "",
            "## Interpretação segura",
            "",
            "O pacote específico deve ser menor que o estado completo na maioria das tarefas, mas a razão varia com a quantidade de registros. O benchmark mede somente o volume local serializado e confirma que o nível desconhecido não aciona conselho ou crítico automaticamente.",
            "",
            "A comparação não mede qualidade da peça, tokens efetivos, custo ou resultado jurídico. Para medir economia real de créditos, seria necessário comparar estas medidas com dados do ambiente de execução do Claude Code.",
        ]
    )
    return "\n".join(lines) + "\n"



def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark local de contexto RDAA")
    parser.add_argument("--fixture", type=Path, default=ROOT / "tests" / "fixtures" / "context_happy.json")
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    args = parser.parse_args()
    result = run_benchmark(args.fixture)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_out.write_text(markdown_report(result), encoding="utf-8")
    print(f"[OK] benchmark gravado em {args.json_out} e {args.markdown_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
