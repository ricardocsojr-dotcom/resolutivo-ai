"""Testes de autenticação OAuth 2.1, Bearer token e segurança de logs."""

import pytest
import hashlib
import base64
import urllib.parse
from starlette.testclient import TestClient
from src.server import app
from src.auth.security import (
    create_access_token,
    verify_token,
    sanitize_log_message,
    OAUTH_CLIENT_ID,
    OAUTH_CLIENT_SECRET,
)

@pytest.fixture
def client():
    return TestClient(app)

def test_jwt_create_and_verify():
    """Testa a geração e verificação de JWT para OAuth 2.1."""
    token = create_access_token(client_id="test-client", scope="mcp:all", expires_in=300)
    assert isinstance(token, str)
    
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "test-client"
    assert payload["scope"] == "mcp:all"

def test_log_sanitization():
    """Garante que dados sensíveis (tokens, CPFs, processos) são mascarados nos logs."""
    raw_log = "Auth token Bearer eyJhbGciOiJIUzI1Ni... para o CPF 123.456.789-00 no processo 0001234-56.2024.8.26.0100"
    sanitized = sanitize_log_message(raw_log)
    assert "Bearer [REDACTED]" in sanitized
    assert "[CPF REDACTED]" in sanitized
    assert "[PROC REDACTED]" in sanitized
    assert "123.456.789-00" not in sanitized
    assert "0001234-56.2024.8.26.0100" not in sanitized

def test_oauth_client_credentials_flow(client):
    """Testa a emissão de token via fluxo client_credentials."""
    response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": OAUTH_CLIENT_ID,
            "client_secret": OAUTH_CLIENT_SECRET,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] == 3600

def test_oauth_authorization_code_with_pkce(client):
    """Testa o fluxo completo de Authorization Code com PKCE (S256)."""
    # 1. Gera code_verifier e code_challenge S256
    code_verifier = "a-very-long-random-string-used-for-pkce-verifier-1234567890"
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

    # 2. Chama /oauth/authorize
    redirect_uri = "https://oauth.googleusercontent.com/gemini/callback"
    auth_resp = client.get(
        "/oauth/authorize",
        params={
            "client_id": OAUTH_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": "random_state_123",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        },
        follow_redirects=False,
    )
    assert auth_resp.status_code == 302
    location = auth_resp.headers["location"]
    parsed = urllib.parse.urlparse(location)
    query = dict(urllib.parse.parse_qsl(parsed.query))
    assert "code" in query
    assert query["state"] == "random_state_123"
    auth_code = query["code"]

    # 3. Troca o code pelo token em /oauth/token com o code_verifier correto
    token_resp = client.post(
        "/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": OAUTH_CLIENT_ID,
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }
    )
    assert token_resp.status_code == 200
    token_data = token_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "Bearer"
