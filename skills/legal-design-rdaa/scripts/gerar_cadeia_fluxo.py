#!/usr/bin/env python3
"""
gerar_cadeia_fluxo.py — Gerador de diagramas de cadeia única (fluxo e responsabilidades).

Uso:
    python3 gerar_cadeia_fluxo.py --spec spec.json --output diagram.svg
    
Spec (JSON):
{
  "titulo": "CADEIA ÚNICA",
  "subtitulo": "FLUXO E RESPONSABILIDADES NA OPERAÇÃO DE LEITE",
  "etapas": [
    {
      "numero": 1,
      "titulo": "FORNECIMENTO\\nINDIVIDUAL",
      "ator": "AUTOR (PRODUTOR)",
      "descricao": "O Autor entrega o leite por\\nmeio da APROLI, sem\\ncontratar diretamente com a Ré.",
      "prova": "Relatórios de captação. Evento 48",
      "destacado": false
    },
    ... (até 6 etapas)
  ],
  "ponto_central": "A Ré participa apenas das etapas 3 e 4. O repasse individual...",
  "disclaimer": "Esquema ilustrativo do fluxo negocial. Não substitui a prova documental.",
  "etapas_destacadas": [3, 4]  # números das etapas a destacar
}
"""

import json
import sys
import os
from pathlib import Path

# Paleta oficial do escritório
COR_DESTAQUE = "#F7A800"     # Laranja
COR_ESTRUTURA = "#63666A"   # Cinza
COR_TEXTO = "#000000"       # Preto
COR_FUNDO = "#FFFFFF"       # Branco
COR_BORDA = "#C9CBCD"       # Borda cinza claro
COR_SEPARADOR = "#EDEEEF"   # Separador muito claro

# Dimensões
LARGURA_SVG = 1040
ALTURA_SVG = 314
MARGIN_X = 24
MARGIN_Y = 14
ESPACO_ETAPAS = 62  # Y inicial das caixas de etapas
ALTURA_CAIXA = 150
ALTURA_HEADER = 48  # Espaço para título e subtítulo

def gerar_cadeia_unica(spec_path, output_path=None):
    """Gera diagram SVG de cadeia única a partir de spec JSON."""
    
    with open(spec_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    
    etapas = spec.get('etapas', [])
    titulo = spec.get('titulo', 'CADEIA ÚNICA')
    subtitulo = spec.get('subtitulo', '')
    ponto_central = spec.get('ponto_central', '')
    disclaimer = spec.get('disclaimer', '')
    etapas_destacadas = set(spec.get('etapas_destacadas', []))
    
    # Validação
    if len(etapas) < 2 or len(etapas) > 6:
        print(f"Erro: esperado 2-6 etapas, recebido {len(etapas)}", file=sys.stderr)
        sys.exit(1)
    
    # Calcular dimensões baseado no número de etapas
    num_etapas = len(etapas)
    largura_caixa = (LARGURA_SVG - 2*MARGIN_X) / num_etapas
    
    # Iniciar SVG
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGURA_SVG} {ALTURA_SVG}" font-family="Lato, \'Segoe UI\', Tahoma, Arial, sans-serif">',
        f'<rect width="{LARGURA_SVG}" height="{ALTURA_SVG}" fill="{COR_FUNDO}"/>'
    ]
    
    # Barra de cor (lado esquerdo do título)
    svg_lines.append(f'<rect x="{MARGIN_X}" y="{MARGIN_Y}" width="6" height="40" fill="{COR_DESTAQUE}"/>')
    
    # Título
    svg_lines.append(f'<text x="{MARGIN_X+18}" y="{MARGIN_Y+18}" font-size="19" font-weight="800" fill="{COR_TEXTO}" letter-spacing="0.5">{titulo}</text>')
    
    # Subtítulo
    if subtitulo:
        svg_lines.append(f'<text x="{MARGIN_X+18}" y="{MARGIN_Y+35}" font-size="11" font-weight="700" fill="{COR_ESTRUTURA}" letter-spacing="1.3">{subtitulo}</text>')
    
    # Headers de ator (faixa de informação)
    x_etapa = MARGIN_X
    for i, etapa in enumerate(etapas):
        ator = etapa.get('ator', '')
        cor_faixa = COR_DESTAQUE if (etapa.get('numero', i+1) in etapas_destacadas) else COR_ESTRUTURA
        cor_texto_faixa = COR_TEXTO if (etapa.get('numero', i+1) in etapas_destacadas) else COR_FUNDO
        
        svg_lines.append(f'<rect x="{x_etapa}" y="{ESPACO_ETAPAS}" width="{largura_caixa}" height="20" rx="3" fill="{cor_faixa}"/>')
        svg_lines.append(f'<text x="{x_etapa + largura_caixa/2}" y="{ESPACO_ETAPAS + 14}" font-size="9" font-weight="800" fill="{cor_texto_faixa}" text-anchor="middle" letter-spacing="1">{ator}</text>')
        
        x_etapa += largura_caixa
    
    # Caixas de etapas
    x_etapa = MARGIN_X
    for i, etapa in enumerate(etapas):
        num_etapa = etapa.get('numero', i+1)
        titulo_etapa = etapa.get('titulo', '')
        descricao = etapa.get('descricao', '')
        prova = etapa.get('prova', '')
        destacado = num_etapa in etapas_destacadas
        
        cor_borda_caixa = COR_DESTAQUE if destacado else COR_BORDA
        espessura_borda = "1.6" if destacado else "1"
        cor_numero = COR_DESTAQUE
        cor_header_caixa = COR_DESTAQUE if destacado else COR_ESTRUTURA
        
        # Caixa principal
        svg_lines.append(f'<rect x="{x_etapa}" y="{ESPACO_ETAPAS + 30}" width="{largura_caixa}" height="{ALTURA_CAIXA}" rx="6" fill="{COR_FUNDO}" stroke="{cor_borda_caixa}" stroke-width="{espessura_borda}"/>')
        
        # Header da caixa
        svg_lines.append(f'<rect x="{x_etapa}" y="{ESPACO_ETAPAS + 30}" width="{largura_caixa}" height="4" rx="2" fill="{cor_header_caixa}"/>')
        
        # Círculo com número
        cx = x_etapa + 17
        cy = ESPACO_ETAPAS + 54
        svg_lines.append(f'<circle cx="{cx}" cy="{cy}" r="12" fill="{cor_numero}"/>')
        svg_lines.append(f'<text x="{cx}" y="{cy + 4.3}" font-size="12.5" font-weight="800" fill="{COR_FUNDO}" text-anchor="middle">{num_etapa}</text>')
        
        # Título da etapa (com quebras de linha automáticas)
        txt_x = x_etapa + 36
        txt_y = ESPACO_ETAPAS + 50
        for linha in titulo_etapa.split('\\n'):
            svg_lines.append(f'<text x="{txt_x}" y="{txt_y}" font-size="10.5" font-weight="800" fill="{COR_TEXTO}">{linha}</text>')
            txt_y += 12
        
        # Descrição
        svg_lines.append(f'<text font-size="9" fill="#2b2b2b">')
        desc_y = ESPACO_ETAPAS + 72
        for linha in descricao.split('\\n'):
            if linha.strip():
                svg_lines.append(f'<tspan x="{x_etapa + 14}" y="{desc_y}">{linha}</tspan>')
                desc_y += 11.5
        svg_lines.append('</text>')
        
        # Separador
        sep_y = ESPACO_ETAPAS + 116
        svg_lines.append(f'<line x1="{x_etapa + 14}" y1="{sep_y}" x2="{x_etapa + largura_caixa - 14}" y2="{sep_y}" stroke="{COR_SEPARADOR}" stroke-width="1"/>')
        
        # Checkbox + prova
        checkbox_y = sep_y + 8
        svg_lines.append(f'<rect x="{x_etapa + 14}" y="{checkbox_y}" width="7" height="9" rx="1" fill="none" stroke="{COR_ESTRUTURA}" stroke-width="1"/>')
        
        prova_y = checkbox_y + 7
        for linha in prova.split('\\n'):
            if linha.strip():
                svg_lines.append(f'<tspan x="{x_etapa + 26}" y="{prova_y}">{linha}</tspan>')
                prova_y += 9.5
        
        # Seta para próxima etapa
        if i < len(etapas) - 1:
            seta_y = ESPACO_ETAPAS + 75
            x_inicio = x_etapa + largura_caixa
            x_fim = x_etapa + largura_caixa + 20
            svg_lines.append(f'<path d="M {x_inicio} {seta_y} L {x_fim} {seta_y}" stroke="{COR_ESTRUTURA}" stroke-width="2"/>')
            svg_lines.append(f'<path d="M {x_fim-6} {seta_y-5} L {x_fim} {seta_y} L {x_fim-6} {seta_y+5}" fill="{COR_ESTRUTURA}"/>')
        
        x_etapa += largura_caixa
    
    # Caixa de ponto central
    if ponto_central:
        caixa_y = ESPACO_ETAPAS + 30 + ALTURA_CAIXA + 6
        svg_lines.append(f'<rect x="{MARGIN_X}" y="{caixa_y}" width="{LARGURA_SVG - 2*MARGIN_X}" height="28" rx="4" fill="{COR_SEPARADOR}"/>')
        svg_lines.append(f'<rect x="{MARGIN_X}" y="{caixa_y}" width="6" height="28" fill="{COR_DESTAQUE}"/>')
        svg_lines.append(f'<text x="{MARGIN_X+18}" y="{caixa_y+18}" font-size="9.7" fill="{COR_TEXTO}"><tspan font-weight="800">Ponto central. </tspan>{ponto_central}</text>')
        
        # Disclaimer
        disc_y = caixa_y + 28 + 15
        svg_lines.append(f'<text x="{MARGIN_X}" y="{disc_y}" font-size="7.3" fill="{COR_ESTRUTURA}">{disclaimer}</text>')
    
    svg_lines.append('</svg>')
    
    # Escrever arquivo
    output = output_path or spec_path.replace('.json', '.svg')
    with open(output, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg_lines))
    
    print(f"✅ Diagrama gerado: {output}")
    return output


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 gerar_cadeia_fluxo.py --spec spec.json [--output diagram.svg]", file=sys.stderr)
        sys.exit(2)
    
    spec_path = None
    output_path = None
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--spec':
            spec_path = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == '--output':
            output_path = sys.argv[i+1]
            i += 2
        else:
            i += 1
    
    if not spec_path:
        print("Erro: --spec é obrigatório", file=sys.stderr)
        sys.exit(2)
    
    gerar_cadeia_unica(spec_path, output_path)
