"""Testes unitários e de integração do Servidor MCP Resolutivo.AI."""

import pytest
import asyncio
from starlette.testclient import TestClient
from src.server import app, mcp_server

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    """Verifica se o endpoint /health responde status 200 e payload esperado."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "resolutivo-ai-mcp"
    assert data["version"] == "3.0.0"
    assert data["mcp_endpoint"] == "/mcp"
    assert data["capabilities"]["tools"] is True
    assert data["capabilities"]["prompts"] is True
    assert data["capabilities"]["resources"] is True

def test_oauth_well_known_metadata(client):
    """Verifica se os metadados do Authorization Server OAuth 2.1 seguem a RFC 8414."""
    response = client.get("/.well-known/oauth-authorization-server")
    assert response.status_code == 200
    data = response.json()
    assert "authorization_endpoint" in data
    assert "token_endpoint" in data
    assert "code_challenge_methods_supported" in data
    assert "S256" in data["code_challenge_methods_supported"]
    assert "authorization_code" in data["grant_types_supported"]

def test_mcp_tools_and_prompts_discovery():
    """Verifica se todas as ferramentas, prompts e recursos estão registrados no FastMCP."""
    async def _run():
        tools = await mcp_server.list_tools()
        tool_names = {t.name for t in tools}
        
        assert "consultar_processo" in tool_names
        assert "calcular_atualizacao_judicial" in tool_names
        assert "liquidar_pedidos_provisao" in tool_names
        assert "classificar_tipo_peca" in tool_names
        assert "validar_esqueleto_peca" in tool_names
        assert "verificar_estilo_rdaa" in tool_names
        assert "converter_tabela_perfil" in tool_names
        assert "listar_tribunais" in tool_names

        prompts = await mcp_server.list_prompts()
        prompt_names = {p.name for p in prompts}
        assert "redigir_peca" in prompt_names
        assert "revisar_peca" in prompt_names
        assert "analisar_risco_processual" in prompt_names
        assert "conselho_deliberativo" in prompt_names

        resources = await mcp_server.list_resources()
        resource_uris = {str(r.uri) for r in resources}
        assert "rdaa://perfil/escritorio" in resource_uris
        assert "rdaa://regras/redacao" in resource_uris

    asyncio.run(_run())
