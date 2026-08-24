"""Ferramentas MCP para atualização monetária e cálculo judicial determinístico."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from ..auth.security import logger

# Caminhos base para índices e manifestos do motor de cálculo
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDICES_DIR = PROJECT_ROOT / "skills" / "calculo-judicial" / "references" / "indices"
MANIFEST_PATH = PROJECT_ROOT / "skills" / "calculo-judicial" / "references" / "index_manifest.json"

try:
    from skills.calculo_judicial.scripts.calculo_motor import calculate, MotorError
except ImportError:
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "skills" / "calculo-judicial" / "scripts"))
    from calculo_motor import calculate, MotorError

def register_calculo_tools(mcp: FastMCP) -> None:
    """Registra ferramentas de cálculo judicial determinístico no servidor FastMCP."""

    @mcp.tool()
    def calcular_atualizacao_judicial(
        principal: float,
        data_inicio_correcao: str,
        data_final: str,
        indice: str = "tjsp",
        convencao_indice: str = "meses_calendario_inclusivos",
        data_inicio_juros: Optional[str] = None,
        taxa_juros_mensal: Optional[float] = 1.0,
        base_juros: str = "principal_corrigido",
        modo: str = "resumo",
        tratamento_periodo_parcial: Optional[str] = "mes_completo_declarado",
    ) -> str:
        """
        Executa cálculo aritmético e determinístico de atualização monetária e juros moratórios judiciais.

        Args:
            principal: Valor numérico original a ser atualizado (ex: 15000.00).
            data_inicio_correcao: Data inicial da correção monetária no formato ISO (ex: '2023-01-01').
            data_final: Data final de fechamento do cálculo (ex: '2024-01-31').
            indice: Código do índice cadastrado no manifesto: 'tjsp', 'inpc', 'ipca-e', 'igpm', 'cdi_diaria', etc.
            convencao_indice: 'meses_calendario_inclusivos' (mensal) ou 'registros_com_data_no_intervalo_inclusivo' (diário).
            data_inicio_juros: Data inicial de incidência de juros de mora (YYYY-MM-DD), se houver.
            taxa_juros_mensal: Percentual mensal de juros simples (ex: 1.0 para 1% a.m.).
            base_juros: Base de cálculo dos juros: 'principal_corrigido' ou 'principal'.
            modo: Nível de detalhamento: 'resumo' ou 'detalhado' (com linha a linha).
            tratamento_periodo_parcial: 'mes_completo_declarado' para meses parciais declarados como competência inteira.

        Returns:
            JSON com valor principal corrigido, total de juros, fator de correção e valor total final liquidado.
        """
        payload: Dict[str, Any] = {
            "principal": principal,
            "data_inicio_correcao": data_inicio_correcao,
            "data_final": data_final,
            "indice": indice,
            "convencao_indice": convencao_indice,
            "modo": modo,
            "tratamento_periodo_parcial": tratamento_periodo_parcial,
        }

        if data_inicio_juros and taxa_juros_mensal is not None:
            payload["data_inicio_juros"] = data_inicio_juros
            payload["juros"] = {
                "tipo": "simples_mensal",
                "taxa": taxa_juros_mensal,
                "base": base_juros,
                "convencao": "meses_calendario_inclusivos",
            }

        try:
            result = calculate(
                payload,
                indices_dir=INDICES_DIR,
                manifest_path=MANIFEST_PATH,
            )
            return json.dumps({
                "status": "success",
                "resultado": result,
            }, ensure_ascii=False, indent=2)
        except MotorError as e:
            return json.dumps({
                "status": "error",
                "code": e.code,
                "message": e.message,
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Erro inesperado no motor de cálculo: {str(e)}",
            }, ensure_ascii=False, indent=2)

    @mcp.tool()
    def listar_indices_disponiveis() -> str:
        """
        Lista todos os índices de correção monetária oficiais disponíveis no motor de cálculo.

        Returns:
            JSON com relação de índices cadastrados, tipos de série, unidades e status de aprovação.
        """
        if not MANIFEST_PATH.is_file():
            return json.dumps({"status": "error", "message": "Manifesto de índices não encontrado."}, ensure_ascii=False)
        try:
            data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            indices = {
                k: {
                    "tipo_serie": v.get("tipo_serie"),
                    "unidade": v.get("unidade"),
                    "status": v.get("status"),
                    "convencoes": v.get("convencoes"),
                }
                for k, v in data.items()
                if isinstance(v, dict)
            }
            return json.dumps({"status": "success", "indices": indices}, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
