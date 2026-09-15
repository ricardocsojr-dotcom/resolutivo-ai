"""Contratos canônicos do motor RDAA V4.

Define estado, pacotes, recibos e erros.  Todas as fronteiras do motor
passam por estas estruturas – nenhum ``dict`` genérico é aceito.

Regras:
- ``RDAAState`` é o checkpoint autoritativo do LangGraph.
- ``Packet`` é o pacote mínimo enviado a um Combo via OmniRoute.
- ``Receipt`` registra a resposta do OmniRoute (ou sua ausência).
- Falha de validação levanta ``ContractError`` e bloqueia a fase.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, TypedDict


# ---------------------------------------------------------------------------
# Estado canônico (checkpoint do LangGraph)
# ---------------------------------------------------------------------------

class RDAAState(TypedDict, total=False):
    """Estado persistido pelo LangGraph em cada checkpoint."""

    matter_id: str
    nivel_peca: str                          # A | B | C
    phase: str                               # fase corrente do grafo
    status: str                              # executing | awaiting_approval | paused | aborted | published | vault_registered
    history: list[str]                       # fases visitadas, em ordem
    outputs: dict[str, Any]                  # saídas por papel (planner, writer, …)
    approvals: dict[str, dict[str, Any]]     # gates aprovados: gate → registro
    failures: dict[str, int]                 # contagem de falhas por fase
    consecutive_failures: int                # falhas consecutivas (disjuntor)
    hashes: dict[str, str]                   # sha256 de artefatos-chave
    state_dir: str                           # diretório canônico da matéria
    route: dict[str, Any]                    # rota calculada (snapshot de roteamento.json)
    executions: list[dict[str, Any]]         # registros de execuções de workers
    vault: dict[str, Any]                    # lookups e syncs
    transitions: list[dict[str, Any]]        # ledger de transições


# ---------------------------------------------------------------------------
# Papéis lógicos e mapeamento papel → fase de saída
# ---------------------------------------------------------------------------

ROLE_OUTPUT_PHASE: dict[str, str] = {
    "planner":  "sources_ready",
    "writer":   "draft_ready",
    "critic":   "critique_ready",
    "validator": "candidate_ready",
}

VALID_ROLES = frozenset({"planner", "writer", "writer_heavy", "writer_light",
                          "critic", "validator", "research", "reader"})

HUMAN_GATES: dict[str, str] = {
    "awaiting_skeleton_approval": "skeleton_approval",
    "release_ready":             "release_approval",
}


# ---------------------------------------------------------------------------
# Erros tipados
# ---------------------------------------------------------------------------

class ContractError(ValueError):
    """Violação de contrato – bloqueia a fase corrente."""


class GateError(PermissionError):
    """Tentativa de avançar sem aprovação humana."""


class CircuitBreakerError(RuntimeError):
    """Disjuntor aberto – matéria pausada."""


# ---------------------------------------------------------------------------
# Pacote mínimo
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Packet:
    """Pacote imutável entregue a um worker para um papel."""

    role: str
    combo: str                    # identificador do modelo em roteamento.json (legado de nome)
    system_prompt: str            # regras e contrato da etapa
    user_prompt: str              # pacote mínimo da matéria
    matter_id: str
    phase: str
    output_contract: str = ""     # nome do contrato de saída esperado
    timeout_seconds: int = 600
    effort: str = "medium"        # low | medium | high — esforço de raciocínio do worker

    def __post_init__(self) -> None:
        if self.role not in VALID_ROLES:
            raise ContractError(f"papel inválido: {self.role}")
        if not self.combo:
            raise ContractError("combo não informado")
        if not self.system_prompt.strip():
            raise ContractError("system_prompt vazio")
        if not self.user_prompt.strip():
            raise ContractError("user_prompt vazio")

    def sha256(self) -> str:
        """Hash determinístico do conteúdo do pacote."""
        blob = json.dumps(
            {"role": self.role, "combo": self.combo,
             "system": self.system_prompt, "user": self.user_prompt},
            ensure_ascii=False, sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    def to_omniroute_payload(self) -> dict[str, Any]:
        """Monta o corpo do POST para /v1/responses."""
        return {
            "model": self.combo,
            "input": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": self.user_prompt},
            ],
        }


# ---------------------------------------------------------------------------
# Recibo de execução
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class Receipt:
    """Recibo de uma chamada ao OmniRoute."""

    role: str
    transport: Literal["omniroute_http", "chat_passthrough"] = "omniroute_http"
    requested_combo: str = ""
    endpoint: str = "/v1/responses"
    request_id: str | None = None
    resolved_provider: str | None = None
    resolved_model: str | None = None
    fallback_used: str | None = None
    prompt_path: str = ""
    prompt_sha256: str = ""
    output_path: str = ""
    output_sha256: str = ""
    started_at: str = ""
    finished_at: str = ""
    duration_ms: int = 0
    http_status: int = 0
    outcome: Literal["ok", "error", "timeout", "quota", "invalid"] = "ok"
    error_message: str = ""

    def __post_init__(self) -> None:
        if not self.started_at:
            self.started_at = _now()

    def finalize(self, *, output_path: Path | None = None,
                 http_status: int = 200,
                 outcome: str = "ok",
                 error_message: str = "") -> None:
        """Fecha o recibo após a chamada."""
        self.finished_at = _now()
        self.http_status = http_status
        self.outcome = outcome  # type: ignore[assignment]
        self.error_message = error_message
        if output_path and output_path.is_file():
            self.output_path = str(output_path)
            self.output_sha256 = sha256_file(output_path)
        start = datetime.fromisoformat(self.started_at)
        end = datetime.fromisoformat(self.finished_at)
        self.duration_ms = int((end - start).total_seconds() * 1000)

    def to_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in self.__slots__}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    """SHA-256 incremental de um arquivo."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    """SHA-256 de uma string UTF-8."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_level(level: str) -> str:
    """Normaliza e valida o nível da peça."""
    level = str(level).strip().upper()
    if level not in {"A", "B", "C"}:
        raise ContractError(f"nivel_peca deve ser A, B ou C, recebido: {level!r}")
    return level


def load_route(level: str, route_path: Path | None = None) -> dict[str, Any]:
    """Carrega e valida a rota para o nível informado."""
    from pathlib import Path as _P
    if route_path is None:
        route_path = _P(__file__).resolve().parent / "roteamento.json"
    level = validate_level(level)
    payload = json.loads(route_path.read_text(encoding="utf-8"))
    spec = payload.get("levels", {}).get(level)
    if not isinstance(spec, dict):
        raise ContractError(f"rota para nível {level} não encontrada em {route_path}")
    return spec


def validate_phase_for_role(role: str, phase: str, route: dict[str, Any]) -> None:
    """Garante que o papel pode operar na fase corrente."""
    allowed = set(route.get("worker_allowed_phases", {}).get(role, []))
    if phase not in allowed:
        raise ContractError(
            f"papel {role} não autorizado na fase {phase}; "
            f"fases permitidas: {sorted(allowed)}"
        )
