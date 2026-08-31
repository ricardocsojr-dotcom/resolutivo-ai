#!/usr/bin/env python3
"""
verificar_formatacao.py — QA automático pós-geração para peças RDAA.

Implementa em código o "Checklist de verificação pós-geração" do plano de
melhorias: em vez de converter para PDF e conferir visualmente, este script
inspeciona o XML do .docx gerado e confere estruturalmente cada regra.

Uso:
    python3 verificar_formatacao.py caminho/para/peca.docx

Sai com código 0 se tudo passar, 1 caso contrário (e imprime o que falhou).
"""

import sys
import re
import zipfile
from lxml import etree

# ponytail: mesmo fix de construir_peca.py — sem isso, mensagem com acento sai
# como mojibake quando outro script (qa_gate.py) captura este stdout no Windows.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG_REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
TW2CM = lambda emu: round(int(emu) / 635)  # EMU -> twips, arredondado


def _document_root(docx_path):
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read('word/document.xml')
    return etree.fromstring(xml)


def _footer_roots(docx_path):
    with zipfile.ZipFile(docx_path) as z:
        names = [n for n in z.namelist() if re.match(r'word/footer\d*\.xml$', n)]
        return [etree.fromstring(z.read(n)) for n in names]


def _header_roots(docx_path):
    with zipfile.ZipFile(docx_path) as z:
        names = [n for n in z.namelist() if re.match(r'word/header\d*\.xml$', n)]
        return [etree.fromstring(z.read(n)) for n in names]


def _body_root(docx_path):
    root = _document_root(docx_path)
    body = root.find('w:body', NS)
    if body is None:
        raise ValueError('word/document.xml sem elemento w:body.')
    return body


def _element_text(element):
    return ''.join(t.text or '' for t in element.findall('.//w:t', NS))


def _paragraphs(docx_path):
    root = _document_root(docx_path)
    return root.findall('.//w:body/w:p', NS) + \
        [p for tbl in root.findall('.//w:body/w:tbl', NS) for p in tbl.findall('.//w:p', NS)]


def _tabs(p):
    return p.findall('.//w:pPr/w:tabs/w:tab', NS)


def _ind(p):
    el = p.find('.//w:pPr/w:ind', NS)
    if el is None:
        return {}
    return {k.split('}')[-1]: v for k, v in el.attrib.items()}


def _spacing(p):
    el = p.find('.//w:pPr/w:spacing', NS)
    if el is None:
        return {}
    return {k.split('}')[-1]: v for k, v in el.attrib.items()}


def _border_bottom(p):
    return p.find('.//w:pPr/w:pBdr/w:bottom', NS)


def _border_top(p):
    return p.find('.//w:pPr/w:pBdr/w:top', NS)


def _has_border(p):
    return p.find('.//w:pPr/w:pBdr', NS) is not None


def _is_titulo_border(p):
    """Título (I./II./III.) tem SÓ borda inferior. A caixa de
    Processo/Partes tem borda nos 4 lados — não deve ser contada como
    título aqui, mesmo tendo w:bottom também."""
    return _border_bottom(p) is not None and _border_top(p) is None


def _paragraph_style_name(p):
    style = p.find('./w:pPr/w:pStyle', NS)
    if style is None:
        return None
    value = style.get(f'{{{NS["w"]}}}val')
    return value.replace('_', '').replace(' ', '').casefold() if value else None


def _is_true_toggle(el):
    """OOXML boolean toggle: elemento presente sem @val (ou @val não em
    0/false/none) = ligado. @val='0'/'false'/'none' = desligado."""
    if el is None:
        return False
    val = el.get(f'{{{NS["w"]}}}val')
    return val not in ('0', 'false', 'none')


def _runs_text_bold_underline(p):
    out = []
    for r in p.findall('w:r', NS):
        t = ''.join(t.text or '' for t in r.findall('w:t', NS))
        rpr = r.find('w:rPr', NS)
        bold = rpr is not None and _is_true_toggle(rpr.find('w:b', NS))
        underline = rpr is not None and _is_true_toggle(rpr.find('w:u', NS))
        out.append((t, bold, underline))
    return out


def _numbering_defs(docx_path):
    """Lê word/numbering.xml e retorna {numId: {numFmt, lvlText, left, hanging, tab}}."""
    with zipfile.ZipFile(docx_path) as z:
        if 'word/numbering.xml' not in z.namelist():
            return {}
        xml = z.read('word/numbering.xml')
    root = etree.fromstring(xml)

    abstract_map = {}
    for abstract in root.findall('w:abstractNum', NS):
        abs_id = abstract.get(f'{{{NS["w"]}}}abstractNumId')
        for lvl in abstract.findall('w:lvl', NS):
            if lvl.get(f'{{{NS["w"]}}}ilvl') == '0':
                fmt_el = lvl.find('w:numFmt', NS)
                txt_el = lvl.find('w:lvlText', NS)
                jc_el = lvl.find('w:lvlJc', NS)
                pPr = lvl.find('w:pPr', NS)
                ind_el = pPr.find('w:ind', NS) if pPr is not None else None
                tab_el = pPr.find('.//w:tab', NS) if pPr is not None else None
                abstract_map[abs_id] = {
                    'numFmt': fmt_el.get(f'{{{NS["w"]}}}val') if fmt_el is not None else None,
                    'lvlText': txt_el.get(f'{{{NS["w"]}}}val') if txt_el is not None else None,
                    'jc': jc_el.get(f'{{{NS["w"]}}}val') if jc_el is not None else None,
                    'left': ind_el.get(f'{{{NS["w"]}}}left') if ind_el is not None else None,
                    'hanging': ind_el.get(f'{{{NS["w"]}}}hanging') if ind_el is not None else None,
                    'tab': tab_el.get(f'{{{NS["w"]}}}pos') if tab_el is not None else None,
                }
                break

    num_map = {}
    for num in root.findall('w:num', NS):
        num_id = num.get(f'{{{NS["w"]}}}numId')
        abs_ref = num.find('w:abstractNumId', NS)
        if abs_ref is not None:
            abs_id = abs_ref.get(f'{{{NS["w"]}}}val')
            if abs_id in abstract_map:
                num_map[num_id] = abstract_map[abs_id]

    return num_map


def _para_num_id(p):
    """Retorna o numId do parágrafo ou None se não tiver numeração nativa."""
    numPr = p.find('w:pPr/w:numPr', NS)
    if numPr is None:
        return None
    numId_el = numPr.find('w:numId', NS)
    return numId_el.get(f'{{{NS["w"]}}}val') if numId_el is not None else None


def checar(docx_path):
    problemas = []
    paragrafos = _paragraphs(docx_path)
    textos = [''.join(t.text or '' for t in p.findall('.//w:t', NS)) for p in paragrafos]

    # Definições de numeração nativa (Fase 1)
    num_defs = _numbering_defs(docx_path)

    # Abertura: parágrafo com nome da parte em negrito+sublinhado, sem
    # borda, recuo de 1ª linha em 2cm — distingue da caixa Processo/partes
    # (tem borda) e do título (tem borda + recuo deslocado, não firstLine).
    # Decisão de 2026-08: negrito+sublinhado no nome da parte é a UNICA
    # excecao a vedacao geral de sublinhado (praxe forense de abertura).
    aberturas = [p for p in paragrafos if len(_runs_text_bold_underline(p)) >= 2
                 and _runs_text_bold_underline(p)[0][1] and _runs_text_bold_underline(p)[0][2]
                 and not _has_border(p)
                 and _ind(p).get('firstLine') == '1134']
    if not aberturas:
        problemas.append("Item 1: nenhum parágrafo de abertura com nome da parte em negrito+sublinhado encontrado.")

    # 1a. O corpo não deve começar com um parágrafo vazio antes do
    # endereçamento. O respiro institucional fica no cabeçalho.
    body = _body_root(docx_path)
    body_paras = body.findall('w:p', NS)
    if body_paras:
        first_nonempty = next((i for i, p in enumerate(body_paras)
                               if _element_text(p).strip()), None)
        if first_nonempty is not None and any(not _element_text(p).strip()
                                              for p in body_paras[:first_nonempty]):
            problemas.append("Item 1a: corpo iniciado com parágrafo vazio antes do endereçamento.")

    # 1b. O cabeçalho deve conter a logo e um parágrafo de respiro depois
    # dela. Sem o respiro, o texto do corpo pode ficar visualmente sufocado.
    headers = _header_roots(docx_path)
    if not headers:
        problemas.append("Item 1b: nenhum cabeçalho encontrado.")
    else:
        for header in headers:
            header_paras = header.findall('.//w:p', NS)
            if len(header_paras) < 2 or _element_text(header_paras[1]).strip():
                problemas.append("Item 1b: cabeçalho sem parágrafo de respiro após a logo.")

    # 1. Manual §2.9 / decisão 2026-08: destaque de elementos do texto é
    #    negrito, exceto o nome da parte na abertura (negrito+sublinhado,
    #    ver acima) — sublinhado em qualquer outro lugar continua proibido.
    runs_sublinhados = 0
    for p in paragrafos:
        runs = _runs_text_bold_underline(p)
        primeiro = runs[0] if (p in aberturas and runs) else None
        for run_info in runs:
            t, bold, underline = run_info
            if run_info is primeiro:
                continue  # nome da parte na abertura: sublinhado esperado
            if underline and t.strip():
                runs_sublinhados += 1
    if runs_sublinhados:
        problemas.append(f"Item 1: sublinhado proibido (Manual §2.9) encontrado em {runs_sublinhados} run(s) fora da abertura.")
    for p in aberturas:
        runs = _runs_text_bold_underline(p)
        if len(runs) >= 3:
            t3, bold3, _u3 = runs[2]
            if t3.strip() and (not bold3 or t3 != t3.upper()):
                problemas.append(f"Item 1: nome_peca {t3[:30]!r} deveria estar em negrito e CAIXA ALTA.")

    # 2. Títulos: numeração nativa (upperRoman) + borda inferior, spacing 0/0
    #    Detecção primária: numPr com numFmt=upperRoman
    #    Fallback: borda inferior sem borda superior (docs legados)
    titulos_nativo = [p for p in paragrafos
                      if _para_num_id(p) and _para_num_id(p) in num_defs
                      and num_defs[_para_num_id(p)]['numFmt'] == 'upperRoman']
    titulos_legado = [p for p in paragrafos
                      if _is_titulo_border(p) and _para_num_id(p) is None]
    titulos = titulos_nativo + titulos_legado
    titulos_para_caracteres = list(titulos)
    for p in paragrafos:
        if _paragraph_style_name(p) in {'rdaatítulo2', 'rdaatítulo3', 'rdaatítulorazões'} and p not in titulos_para_caracteres:
            titulos_para_caracteres.append(p)
    if not titulos:
        problemas.append("Item 2: nenhum título encontrado (nem por numPr/upperRoman nem por borda).")
    for p in titulos:
        idx = paragrafos.index(p)
        num_id = _para_num_id(p)
        if num_id and num_id in num_defs:
            # Verificar geometria do nível de numeração
            info = num_defs[num_id]
            if info['left'] != '1134' or info['hanging'] != '1134':
                problemas.append(f"Item 2: título {textos[idx][:30]!r} com geometria de numeração "
                                  f"left={info['left']}/hanging={info['hanging']}, esperado 1134/1134.")
            if info['tab'] != '1134':
                problemas.append(f"Item 2: título {textos[idx][:30]!r} com tab de numeração em {info['tab']}, esperado 1134.")
        else:
            # Fallback legado: checar tabStop e indent no parágrafo
            tabs = _tabs(p)
            positions = [t.get(f'{{{NS["w"]}}}pos') for t in tabs]
            if '1134' not in positions:
                problemas.append(f"Item 2: título {textos[idx][:30]!r} sem tabStop em 1134 (2cm).")
            ind = _ind(p)
            if ind.get('left') != '1134' or ind.get('hanging') != '1134':
                problemas.append(f"Item 2: título {textos[idx][:30]!r} sem recuo deslocado left=1134/hanging=1134: {ind}")
        sp = _spacing(p)
        if sp.get('before') != '0' or sp.get('after') != '0':
            problemas.append(f"Item 2: título {textos[idx][:30]!r} com spacing != 0/0: {sp}")
        border = _border_bottom(p)
        sz_val = border.get(f'{{{NS["w"]}}}sz') if border is not None else None
        if sz_val != '4':
            problemas.append(f"Item 2: título {textos[idx][:30]!r} com borda sz={sz_val}, esperado 4 (0,5pt).")
        titulo_texto = textos[idx].strip()
        if re.match(r'^[IVXLC]+\.\s*(DA|DO|DE|DOS|DAS)\b', titulo_texto, re.IGNORECASE):
            problemas.append(f"Item 2: título {titulo_texto[:40]!r} começa com Da/Do/De — evitar sempre (redacao-rdaa.md).")

    for p in titulos_para_caracteres:
        idx = paragrafos.index(p)
        titulo_texto = textos[idx].strip()
        if ':' in titulo_texto:
            problemas.append(f"Item 2: título {titulo_texto[:60]!r} contém dois-pontos proibido.")
        if '—' in titulo_texto or '–' in titulo_texto:
            problemas.append(f"Item 2: título {titulo_texto[:60]!r} contém travessão proibido.")

    # 2b. Endereçamento: 1º parágrafo de texto do corpo (sem borda), entrelinha
    #     SIMPLES (Apontamentos 2026-07: estava em 1,5), seguido de 2
    #     parágrafos vazios (estava só 1).
    primeiro_texto = next((p for p in paragrafos if textos[paragrafos.index(p)].strip()), None)
    if primeiro_texto is not None and not _has_border(primeiro_texto):
        sp = _spacing(primeiro_texto)
        if sp.get('line') != '240':
            problemas.append("Item 2b: endereçamento sem entrelinha simples (line=240) — Apontamentos 2026-07.")
        idx_end = paragrafos.index(primeiro_texto)
        n_blank = 0
        j = idx_end + 1
        while j < len(textos) and textos[j].strip() == '':
            n_blank += 1
            j += 1
        if n_blank < 2:
            problemas.append(f"Item 2b: endereçamento seguido de {n_blank} parágrafo(s) vazio(s), esperado 2.")

    # 3b. Quadro Processo/partes (borda nos 4 lados) seguido de 2 parágrafos
    #     vazios (estava só 1) — Apontamentos 2026-07.
    # Forma masculina e feminina de cada polo — parte requerida/autora
    # frequentemente é pessoa jurídica ou física de nome feminino, e
    # "Autor "/"Réu " não casam com "Autora "/"Ré " por substring.
    KEYWORDS_CAIXA = (
        'Processo:', 'Processo ', 'Autor:', 'Autor ', 'Autora:', 'Autora ',
        'Réu:', 'Réu ', 'Reu:', 'Reu ', 'Ré:', 'Ré ', 'Re:', 'Re ',
        'Parte ',
        'Requerente:', 'Requerente ', 'Requerido:', 'Requerido ', 'Requerida:', 'Requerida ',
        'Embargante:', 'Embargante ', 'Embargado:', 'Embargado ', 'Embargada:', 'Embargada ',
        'Agravante:', 'Agravante ', 'Agravado:', 'Agravado ', 'Agravada:', 'Agravada ',
        'Apelante:', 'Apelante ', 'Apelado:', 'Apelado ', 'Apelada:', 'Apelada ',
        'Exequente:', 'Exequente ', 'Executado:', 'Executado ', 'Executada:', 'Executada ',
        'Impetrante:', 'Impetrante ', 'Impetrado:', 'Impetrado ', 'Impetrada:', 'Impetrada ',
        'Exeqte:', 'Exeqte ', 'Execdo:', 'Execdo ', 'Execda:', 'Execda '
    )
    caixa_processo = [p for p in paragrafos if _border_top(p) is not None
                      and (any(k.lower() in textos[paragrafos.index(p)].lower() for k in KEYWORDS_CAIXA)
                           or (':' in textos[paragrafos.index(p)] and len(textos[paragrafos.index(p)]) < 80))]
    if caixa_processo:
        idx_caixa = paragrafos.index(caixa_processo[-1])
        n_blank = 0
        j = idx_caixa + 1
        while j < len(textos) and textos[j].strip() == '':
            n_blank += 1
            j += 1
        if n_blank < 2:
            problemas.append(f"Item 3b: quadro (Processo/partes) seguido de {n_blank} parágrafo(s) vazio(s), esperado 2.")

    # 3. Parágrafos numerados: numeração nativa (decimal + ".") ou regex legado (exclui lista de documentos)
    numerados_nativo = [p for p in paragrafos
                        if _para_num_id(p) and _para_num_id(p) in num_defs
                        and num_defs[_para_num_id(p)]['numFmt'] == 'decimal'
                        and num_defs[_para_num_id(p)].get('jc') != 'center'
                        and num_defs[_para_num_id(p)].get('lvlText') == '%1.'
                        and not _is_titulo_border(p) and p not in titulos]
    numerados_legado = [p for p in paragrafos
                        if re.match(r'^\d+\.\s', textos[paragrafos.index(p)])
                        and _border_bottom(p) is None
                        and p not in numerados_nativo]
    numerados = numerados_nativo + numerados_legado
    for p in numerados:
        idx = paragrafos.index(p)
        num_id = _para_num_id(p)
        if num_id and num_id in num_defs:
            info = num_defs[num_id]
            left_val = info.get('left', '0') or '0'
            if left_val not in ('0', None) or info.get('tab') != '1134':
                problemas.append(f"Item 3: numerado {textos[idx][:30]!r} com geometria de numeração "
                                  f"left={left_val}/tab={info.get('tab')}, esperado left=0/tab=1134.")
        else:
            tabs = _tabs(p)
            positions = [t.get(f'{{{NS["w"]}}}pos') for t in tabs]
            if '1134' not in positions:
                problemas.append(f"Item 3: parágrafo numerado {textos[idx][:30]!r} sem tabStop em 1134.")
            ind = _ind(p)
            if ind.get('left') != '0' or ind.get('firstLine') != '0':
                problemas.append(f"Item 3/6-bis: parágrafo numerado {textos[idx][:30]!r} com indent != 0/0: {ind}")
        # próximo parágrafo deve ser vazio
        if idx + 1 < len(textos) and textos[idx + 1].strip() != '':
            problemas.append(f"Item 3: parágrafo numerado {textos[idx][:30]!r} não é seguido de parágrafo vazio.")

    # 4. Alíneas: numeração nativa (lowerLetter + ")") ou regex legado (exclui titulo3 que usa "%1.")
    alineas_nativo = [p for p in paragrafos
                      if _para_num_id(p) and _para_num_id(p) in num_defs
                      and num_defs[_para_num_id(p)]['numFmt'] == 'lowerLetter'
                      and num_defs[_para_num_id(p)].get('lvlText') in ('%1)', '%2)')
                      and p not in titulos]
    alineas_legado = [p for p in paragrafos
                      if re.match(r'^[a-z]\)\s', textos[paragrafos.index(p)])
                      and p not in alineas_nativo]
    alineas = alineas_nativo + alineas_legado
    for p in alineas:
        idx = paragrafos.index(p)
        num_id = _para_num_id(p)
        if num_id and num_id in num_defs:
            info = num_defs[num_id]
            # Suporta nível 0 (1701/567) e nível 1 (2268/567)
            if (info['left'], info['hanging']) not in [('1701', '567'), ('2268', '567')]:
                problemas.append(f"Item 4: alínea {textos[idx][:30]!r} com geometria de numeração "
                                  f"left={info['left']}/hanging={info['hanging']}, esperado 1701/567 ou 2268/567.")
        else:
            ind = _ind(p)
            if ind.get('left') != '1701':
                problemas.append(f"Item 4: alínea {textos[idx][:30]!r} com left != 1701: {ind}")
            if ind.get('hanging') != '567' and ind.get('firstLine') != '-567':
                problemas.append(f"Item 4: alínea {textos[idx][:30]!r} sem hanging de 567 (1cm): {ind}")
            tabs = _tabs(p)
            positions = [t.get(f'{{{NS["w"]}}}pos') for t in tabs]
            if '1701' not in positions:
                problemas.append(f"Item 4: alínea {textos[idx][:30]!r} sem tabStop em 1701 (3cm).")

    # 5. Citações: left=1134, entrelinha simples (line=240), spacing 0/0
    # Exclui títulos: mesmo left=1134 (recuo de 2cm), mas têm borda inferior
    # — citação de bloco nunca tem borda. Sem esse filtro, título e citação
    # colidiam nesta detecção (bug pré-existente que passava despercebido
    # porque as checagens antigas de entrelinha/spacing batiam nos dois).
    citacoes = [p for p in paragrafos if _ind(p).get('left') == '1134' and not _has_border(p)]
    # Citações são opcionais: se não houver no documento, nada a checar.
    for p in citacoes:
        idx = paragrafos.index(p)
        sp = _spacing(p)
        if sp.get('line') != '240':
            problemas.append(f"Item 5: citação {textos[idx][:30]!r} sem entrelinha simples (line=240): {sp}")
        if sp.get('after') != '0' or sp.get('before') != '0':
            problemas.append(f"Item 5: citação {textos[idx][:30]!r} com spacing != 0/0: {sp}")
        # Correções.md: citação deve ser Tahoma 9pt (sz=18 em meio-pontos),
        # não o 10,5pt padrão do corpo — bug real que passou despercebido
        # porque não havia checagem de tamanho de fonte neste item.
        for r in p.findall('.//w:r', NS):
            rpr = r.find('w:rPr', NS)
            sz = rpr.find('w:sz', NS) if rpr is not None else None
            sz_val = sz.get(f'{{{NS["w"]}}}val') if sz is not None else None
            if sz_val != '18':
                problemas.append(f"Item 5: citação {textos[idx][:30]!r} com fonte {sz_val} (meio-pontos), esperado 18 (9pt).")

    # 6. Regra central: todo parágrafo com tab deve ter tabStop explícito
    #    Parágrafos com numeração nativa não têm tab char no texto (tab vem do w:lvl)
    non_num_com_tab = [i for i, t in enumerate(textos)
                       if '\t' in t and _para_num_id(paragrafos[i]) is None]
    sem_tabstop = [i for i in non_num_com_tab if not _tabs(paragrafos[i])]
    if sem_tabstop:
        problemas.append(f"Item 6: {len(sem_tabstop)} parágrafo(s) usam '\\t' sem tabStop "
                          f"explícito (vão cair no intervalo padrão do Word, ~1,25cm).")

    # 6b. Regressão: nenhum parágrafo sem numPr pode ter texto começando com
    #     padrão de numeral digitado — detecta a causa raiz do bug "10." duplicado.
    for i, t in enumerate(textos):
        if _para_num_id(paragrafos[i]) is not None:
            continue
        if _has_border(paragrafos[i]):
            continue  # Caixa de Processo/partes pode ter números
        txt = t.strip()
        if re.match(r'^[IVX]+\.\s', txt) or re.match(r'^\d+\.\s', txt) or re.match(r'^[a-z]\)\s', txt):
            problemas.append(f"Item 6b: parágrafo {txt[:40]!r} tem numeral digitado sem numeração "
                              f"nativa (w:numPr) — provável bug de numeração manual.")

    # 7a. Tabela de assinaturas: grade 2x2 sem bordas, 4 signatários fixos
    #      (Wanderley/Flávia/Alessandra/Ricardo Cesar — confirmado contra
    #      peça real assinada em 2026-07-19), largura de página útil dividida
    #      em 2 colunas (9638/2 = 4819 twips cada).
    # Correções.md, item 12: a peça pode ter outras tabelas no corpo (quadros
    # de metadados, cronologia, comparativos) e recursos compostos podem ter
    # duas tabelas de assinatura (interposição + razões). O validador não
    # pode mais presumir "a primeira tabela do documento" — identifica a(s)
    # tabela(s) de assinatura pelo conteúdo (nomes dos signatários).
    root = _document_root(docx_path)
    tabelas = root.findall('.//w:body/w:tbl', NS)
    tabelas_assinatura = []
    for t in tabelas:
        nomes_t = [''.join(x.text or '' for x in r.findall('.//w:t', NS)) for r in t.findall('.//w:tr', NS)]
        if any(nome in n for n in nomes_t for nome in ('Wanderley', 'Flávia', 'Alessandra', 'Ricardo Cesar')):
            tabelas_assinatura.append(t)

    if not tabelas_assinatura:
        problemas.append("Item 7: nenhuma tabela de assinaturas encontrada (assinatura deve ser Table, não parágrafos soltos).")
    for tbl in tabelas_assinatura:
        grid = tbl.find('w:tblGrid', NS)
        cols = grid.findall('w:gridCol', NS) if grid is not None else []
        if len(cols) != 2:
            problemas.append(f"Item 7: tabela de assinaturas com {len(cols)} coluna(s), esperado 2.")
        largura = cols[0].get(f'{{{NS["w"]}}}w') if cols else None
        if largura != '4819':
            problemas.append(f"Item 7: largura da coluna da tabela de assinaturas é {largura}, esperado 4819 (metade da largura útil A4 com margem 2cm).")
        linhas_tbl = tbl.findall('w:tr', NS)
        if len(linhas_tbl) != 2:
            problemas.append(f"Item 7: tabela de assinaturas com {len(linhas_tbl)} linha(s), esperado 2 (grade 2x2).")
        tblPr = tbl.find('w:tblPr', NS)
        borders = tblPr.find('w:tblBorders', NS) if tblPr is not None else None
        # Ausencia de w:tblBorders NAO e erro: sem o elemento, a tabela usa o
        # estilo padrao "Table Normal" do Word, que ja e sem borda. So e erro
        # se o elemento existe e algum lado foi setado para algo != 'none'
        # (bug real corrigido em 2026-08: o check antigo tratava ausencia
        # como falha, dando falso positivo em toda peca gerada corretamente).
        if borders is not None and any(b.get(f'{{{NS["w"]}}}val') != 'none' for b in borders):
            problemas.append("Item 7: tabela de assinaturas com borda explícita != 'none'.")

        # Margem interna é requisito visual do padrão RDAA. A ausência do
        # elemento fazia a mutação de regressão passar silenciosamente, pois
        # o Word aplicava a margem padrão sem que o QA percebesse.
        mar = tblPr.find('w:tblCellMar', NS) if tblPr is not None else None
        esperadas = {'top': '57', 'bottom': '170', 'left': '113', 'right': '113'}
        if mar is None:
            problemas.append("Item 7: tabela de assinaturas sem margem interna explícita (tblCellMar).")
        else:
            for side, expected in esperadas.items():
                el = mar.find(f'w:{side}', NS)
                actual = el.get(f'{{{NS["w"]}}}w') if el is not None else None
                if actual != expected:
                    problemas.append(f"Item 7: margem interna {side}={actual}, esperada {expected} twips.")

        nomes_tabela = [''.join(x.text or '' for x in r.findall('.//w:t', NS)) for r in tbl.findall('.//w:tr', NS)]
        for nome_esperado in ('Wanderley', 'Flávia', 'Alessandra', 'Ricardo Cesar'):
            if not any(nome_esperado in n for n in nomes_tabela):
                problemas.append(f"Item 7: signatário {nome_esperado!r} não encontrado na tabela de assinaturas.")
        if not any('Assinado Eletronicamente' in n for n in nomes_tabela):
            problemas.append("Item 7: linha '(Assinado Eletronicamente)' não encontrada sob o primeiro signatário.")

    # 7a-bis. Somente a tabela de assinaturas final deve aparecer depois do
    # fecho/data. Em recurso composto, tabelas anteriores podem existir antes
    # de "inicio_razoes"; por isso a checagem é feita apenas na última tabela.
    # Recalcula as tabelas a partir da MESMA árvore `body` usada na busca de
    # posição. Comparar elementos vindos de duas chamadas separadas de
    # _document_root() falha por identidade de objeto e deixava a mutação de
    # ordem passar silenciosamente.
    tabelas_assinatura_no_body = []
    for child in body:
        if etree.QName(child).localname != 'tbl':
            continue
        nomes = [''.join(x.text or '' for x in r.findall('.//w:t', NS))
                 for r in child.findall('.//w:tr', NS)]
        if any(nome in n for n in nomes for nome in ('Wanderley', 'Flávia', 'Alessandra', 'Ricardo Cesar')):
            tabelas_assinatura_no_body.append(child)

    if tabelas_assinatura_no_body:
        ultima_assinatura = tabelas_assinatura_no_body[-1]
        body_children = list(body)
        idx_assinatura = body_children.index(ultima_assinatura)
        anteriores = [_element_text(el).strip() for el in body_children[:idx_assinatura]
                      if etree.QName(el).localname == 'p']
        if not any(re.search(r'(nestes termos|aguarda deferimento|pede deferimento|requer deferimento)',
                             texto, re.IGNORECASE) for texto in anteriores):
            problemas.append("Item 7a: tabela de assinaturas final não está precedida por fecho com deferimento.")

    # 7b. Numeração de página no rodapé (campos PAGE / NUMPAGES)
    footers = _footer_roots(docx_path)
    if not footers:
        problemas.append("Item 7: nenhum rodapé encontrado no documento.")
    else:
        instr_codes = [i.text.strip() for f in footers for i in f.findall('.//w:instrText', NS)]
        if 'PAGE' not in instr_codes:
            problemas.append("Item 7: campo de página 'PAGE' não encontrado no rodapé.")
        if 'NUMPAGES' not in instr_codes:
            problemas.append("Item 7: campo de total de páginas 'NUMPAGES' não encontrado no rodapé.")

    # 7c. Parágrafos vazios sem spacing.before/after extra (só a altura da
    #      linha vazia, nunca espaçamento somado)
    blanks_com_spacing_extra = 0
    for p in paragrafos:
        idx = paragrafos.index(p)
        if textos[idx].strip():
            continue
        sp = _spacing(p)
        if sp.get('after') not in ('0', None) or sp.get('before') not in ('0', None):
            blanks_com_spacing_extra += 1
    if blanks_com_spacing_extra:
        problemas.append(f"Item 7: {blanks_com_spacing_extra} parágrafo(s) vazio(s) com spacing.before/after != 0 "
                          f"(o espaço deve vir só da altura da linha vazia, não de espaçamento somado).")

    # 7d. Fonte/cor da linha do site no rodapé. Confirmado com o escritório
    #      (17/07/2026): 7pt (sz=14 em meio-pontos) e dourado FFC000 —
    #      diferente do resto do rodapé, que continua em 8pt/preto.
    #      Correções.md: domínio deve ser exatamente minúsculo
    #      "romanodonadel.com.br" — maiúsculo é erro, não só variação de caixa.
    for f in footers:
        for p in f.findall('.//w:p', NS):
            txt = ''.join(x.text or '' for x in p.findall('.//w:t', NS)).strip()
            if txt.lower() == 'romanodonadel.com.br':
                if txt != 'romanodonadel.com.br':
                    problemas.append(f"Item 7: domínio do rodapé {txt!r} contém letra maiúscula, esperado 'romanodonadel.com.br'.")
                for r in p.findall('.//w:r', NS):
                    rpr = r.find('w:rPr', NS)
                    sz = rpr.find('w:sz', NS) if rpr is not None else None
                    color = rpr.find('w:color', NS) if rpr is not None else None
                    sz_val = sz.get(f'{{{NS["w"]}}}val') if sz is not None else None
                    color_val = color.get(f'{{{NS["w"]}}}val') if color is not None else None
                    if sz_val != '14':
                        problemas.append(f"Item 7: rodapé 'romanodonadel.com.br' com tamanho {sz_val} (meio-pontos), esperado 14 (7pt).")
                    if color_val != 'FFC000':
                        problemas.append(f"Item 7: rodapé 'romanodonadel.com.br' com cor {color_val}, esperado FFC000 (dourado).")

    # 7e. Linha superior do rodapé e paginação à direita (Apontamentos
    #      2026-07: rodapé sem linha separando do corpo, e paginação
    #      centralizada). Endereço em title-case, não caixa alta.
    for f in footers:
        paras_f = f.findall('.//w:p', NS)
        if not paras_f:
            continue
        p1 = paras_f[0]
        if _border_top(p1) is None:
            problemas.append("Item 7: 1ª linha do rodapé sem borda superior separando do corpo.")
        txt1 = ''.join(x.text or '' for x in p1.findall('.//w:t', NS)).strip()
        if txt1 and txt1 == txt1.upper() and txt1 != txt1.lower():
            problemas.append(f"Item 7: endereço do rodapé em CAIXA ALTA {txt1[:40]!r}, esperado title-case.")
        for p in paras_f:
            instr = [i.text.strip() for i in p.findall('.//w:instrText', NS) if i.text]
            if 'PAGE' in instr:
                jc = p.find('.//w:pPr/w:jc', NS)
                jc_val = jc.get(f'{{{NS["w"]}}}val') if jc is not None else None
                if jc_val != 'right':
                    problemas.append(f"Item 7: paginação do rodapé alinhada em {jc_val!r}, esperado 'right'.")

    # 7f. E-mails da tabela de assinaturas devem ser hyperlinks mailto,
    #      azuis (#0563C1) e sublinhados. A regra é delimitada à tabela de
    #      assinaturas para não reinterpretar texto jurídico ou boilerplate
    #      fora desse bloco.
    with zipfile.ZipFile(docx_path) as z:
        rels_root = etree.fromstring(z.read('word/_rels/document.xml.rels'))
    relationship_targets = {
        rel.get('Id'): rel.get('Target')
        for rel in rels_root.findall(f'{{{PKG_REL_NS}}}Relationship')
    }
    emails_com_formato_invalido = 0
    for tbl in tabelas_assinatura:
        for p in tbl.findall('.//w:p', NS):
            for r in p.findall('.//w:r', NS):
                t = ''.join(x.text or '' for x in r.findall('w:t', NS))
                if '@' not in t:
                    continue
                hyperlink = r.getparent()
                is_hyperlink = hyperlink is not None and etree.QName(hyperlink).localname == 'hyperlink'
                rid = hyperlink.get(f'{{{R_NS}}}id') if is_hyperlink else None
                target = relationship_targets.get(rid)
                rpr = r.find('w:rPr', NS)
                underline = rpr is not None and _is_true_toggle(rpr.find('w:u', NS))
                color_el = rpr.find('w:color', NS) if rpr is not None else None
                color_val = color_el.get(f'{{{NS["w"]}}}val') if color_el is not None else None
                if (not is_hyperlink or not target or not target.lower().startswith('mailto:')
                        or color_val is None or color_val.upper() != '0563C1'
                        or not underline):
                    emails_com_formato_invalido += 1
    if emails_com_formato_invalido:
        problemas.append(f"Item 7: {emails_com_formato_invalido} e-mail(s) da tabela de assinaturas "
                         "sem hyperlink mailto azul (#0563C1) e sublinhado.")

    return problemas


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 verificar_formatacao.py caminho/para/peca.docx", file=sys.stderr)
        sys.exit(2)

    docx_path = sys.argv[1]
    problemas = checar(docx_path)

    if problemas:
        print(f"[ERRO] {len(problemas)} problema(s) de formatacao encontrado(s) em {docx_path}:")
        for p in problemas:
            print(f"  - {p}")
        sys.exit(1)
    else:
        print(f"[OK] Todos os itens do checklist RDAA passaram em {docx_path}")
        sys.exit(0)


if __name__ == '__main__':
    main()
