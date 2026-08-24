"""Ferramentas MCP para utilidades de base e conversão de dados."""

import json
import csv
import io
from pathlib import Path
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parents[2]

try:
    from skills.perfil_csv.scripts.convert_perfil import convert_row
except ImportError:
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "skills" / "perfil-csv" / "scripts"))
    from convert_perfil import convert_row

def register_base_tools(mcp: FastMCP) -> None:
    """Registra ferramentas de base de dados e utilitários no FastMCP."""

    @mcp.tool()
    def converter_tabela_perfil(linhas_json: str) -> str:
        """
        Converte linhas extraídas de tabela de parcelas/custas/honorários para o formato CSV 'perfil'.

        Args:
            linhas_json: JSON com lista de objetos representando parcelas. Exemplo:
                [
                  {
                    "data": "14/06/2014",
                    "valor": "1.804,00",
                    "tipo": "Principal",
                    "historico": "Parcela 01",
                    "correcao": "S",
                    "juros": "S",
                    "dtJuros": "14/06/2014"
                  }
                ]

        Returns:
            JSON com as linhas convertidas em formato CSV 'perfil' (data,valor,tipo,histórico,mostraTipo,t,correção,juros,dtJuros).
        """
        try:
            rows = json.loads(linhas_json)
            if not isinstance(rows, list):
                return json.dumps({"status": "error", "message": "linhas_json deve ser uma lista de objetos."}, ensure_ascii=False)

            out_lines = []
            errors = []
            for i, row in enumerate(rows, start=1):
                try:
                    out_lines.append(convert_row(row, i))
                except ValueError as e:
                    errors.append(str(e))

            if errors:
                return json.dumps({"status": "error", "message": "Inconsistências nos dados", "errors": errors}, ensure_ascii=False)

            buf = io.StringIO()
            writer = csv.writer(buf, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
            for line in out_lines:
                writer.writerow(line)

            return json.dumps({
                "status": "success",
                "total_linhas": len(out_lines),
                "csv_output": buf.getvalue(),
            }, ensure_ascii=False, indent=2)

        except json.JSONDecodeError as e:
            return json.dumps({"status": "error", "message": f"JSON inválido: {str(e)}"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
