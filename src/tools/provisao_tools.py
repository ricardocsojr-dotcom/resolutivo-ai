"""Ferramentas MCP para liquidação de pedidos e provisionamento determinístico de risco."""

import json
from decimal import Decimal
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

try:
    from skills.previsao_condenacao_rdaa.scripts.liquidar_pedidos import processar, normalizar_risco
except ImportError:
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "skills" / "previsao-condenacao-rdaa" / "scripts"))
    from liquidar_pedidos import processar, normalizar_risco

def register_provisao_tools(mcp: FastMCP) -> None:
    """Registra ferramentas de liquidação e provisão no servidor FastMCP."""

    @mcp.tool()
    def liquidar_pedidos_provisao(pedidos_json: str) -> str:
        """
        Executa a liquidação aritmética de pedidos e cálculo de provisão ponderada por probabilidade de risco.
        Tira a soma de parcelas e multiplicação de probabilidade do texto livre e executa via Decimal determinístico.

        Args:
            pedidos_json: String JSON contendo lista de objetos de pedidos. Exemplo:
                [
                  {
                    "pedido": "Repetição de indébito - cobranças jan/2022 a mar/2023",
                    "tipo": "material",
                    "valor_unitario": 89.90,
                    "periodicidade": "mensal",
                    "data_inicio": "2022-01-01",
                    "data_fim": "2023-03-01",
                    "risco": "provavel"
                  },
                  {
                    "pedido": "Dano moral - negativação indevida",
                    "tipo": "moral",
                    "valor_unitario": 8000.00,
                    "periodicidade": "unico",
                    "risco": "possivel"
                  }
                ]

        Returns:
            JSON com as linhas liquidadas (valor base, percentual de risco, provisão ponderada) e totais consolidados.
        """
        try:
            pedidos = json.loads(pedidos_json)
            if not isinstance(pedidos, list):
                return json.dumps({
                    "status": "error",
                    "message": "pedidos_json deve ser uma lista JSON de objetos de pedido.",
                }, ensure_ascii=False)

            linhas, total_liquidado, total_provisao = processar(pedidos)

            linhas_formatadas = [
                {
                    "pedido": l["pedido"],
                    "tipo": l["tipo"],
                    "valor_liquidado": float(l["valor_liquidado"]),
                    "risco_percentual": float(l["risco_pct"] * 100),
                    "provisao_ponderada": float(l["provisao_ponderada"]),
                }
                for l in linhas
            ]

            return json.dumps({
                "status": "success",
                "total_pedidos": len(linhas_formatadas),
                "total_liquidado": float(total_liquidado),
                "total_provisao_ponderada": float(total_provisao),
                "linhas": linhas_formatadas,
            }, ensure_ascii=False, indent=2)

        except json.JSONDecodeError as e:
            return json.dumps({"status": "error", "message": f"JSON inválido: {str(e)}"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Falha na liquidação: {str(e)}"}, ensure_ascii=False)
