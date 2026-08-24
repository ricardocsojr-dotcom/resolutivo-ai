"""Ferramentas MCP para revisão, classificação e verificação de estilo de peças forenses."""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REVISOR_SCRIPTS = PROJECT_ROOT / "skills" / "revisor-rdaa" / "scripts"

if str(REVISOR_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(REVISOR_SCRIPTS))

from classificacao_peca import validate_piece_contract, NIVEL_CONFIG
from validar_esqueleto import validate_skeleton
from verificar_estilo import (
    checar_travessao,
    checar_ponto_e_virgula,
    checar_aberturas_defensivas,
    checar_dois_pontos,
    checar_aposto_explicativo,
    checar_tricolon_negacao,
)

def register_revisor_tools(mcp: FastMCP) -> None:
    """Registra ferramentas de revisão e governança de peças jurídicas no FastMCP."""

    @mcp.tool()
    def classificar_tipo_peca(
        nivel_peca: str,
        modo_redacao: str = "direta",
        exigir_esqueleto: bool = True,
    ) -> str:
        """
        Classifica e valida o contrato operacional e nível de complexidade de uma peça jurídica RDAA.

        Args:
            nivel_peca: Nível de produção:
                - 'A' (Premium): Todos os recursos, redação por blocos autorizada, esqueleto recomendado.
                - 'B' (Desenvolvida): Baseada no processo com desenvolvimento/visual, redação por blocos permitida.
                - 'C' (Simples): Peça muito simples em parágrafos curtos, redação direta sem blocos.
            modo_redacao: Modo pretendido: 'direta', 'blocos' ou 'molde_controlado'.
            exigir_esqueleto: Exigência de esqueleto estrutural (obrigatório true para A/B, false para C).

        Returns:
            JSON com status de validação ('PASS' ou 'BLOCK'), permissões operacionais e orientações de produção.
        """
        nivel = nivel_peca.strip().upper()
        ctx = {
            "nivel_peca": nivel,
            "modo_redacao": modo_redacao.strip().lower(),
            "exigir_esqueleto": (exigir_esqueleto if nivel != "C" else False),
        }
        res = validate_piece_contract(ctx)
        config = NIVEL_CONFIG.get(nivel, {})
        return json.dumps({
            "status": res.get("status"),
            "nivel": nivel,
            "configuracao": config,
            "findings": res.get("findings", []),
        }, ensure_ascii=False, indent=2)

    @mcp.tool()
    def validar_esqueleto_peca(esqueleto_json: str) -> str:
        """
        Valida objetivamente o checklist estrutural do esqueleto de uma peça jurídica contra os requisitos do CPC e aprovação de fontes.

        Args:
            esqueleto_json: JSON contendo a estrutura do esqueleto da peça, com seções, fontes_status ('selecionadas'/'sem_fontes') e aprovacao. Exemplo:
                {
                  "esqueleto": {
                    "tipo_peca": "contestacao",
                    "status": "aprovado",
                    "aprovacao": {"status": "aprovado"},
                    "fontes_status": "selecionadas",
                    "fontes_selecionadas": ["FONTE-1", "DOC-CONTRATO"],
                    "secoes": ["tempestividade", "sintese_fatos", "merito_inexistencia_dano", "pedidos"]
                  }
                }

        Returns:
            JSON com status ('PASS' ou 'BLOCK') e lista de inconformidades estruturais encontradas.
        """
        try:
            context = json.loads(esqueleto_json)
            if not isinstance(context, dict):
                return json.dumps({"status": "BLOCK", "findings": [{"message": "O esqueleto deve ser um objeto JSON."}]}, ensure_ascii=False)
            
            # Se vier sem a chave raiz 'esqueleto', empacota
            if "esqueleto" not in context and "skeleton" not in context:
                context = {"esqueleto": context}

            result = validate_skeleton(context)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except json.JSONDecodeError as e:
            return json.dumps({"status": "BLOCK", "findings": [{"message": f"JSON inválido: {str(e)}"}]}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "BLOCK", "findings": [{"message": f"Erro na validação: {str(e)}"}]}, ensure_ascii=False)

    @mcp.tool()
    def verificar_estilo_rdaa(texto_peca: str) -> str:
        """
        Realiza auditoria estilométrica objetiva no texto de uma peça jurídica conforme o Checklist 3 do RDAA.
        Verifica vícios objetivos de redação: travessões (proibidos), ponto-e-vírgula em prosa corrida, aberturas defensivas repetitivas, etc.

        Args:
            texto_peca: Texto completo ou parágrafos da petição a serem inspecionados.

        Returns:
            JSON com status ('APROVADO' ou 'REPROVADO') e apontamento detalhado de cada violação encontrada com número do parágrafo.
        """
        linhas = [l.strip() for l in texto_peca.splitlines() if l.strip()]
        if not linhas:
            return json.dumps({"status": "APROVADO", "total_paragrafos": 0, "violacoes": []}, ensure_ascii=False)

        violacoes = []
        
        # 1. Checagem de travessão
        problemas_travessao, _ = checar_travessao(linhas)
        violacoes.extend(problemas_travessao)

        # 2. Checagem de ponto-e-vírgula fora de lista
        problemas_ponto_virgula = checar_ponto_e_virgula(linhas)
        violacoes.extend(problemas_ponto_virgula)

        # 3. Checagem de aberturas defensivas
        problemas_aberturas = checar_aberturas_defensivas(linhas)
        violacoes.extend(problemas_aberturas)

        # 4. Checagem de dois-pontos
        try:
            problemas_dois_pontos = checar_dois_pontos(linhas)
            violacoes.extend(problemas_dois_pontos)
        except Exception:
            pass

        # 5. Checagem de aposto explicativo em parênteses
        try:
            problemas_parenteses = checar_aposto_explicativo(linhas)
            violacoes.extend(problemas_parenteses)
        except Exception:
            pass

        # 6. Checagem de tricolon de negação
        try:
            problemas_tricolon = checar_tricolon_negacao(linhas)
            violacoes.extend(problemas_tricolon)
        except Exception:
            pass

        status = "REPROVADO" if violacoes else "APROVADO"
        return json.dumps({
            "status": status,
            "total_paragrafos_analisados": len(linhas),
            "total_violacoes": len(violacoes),
            "violacoes": violacoes,
        }, ensure_ascii=False, indent=2)
