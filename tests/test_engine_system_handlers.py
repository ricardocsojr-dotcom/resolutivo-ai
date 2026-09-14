"""Testes do mecanismo de system_handlers no motor RDAA V4.

Verifica que fases sem papel de IA podem executar handlers
deterministicos (nao-IA), seguindo o mesmo tratamento de disjuntor
e projecao de manifesto que workers de IA.
"""

from pathlib import Path

from orquestracao.engine import RDAAEngine


ROUTE_PATH = Path(__file__).resolve().parents[1] / "orquestracao" / "roteamento.json"


def fake_worker(role, state):
    return {"role": role, "ok": True}


def test_system_handler_executa_em_fase_sem_papel(tmp_path):
    """Um system_handler roda numa fase de sistema (ex.: qa_passed).

    Nota: o ``state`` recebido pelo handler e o snapshot ANTES da
    atualizacao do node atual -- por isso ``state['phase']`` ainda
    reflete a fase anterior, nao a fase que esta sendo processada.
    """
    calls = []

    def qa_handler(state):
        calls.append("chamado")
        return {"status": "PASS"}

    def pub_handler(state):
        return {"status": "ok"}

    def vault_handler(state):
        return {"status": "ok"}

    engine = RDAAEngine(
        tmp_path / "c",
        "C",
        worker=fake_worker,
        system_handlers={"qa_passed": qa_handler, "published": pub_handler, "vault_registered": vault_handler},
        route_path=ROUTE_PATH,
    )
    try:
        result = engine.initialize("materia-1")
        assert calls == ["chamado"]
        assert result["outputs"]["system:qa_passed"] == {"status": "PASS"}
        assert result["phase"] == "vault_registered"
    finally:
        engine.close()


def test_system_handler_falha_incrementa_disjuntor(tmp_path):
    """Falha em um system_handler incrementa o disjuntor (1 falha por travessia).

    Dentro de uma única chamada ``initialize`` (um só invoke do grafo),
    cada nó é visitado uma vez; o disjuntor só abre (pausa) quando o
    mesmo nó falha em travessias subsequentes (retomadas), acumulando
    ``consecutive_failures`` ao longo de invocações separadas.
    """
    def failing_handler(state):
        raise RuntimeError("qa reprovado")

    engine = RDAAEngine(
        tmp_path / "c",
        "C",
        worker=fake_worker,
        system_handlers={"qa_passed": failing_handler},
        route_path=ROUTE_PATH,
    )
    try:
        result = engine.initialize("materia-2")
        assert result["consecutive_failures"] == 1
        executions = result.get("executions", [])
        qa_executions = [e for e in executions if e["phase"] == "qa_passed"]
        assert qa_executions[-1]["outcome"] == "error"
        assert qa_executions[-1]["role"] == "system:qa_passed"
    finally:
        engine.close()


def test_sem_system_handler_fase_critica_levanta_contrato(tmp_path):
    engine = RDAAEngine(
        tmp_path / "c",
        "C",
        worker=fake_worker,
        route_path=ROUTE_PATH,
    )
    try:
        result = engine.initialize("materia-3")
        assert result["status"] == "failed"

        state = engine.state()
        error_msg = state["executions"][-1]["error"]
        assert "handler de sistema obrigatorio ausente" in error_msg
    finally:
        engine.close()
