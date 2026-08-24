"""Ferramentas MCP para integração com DataJud e DJEN (CNJ)."""

import json
import httpx
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP
from ..auth.security import DATAJUD_APIKEY, logger

DATAJUD_BASE = "https://api-publica.datajud.cnj.jus.br"
DJEN_BASE = "https://comunica.pje.jus.br/api"

HEADERS_DATAJUD = {
    "Authorization": f"APIKey {DATAJUD_APIKEY}",
    "Content-Type": "application/json",
}

INDICES_TRIBUNAL: Dict[str, str] = {
    "STF": "api_publica_stf",
    "STJ": "api_publica_stj",
    "TST": "api_publica_tst",
    "TSE": "api_publica_tse",
    "STM": "api_publica_stm",
    "TRF1": "api_publica_trf1",
    "TRF2": "api_publica_trf2",
    "TRF3": "api_publica_trf3",
    "TRF4": "api_publica_trf4",
    "TRF5": "api_publica_trf5",
    "TRF6": "api_publica_trf6",
    "TJAC": "api_publica_tjac",
    "TJAL": "api_publica_tjal",
    "TJAM": "api_publica_tjam",
    "TJAP": "api_publica_tjap",
    "TJBA": "api_publica_tjba",
    "TJCE": "api_publica_tjce",
    "TJDF": "api_publica_tjdf",
    "TJES": "api_publica_tjes",
    "TJGO": "api_publica_tjgo",
    "TJMA": "api_publica_tjma",
    "TJMG": "api_publica_tjmg",
    "TJMS": "api_publica_tjms",
    "TJMT": "api_publica_tjmt",
    "TJPA": "api_publica_tjpa",
    "TJPB": "api_publica_tjpb",
    "TJPE": "api_publica_tjpe",
    "TJPI": "api_publica_tjpi",
    "TJPR": "api_publica_tjpr",
    "TJRJ": "api_publica_tjrj",
    "TJRN": "api_publica_tjrn",
    "TJRO": "api_publica_tjro",
    "TJRR": "api_publica_tjrr",
    "TJRS": "api_publica_tjrs",
    "TJSC": "api_publica_tjsc",
    "TJSE": "api_publica_tjse",
    "TJSP": "api_publica_tjsp",
    "TJTO": "api_publica_tjto",
    "TRT1": "api_publica_trt1",
    "TRT2": "api_publica_trt2",
    "TRT3": "api_publica_trt3",
    "TRT4": "api_publica_trt4",
    "TRT5": "api_publica_trt5",
    "TRT6": "api_publica_trt6",
    "TRT7": "api_publica_trt7",
    "TRT8": "api_publica_trt8",
    "TRT9": "api_publica_trt9",
    "TRT10": "api_publica_trt10",
    "TRT11": "api_publica_trt11",
    "TRT12": "api_publica_trt12",
    "TRT13": "api_publica_trt13",
    "TRT14": "api_publica_trt14",
    "TRT15": "api_publica_trt15",
    "TRT16": "api_publica_trt16",
    "TRT17": "api_publica_trt17",
    "TRT18": "api_publica_trt18",
    "TRT19": "api_publica_trt19",
    "TRT20": "api_publica_trt20",
    "TRT21": "api_publica_trt21",
    "TRT22": "api_publica_trt22",
    "TRT23": "api_publica_trt23",
    "TRT24": "api_publica_trt24",
}

def _datajud_post(indice: str, body: dict) -> dict:
    url = f"{DATAJUD_BASE}/{indice}/_search"
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, headers=HEADERS_DATAJUD, json=body)
        resp.raise_for_status()
        return resp.json()

def _formatar_processo(hit: dict) -> dict:
    """Extrai campos relevantes e limpos de um hit do DataJud."""
    src = hit.get("_source", {})
    return {
        "numero_processo": src.get("numeroProcesso"),
        "tribunal": src.get("tribunal"),
        "classe": src.get("classe", {}).get("nome"),
        "assuntos": [a.get("nome") for a in src.get("assuntos", []) if a.get("nome")],
        "orgao_julgador": src.get("orgaoJulgador", {}).get("nome"),
        "data_ajuizamento": src.get("dataAjuizamento"),
        "ultima_atualizacao": src.get("dataHoraUltimaAtualizacao"),
        "grau": src.get("grau"),
        "partes": [
            {
                "tipo": p.get("polo"),
                "nome": p.get("nome"),
                "documento": p.get("documento"),
            }
            for p in src.get("partes", [])
        ],
        "movimentos_recentes": [
            {
                "data": m.get("dataHora"),
                "descricao": m.get("nome"),
                "complemento": m.get("complementosTabelados", [{}])[0].get("descricao") if m.get("complementosTabelados") else None,
            }
            for m in sorted(
                src.get("movimentos", []),
                key=lambda x: x.get("dataHora", ""),
                reverse=True,
            )[:10]
        ],
    }

def register_cnj_tools(mcp: FastMCP) -> None:
    """Registra as ferramentas do CNJ no servidor FastMCP."""

    @mcp.tool()
    def consultar_processo(numero_processo: str, tribunal: str) -> str:
        """
        Consulta um processo judicial pelo número CNJ no DataJud (Base Nacional de Processos).

        Args:
            numero_processo: Número do processo com ou sem pontuação (ex: '0000000-00.0000.8.26.0000' ou '00000000000008260000').
            tribunal: Sigla do tribunal (ex: 'TJSP', 'TJMG', 'STJ', 'TRF3'). Use listar_tribunais() para ver siglas válidas.

        Returns:
            JSON com dados do processo: partes, classe, assuntos, órgão julgador e 10 últimos movimentos.
        """
        tribunal_clean = tribunal.strip().upper()
        indice = INDICES_TRIBUNAL.get(tribunal_clean)
        if not indice:
            return json.dumps({
                "status": "error",
                "message": f"Tribunal '{tribunal}' não reconhecido.",
                "tribunais_disponiveis": sorted(list(INDICES_TRIBUNAL.keys())),
            }, ensure_ascii=False)

        num_limpo = numero_processo.strip().replace(".", "").replace("-", "")
        body = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"numeroProcesso": numero_processo.strip()}},
                        {"match": {"numeroProcesso": num_limpo}},
                    ]
                }
            }
        }

        try:
            data = _datajud_post(indice, body)
            hits = data.get("hits", {}).get("hits", [])
            if not hits:
                return json.dumps({"status": "not_found", "message": "Processo não encontrado na base pública do DataJud.", "numero_processo": numero_processo}, ensure_ascii=False)
            processos = [_formatar_processo(h) for h in hits]
            return json.dumps({"status": "success", "processos": processos}, ensure_ascii=False, indent=2)
        except httpx.HTTPStatusError as e:
            return json.dumps({"status": "error", "message": f"Erro HTTP {e.response.status_code} na API do DataJud"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Falha na consulta ao DataJud: {str(e)}"}, ensure_ascii=False)

    @mcp.tool()
    def buscar_processos_por_parte(nome_parte: str, tribunal: str, polo: str = "ATIVO", tamanho: int = 10) -> str:
        """
        Busca processos pelo nome da parte (pessoa física ou jurídica) no DataJud.

        Args:
            nome_parte: Nome completo ou termo de busca da parte.
            tribunal: Sigla do tribunal (ex: 'TJSP', 'TJMG', 'TRF1').
            polo: Polo processual: 'ATIVO', 'PASSIVO' ou 'TESTEMUNHA' (padrão: 'ATIVO').
            tamanho: Quantidade de resultados a retornar (máximo 10).

        Returns:
            JSON com contagem total e lista resumida dos processos encontrados.
        """
        tribunal_clean = tribunal.strip().upper()
        indice = INDICES_TRIBUNAL.get(tribunal_clean)
        if not indice:
            return json.dumps({"status": "error", "message": f"Tribunal '{tribunal}' não reconhecido."}, ensure_ascii=False)

        body = {
            "size": min(max(tamanho, 1), 10),
            "query": {
                "bool": {
                    "must": [
                        {"match": {"partes.nome": nome_parte}},
                        {"match": {"partes.polo": polo.upper()}},
                    ]
                }
            },
        }

        try:
            data = _datajud_post(indice, body)
            hits = data.get("hits", {}).get("hits", [])
            total = data.get("hits", {}).get("total", {}).get("value", 0)
            return json.dumps({
                "status": "success",
                "total_encontrado": total,
                "exibindo": len(hits),
                "processos": [_formatar_processo(h) for h in hits],
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def buscar_processos_por_assunto(assunto: str, tribunal: str, tamanho: int = 5) -> str:
        """
        Pesquisa processos por assunto/matéria jurídica no DataJud.

        Args:
            assunto: Termo do assunto jurídico (ex: 'dano moral', 'negativação indevida', 'repetição de indébito').
            tribunal: Sigla do tribunal (ex: 'TJSP', 'TJMG', 'STJ').
            tamanho: Quantidade de processos a retornar (máximo 10).

        Returns:
            JSON com processos recentes cadastrados sob o assunto no tribunal.
        """
        tribunal_clean = tribunal.strip().upper()
        indice = INDICES_TRIBUNAL.get(tribunal_clean)
        if not indice:
            return json.dumps({"status": "error", "message": f"Tribunal '{tribunal}' não reconhecido."}, ensure_ascii=False)

        body = {
            "size": min(max(tamanho, 1), 10),
            "query": {"match": {"assuntos.nome": assunto}},
            "sort": [{"dataHoraUltimaAtualizacao": {"order": "desc"}}],
        }

        try:
            data = _datajud_post(indice, body)
            hits = data.get("hits", {}).get("hits", [])
            total = data.get("hits", {}).get("total", {}).get("value", 0)
            return json.dumps({
                "status": "success",
                "total_encontrado": total,
                "exibindo": len(hits),
                "processos": [_formatar_processo(h) for h in hits],
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

    @mcp.tool()
    def listar_tribunais() -> str:
        """
        Lista todas as siglas de tribunais suportados pelo DataJud e seus respectivos índices.

        Returns:
            JSON com a relação de siglas e nomes de índices do DataJud.
        """
        return json.dumps({
            "status": "success",
            "tribunais": INDICES_TRIBUNAL,
            "total": len(INDICES_TRIBUNAL),
        }, ensure_ascii=False, indent=2)

    @mcp.tool()
    def buscar_publicacoes_djen(numero_processo: str) -> str:
        """
        Busca publicações e intimações no Diário de Justiça Eletrônico Nacional (DJEN) pelo número do processo via portal Comunica PJe.

        Args:
            numero_processo: Número do processo no padrão CNJ.

        Returns:
            JSON com as comunicações oficiais publicadas no DJEN.
        """
        num_clean = numero_processo.strip()
        url = f"{DJEN_BASE}/comunicacao/consulta-publica"
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.get(url, params={"numeroProcesso": num_clean}, follow_redirects=True)
                if resp.status_code == 200:
                    return json.dumps({"status": "success", "data": resp.json()}, ensure_ascii=False, indent=2)
                
                # Fallback para endpoint v1
                resp2 = client.get(f"{DJEN_BASE}/v1/comunicacoes", params={"numeroProcesso": num_clean})
                if resp2.status_code == 200:
                    return json.dumps({"status": "success", "data": resp2.json()}, ensure_ascii=False, indent=2)

                return json.dumps({
                    "status": "not_found",
                    "message": "Nenhuma publicação localizada no DJEN para este número de processo.",
                    "status_code": resp.status_code,
                }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Falha na consulta ao DJEN: {str(e)}"}, ensure_ascii=False)

    @mcp.tool()
    def buscar_publicacoes_dje_cnj(numero_processo: str, data_inicio: str = "", data_fim: str = "") -> str:
        """
        Localiza movimentações de publicação em Diário de Justiça Eletrônico (DJe) nos autos do processo no DataJud.

        Args:
            numero_processo: Número CNJ do processo (ex: '0000000-00.0000.8.26.0000').
            data_inicio: Filtro inicial por data no formato YYYY-MM-DD (opcional).
            data_fim: Filtro final por data no formato YYYY-MM-DD (opcional).

        Returns:
            JSON com intimações e despachos publicados identificados nos movimentos processuais.
        """
        num_limpo = numero_processo.replace(".", "").replace("-", "").strip()
        tribunal = None
        if len(num_limpo) >= 20:
            segmento = num_limpo[13]
            codigo_tribunal = num_limpo[14:16]
            CODIGO_TRIBUNAL = {
                ("1", "00"): "STF", ("3", "00"): "STJ", ("6", "00"): "TSE", ("7", "00"): "STM",
                ("4", "01"): "TRF1", ("4", "02"): "TRF2", ("4", "03"): "TRF3",
                ("4", "04"): "TRF4", ("4", "05"): "TRF5", ("4", "06"): "TRF6",
                ("5", "00"): "TST",
                **{("5", f"{n:02d}"): f"TRT{n}" for n in range(1, 25)},
                ("8", "01"): "TJAC", ("8", "02"): "TJAL", ("8", "03"): "TJAP", ("8", "04"): "TJAM",
                ("8", "05"): "TJBA", ("8", "06"): "TJCE", ("8", "07"): "TJDF", ("8", "08"): "TJES",
                ("8", "09"): "TJGO", ("8", "10"): "TJMA", ("8", "11"): "TJMT", ("8", "12"): "TJMS",
                ("8", "13"): "TJMG", ("8", "14"): "TJPA", ("8", "15"): "TJPB", ("8", "16"): "TJPR",
                ("8", "17"): "TJPE", ("8", "18"): "TJPI", ("8", "19"): "TJRJ", ("8", "20"): "TJRN",
                ("8", "21"): "TJRS", ("8", "22"): "TJRO", ("8", "23"): "TJRR", ("8", "24"): "TJSC",
                ("8", "25"): "TJSE", ("8", "26"): "TJSP", ("8", "27"): "TJTO",
            }
            tribunal = CODIGO_TRIBUNAL.get((segmento, codigo_tribunal))

        if not tribunal:
            return json.dumps({
                "status": "error",
                "message": "Não foi possível deduzir a sigla do tribunal pelo NPU. Use consultar_processo() informando o tribunal.",
            }, ensure_ascii=False)

        indice = INDICES_TRIBUNAL.get(tribunal)
        if not indice:
            return json.dumps({"status": "error", "message": f"Índice do DataJud não disponível para {tribunal}."}, ensure_ascii=False)

        body = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"numeroProcesso": numero_processo.strip()}},
                        {"match": {"numeroProcesso": num_limpo}},
                    ]
                }
            },
            "_source": ["numeroProcesso", "tribunal", "movimentos"],
        }

        try:
            data = _datajud_post(indice, body)
            hits = data.get("hits", {}).get("hits", [])
            if not hits:
                return json.dumps({"status": "not_found", "message": "Processo não encontrado no DataJud."}, ensure_ascii=False)

            src = hits[0].get("_source", {})
            movimentos = src.get("movimentos", [])
            palavras_dje = ["dje", "diário", "publicação", "intimação", "publicado"]
            publicacoes = [
                {
                    "data": m.get("dataHora"),
                    "descricao": m.get("nome"),
                    "complemento": " | ".join(
                        c.get("descricao", "") for c in m.get("complementosTabelados", [])
                    ),
                }
                for m in movimentos
                if any(p in (m.get("nome") or "").lower() for p in palavras_dje)
            ]
            publicacoes.sort(key=lambda x: x.get("data", ""), reverse=True)

            if data_inicio:
                publicacoes = [p for p in publicacoes if p.get("data", "") >= data_inicio]
            if data_fim:
                publicacoes = [p for p in publicacoes if p.get("data", "") <= data_fim + "T23:59:59"]

            return json.dumps({
                "status": "success",
                "numero_processo": numero_processo,
                "tribunal": tribunal,
                "total_publicacoes_encontradas": len(publicacoes),
                "publicacoes": publicacoes,
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
