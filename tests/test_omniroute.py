"""Testes unitários para orquestracao/omniroute.py."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from orquestracao.contracts import ContractError, Packet
from orquestracao.omniroute import OmniRouteClient, chat_passthrough


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _packet(**overrides) -> Packet:
    defaults = dict(
        role="writer",
        combo="RJ-Escrita-Pesada",
        system_prompt="regras da etapa",
        user_prompt="pacote mínimo da matéria",
        matter_id="test-001",
        phase="drafting",
    )
    defaults.update(overrides)
    return Packet(**defaults)


def _mock_response(status=200, json_body=None):
    """Cria um httpx.Response mockado."""
    if json_body is None:
        json_body = {
            "output": [{
                "type": "message",
                "content": [{"type": "output_text", "text": "Rascunho da peça."}],
            }],
        }
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status
    resp.headers = {"x-request-id": "req-12345"}
    resp.json.return_value = json_body
    resp.raise_for_status = MagicMock()
    if status >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            f"HTTP {status}", request=MagicMock(), response=resp,
        )
    return resp


# ---------------------------------------------------------------------------
# OmniRouteClient.send — sucesso
# ---------------------------------------------------------------------------

@patch.dict("os.environ", {"OMNIROUTE_API_KEY": "sk-test"})
def test_send_sucesso_formato_responses():
    client = OmniRouteClient()
    packet = _packet()
    mock_resp = _mock_response()

    with patch("httpx.Client") as MockClient:
        mock_instance = MagicMock()
        mock_instance.post.return_value = mock_resp
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        MockClient.return_value = mock_instance

        content, receipt = client.send(packet)

    assert content == "Rascunho da peça."
    assert receipt.outcome == "ok"
    assert receipt.http_status == 200
    assert receipt.request_id == "req-12345"
    assert receipt.requested_combo == "RJ-Escrita-Pesada"


@patch.dict("os.environ", {"OMNIROUTE_API_KEY": "sk-test"})
def test_send_sucesso_formato_chat_completions():
    client = OmniRouteClient()
    packet = _packet()
    body = {"choices": [{"message": {"content": "Resposta chat."}}]}
    mock_resp = _mock_response(json_body=body)

    with patch("httpx.Client") as MockClient:
        mock_instance = MagicMock()
        mock_instance.post.return_value = mock_resp
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        MockClient.return_value = mock_instance

        content, receipt = client.send(packet)

    assert content == "Resposta chat."
    assert receipt.outcome == "ok"


@patch.dict("os.environ", {"OMNIROUTE_API_KEY": "sk-test"})
def test_send_persiste_output(tmp_path):
    client = OmniRouteClient()
    packet = _packet()
    mock_resp = _mock_response()

    with patch("httpx.Client") as MockClient:
        mock_instance = MagicMock()
        mock_instance.post.return_value = mock_resp
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        MockClient.return_value = mock_instance

        content, receipt = client.send(packet, output_dir=tmp_path / "artifacts")

    assert receipt.output_path
    assert Path(receipt.output_path).is_file()
    assert receipt.output_sha256
    assert (tmp_path / "artifacts" / "writer-001.receipt.json").is_file()


# ---------------------------------------------------------------------------
# OmniRouteClient.send — falhas
# ---------------------------------------------------------------------------

@patch.dict("os.environ", {"OMNIROUTE_API_KEY": "sk-test"})
def test_send_resposta_sem_conteudo():
    client = OmniRouteClient()
    packet = _packet()
    mock_resp = _mock_response(json_body={"empty": True})

    with patch("httpx.Client") as MockClient:
        mock_instance = MagicMock()
        mock_instance.post.return_value = mock_resp
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        MockClient.return_value = mock_instance

        with pytest.raises(ContractError, match="conteúdo válido"):
            client.send(packet)


@patch.dict("os.environ", {"OMNIROUTE_API_KEY": "sk-test"})
def test_send_quota_excedida():
    client = OmniRouteClient()
    packet = _packet()
    mock_resp = _mock_response(status=429)

    with patch("httpx.Client") as MockClient:
        mock_instance = MagicMock()
        mock_instance.post.return_value = mock_resp
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        MockClient.return_value = mock_instance

        with pytest.raises(ContractError, match="quota"):
            client.send(packet)


def test_send_sem_api_key():
    client = OmniRouteClient()
    packet = _packet()
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ContractError, match="OMNIROUTE_API_KEY"):
            client.send(packet)


# ---------------------------------------------------------------------------
# _extract_content
# ---------------------------------------------------------------------------

def test_extract_content_formato_simplificado():
    payload = {"content": "Texto direto."}
    result = OmniRouteClient._extract_content(payload)
    assert result == "Texto direto."


def test_extract_content_responses_aceita_parte_textual_do_provider():
    payload = {"output": [{"type": "message", "content": [{"type": "text", "text": "Texto."}]}]}
    assert OmniRouteClient._extract_content(payload) == "Texto."


def test_extract_content_expoe_erro_do_omniroute():
    with pytest.raises(ContractError, match="modelo indisponível"):
        OmniRouteClient._extract_content({"status": "failed", "error": {"message": "modelo indisponível"}})


def test_extract_provider_info_nao_confunde_usage_com_provider():
    from orquestracao.contracts import Receipt
    receipt = Receipt(role="writer")
    OmniRouteClient._extract_provider_info(
        {"model": "Modelo X", "provider": "provedor-y", "usage": {"input_tokens": 10}},
        receipt,
    )
    assert receipt.resolved_model == "Modelo X"
    assert receipt.resolved_provider == "provedor-y"


def test_extract_content_vazio():
    with pytest.raises(ContractError, match="conteúdo válido"):
        OmniRouteClient._extract_content({})


# ---------------------------------------------------------------------------
# chat_passthrough
# ---------------------------------------------------------------------------

def test_chat_passthrough(tmp_path):
    out = tmp_path / "output.md"
    receipt = chat_passthrough("Peça simples nível C.", out)
    assert out.is_file()
    assert out.read_text(encoding="utf-8").strip() == "Peça simples nível C."
    assert receipt.transport == "chat_passthrough"
    assert receipt.outcome == "ok"
    assert receipt.output_sha256
    assert receipt.requested_combo == "chat_session"
