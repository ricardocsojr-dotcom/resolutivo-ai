"""Cliente HTTP único para o OmniRoute.

Responsabilidades:
- Enviar pacotes a ``/v1/responses`` com o nome exato do Combo como ``model``.
- Registrar status HTTP, request ID e duração.
- Re-tentar apenas falha transitória autorizada, sem mudar Combo.
- Quota, indisponibilidade ou resposta inválida contam como falha da etapa.
- API key vem exclusivamente de variável de ambiente; nunca persistida.

Regra V4:  O RDAA não cria fallback próprio; fallback pertence ao Combo.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from orquestracao.contracts import (
    ContractError,
    Packet,
    Receipt,
    sha256_file,
    sha256_text,
)

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

DEFAULT_ENDPOINT = "/v1/responses"
DEFAULT_BASE_URL = os.environ.get("OMNIROUTE_BASE_URL", "http://localhost:20128")
DEFAULT_TIMEOUT = 600  # segundos
MAX_RETRIES = 1        # 1 retry para falha transitória (total = 2 tentativas)
TRANSIENT_CODES = frozenset({429, 502, 503, 504})


def _api_key() -> str:
    """Resolve API key exclusivamente de variável de ambiente."""
    key = os.environ.get("OMNIROUTE_API_KEY", "")
    if not key:
        raise ContractError(
            "OMNIROUTE_API_KEY não definida; "
            "a chave deve vir do ambiente, nunca de arquivo"
        )
    return key


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Cliente
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class OmniRouteClient:
    """Cliente HTTP para ``/v1/responses`` do OmniRoute."""

    base_url: str = DEFAULT_BASE_URL
    timeout: int = DEFAULT_TIMEOUT

    def send(
        self,
        packet: Packet,
        *,
        output_dir: Path | None = None,
    ) -> tuple[str, Receipt]:
        """Envia um pacote e devolve (conteúdo da resposta, recibo).

        Raises:
            ContractError: resposta inválida, quota ou payload incompatível.
            httpx.HTTPStatusError: erro HTTP não-transitório após retries.
        """
        receipt = Receipt(
            role=packet.role,
            requested_combo=packet.combo,
            endpoint=DEFAULT_ENDPOINT,
            prompt_sha256=packet.sha256(),
        )

        body = packet.to_omniroute_payload()
        url = f"{self.base_url}{DEFAULT_ENDPOINT}"
        headers = {
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
        }

        content = ""
        last_exc: Exception | None = None

        for attempt in range(1 + MAX_RETRIES):
            try:
                started = time.monotonic()
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(url, json=body, headers=headers)

                receipt.http_status = resp.status_code
                receipt.request_id = resp.headers.get("x-request-id")

                if resp.status_code in TRANSIENT_CODES and attempt < MAX_RETRIES:
                    time.sleep(min(2 ** attempt, 8))
                    continue

                resp.raise_for_status()

                payload = resp.json()
                content = self._extract_content(payload)
                receipt.finalize(outcome="ok", http_status=resp.status_code)

                # Persiste saída se output_dir informado
                if output_dir:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    out_path = output_dir / f"{packet.role}-001.md"
                    out_path.write_text(content + "\n", encoding="utf-8")
                    receipt.output_path = str(out_path)
                    receipt.output_sha256 = sha256_file(out_path)

                # Tenta extrair metadados do provider resolvido
                self._extract_provider_info(payload, receipt)

                return content, receipt

            except httpx.HTTPStatusError as exc:
                last_exc = exc
                status = exc.response.status_code
                if status == 429:
                    receipt.finalize(outcome="quota", http_status=status,
                                    error_message="quota excedida pelo OmniRoute")
                    raise ContractError("quota excedida pelo OmniRoute") from exc
                receipt.finalize(outcome="error", http_status=status,
                                error_message=str(exc))
                raise

            except httpx.TimeoutException as exc:
                last_exc = exc
                receipt.finalize(outcome="timeout", http_status=0,
                                error_message=f"timeout após {self.timeout}s")
                raise ContractError(f"timeout no OmniRoute: {exc}") from exc

            except Exception as exc:
                last_exc = exc
                receipt.finalize(outcome="error", http_status=0,
                                error_message=str(exc))
                raise

        # Não deveria chegar aqui, mas caso chegue:
        receipt.finalize(outcome="error", error_message=str(last_exc))
        raise ContractError(f"falha após {1 + MAX_RETRIES} tentativas: {last_exc}")

    # --- Extração de conteúdo ---

    @staticmethod
    def _extract_content(payload: dict[str, Any]) -> str:
        """Extrai o texto da resposta do OmniRoute.

        Suporta os formatos:
        - {"output": [{"content": [{"text": "..."}]}]}   (Responses API)
        - {"choices": [{"message": {"content": "..."}}]}  (Chat Completions)
        - {"content": "..."}                              (simplificado)
        """
        # Formato Responses API
        if "output" in payload and isinstance(payload["output"], list):
            for item in payload["output"]:
                if isinstance(item, dict) and item.get("type") == "message":
                    for part in item.get("content", []):
                        if isinstance(part, dict) and part.get("type") == "output_text":
                            text = part.get("text", "").strip()
                            if text:
                                return text

        # Formato Chat Completions
        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            msg = choices[0].get("message", {})
            text = msg.get("content", "").strip()
            if text:
                return text

        # Formato simplificado
        if isinstance(payload.get("content"), str) and payload["content"].strip():
            return payload["content"].strip()

        raise ContractError(
            "resposta do OmniRoute não contém conteúdo válido; "
            f"chaves recebidas: {sorted(payload.keys())}"
        )

    @staticmethod
    def _extract_provider_info(payload: dict[str, Any], receipt: Receipt) -> None:
        """Tenta extrair informações do provider resolvido (não obrigatório)."""
        # Apenas registra se disponível – nunca falha
        try:
            if "model" in payload:
                receipt.resolved_model = str(payload["model"])
            usage = payload.get("usage", {})
            if isinstance(usage, dict) and usage:
                # Armazena como metadata no receipt via resolved_provider
                receipt.resolved_provider = json.dumps(usage, ensure_ascii=False)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Modo passthrough para nível C (motor == chat)
# ---------------------------------------------------------------------------

def chat_passthrough(prompt: str, output_path: Path) -> Receipt:
    """Para nível C: o modelo do chat escreve diretamente, sem HTTP.

    O conteúdo é copiado do prompt para a saída.  Não há chamada a CLI.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt + "\n", encoding="utf-8")
    receipt = Receipt(
        role="writer",
        transport="chat_passthrough",
        requested_combo="chat_session",
        prompt_sha256=sha256_text(prompt),
        output_path=str(output_path),
        output_sha256=sha256_file(output_path),
    )
    receipt.finalize(outcome="ok", http_status=200)
    return receipt
