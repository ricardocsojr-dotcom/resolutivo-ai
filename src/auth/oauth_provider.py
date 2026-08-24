"""Provedor OAuth 2.1 e endpoints de metadados para conexão remota (Gemini Connected App)."""

import hashlib
import base64
import urllib.parse
import uuid
import time
from typing import Dict
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response

from .security import (
    AUTH_MODE,
    OAUTH_CLIENT_ID,
    OAUTH_CLIENT_SECRET,
    SERVER_BASE_URL,
    create_access_token,
    logger,
)

# Armazenamento temporário em memória para authorization codes e PKCE
AUTH_CODES: Dict[str, dict] = {}

def _clean_expired_codes():
    now = time.time()
    expired = [k for k, v in AUTH_CODES.items() if v.get("expires_at", 0) < now]
    for k in expired:
        AUTH_CODES.pop(k, None)

async def oauth_metadata_endpoint(request: Request) -> JSONResponse:
    """Retorna metadados do Authorization Server conforme RFC 8414 / RFC 8414 OAuth 2.0 Authorization Server Metadata."""
    base = SERVER_BASE_URL.rstrip("/")
    return JSONResponse({
        "issuer": base,
        "authorization_endpoint": f"{base}/oauth/authorize",
        "token_endpoint": f"{base}/oauth/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "client_credentials"],
        "code_challenge_methods_supported": ["S256", "plain"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic", "none"],
        "scopes_supported": ["mcp:all", "read", "write"],
    })

async def oauth_authorize_endpoint(request: Request) -> Response:
    """Endpoint /oauth/authorize que atende o fluxo de consentimento/autorização do Gemini."""
    _clean_expired_codes()
    params = request.query_params
    client_id = params.get("client_id")
    redirect_uri = params.get("redirect_uri")
    response_type = params.get("response_type", "code")
    state = params.get("state", "")
    code_challenge = params.get("code_challenge")
    code_challenge_method = params.get("code_challenge_method", "plain")
    scope = params.get("scope", "mcp:all")

    if not redirect_uri:
        return JSONResponse({"error": "invalid_request", "error_description": "redirect_uri é obrigatório"}, status_code=400)

    if client_id != OAUTH_CLIENT_ID:
        logger.warning("Tentativa de autorização com client_id inválido")
        return JSONResponse({"error": "unauthorized_client", "error_description": "client_id não reconhecido"}, status_code=400)

    if response_type != "code":
        return JSONResponse({"error": "unsupported_response_type", "error_description": "Apenas response_type=code é suportado"}, status_code=400)

    # Gera authorization code
    code = f"auth_code_{uuid.uuid4().hex}"
    AUTH_CODES[code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "scope": scope,
        "expires_at": time.time() + 300,  # 5 minutos
    }

    # Redireciona de volta com o código
    parsed_redirect = urllib.parse.urlparse(redirect_uri)
    query = dict(urllib.parse.parse_qsl(parsed_redirect.query))
    query["code"] = code
    if state:
        query["state"] = state
    
    new_query = urllib.parse.urlencode(query)
    target_url = urllib.parse.urlunparse((
        parsed_redirect.scheme,
        parsed_redirect.netloc,
        parsed_redirect.path,
        parsed_redirect.params,
        new_query,
        parsed_redirect.fragment
    ))

    logger.info("Autorização concedida com sucesso via OAuth 2.1")
    return RedirectResponse(url=target_url, status_code=302)

async def oauth_token_endpoint(request: Request) -> JSONResponse:
    """Endpoint /oauth/token para troca de authorization_code ou client_credentials por access_token."""
    _clean_expired_codes()
    content_type = request.headers.get("content-type", "")
    
    if "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        grant_type = form.get("grant_type")
        client_id = form.get("client_id")
        client_secret = form.get("client_secret")
        code = form.get("code")
        redirect_uri = form.get("redirect_uri")
        code_verifier = form.get("code_verifier")
    elif "application/json" in content_type:
        try:
            body = await request.json()
        except Exception:
            body = {}
        grant_type = body.get("grant_type")
        client_id = body.get("client_id")
        client_secret = body.get("client_secret")
        code = body.get("code")
        redirect_uri = body.get("redirect_uri")
        code_verifier = body.get("code_verifier")
    else:
        # Tentar form por padrão
        form = await request.form()
        grant_type = form.get("grant_type")
        client_id = form.get("client_id")
        client_secret = form.get("client_secret")
        code = form.get("code")
        redirect_uri = form.get("redirect_uri")
        code_verifier = form.get("code_verifier")

    # Autenticação via Basic Auth no header se presente
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Basic "):
        try:
            decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
            if ":" in decoded:
                h_id, h_sec = decoded.split(":", 1)
                client_id = h_id
                client_secret = h_sec
        except Exception:
            pass

    # Validação do fluxo client_credentials
    if grant_type == "client_credentials":
        if client_id != OAUTH_CLIENT_ID or client_secret != OAUTH_CLIENT_SECRET:
            return JSONResponse({"error": "invalid_client", "error_description": "Credenciais de cliente inválidas"}, status_code=401)
        
        token = create_access_token(client_id=client_id or "client", scope="mcp:all", expires_in=3600)
        return JSONResponse({
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "mcp:all"
        })

    # Validação do fluxo authorization_code
    if grant_type == "authorization_code":
        if not code or code not in AUTH_CODES:
            return JSONResponse({"error": "invalid_grant", "error_description": "Código de autorização inválido ou expirado"}, status_code=400)
        
        stored = AUTH_CODES.pop(code)
        
        # Validar PKCE se foi fornecido no authorize
        if stored.get("code_challenge"):
            if not code_verifier:
                return JSONResponse({"error": "invalid_grant", "error_description": "code_verifier é obrigatório para PKCE"}, status_code=400)
            
            method = stored.get("code_challenge_method", "plain")
            if method == "S256":
                digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
                computed_challenge = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
                if computed_challenge != stored["code_challenge"].rstrip("="):
                    return JSONResponse({"error": "invalid_grant", "error_description": "code_verifier inválido para S256"}, status_code=400)
            elif method == "plain":
                if code_verifier != stored["code_challenge"]:
                    return JSONResponse({"error": "invalid_grant", "error_description": "code_verifier inválido"}, status_code=400)

        token = create_access_token(client_id=stored["client_id"], scope=stored.get("scope", "mcp:all"), expires_in=3600)
        return JSONResponse({
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": stored.get("scope", "mcp:all")
        })

    return JSONResponse({"error": "unsupported_grant_type", "error_description": f"grant_type '{grant_type}' não suportado"}, status_code=400)
