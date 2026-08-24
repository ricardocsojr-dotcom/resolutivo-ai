#!/usr/bin/env python3
"""
CNJ MCP Server — DataJud + DJEN
Conecta ao DataJud (Base Nacional de Processos) e ao DJEN (Diário de Justiça
Eletrônico Nacional) usando as APIs públicas do CNJ.

Uso:
    pip install -r requirements.txt
    python server.py
"""

import json
import httpx
from mcp.server.fastmcp import FastMCP

# ─── Configuração ──────────────────────────────────────────────────────────────

DATAJUD_BASE = "https://api-publica.datajud.cnj.jus.br"
DATAJUD_APIKEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="

DJEN_BASE = "https://comunica.pje.jus.br/api"
CNJ_DJE_BASE = "https://www.cnj.jus.br/wp-json/cnj-dje/v1"

HEADERS_DATAJUD = {
    "Authorization": f"APIKey {DATAJUD_APIKEY}",
    "Content-Type": "application/json",
}

# Mapa de siglas de tribunal para índices do DataJud
INDICES_TRIBUNAL = {
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

mcp = FastMCP("CNJ — DataJud e DJEN")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _datajud_post(indice: str, body: dict) -> dict:
    url = f"{DATAJUD_BASE}/{indice}/_search"
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, headers=HEADERS_DATAJUD, json=body)
        resp.raise_for_status()
        return resp.json()


def _formatar_processo(hit: dict) -> dict:
    """Extrai campos relevantes de um hit do ElasticSearch."""
    src = hit.get("_source", {})
    return {
        "numero_processo": src.get("numeroProcesso"),
        "tribunal": src.get("tribunal"),
        "classe": src.get("classe", {}).get("nome"),
        "assuntos": [a.get("nome") for a in src.get("assuntos", [])],
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


# ─── Ferramentas DataJud ───────────────────────────────────────────────────────

@mcp.tool()
def consultar_processo(
    numero_processo: str,
    tribunal: str,
) -> str:
    """
    Consulta um processo judicial pelo número completo no DataJud (CNJ).

    Args:
        numero_processo: Número do processo no formato CNJ (ex: 0000000-00.0000.8.26.0000)
        tribunal: Sigla do tribunal (ex: TJSP, TJMG, STJ, TRF3). Veja listar_tribunais().

    Returns:
        JSON com dados do processo: partes, classe, assuntos, movimentações recentes.
    """
    tribunal_upper = tribunal.upper()
    indice = INDICES_TRIBUNAL.get(tribunal_upper)
    if not indice:
        return json.dumps({
            "erro": f"Tribunal '{tribunal}' não reconhecido.",
            "tribunais_disponiveis": list(INDICES_TRIBUNAL.keys()),
        }, ensure_ascii=False)

    body = {
        "query": {
            "match": {
                "numeroProcesso": numero_processo.strip()
            }
        }
    }

    try:
        data = _datajud_post(indice, body)
        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            return json.dumps({"resultado": "Processo não encontrado.", "numero": numero_processo}, ensure_ascii=False)
        return json.dumps([_formatar_processo(h) for h in hits], ensure_ascii=False, indent=2)
    except httpx.HTTPStatusError as e:
        return json.dumps({"erro": f"Erro HTTP {e.response.status_code}: {e.response.text}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)


@mcp.tool()
def buscar_processos_por_parte(
    nome_parte: str,
    tribunal: str,
    polo: str = "ATIVO",
    tamanho: int = 10,
) -> str:
    """
    Busca processos por nome de parte no DataJud.

    Args:
        nome_parte: Nome da pessoa física ou jurídica.
        tribunal: Sigla do tribunal (ex: TJSP, TJMG).
        polo: Polo processual — ATIVO, PASSIVO ou TESTEMUNHA (padrão: ATIVO).
        tamanho: Quantidade de resultados (máx 10 por consulta pública).

    Returns:
        Lista de processos encontrados com classe, assunto e últimas movimentações.
    """
    tribunal_upper = tribunal.upper()
    indice = INDICES_TRIBUNAL.get(tribunal_upper)
    if not indice:
        return json.dumps({"erro": f"Tribunal '{tribunal}' não reconhecido."}, ensure_ascii=False)

    body = {
        "size": min(tamanho, 10),
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
        result = {
            "total_encontrado": total,
            "exibindo": len(hits),
            "processos": [_formatar_processo(h) for h in hits],
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)


@mcp.tool()
def buscar_processos_por_assunto(
    assunto: str,
    tribunal: str,
    tamanho: int = 5,
) -> str:
    """
    Busca processos por assunto/matéria no DataJud.

    Args:
        assunto: Assunto jurídico (ex: "dano moral", "negativação indevida").
        tribunal: Sigla do tribunal.
        tamanho: Número de resultados (máx 10).

    Returns:
        Lista de processos sobre o assunto no tribunal.
    """
    tribunal_upper = tribunal.upper()
    indice = INDICES_TRIBUNAL.get(tribunal_upper)
    if not indice:
        return json.dumps({"erro": f"Tribunal '{tribunal}' não reconhecido."}, ensure_ascii=False)

    body = {
        "size": min(tamanho, 10),
        "query": {
            "match": {
                "assuntos.nome": assunto
            }
        },
        "sort": [{"dataHoraUltimaAtualizacao": {"order": "desc"}}],
    }

    try:
        data = _datajud_post(indice, body)
        hits = data.get("hits", {}).get("hits", [])
        total = data.get("hits", {}).get("total", {}).get("value", 0)
        result = {
            "total_encontrado": total,
            "exibindo": len(hits),
            "processos": [_formatar_processo(h) for h in hits],
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)


@mcp.tool()
def listar_tribunais() -> str:
    """
    Lista todos os tribunais disponíveis no DataJud com suas siglas.

    Returns:
        Dicionário com sigla → nome do índice no DataJud.
    """
    return json.dumps(INDICES_TRIBUNAL, ensure_ascii=False, indent=2)


# ─── Ferramentas DJEN ─────────────────────────────────────────────────────────

@mcp.tool()
def buscar_publicacoes_djen(
    numero_processo: str,
) -> str:
    """
    Busca publicações no Diário de Justiça Eletrônico Nacional (DJEN/DJe)
    pelo número do processo via portal PJe do CNJ.

    Args:
        numero_processo: Número do processo no formato CNJ.

    Returns:
        Publicações encontradas no DJEN (intimações, despachos, decisões publicadas).
    """
    url = f"{DJEN_BASE}/comunicacao/consulta-publica"
    params = {"numeroProcesso": numero_processo.strip()}

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, params=params, follow_redirects=True)
            if resp.status_code == 200:
                return json.dumps(resp.json(), ensure_ascii=False, indent=2)
            # Fallback: tentar endpoint alternativo do PJe
            url2 = f"https://comunica.pje.jus.br/api/v1/comunicacoes"
            resp2 = client.get(url2, params={"numeroProcesso": numero_processo.strip()})
            if resp2.status_code == 200:
                return json.dumps(resp2.json(), ensure_ascii=False, indent=2)
            return json.dumps({
                "aviso": "DJEN não retornou dados para este processo.",
                "status": resp.status_code,
                "dica": "Verifique se o processo tramita em tribunal que já aderiu ao DJEN (resolução CNJ 455/2022).",
                "tribunais_djen": [
                    "STJ", "STF", "TRF1", "TRF2", "TRF3", "TRF4", "TRF5", "TRF6",
                    "TJMG", "TJSP", "TJRS", "TJPR", "TJSC", "TJRJ",
                    "TRT2", "TRT3", "TRT4", "TRT9", "TRT15",
                ],
            }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"erro": str(e), "dica": "DJEN pode requerer VPN ou estar em manutenção."}, ensure_ascii=False)


@mcp.tool()
def buscar_publicacoes_dje_cnj(
    numero_processo: str,
    data_inicio: str = "",
    data_fim: str = "",
) -> str:
    """
    Consulta publicações no Diário de Justiça Eletrônico do CNJ.
    Útil para intimações e despachos publicados em processos federais e de tribunais superiores.

    Args:
        numero_processo: Número do processo CNJ.
        data_inicio: Data início no formato YYYY-MM-DD (opcional).
        data_fim: Data fim no formato YYYY-MM-DD (opcional).

    Returns:
        Lista de publicações encontradas no DJe do CNJ.
    """
    # Consulta via DataJud: os movimentos incluem publicações no DJe
    # NPU oficial (Resolução CNJ 65/2008): NNNNNNN-DD.AAAA.J.TR.OOOO
    # posição 13 = segmento de Justiça (1 dígito), posições 14-15 = tribunal (2 dígitos)
    num_limpo = numero_processo.replace(".", "").replace("-", "")
    if len(num_limpo) >= 20:
        segmento = num_limpo[13]
        codigo_tribunal = num_limpo[14:16]
        # Tabela oficial segmento+tribunal do CNJ
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
    else:
        tribunal = None

    if not tribunal:
        return json.dumps({
            "erro": "Não foi possível identificar o tribunal pelo número do processo.",
            "dica": "Use consultar_processo() informando o tribunal manualmente.",
        }, ensure_ascii=False)

    indice = INDICES_TRIBUNAL.get(tribunal)
    if not indice:
        return json.dumps({"erro": f"Índice não disponível para {tribunal}."}, ensure_ascii=False)

    # Busca no DataJud e filtra movimentos de publicação no DJe
    body = {
        "query": {"match": {"numeroProcesso": numero_processo.strip()}},
        "_source": ["numeroProcesso", "tribunal", "movimentos"],
    }

    try:
        data = _datajud_post(indice, body)
        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            return json.dumps({"resultado": "Processo não encontrado no DataJud."}, ensure_ascii=False)

        src = hits[0].get("_source", {})
        movimentos = src.get("movimentos", [])

        # Palavras-chave que identificam publicações no DJe
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

        # Filtrar por data se informado
        if data_inicio:
            publicacoes = [p for p in publicacoes if p.get("data", "") >= data_inicio]
        if data_fim:
            publicacoes = [p for p in publicacoes if p.get("data", "") <= data_fim + "T23:59:59"]

        return json.dumps({
            "numero_processo": numero_processo,
            "tribunal": tribunal,
            "total_publicacoes_encontradas": len(publicacoes),
            "publicacoes": publicacoes,
            "todos_movimentos_count": len(movimentos),
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"erro": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
