#!/usr/bin/env python3
"""Compilador Canônico Markdown -> JSON de Blocos RDAA.

Converte petições e manifestações redigidas em Markdown no payload JSON estruturado
exigido pelo gerador nativo OOXML (construir_peca.py), garantindo conformidade
automática de endereçamento, pedidos, numeração e local/data.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Força UTF-8 no Windows
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

MESES_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]


def data_local_uberlandia(dt: datetime | None = None) -> str:
    """Gera o fechamento de data institucional sempre em Uberlândia/MG."""
    dt = dt or datetime.now()
    mes = MESES_PT[dt.month - 1]
    return f"Uberlândia/MG, {dt.day} de {mes} de {dt.year}."


def normalizar_enderecamento(texto_bruto: str) -> str:
    """Padroniza o endereçamento formal para o padrão institucional solene."""
    s = texto_bruto.strip()
    # Se já estiver no padrão solene completo, preserva
    if s.startswith("EXCELENTÍSSIMO") or s.startswith("EXMO"):
        return s
    
    # Se for tribunal
    if re.search(r'\b(?:TRIBUNAL|TJ[A-Z]{2}|TRF\d|STJ|STF)\b', s, re.IGNORECASE):
        m = re.search(r'\b(?:ao\s+)?(?:egrégio\s+)?(tribunal\s+de\s+justiça\s+do\s+estado\s+d[eo]\s+[a-zç\s]+|trf\s*\dª?\s*região|superior\s+tribunal\s+de\s+justiça|supremo\s+tribunal\s+federal)\b', s, re.IGNORECASE)
        nome_tribunal = m.group(1).upper() if m else s.upper()
        return f"EXCELENTÍSSIMO SENHOR DOUTOR DESEMBARGADOR PRESIDENTE DO EGRÉGIO {nome_tribunal}"

    # Padrão de 1º grau (Vara Cível / Empresarial / Juizado)
    m_vara = re.search(r'(\d+ª?\s+VARA\s+[^,\n\r]+)', s, re.IGNORECASE)
    m_comarca = re.search(r'(?:DE|DA COMARCA DE)\s+([A-ZÇÃÕÁÉÍÓÚ\s]+?)(?:/|-|\s+ESTADO|\s*$)', s, re.IGNORECASE)
    m_uf = re.search(r'[/-]\s*([A-Z]{2})\b', s)
    
    vara = m_vara.group(1).upper() if m_vara else "14ª VARA CÍVEL E EMPRESARIAL"
    comarca = m_comarca.group(1).strip().upper() if m_comarca else "BELÉM"
    uf = m_uf.group(1).upper() if m_uf else "PA"
    
    return f"EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA {vara} DA COMARCA DE {comarca}/{uf}"


def compilar_markdown_para_contexto(
    markdown_text: str,
    *,
    matter_id: str | None = None,
    nivel_peca: str = "B",
    processo: str | None = None,
    partes_str: str | None = None,
) -> dict[str, Any]:
    """Compila o texto Markdown gerado por qualquer LLM no schema JSON de blocos RDAA."""
    lines = [l.rstrip() for l in markdown_text.splitlines()]
    
    # 1. Extração de Metadados Iniciais (Endereçamento, Processo, Partes)
    enderecamento = ""
    numero_processo = processo or ""
    partes = partes_str or ""
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Endereçamento
        if not enderecamento and (line.startswith("AO JUÍZO") or line.startswith("EXCELENTÍSSIMO") or line.startswith("EXMO")):
            enderecamento = normalizar_enderecamento(line)
            i += 1
            continue
            
        # Processo
        m_proc = re.search(r'(?:Processo(?:\s+n[ºo]?)?:?\s*)(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})', line, re.IGNORECASE)
        if m_proc and not numero_processo:
            numero_processo = m_proc.group(1)
            i += 1
            continue
            
        # Partes (Quadro com borda)
        if (line.startswith("Autora:") or line.startswith("Autor:") or line.startswith("Requerente:") or line.startswith("Exequente:") or line.startswith("Embargante:")) and not partes:
            quadro_lines = [line]
            j = i + 1
            while j < len(lines) and lines[j].strip() and (lines[j].startswith("Ré:") or lines[j].startswith("Réu:") or lines[j].startswith("Requerido:") or lines[j].startswith("Executado:") or lines[j].startswith("Embargado:")):
                quadro_lines.append(lines[j].strip())
                j += 1
            partes = "\n".join(quadro_lines)
            i = j
            continue
            
        # Se encontrou o parágrafo de qualificação/abertura, para os metadados
        if "já qualificada" in line or "já qualificado" in line or "vem, respeitosamente" in line:
            break
            
        i += 1
        
    corpo_lines = lines[i:]
    
    # 2. Parsing dos Blocos do Corpo
    blocos: list[dict[str, Any]] = []
    publicacoes_texto = ""
    
    # Detecta se há bloco de abertura inicial
    abertura_encontrada = False
    idx_linha = 0
    
    while idx_linha < len(corpo_lines):
        raw = corpo_lines[idx_linha].strip()
        if not raw:
            idx_linha += 1
            continue
            
        # Se for cláusula de publicações / intimações
        if raw.startswith("Requer que as publicações") or raw.startswith("Requer que as intimações"):
            publicacoes_texto = raw
            idx_linha += 1
            continue
            
        # Se for o fecho final ou data ou assinaturas manuais, ignora o restante do corpo
        if "Nestes termos" in raw or "aguarda deferimento" in raw or re.match(r'^[A-ZÇÃÕÁÉÍÓÚa-zçãõáéíóú\s]+/[A-Z]{2},\s*\d+', raw):
            break
        if raw.startswith("Wanderley Romano") or raw.startswith("Flávia Almeida") or raw.startswith("Alessandra Xavier") or raw.startswith("Ricardo Cesar"):
            break
        if raw.startswith("(Assinado Eletronicamente)"):
            break

        # Bloco Abertura (Qualificação)
        if not abertura_encontrada and ("já qualificada" in raw or "já qualificado" in raw or "vem, respeitosamente" in raw):
            # Limpa tags html manuais se houver
            clean_open = re.sub(r'</?[bui]>', '', raw)
            m_open = re.match(r'^(.*?),\s*(já\s+qualificad[ao].*?)(?:,\s*com\s+fundamento\s+no\s+(.*?))?,\s*(?:vem|apresentar|formular|interpor|propor|opor)\s*(.*?)(?:,\s*pelas\s+razões|\.\s*$)', clean_open, re.IGNORECASE)
            
            nome_parte = "TRIVALE ADMINISTRAÇÃO LTDA."
            nome_peca = "MANIFESTAÇÃO"
            resto = ", já qualificada nos autos, por seus advogados que esta subscrevem, vem, respeitosamente, à presença de Vossa Excelência, "
            resto_depois = ", pelas razões a seguir expostas."
            
            # Extrai nome da parte em destaque se presente
            m_parte = re.search(r'^([A-ZÇÃÕÁÉÍÓÚ\s\.\-–]+?(?:LTDA\.?|S/?A|EIRELI|ME)?),', clean_open)
            if m_parte:
                nome_parte = m_parte.group(1).strip()
            
            # Extrai nome da peça
            m_peca = re.search(r'\b(?:apresentar|formular|interpor|propor|opor)\s+(?:a\s+|o\s+)?(\b[A-ZÇÃÕÁÉÍÓÚ\s\-–]{4,}\b)', clean_open)
            if m_peca:
                nome_peca = m_peca.group(1).strip()
                
            blocos.append({
                "tipo": "abertura",
                "nome_parte": nome_parte,
                "resto": resto,
                "nome_peca": nome_peca,
                "resto_depois": resto_depois
            })
            abertura_encontrada = True
            idx_linha += 1
            continue

        # Título Nível 1 (# ou algarismo romano I., II. ou **TÍTULO**)
        m_tit1 = re.match(r'^(?:#\s+|(?:\*\*)?(?:[IVXLCDM]+\.?\s+)?)([A-ZÇÃÕÁÉÍÓÚ\s\.\-–]{4,})(?:\*\*)?$', raw)
        if (raw.startswith("# ") or (raw.startswith("**") and raw.endswith("**") and len(raw) < 80 and not raw.startswith("**VIII. PEDIDOS"))) and not re.match(r'^\d+\.', raw):
            tit_text = raw.lstrip("#* ").rstrip("* ")
            tit_text = re.sub(r'^[IVXLCDM]+\.\s*', '', tit_text).strip()
            # Remove pontuações proibidas em títulos
            tit_text = re.sub(r'[:—–]', '', tit_text).strip()
            blocos.append({"tipo": "titulo", "texto": tit_text, "sequencia": "corpo"})
            idx_linha += 1
            continue

        # Título Nível 2 (## ou 1. Subtópico)
        if raw.startswith("## "):
            tit2_text = raw.removeprefix("## ").strip()
            tit2_text = re.sub(r'[:—–]', '', tit2_text).strip()
            blocos.append({"tipo": "titulo2", "texto": tit2_text, "sequencia": "corpo"})
            idx_linha += 1
            continue

        # Título de Pedidos
        if "PEDIDOS" in raw.upper() and (raw.startswith("#") or raw.startswith("**")):
            blocos.append({"tipo": "titulo", "texto": "PEDIDOS", "sequencia": "corpo"})
            idx_linha += 1
            continue

        # Alíneas de pedidos (a., a), i., i), 1., 1))
        m_alinea = re.match(r'^(?:[a-z]|\d+|[ivxlcdm]+)[.)]\s*(.*)$', raw, re.IGNORECASE)
        if m_alinea and ("requer" in markdown_text.lower() or idx_linha > len(corpo_lines) - 20):
            texto_alinea = m_alinea.group(1).strip()
            # Remove travessões proibidos
            texto_alinea = texto_alinea.replace("—", ", ")
            blocos.append({
                "tipo": "alinea",
                "texto": texto_alinea,
                "nivel": 0,
                "sequencia": "pedidos"
            })
            idx_linha += 1
            continue

        # Parágrafo Numerado do Corpo
        m_num = re.match(r'^\d+\.\s*(.*)$', raw)
        texto_paragrafo = m_num.group(1).strip() if m_num else raw
        
        # Substitui travessões automáticos por vírgula
        texto_paragrafo = texto_paragrafo.replace("—", ", ")
        
        # Se for introdução de pedidos com dois-pontos
        if texto_paragrafo.endswith("requer:") or texto_paragrafo.endswith("requerem:"):
            # É permitido dois pontos antes de alíneas
            pass
            
        blocos.append({
            "tipo": "numerado",
            "texto": texto_paragrafo,
            "sequencia": "corpo"
        })
        idx_linha += 1

    # Adiciona bloco de assinaturas ao final
    blocos.append({"tipo": "assinaturas"})
    
    return {
        "matter_id": matter_id or (f"{numero_processo}-peca" if numero_processo else "peca-rdaa"),
        "nivel_peca": nivel_peca,
        "modo_redacao": "blocos",
        "redacao_por_blocos": True,
        "exigir_esqueleto": nivel_peca in {"A", "B"},
        "enderecamento": enderecamento or "EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(A) DE DIREITO DA 14ª VARA CÍVEL E EMPRESARIAL DA COMARCA DE BELÉM/PA",
        "numero_processo": numero_processo or "0879903-83.2025.8.14.0301",
        "partes": partes or "Autora: TRIVALE ADMINISTRAÇÃO LTDA.\nRé: EQUATORIAL PARÁ DISTRIBUIDORA DE ENERGIA S.A.",
        "blocos": blocos,
        "publicacoes_texto": publicacoes_texto or (
            "Requer que as publicações referentes a este feito sejam realizadas exclusivamente "
            "em nome do advogado Wanderley Romano Donadel, OAB/MG 78.870, pelo endereço eletrônico "
            "wanderley@romanodonadel.com.br, e que as correspondências postais sejam encaminhadas à "
            "Avenida dos Vinhedos, n.º 200, Conjunto 4, Gávea Office, Morada da Colina, Uberlândia/MG, "
            "CEP 38.411-159, sob pena de nulidade."
        ),
        "data_local": data_local_uberlandia(),
        "fecho": "Nestes termos, aguarda deferimento."
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compilador Markdown -> Contexto JSON RDAA")
    parser.add_argument("input_markdown", type=Path, help="Arquivo .md de entrada")
    parser.add_argument("--output", type=Path, required=True, help="Arquivo .json de saída")
    parser.add_argument("--matter-id", help="Identificador da matéria")
    parser.add_argument("--nivel", choices=["A", "B", "C", "a", "b", "c"], default="B")
    parser.add_argument("--processo", help="Número do processo CNJ")
    
    args = parser.parse_args()
    
    if not args.input_markdown.is_file():
        print(f"[ERRO] Arquivo não encontrado: {args.input_markdown}", file=sys.stderr)
        return 1
        
    md_content = args.input_markdown.read_text(encoding="utf-8")
    contexto = compilar_markdown_para_contexto(
        md_content,
        matter_id=args.matter_id,
        nivel_peca=args.nivel.upper(),
        processo=args.processo
    )
    
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(contexto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] Contexto compilado com sucesso: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
