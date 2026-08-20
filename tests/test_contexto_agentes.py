#!/usr/bin/env python3
"""Regressões do contexto compartilhado e provenance de pesquisa."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "revisor-rdaa" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from contexto_rdaa import build_context_pack, register_research  # noqa: E402
from estado_rdaa import add_provenance, initialize_state, persist_context  # noqa: E402



def _write_state(state_dir: Path, payload: dict) -> None:
    paths = initialize_state(state_dir, matter_id=payload["matter_id"])
    paths["state"].write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")



def _base_state(matter_id: str) -> dict:
    return {
        "schema_version": "2",
        "matter_id": matter_id,
        "facts": [{"id": "F-1", "campo": "numero_processo", "valor": matter_id}],
        "theses": [
            {"id": "T-1", "texto": "Tese aprovada", "status": "aprovada"},
            {"id": "T-2", "texto": "Tese em avaliação", "status": "proposta"},
        ],
        "hypotheses": [{"id": "H-1", "texto": "Hipótese alternativa", "status": "alternativa"}],
        "citations": [{"id": "C-1", "texto": "Citação selecionada"}],
        "decisions": [{"id": "D-1", "veredito": "Próximo passo explícito"}],
        "pending": [{"id": "P-1", "texto": "Conferir documento"}],
        "rules": [{"id": "R-1", "texto": "Regra formal"}],
        "semantic_blocks": [{"id": "B-1", "tipo": "numerado", "semantic_ids": ["T-1"]}],
    }



def _provenance_lines(state_dir: Path) -> list[dict]:
    path = state_dir / "provenance.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]



def test_build_context_pack_projects_only_relevant_fields() -> None:
    with tempfile.TemporaryDirectory() as temp:
        state_dir = Path(temp) / "caso-1"
        _write_state(state_dir, _base_state("caso-1"))
        add_provenance(
            state_dir,
            {
                "id": "SRC-1",
                "tipo": "jurisprudencia",
                "fonte": "STJ",
                "localizacao": "https://stj.example/1",
                "trecho": "Ementa literal",
                "status": "verificada_externamente",
                "origem": "buscar-jurisprudencia",
            },
        )

        redator = build_context_pack(state_dir, "redator")
        critico = build_context_pack(state_dir, "critico")
        revisor = build_context_pack(state_dir, "revisor")

        assert redator["task_type"] == "redator"
        assert redator["facts"] and redator["theses"] and redator["sources"]
        assert redator["decisions"] and redator["rules"]
        assert redator["semantic_blocks"]
        assert redator["hypotheses"] == []

        assert critico["facts"] and critico["theses"] and critico["hypotheses"]
        assert critico["sources"] and critico["pending"]
        assert critico["decisions"] == []
        assert critico["rules"] == []
        assert critico.get("semantic_blocks", []) == []

        assert revisor["facts"] and revisor["sources"] and revisor["pending"]
        assert revisor["rules"] and revisor["semantic_blocks"]
        assert revisor["theses"] == []
        assert revisor["decisions"] == []
        assert revisor["hypotheses"] == []


def test_register_research_marks_external_verification_and_deduplicates() -> None:
    with tempfile.TemporaryDirectory() as temp:
        state_dir = Path(temp) / "caso-pesquisa"
        first = register_research(
            state_dir,
            "jurisprudencia",
            {
                "id": "SRC-J-1",
                "fonte": "Jusbrasil",
                "url": "https://example.test/julgado-1",
                "trecho": "Ementa literal conferida",
                "origem": "buscar-jurisprudencia",
                "conferencia": {"metodo": "navegador", "data": "2026-08-20"},
            },
        )
        second = register_research(
            state_dir,
            "jurisprudencia",
            {
                "id": "SRC-J-1",
                "fonte": "Jusbrasil",
                "url": "https://example.test/julgado-1",
                "trecho": "Ementa literal conferida",
                "origem": "buscar-jurisprudencia",
                "conferencia": {"metodo": "navegador", "data": "2026-08-20"},
            },
        )

        assert first[0]["status"] == "verificada_externamente"
        assert second[0]["status"] == "verificada_externamente"
        lines = _provenance_lines(state_dir)
        assert len(lines) == 1
        assert lines[0]["id"] == "SRC-J-1"
        assert lines[0]["status"] == "verificada_externamente"
        assert lines[0]["origem"] == "buscar-jurisprudencia"
        assert lines[0]["conferencia"]["metodo"] == "navegador"
        assert lines[0]["conferencia"]["data"] == "2026-08-20"
        assert build_context_pack(state_dir, "pesquisa")["matter_id"] == "caso-pesquisa"


def test_different_agents_receive_different_packs_from_same_state() -> None:
    with tempfile.TemporaryDirectory() as temp:
        state_dir = Path(temp) / "caso-agentes"
        _write_state(state_dir, _base_state("caso-agentes"))
        register_research(state_dir, "lei", {"fonte": "Portal oficial", "texto": "Art. 1º"})

        council = build_context_pack(state_dir, "conselho")
        writer = build_context_pack(state_dir, "redator")

        assert council != writer
        assert council["hypotheses"]
        assert council["decisions"]
        assert writer["decisions"]
        assert writer["hypotheses"] == []
        assert writer["rules"]


def test_persist_context_structures_explicit_semantic_entities() -> None:
    with tempfile.TemporaryDirectory() as temp:
        state_dir = Path(temp) / "caso-semantico"
        context = {
            "numero_processo": "0000000-00.0000.8.26.0001",
            "teses": [{"id": "T-EXPLICIT", "texto": "Tese fornecida", "status": "proposta"}],
            "pedidos": ["Pedido principal"],
            "riscos": [{"id": "RISK-EXPLICIT", "descricao": "Risco declarado", "nivel": "alto"}],
            "decisoes": [{"id": "D-EXPLICIT", "veredito": "Decisão declarada"}],
            "regras": [{"id": "RULE-EXPLICIT", "texto": "Regra formal"}],
        }
        persist_context(state_dir, context)
        state = json.loads((state_dir / "matter_state.json").read_text(encoding="utf-8"))

        assert state["schema_version"] == "3"
        assert state["theses_structured"][0]["id"] == "T-EXPLICIT"
        assert state["requests"][0]["tipo"] == "pedido"
        assert state["risks"][0]["nivel"] == "alto"
        assert state["decisions"][0]["id"] == "D-EXPLICIT"
        assert state["rules"][0]["id"] == "RULE-EXPLICIT"


def test_matter_isolation_is_preserved_for_research_and_context() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        case_a = root / "processo-A"
        case_b = root / "processo-B"
        _write_state(case_a, _base_state("processo-A"))
        _write_state(case_b, _base_state("processo-B"))
        register_research(case_a, "lei", {"id": "SRC-A", "fonte": "Fonte A", "trecho": "A"})
        register_research(case_b, "lei", {"id": "SRC-B", "fonte": "Fonte B", "trecho": "B"})

        pack_a = build_context_pack(case_a, "pesquisa")
        pack_b = build_context_pack(case_b, "pesquisa")

        assert pack_a["matter_id"] == "processo-A"
        assert pack_b["matter_id"] == "processo-B"
        assert {item["id"] for item in pack_a["sources"]} == {"SRC-A"}
        assert {item["id"] for item in pack_b["sources"]} == {"SRC-B"}


if __name__ == "__main__":
    test_build_context_pack_projects_only_relevant_fields()
    test_register_research_marks_external_verification_and_deduplicates()
    test_different_agents_receive_different_packs_from_same_state()
    test_persist_context_structures_explicit_semantic_entities()
    test_matter_isolation_is_preserved_for_research_and_context()
    print("[OK] contexto de agentes, registro de pesquisa e isolamento passaram")
