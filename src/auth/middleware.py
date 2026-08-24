"""Middleware de autenticação e controle de acesso para o servidor MCP."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .security import (
    AUTH_MODE,
    verify_token,
    logger,
)

PUBLIC_PATHS = {
    "/health",
    "/.well-known/oauth-authorization-server",
    "/oauth/authorize",
    "/oauth/token",
    "/favicon.ico",
}

class MCPAuthMiddleware(BaseHTTPMiddleware):
    """Middleware Starlette para autenticação em endpoints MCP."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Permite requisições OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            response = Response(status_code=204)
            self._add_cors_headers(response)
            return response

        # Ignora rotas públicas
        if path in PUBLIC_PATHS or path.startswith("/.well-known/"):
            response = await call_next(request)
            self._add_cors_headers(response)
            return response

        # Se AUTH_MODE for "none", permite livremente (desenvolvimento / teste local)
        if AUTH_MODE == "none":
            response = await call_next(request)
            self._add_cors_headers(response)
            return response

        # Para AUTH_MODE "bearer" ou "oauth", exige token Bearer válido
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            logger.warning(f"Acesso negado em {path}: Cabeçalho Authorization ausente ou inválido")
            response = JSONResponse(
                {"error": "unauthorized", "message": "Autenticação obrigatória. Forneça 'Authorization: Bearer <token>'."},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"}
            )
            self._add_cors_headers(response)
            return response

        token = auth_header[7:].strip()
        payload = verify_token(token)
        if not payload:
            logger.warning(f"Acesso negado em {path}: Token inválido ou expirado")
            response = JSONResponse(
                {"error": "unauthorized", "message": "Token inválido, expirado ou revogado."},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
            )
            self._add_cors_headers(response)
            return response

        # Armazena dados de autenticação no estado da requisição
        request.state.auth_user = payload
        response = await call_next(request)
        self._add_cors_headers(response)
        return response

    def _add_cors_headers(self, response: Response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, HEAD"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, MCP-Session-Id, Last-Event-ID"
        response.headers["Access-Control-Expose-Headers"] = "Content-Type, MCP-Session-Id"
