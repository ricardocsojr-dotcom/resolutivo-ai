"""Servidor MCP Principal do Resolutivo.AI.

Implementa o protocolo MCP oficial via FastMCP com transporte Streamable HTTP,
endpoints /mcp, /health, autenticação OAuth 2.1 / Bearer e suporte a execução local e remota.
"""

import os
import sys
import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

# Garante que a raiz do projeto esteja no sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.auth.security import (
    AUTH_MODE,
    SERVER_BASE_URL,
    logger,
)
from src.auth.middleware import MCPAuthMiddleware
from src.auth.oauth_provider import (
    oauth_metadata_endpoint,
    oauth_authorize_endpoint,
    oauth_token_endpoint,
)
from src.tools.cnj_tools import register_cnj_tools
from src.tools.calculo_tools import register_calculo_tools
from src.tools.provisao_tools import register_provisao_tools
from src.tools.revisor_tools import register_revisor_tools
from src.tools.base_tools import register_base_tools
from src.prompts.prompts_registry import register_prompts
from src.resources.resources_registry import register_resources

SERVER_INSTRUCTIONS = """Servidor MCP do Resolutivo.AI — Escritório Romano Donadel Advogados Associados (RDAA).
Disponibiliza ferramentas determinísticas de cálculos judiciais, consulta processual pública (DataJud/DJEN),
validação de regras de estilo, liquidação de pedidos e recursos normativos do contencioso cível e consumerista."""

def create_mcp_server() -> FastMCP:
    """Instancia e configura o servidor FastMCP com todas as ferramentas, prompts e recursos."""
    mcp = FastMCP(
        name="Resolutivo.AI",
        instructions=SERVER_INSTRUCTIONS,
    )

    # 1. Registro de Ferramentas
    register_cnj_tools(mcp)
    register_calculo_tools(mcp)
    register_provisao_tools(mcp)
    register_revisor_tools(mcp)
    register_base_tools(mcp)

    # 2. Registro de Prompts
    register_prompts(mcp)

    # 3. Registro de Recursos
    register_resources(mcp)

    # 4. Registro de Rotas Personalizadas (Health Check e OAuth 2.1)
    @mcp.custom_route("/health", methods=["GET", "HEAD"])
    async def health_endpoint(request: Request) -> JSONResponse:
        return JSONResponse({
            "status": "healthy",
            "service": "resolutivo-ai-mcp",
            "version": "3.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "auth_mode": AUTH_MODE,
            "mcp_endpoint": "/mcp",
            "capabilities": {
                "tools": True,
                "prompts": True,
                "resources": True,
                "streamable_http": True,
            },
        })

    @mcp.custom_route("/.well-known/oauth-authorization-server", methods=["GET"])
    async def well_known_oauth(request: Request) -> JSONResponse:
        return await oauth_metadata_endpoint(request)

    @mcp.custom_route("/oauth/authorize", methods=["GET", "POST"])
    async def oauth_authorize(request: Request):
        return await oauth_authorize_endpoint(request)

    @mcp.custom_route("/oauth/token", methods=["POST"])
    async def oauth_token(request: Request):
        return await oauth_token_endpoint(request)

    return mcp

# Instância padrão do FastMCP
mcp_server = create_mcp_server()

def get_starlette_app() -> Starlette:
    """Gera a aplicação Starlette configurada com transporte Streamable HTTP e middleware de autenticação."""
    app = mcp_server.streamable_http_app()
    # Adiciona o middleware de autenticação
    app.add_middleware(MCPAuthMiddleware)
    return app

app = get_starlette_app()

def main():
    parser = argparse.ArgumentParser(description="Servidor MCP Resolutivo.AI")
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"), help="Host para vinculação (padrão: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")), help="Porta HTTP (padrão: 8000)")
    parser.add_argument("--transport", default="streamable-http", choices=["streamable-http", "sse", "stdio"], help="Tipo de transporte MCP")
    args = parser.parse_args()

    logger.info(f"Iniciando Servidor MCP Resolutivo.AI (transporte: {args.transport}, auth_mode: {AUTH_MODE})")

    if args.transport == "stdio":
        mcp_server.run(transport="stdio")
    elif args.transport == "sse":
        import uvicorn
        sse_app = mcp_server.sse_app()
        sse_app.add_middleware(MCPAuthMiddleware)
        uvicorn.run(sse_app, host=args.host, port=args.port)
    else:
        import uvicorn
        uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
