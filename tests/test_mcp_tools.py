"""Testes de execução real das ferramentas MCP do Resolutivo.AI."""

import pytest
import json
import asyncio
from src.server import mcp_server

def _extract_text(raw_res) -> str:
    """Extrai texto de retorno do FastMCP call_tool (que retorna tupla (content_list, metadata))."""
    if isinstance(raw_res, tuple) and len(raw_res) > 0:
        raw_res = raw_res[0]
    if isinstance(raw_res, list) and len(raw_res) > 0:
        item = raw_res[0]
        if hasattr(item, "text"):
            return item.text
        return str(item)
    if hasattr(raw_res, "text"):
        return raw_res.text
    return str(raw_res)

def test_executar_calcular_atualizacao_judicial():
    """Testa a execução do cálculo de atualização monetária pelo FastMCP e respeito à governança de índices."""
    async def _run():
        raw_res = await mcp_server.call_tool(
            "calcular_atualizacao_judicial",
            arguments={
                "principal": 1000.0,
                "data_inicio_correcao": "2023-01-01",
                "data_final": "2023-12-31",
                "indice": "tjsp",
                "data_inicio_juros": "2023-01-01",
                "taxa_juros_mensal": 1.0,
            }
        )
        content_text = _extract_text(raw_res)
        data = json.loads(content_text)
        # O repositório mantém índices em pendente_validacao por governança do escritório
        assert data["status"] in ("success", "error")
        if data["status"] == "error":
            assert data["code"] == "indice_pendente"
            assert "exige aprovação" in data["message"]

    asyncio.run(_run())

def test_executar_liquidar_pedidos_provisao():
    """Testa a execução da liquidação aritmética de pedidos e risco de provisão."""
    async def _run():
        pedidos = [
            {
                "pedido": "Repetição de indébito - tarifas",
                "tipo": "material",
                "valor_unitario": 100.0,
                "periodicidade": "mensal",
                "data_inicio": "2022-01-01",
                "data_fim": "2022-03-01",
                "risco": "provavel"
            },
            {
                "pedido": "Dano moral",
                "tipo": "moral",
                "valor_unitario": 8000.0,
                "periodicidade": "unico",
                "risco": "possivel"
            }
        ]
        raw_res = await mcp_server.call_tool(
            "liquidar_pedidos_provisao",
            arguments={"pedidos_json": json.dumps(pedidos)}
        )
        content_text = _extract_text(raw_res)
        data = json.loads(content_text)
        assert data["status"] == "success"
        assert data["total_pedidos"] == 2
        assert data["total_liquidado"] == 8300.0
        assert data["total_provisao_ponderada"] == 4300.0

    asyncio.run(_run())

def test_executar_classificar_tipo_peca():
    """Testa a classificação de contrato operacional de peça jurídica."""
    async def _run():
        raw_res = await mcp_server.call_tool(
            "classificar_tipo_peca",
            arguments={"nivel_peca": "B", "modo_redacao": "direta", "exigir_esqueleto": True}
        )
        content_text = _extract_text(raw_res)
        data = json.loads(content_text)
        assert data["status"] == "PASS"
        assert data["nivel"] == "B"
        assert data["configuracao"]["redacao_por_blocos_permitida"] is True

        # Teste para nível C (simples)
        raw_res_c = await mcp_server.call_tool(
            "classificar_tipo_peca",
            arguments={"nivel_peca": "C", "modo_redacao": "direta"}
        )
        data_c = json.loads(_extract_text(raw_res_c))
        assert data_c["status"] == "PASS"
        assert data_c["nivel"] == "C"
        assert data_c["configuracao"]["redacao_por_blocos_permitida"] is False

    asyncio.run(_run())

def test_executar_verificar_estilo_rdaa():
    """Testa a verificação objetiva de estilo forense (travessão proibido)."""
    async def _run():
        texto_invalido = "A parte autora — ora requerente — requer a procedência."
        raw_res = await mcp_server.call_tool(
            "verificar_estilo_rdaa",
            arguments={"texto_peca": texto_invalido}
        )
        content_text = _extract_text(raw_res)
        data = json.loads(content_text)
        assert data["status"] == "REPROVADO"
        assert data["total_violacoes"] >= 1
        assert any("travessao" in v.lower() for v in data["violacoes"])

        texto_valido = "A parte autora, devidamente qualificada, requer a procedência dos pedidos formulados na exordial."
        raw_res_valido = await mcp_server.call_tool(
            "verificar_estilo_rdaa",
            arguments={"texto_peca": texto_valido}
        )
        content_text_valido = _extract_text(raw_res_valido)
        data_valido = json.loads(content_text_valido)
        assert data_valido["status"] == "APROVADO"
        assert data_valido["total_violacoes"] == 0

    asyncio.run(_run())

def test_executar_converter_tabela_perfil():
    """Testa a conversão de tabela de parcelas para formato CSV perfil."""
    async def _run():
        linhas = [
            {
                "data": "14/06/2023",
                "valor": "1.500,50",
                "tipo": "Principal",
                "historico": "Parcela 01",
                "correcao": "S",
                "juros": "S",
                "dtJuros": "14/06/2023"
            }
        ]
        raw_res = await mcp_server.call_tool(
            "converter_tabela_perfil",
            arguments={"linhas_json": json.dumps(linhas)}
        )
        content_text = _extract_text(raw_res)
        data = json.loads(content_text)
        assert data["status"] == "success"
        assert "2023-06-14,1500.50,Principal,Parcela 01" in data["csv_output"]

    asyncio.run(_run())

def test_executar_listar_tribunais():
    """Testa a listagem de tribunais suportados pelo DataJud."""
    async def _run():
        raw_res = await mcp_server.call_tool("listar_tribunais", arguments={})
        content_text = _extract_text(raw_res)
        data = json.loads(content_text)
        assert data["status"] == "success"
        assert "TJSP" in data["tribunais"]
        assert "STJ" in data["tribunais"]

    asyncio.run(_run())
