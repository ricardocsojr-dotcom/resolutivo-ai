import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Core Tokens
COLOR_BG = RGBColor(255, 255, 255)
COLOR_TEXT_PRIMARY = RGBColor(0, 0, 0)
COLOR_STRUCTURE = RGBColor(99, 102, 106) # #63666A
COLOR_ACCENT = RGBColor(247, 168, 0)      # #F7A800
COLOR_CARD_BG = RGBColor(248, 249, 250)
COLOR_CARD_BORDER = RGBColor(220, 224, 230)
COLOR_LIGHT_ACCENT = RGBColor(254, 248, 235)

FONT_FAMILY = "Arial" # Fallback since Lato is not in Windows Fonts

LOGO_PATH = "C:/Projetos/resolutivo-ai/skills/romano-donadel-slide-style/assets/logo_romano_donadel.png"
OUTPUT_PPTX = "C:/Projetos/resolutivo-ai/Apresentacao_Caso_Silvio_Afonso_Romano_Donadel.pptx"

prs = Presentation()
prs.slide_width = Emu(12192000) # 16:9 widescreen
prs.slide_height = Emu(6858000)
blank_layout = prs.slide_layouts[6] # completely blank layout

def add_header(slide, title_text, category_text=""):
    # Header Accent line
    rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(594360), Emu(450000), Emu(60000), Emu(420000))
    rule.fill.solid()
    rule.fill.fore_color.rgb = COLOR_ACCENT
    rule.line.color.rgb = COLOR_ACCENT
    
    # Title Box
    title_box = slide.shapes.add_textbox(Emu(750000), Emu(380000), Emu(9500000), Emu(600000))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    if category_text:
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = FONT_FAMILY
        p_cat.font.size = Pt(9.5)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_ACCENT
        p_title = tf.add_paragraph()
    else:
        p_title = tf.paragraphs[0]
        
    p_title.text = title_text.upper()
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(17)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_PRIMARY
    
    # Logo top-right
    if os.path.exists(LOGO_PATH):
        slide.shapes.add_picture(LOGO_PATH, Emu(10400000), Emu(300000), width=Emu(1250000))

def add_footer(slide, page_num, total_pages=7):
    # Divider line
    div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(594360), Emu(6420000), Emu(11000000), Emu(10000))
    div.fill.solid()
    div.fill.fore_color.rgb = COLOR_CARD_BORDER
    div.line.color.rgb = COLOR_CARD_BORDER
    
    # Left info
    tb_left = slide.shapes.add_textbox(Emu(594360), Emu(6460000), Emu(4500000), Emu(250000))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = False
    tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0
    p_l = tf_l.paragraphs[0]
    p_l.text = "CONFIDENCIAL | ROMANO DONADEL ADVOGADOS | SETEMBRO 2026"
    p_l.font.name = FONT_FAMILY
    p_l.font.size = Pt(8.5)
    p_l.font.color.rgb = COLOR_STRUCTURE
    
    # Right page
    tb_right = slide.shapes.add_textbox(Emu(10500000), Emu(6460000), Emu(1100000), Emu(250000))
    tf_r = tb_right.text_frame
    tf_r.word_wrap = False
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0
    p_r = tf_r.paragraphs[0]
    p_r.text = f"{page_num:02d} / {total_pages:02d}"
    p_r.alignment = PP_ALIGN.RIGHT
    p_r.font.name = FONT_FAMILY
    p_r.font.size = Pt(8.5)
    p_r.font.bold = True
    p_r.font.color.rgb = COLOR_STRUCTURE

# ==========================================================
# SLIDE 1: CAPA (COVER)
# ==========================================================
slide1 = prs.slides.add_slide(blank_layout)

# Orange vertical accent bar
bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(658368), Emu(1400000), Emu(100000), Emu(3600000))
bar.fill.solid()
bar.fill.fore_color.rgb = COLOR_ACCENT
bar.line.color.rgb = COLOR_ACCENT

# Logo
if os.path.exists(LOGO_PATH):
    slide1.shapes.add_picture(LOGO_PATH, Emu(9800000), Emu(600000), width=Emu(1800000))

# Title & Subtitle Box
tb_cover = slide1.shapes.add_textbox(Emu(980000), Emu(1500000), Emu(9000000), Emu(3400000))
tf_c = tb_cover.text_frame
tf_c.word_wrap = True
tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0

p1 = tf_c.paragraphs[0]
p1.text = "RELATÓRIO ESTRATÉGICO CONTENCIOSO"
p1.font.name = FONT_FAMILY
p1.font.size = Pt(13)
p1.font.bold = True
p1.font.color.rgb = COLOR_ACCENT

p2 = tf_c.add_paragraph()
p2.text = "CASO SÍLVIO LUIZ AFONSO"
p2.font.name = FONT_FAMILY
p2.font.size = Pt(32)
p2.font.bold = True
p2.font.color.rgb = COLOR_TEXT_PRIMARY
p2.space_before = Pt(12)
p2.space_after = Pt(8)

p3 = tf_c.add_paragraph()
p3.text = "Panorama Geral das Frentes Processuais, Gestão de Passivo Tributário e Defesa Patrimonial Ativa"
p3.font.name = FONT_FAMILY
p3.font.size = Pt(15)
p3.font.color.rgb = COLOR_STRUCTURE
p3.space_after = Pt(28)

p4 = tf_c.add_paragraph()
p4.text = "CLIENTE: Sílvio Luiz Afonso  |  ADVERSÁRIA: Ana Lúcia de Oliveira Afonso"
p4.font.name = FONT_FAMILY
p4.font.size = Pt(11)
p4.font.bold = True
p4.font.color.rgb = COLOR_TEXT_PRIMARY
p4.space_after = Pt(4)

p5 = tf_c.add_paragraph()
p5.text = "PATROCÍNIO: Romano Donadel Advogados Associados  |  DATA: Setembro / 2026"
p5.font.name = FONT_FAMILY
p5.font.size = Pt(10)
p5.font.color.rgb = COLOR_STRUCTURE

add_footer(slide1, 1, 7)

# ==========================================================
# SLIDE 2: RESUMO EXECUTIVO (DASHBOARD ESTRATÉGICO)
# ==========================================================
slide2 = prs.slides.add_slide(blank_layout)
add_header(slide2, "Resumo Executivo & Visão Global do Caso", "Governança Processual")
add_footer(slide2, 2, 7)

# 3 Metric Cards
cards_data = [
    ("03 FRENTES INTEGRADAS", "Gestão Coordenada", "Divórcio & Partilha (3ª Família)\nArbitramento de Aluguel (10ª Cível)\nExecução de Alimentos autônoma"),
    ("02 IMÓVEIS CENTRAIS", "Imóveis Objeto", "Rua das Begônias nº 108 (Posse de Ana)\nEd. Sense Vertical Living (Aquisição particular protegida)"),
    ("100% RISCO RECHAÇADO", "Vitórias Estratégicas", "Astreintes de R$ 10 mil afastadas no TJMG\nBloqueio à compensação cruzada\nÔnus primário mantido na reconvinte")
]

card_w = Emu(3450000)
card_h = Emu(2000000)
card_y = Emu(1250000)

for idx, (val, sub, desc) in enumerate(cards_data):
    card_x = Emu(594360 + idx * 3750000)
    
    # Background Box
    bg = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_x, card_y, card_w, card_h)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_CARD_BG
    bg.line.color.rgb = COLOR_CARD_BORDER
    bg.line.width = Pt(1)
    
    # Orange Top line
    tline = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, card_x, card_y, card_w, Emu(50000))
    tline.fill.solid()
    tline.fill.fore_color.rgb = COLOR_ACCENT
    tline.line.color.rgb = COLOR_ACCENT
    
    # Card Text
    tb = slide2.shapes.add_textbox(card_x + Emu(180000), card_y + Emu(140000), card_w - Emu(360000), card_h - Emu(240000))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p = tf.paragraphs[0]
    p.text = val
    p.font.name = FONT_FAMILY
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT
    
    p_sub = tf.add_paragraph()
    p_sub.text = sub.upper()
    p_sub.font.name = FONT_FAMILY
    p_sub.font.size = Pt(9)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_STRUCTURE
    p_sub.space_after = Pt(8)
    
    for line in desc.split("\n"):
        p_desc = tf.add_paragraph()
        p_desc.text = f"• {line}"
        p_desc.font.name = FONT_FAMILY
        p_desc.font.size = Pt(9.5)
        p_desc.font.color.rgb = COLOR_TEXT_PRIMARY
        p_desc.space_after = Pt(3)

# Lower Executive Box
low_y = Emu(3550000)
low_h = Emu(2550000)
low_w = Emu(11000000)

box_low = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(594360), low_y, low_w, low_h)
box_low.fill.solid()
box_low.fill.fore_color.rgb = COLOR_LIGHT_ACCENT
box_low.line.color.rgb = COLOR_ACCENT
box_low.line.width = Pt(1)

tb_low = slide2.shapes.add_textbox(Emu(850000), low_y + Emu(220000), low_w - Emu(500000), low_h - Emu(440000))
tf_l = tb_low.text_frame
tf_l.word_wrap = True

p_lh = tf_l.paragraphs[0]
p_lh.text = "DIRETRIZ ESTRATÉGICA RDAA — SÍNTESE DA POSIÇÃO PATRIMONIAL"
p_lh.font.name = FONT_FAMILY
p_lh.font.size = Pt(12)
p_lh.font.bold = True
p_lh.font.color.rgb = COLOR_ACCENT
p_lh.space_after = Pt(8)

p_body1 = tf_l.add_paragraph()
p_body1.text = "1. Segregação de Demandas: O passivo de IPTU e o protesto lavrado contra Sílvio decorrem do uso exclusivo exercido por Ana Lúcia. O escritório neutralizou com êxito as alegações de 'violência patrimonial' e desfez tentativas de compensação informal com dívidas de alimentos."
p_body1.font.name = FONT_FAMILY
p_body1.font.size = Pt(10)
p_body1.font.color.rgb = COLOR_TEXT_PRIMARY
p_body1.space_after = Pt(6)

p_body2 = tf_l.add_paragraph()
p_body2.text = "2. Indenização pela Fruição Exclusiva: Em sede de arbitramento de aluguéis, a tese fixada pelo RDAA respalda-se no REsp 1.699.013/DF (STJ): o dever indenizatório independe de expulsão física ou esbulho formal, bastando a impossibilidade fática de coabitação e a oposição manifesta."
p_body2.font.name = FONT_FAMILY
p_body2.font.size = Pt(10)
p_body2.font.color.rgb = COLOR_TEXT_PRIMARY
p_body2.space_after = Pt(6)

p_body3 = tf_l.add_paragraph()
p_body3.text = "3. Blindagem na Reconvenção (Ed. Sense): Preservada a exigência de que a reconvinte comprove aquisição na constância e recursos comuns (CPC, art. 373, I), desarmando inversões probatórias precoces contra o patrimônio particular de Sílvio."
p_body3.font.name = FONT_FAMILY
p_body3.font.size = Pt(10)
p_body3.font.color.rgb = COLOR_TEXT_PRIMARY

# ==========================================================
# SLIDE 3: MATRIZ ANALÍTICA DAS FRENTES PROCESSUAIS
# ==========================================================
slide3 = prs.slides.add_slide(blank_layout)
add_header(slide3, "Matriz Comparativa das Ações em Andamento", "Mapa de Litigiosidade")
add_footer(slide3, 3, 7)

# Analytical Table
table_shape = slide3.shapes.add_table(5, 5, Emu(594360), Emu(1250000), Emu(11000000), Emu(4850000))
tbl = table_shape.table

# Set Column Widths
tbl.columns[0].width = Emu(2100000) # Processo
tbl.columns[1].width = Emu(1700000) # Juízo
tbl.columns[2].width = Emu(2400000) # Objeto Controvertido
tbl.columns[3].width = Emu(2400000) # Posição Atual
tbl.columns[4].width = Emu(2400000) # Diretriz RDAA

headers = ["PROCESSO / AÇÃO", "JUÍZO / FÓRUM", "OBJETO DA DEMANDA", "ESTADO ATUAL", "ESTRATÉGIA DE DEFESA"]
for c_idx, text in enumerate(headers):
    cell = tbl.cell(0, c_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_TEXT_PRIMARY
    p = cell.text_frame.paragraphs[0]
    p.text = text
    p.font.name = FONT_FAMILY
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

rows_data = [
    ("Divórcio c/c Partilha\nProc. 5026681-10.2023", "3ª Vara Família\nUberlândia/MG", "Partilha do patrimônio comum e definição de meação.", "Instrução probatória; pendente perícia de bens.", "Segregar acervo particular e exigir prestação de contas de frutos."),
    ("AI /006 (IPTU Begônias)\nProc. 1.0000.23.223786-7", "TJMG — 8ª Câm. Cível Especializada", "Cobrança integral do IPTU e baixa de protesto da Begônias.", "Liminar afastou multa diária; dever de pagar mantido.", "Sustentar enriquecimento sem causa de Ana (TJMG AC 0013168-49)."),
    ("Arbitramento Aluguéis\nProc. 5033450-63.2025", "10ª Vara Cível\nUberlândia/MG", "Indenização pela ocupação exclusiva da casa da Begônias.", "Saneador proferido; manifesto art. 357, §1º protocolado.", "Consolidar termo inicial (citação/separação) e afastar prova de esbulho."),
    ("Reconvenção (Ed. Sense)\nProc. 5033450-63.2025", "10ª Vara Cível\nUberlândia/MG", "Pretensão de Ana sobre imóvel particular de Sílvio.", "Ônus probatório atribuído à reconvinte (art. 373, I).", "Impedir presunção do art. 1.660 CC; exigir prova documental de aporte.")
]

for r_idx, row in enumerate(rows_data):
    for c_idx, val in enumerate(row):
        cell = tbl.cell(r_idx + 1, c_idx)
        cell.fill.solid()
        if r_idx % 2 == 1:
            cell.fill.fore_color.rgb = COLOR_CARD_BG
        else:
            cell.fill.fore_color.rgb = RGBColor(255, 255, 255)
            
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.name = FONT_FAMILY
        p.font.size = Pt(8.5)
        p.font.color.rgb = COLOR_TEXT_PRIMARY
        if c_idx == 0:
            p.font.bold = True

# ==========================================================
# SLIDE 4: FRENTE 1 — IMÓVEL BEGÔNIAS & IPTU (AI /006 TJMG)
# ==========================================================
slide4 = prs.slides.add_slide(blank_layout)
add_header(slide4, "Frente I — Imóvel Begônias, Passivo de IPTU e Protesto", "Agravo de Instrumento nº 1.0000.23.223786-7/006 — TJMG")
add_footer(slide4, 4, 7)

# Left Column: Fatos & Decisão Agravada
box_l = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(594360), Emu(1250000), Emu(5350000), Emu(4850000))
box_l.fill.solid()
box_l.fill.fore_color.rgb = COLOR_CARD_BG
box_l.line.color.rgb = COLOR_CARD_BORDER

tb_fl = slide4.shapes.add_textbox(Emu(780000), Emu(1400000), Emu(4980000), Emu(4500000))
tf_fl = tb_fl.text_frame
tf_fl.word_wrap = True

p = tf_fl.paragraphs[0]
p.text = "DINÂMICA DOS FATOS E DECISÃO DE 1º GRAU"
p.font.name = FONT_FAMILY
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_ACCENT
p.space_after = Pt(10)

facts = [
    ("Ocupação Exclusiva:", "Ana Lúcia permaneceu residindo com exclusividade no imóvel da Rua das Begônias nº 108 desde a separação de fato (13/03/2023)."),
    ("Inadimplência Tributária:", "A ocupante não adimpliu os tributos municipais (IPTU e taxas), culminando em protesto extrajudicial indevido em nome de Sílvio."),
    ("Decisão da 3ª Vara de Família:", "Determinou que a agravante pague integralmente o IPTU, juros e multas, e promova a baixa do protesto em 15 dias, sob pena de multa diária de R$ 200,00 (teto R$ 10 mil)."),
    ("Inconformismo Recursal:", "Ana recorreu alegando que encargos integram a partilha global, alegando vulnerabilidade econômica e sustentando 'violência patrimonial'.")
]

for title, text in facts:
    p_item = tf_fl.add_paragraph()
    p_item.text = f"• {title} {text}"
    p_item.font.name = FONT_FAMILY
    p_item.font.size = Pt(9.5)
    p_item.font.color.rgb = COLOR_TEXT_PRIMARY
    p_item.space_after = Pt(8)

# Right Column: Contraminuta RDAA & Tese Vencedora
box_r = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(6244360), Emu(1250000), Emu(5350000), Emu(4850000))
box_r.fill.solid()
box_r.fill.fore_color.rgb = RGBColor(255, 255, 255)
box_r.line.color.rgb = COLOR_ACCENT
box_r.line.width = Pt(1.5)

tb_fr = slide4.shapes.add_textbox(Emu(6430000), Emu(1400000), Emu(4980000), Emu(4500000))
tf_fr = tb_fr.text_frame
tf_fr.word_wrap = True

p_r1 = tf_fr.paragraphs[0]
p_r1.text = "FUNDAMENTAÇÃO JURÍDICA E DEFESA RDAA"
p_r1.font.name = FONT_FAMILY
p_r1.font.size = Pt(11)
p_r1.font.bold = True
p_r1.font.color.rgb = COLOR_ACCENT
p_r1.space_after = Pt(10)

defenses = [
    ("Encargos da Posse Exclusiva:", "Quem frui com exclusividade deve arcar com as despesas ordinárias e fiscais do bem. Precedente: TJMG, AC 0013168-49.2018.8.13.0148 (Rel. Des. Carlos Roberto de Faria) e STJ, AREsp 2.462.038/SP."),
    ("Rejeição da 'Violência Patrimonial':", "Descabida a invocação da Lei Maria da Penha para se eximir de tributos municipais de imóvel onde reside, notadamente quando Sílvio é a parte com nome protestado."),
    ("Autonomia da Verba Alimentar:", "Inviabilidade de compensação tácita entre alimentos (objeto de execução própria) e débitos reais de IPTU."),
    ("Desfecho no TJMG (Liminar):", "A 8ª Câmara Cível Especializada manteve a obrigação primária de pagamento imposta a Ana, afastando unicamente as astreintes.")
]

for title, text in defenses:
    p_item = tf_fr.add_paragraph()
    p_item.text = f"✔ {title} {text}"
    p_item.font.name = FONT_FAMILY
    p_item.font.size = Pt(9.5)
    p_item.font.color.rgb = COLOR_TEXT_PRIMARY
    p_item.space_after = Pt(8)

# ==========================================================
# SLIDE 5: FRENTE 2 — ARBITRAMENTO DE ALUGUÉIS (10ª VARA CÍVEL)
# ==========================================================
slide5 = prs.slides.add_slide(blank_layout)
add_header(slide5, "Frente II — Arbitramento de Aluguéis & Ajuste do Saneador", "Ação de Cobrança e Arbitramento nº 5033450-63.2025.8.13.0702")
add_footer(slide5, 5, 7)

# 3 Horizontal Cards for Saneador Adjustments
adjustments = [
    ("PONTO 01: FRUIÇÃO EXCLUSIVA X IMPEDIMENTO FÍSICO",
     "Crítica ao Saneador:", "A decisão exigiu que Sílvio provasse posse 'impedindo ou inviabilizando na prática o uso pelo coproprietário'.",
     "Correção Técnica RDAA:", "Não se exige ato material de esbulho ou expulsão física. A animosidade e impossibilidade fática de coabitação conjugal bastam para gerar a indenização.",
     "Base STJ:", "REsp 1.699.013/DF (Rel. Min. Luis Felipe Salomão): O fato gerador é a posse exclusiva combinada com a oposição inequívoca."),
     
    ("PONTO 02: DELIMITAÇÃO DO TERMO INICIAL",
     "Crítica ao Saneador:", "O juízo indicou apenas 'marco temporal da privação', deixando aberta a qualificação jurídica do ato constitutivo em mora.",
     "Correção Técnica RDAA:", "Fixação da data da citação como piso mínimo garantido e incontroverso, sem ônus adicional probatório a Sílvio.",
     "Pretensão Adicional:", "Resguardo do direito de retroagir a indenização a 13/03/2023 (separação de fato) via documentos do divórcio."),
     
    ("PONTO 03: SUBORDINAÇÃO AO ART. 357, §1º DO CPC",
     "Instrumento Eleito:", "Manifestação de Esclarecimentos e Ajustes (CPC, art. 357, §1º) em vez de Embargos de Declaração genéricos.",
     "Vantagem Processual:", "Fórmula cooperativa que estabiliza o saneador antes da abertura da fase pericial e de especificação de provas.",
     "Subsidiariedade:", "Requerimento subsidiário pelo art. 1.022 para resguardar prequestionamento de eventuais omissões.")
]

card_w5 = Emu(3450000)
card_h5 = Emu(4850000)
card_y5 = Emu(1250000)

for idx, (head, t1, b1, t2, b2, t3, b3) in enumerate(adjustments):
    card_x = Emu(594360 + idx * 3750000)
    
    bg = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, card_x, card_y5, card_w5, card_h5)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_CARD_BG
    bg.line.color.rgb = COLOR_CARD_BORDER
    
    # Orange header strip
    bar = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, card_x, card_y5, card_w5, Emu(550000))
    bar.fill.solid()
    bar.fill.fore_color.rgb = COLOR_TEXT_PRIMARY
    bar.line.color.rgb = COLOR_TEXT_PRIMARY
    
    tb_h = slide5.shapes.add_textbox(card_x + Emu(100000), card_y5 + Emu(80000), card_w5 - Emu(200000), Emu(400000))
    tf_h = tb_h.text_frame
    tf_h.word_wrap = True
    p_h = tf_h.paragraphs[0]
    p_h.text = head
    p_h.font.name = FONT_FAMILY
    p_h.font.size = Pt(9)
    p_h.font.bold = True
    p_h.font.color.rgb = COLOR_ACCENT
    
    tb_b = slide5.shapes.add_textbox(card_x + Emu(150000), card_y5 + Emu(650000), card_w5 - Emu(300000), card_h5 - Emu(750000))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    
    blocks = [(t1, b1, COLOR_STRUCTURE), (t2, b2, COLOR_TEXT_PRIMARY), (t3, b3, COLOR_ACCENT)]
    for i, (ttl, txt, clr) in enumerate(blocks):
        p_t = tf_b.paragraphs[0] if i == 0 else tf_b.add_paragraph()
        p_t.text = ttl
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(9)
        p_t.font.bold = True
        p_t.font.color.rgb = clr
        p_t.space_before = Pt(8) if i > 0 else Pt(0)
        
        p_c = tf_b.add_paragraph()
        p_c.text = txt
        p_c.font.name = FONT_FAMILY
        p_c.font.size = Pt(8.5)
        p_c.font.color.rgb = COLOR_TEXT_PRIMARY

# ==========================================================
# SLIDE 6: FRENTE 3 — DEFESA NA RECONVENÇÃO (SENSE VERTICAL)
# ==========================================================
slide6 = prs.slides.add_slide(blank_layout)
add_header(slide6, "Frente III — Defesa na Reconvenção: Edifício Sense", "Blindagem do Patrimônio Particular & Distribuição de Ônus")
add_footer(slide6, 6, 7)

# Visual balance: 2 Large Cards (O Risco Identificado x A Resposta Técnica RDAA)
box_risk = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(594360), Emu(1250000), Emu(5350000), Emu(4850000))
box_risk.fill.solid()
box_risk.fill.fore_color.rgb = COLOR_CARD_BG
box_risk.line.color.rgb = COLOR_CARD_BORDER

tb_r = slide6.shapes.add_textbox(Emu(800000), Emu(1450000), Emu(4900000), Emu(4450000))
tf_r = tb_r.text_frame
tf_r.word_wrap = True

p_rt = tf_r.paragraphs[0]
p_rt.text = "O RISCO DA PREJUDICIALIDADE PROCESSUAL"
p_rt.font.name = FONT_FAMILY
p_rt.font.size = Pt(11)
p_rt.font.bold = True
p_rt.font.color.rgb = COLOR_STRUCTURE
p_rt.space_after = Pt(12)

risk_points = [
    ("Pretensão Reconvencional de Ana:", "A adversária requereu meação e arbitramento de aluguéis sobre o apartamento no Edifício Sense Vertical Living, alegando tratar-se de patrimônio do casal."),
    ("Ambiguidade na Decisão Judicial:", "O juízo da 10ª Vara Cível distribuiu o ônus probatório atribuindo a Sílvio o encargo de demonstrar a aquisição após a separação ou com recursos exclusivos (art. 373, II, CPC)."),
    ("O Risco de Subversão:", "Havia perigo iminente de que a presunção legal de comunicabilidade (art. 1.660 do CC) operasse como presunção absoluta, dispensando Ana de provar a aquisição na constância conjugal.")
]

for t, d in risk_points:
    p_pt = tf_r.add_paragraph()
    p_pt.text = f"⚠ {t}"
    p_pt.font.name = FONT_FAMILY
    p_pt.font.size = Pt(9.5)
    p_pt.font.bold = True
    p_pt.font.color.rgb = COLOR_TEXT_PRIMARY
    
    p_pd = tf_r.add_paragraph()
    p_pd.text = d
    p_pd.font.name = FONT_FAMILY
    p_pd.font.size = Pt(9)
    p_pd.font.color.rgb = COLOR_STRUCTURE
    p_pd.space_after = Pt(8)

# Right Box: Solução RDAA
box_sol = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(6244360), Emu(1250000), Emu(5350000), Emu(4850000))
box_sol.fill.solid()
box_sol.fill.fore_color.rgb = COLOR_LIGHT_ACCENT
box_sol.line.color.rgb = COLOR_ACCENT
box_sol.line.width = Pt(1.5)

tb_s = slide6.shapes.add_textbox(Emu(6450000), Emu(1450000), Emu(4900000), Emu(4450000))
tf_s = tb_s.text_frame
tf_s.word_wrap = True

p_st = tf_s.paragraphs[0]
p_st.text = "A RESPOSTA TÉCNICA E BLINDAGEM RDAA"
p_st.font.name = FONT_FAMILY
p_st.font.size = Pt(11)
p_st.font.bold = True
p_st.font.color.rgb = COLOR_ACCENT
p_st.space_after = Pt(12)

sol_points = [
    ("Ônus Constitutivo Primário (art. 373, I):", "Esclarecimento preventivo exigindo que Ana arque integralmente com a comprovação do fato constitutivo de seu direito reconvencional."),
    ("Impedimento à Inversão Automática:", "A ausência de prova conclusiva acerca da origem dos recursos não pode transferir a Sílvio o ônus pelo inadimplemento probatório da reconvinte."),
    ("Coexistência Regrada dos Ônus:", "A atribuição do art. 373, II a Sílvio funciona unicamente como contraprova impeditiva, sem afastar o encargo primário de Ana Lúcia."),
    ("Resguardo Probatório Concreto:", "Sílvio detém comprovação bancária e contratual de desembolso autônomo, reservada para a instrução caso a adversária supere seu ônus inicial.")
]

for t, d in sol_points:
    p_pt = tf_s.add_paragraph()
    p_pt.text = f"✔ {t}"
    p_pt.font.name = FONT_FAMILY
    p_pt.font.size = Pt(9.5)
    p_pt.font.bold = True
    p_pt.font.color.rgb = COLOR_TEXT_PRIMARY
    
    p_pd = tf_s.add_paragraph()
    p_pd.text = d
    p_pd.font.name = FONT_FAMILY
    p_pd.font.size = Pt(9)
    p_pd.font.color.rgb = COLOR_TEXT_PRIMARY
    p_pd.space_after = Pt(8)

# ==========================================================
# SLIDE 7: PRÓXIMOS PASSOS & CRONOGRAMA DE EXECUÇÃO
# ==========================================================
slide7 = prs.slides.add_slide(blank_layout)
add_header(slide7, "Cronograma de Ações & Providências Críticas", "Roadmap Estratégico RDAA")
add_footer(slide7, 7, 7)

# 4 Action Steps in Timeline Style
steps = [
    ("ETAPA 01", "JULGAMENTO COLEGIADO NO TJMG (AI /006)", "Acompanhar a pauta da 8ª Câmara Cível Especializada; sustentar oralmente a manutenção da obrigação integral do IPTU por Ana Lúcia e extinção definitiva das astreintes."),
    ("ETAPA 02", "ESPECIFICAÇÃO DE PROVAS NA 10ª VARA CÍVEL", "Requerer perícia de engenharia/imobiliária para fixação do valor locatício da casa da Begônias; acostar certidões do divórcio comprovando oposição fática desde 2023."),
    ("ETAPA 03", "ACOMPANHAMENTO DA BAIXA DO PROTESTO", "Intimar a Municipalidade de Uberlândia e o Tabelionato para certificar cumprimento da determinação liminar que impôs a Ana a quitação/baixa do protesto."),
    ("ETAPA 04", "AVALIAÇÃO PERICIAL NA AÇÃO DE PARTILHA", "Blindar o Edifício Sense na 3ª Vara de Família, exigindo homologação pericial dos bens incontroversos e formalização das cotas de meação com abatimento das dívidas fiscais.")
]

box_step_w = Emu(11000000)
box_step_h = Emu(1050000)
step_y0 = Emu(1250000)
step_gap = Emu(1220000)

for idx, (tag, title, detail) in enumerate(steps):
    sy = step_y0 + idx * step_gap
    
    # Outer Shape
    box = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(594360), sy, box_step_w, box_step_h)
    box.fill.solid()
    box.fill.fore_color.rgb = COLOR_CARD_BG
    box.line.color.rgb = COLOR_CARD_BORDER
    
    # Orange Left Marker
    tag_box = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(594360), sy, Emu(1500000), box_step_h)
    tag_box.fill.solid()
    tag_box.fill.fore_color.rgb = COLOR_ACCENT if idx == 0 else COLOR_TEXT_PRIMARY
    tag_box.line.color.rgb = tag_box.fill.fore_color.rgb
    
    tb_tag = slide7.shapes.add_textbox(Emu(644360), sy + Emu(340000), Emu(1400000), Emu(400000))
    p_t = tb_tag.text_frame.paragraphs[0]
    p_t.text = tag
    p_t.font.name = FONT_FAMILY
    p_t.font.size = Pt(11)
    p_t.font.bold = True
    p_t.font.color.rgb = RGBColor(255, 255, 255)
    p_t.alignment = PP_ALIGN.CENTER
    
    # Text Content
    tb_c = slide7.shapes.add_textbox(Emu(2250000), sy + Emu(150000), Emu(9100000), box_step_h - Emu(300000))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    
    p_title = tf_c.paragraphs[0]
    p_title.text = title
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(10.5)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_PRIMARY
    p_title.space_after = Pt(3)
    
    p_det = tf_c.add_paragraph()
    p_det.text = detail
    p_det.font.name = FONT_FAMILY
    p_det.font.size = Pt(9)
    p_det.font.color.rgb = COLOR_STRUCTURE

# Save Presentation
prs.save(OUTPUT_PPTX)
print(f"PowerPoint gerado com sucesso em: {OUTPUT_PPTX}")
