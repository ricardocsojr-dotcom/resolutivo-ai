import os
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Core Brand Tokens
COLOR_BG = RGBColor(255, 255, 255)
COLOR_TEXT_PRIMARY = RGBColor(0, 0, 0)
COLOR_STRUCTURE = RGBColor(99, 102, 106)      # #63666A
COLOR_ACCENT = RGBColor(247, 168, 0)           # #F7A800
COLOR_CARD_BG = RGBColor(248, 249, 250)
COLOR_CARD_BORDER = RGBColor(229, 231, 235)
COLOR_ACCENT_LIGHT = RGBColor(255, 249, 238)
COLOR_GREEN_BG = RGBColor(236, 253, 245)
COLOR_GREEN_TEXT = RGBColor(4, 120, 87)
COLOR_RED_BG = RGBColor(254, 242, 242)
COLOR_RED_TEXT = RGBColor(185, 28, 28)

FONT_FAMILY = "Arial"
LOGO_PATH = "C:/Projetos/resolutivo-ai/skills/romano-donadel-slide-style/assets/logo_romano_donadel.png"
OUTPUT_PPTX = "C:/Projetos/resolutivo-ai/Apresentacao_Caso_Silvio_Afonso_Romano_Donadel.pptx"

prs = Presentation()
prs.slide_width = Emu(12192000)   # 16:9 widescreen
prs.slide_height = Emu(6858000)
blank_layout = prs.slide_layouts[6]

def add_header(slide, title_text, category_text=""):
    rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(594360), Emu(420000), Emu(50000), Emu(450000))
    rule.fill.solid()
    rule.fill.fore_color.rgb = COLOR_ACCENT
    rule.line.color.rgb = COLOR_ACCENT
    
    tb = slide.shapes.add_textbox(Emu(720000), Emu(360000), Emu(9500000), Emu(600000))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    if category_text:
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = FONT_FAMILY
        p_cat.font.size = Pt(9)
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
    
    if os.path.exists(LOGO_PATH):
        slide.shapes.add_picture(LOGO_PATH, Emu(10500000), Emu(350000), width=Emu(1150000))

def add_footer(slide, page_num, total_pages=7):
    div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(594360), Emu(6420000), Emu(11000000), Emu(8000))
    div.fill.solid()
    div.fill.fore_color.rgb = COLOR_CARD_BORDER
    div.line.color.rgb = COLOR_CARD_BORDER
    
    tb_l = slide.shapes.add_textbox(Emu(594360), Emu(6460000), Emu(5000000), Emu(250000))
    tf_l = tb_l.text_frame
    tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0
    p_l = tf_l.paragraphs[0]
    p_l.text = "CONFIDENCIAL | ROMANO DONADEL ADVOGADOS ASSOCIADOS"
    p_l.font.name = FONT_FAMILY
    p_l.font.size = Pt(8.5)
    p_l.font.color.rgb = COLOR_STRUCTURE
    
    tb_r = slide.shapes.add_textbox(Emu(10500000), Emu(6460000), Emu(1100000), Emu(250000))
    tf_r = tb_r.text_frame
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0
    p_r = tf_r.paragraphs[0]
    p_r.text = f"SLIDE {page_num:02d} / {total_pages:02d}"
    p_r.alignment = PP_ALIGN.RIGHT
    p_r.font.name = FONT_FAMILY
    p_r.font.size = Pt(8.5)
    p_r.font.bold = True
    p_r.font.color.rgb = COLOR_TEXT_PRIMARY

# ==========================================
# SLIDE 1: CAPA
# ==========================================
s1 = prs.slides.add_slide(blank_layout)
if os.path.exists(LOGO_PATH):
    s1.shapes.add_picture(LOGO_PATH, Emu(9800000), Emu(600000), width=Emu(1800000))

bar1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(658368), Emu(1800000), Emu(80000), Emu(3000000))
bar1.fill.solid()
bar1.fill.fore_color.rgb = COLOR_ACCENT
bar1.line.color.rgb = COLOR_ACCENT

tb1 = s1.shapes.add_textbox(Emu(950000), Emu(1900000), Emu(9500000), Emu(2800000))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "DIRETRIZ ESTRATÉGICA RDAA"
p.font.name = FONT_FAMILY
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = COLOR_ACCENT

p2 = tf1.add_paragraph()
p2.text = "CASO SÍLVIO LUIZ AFONSO"
p2.font.name = FONT_FAMILY
p2.font.size = Pt(32)
p2.font.bold = True
p2.font.color.rgb = COLOR_TEXT_PRIMARY
p2.space_before = Pt(8)

p3 = tf1.add_paragraph()
p3.text = "Panorama Estratégico, Gestão de Passivo Tributário e Blindagem de Meação"
p3.font.name = FONT_FAMILY
p3.font.size = Pt(14)
p3.font.color.rgb = COLOR_STRUCTURE
p3.space_before = Pt(6)
p3.space_after = Pt(24)

p4 = tf1.add_paragraph()
p4.text = "CLIENTE: Sílvio Luiz Afonso   |   PARTE ADVERSA: Ana Lúcia de Oliveira Afonso"
p4.font.name = FONT_FAMILY
p4.font.size = Pt(10.5)
p4.font.bold = True
p4.font.color.rgb = COLOR_TEXT_PRIMARY

p5 = tf1.add_paragraph()
p5.text = "PATROCÍNIO: Romano Donadel Advogados   |   DATA: Setembro / 2026"
p5.font.name = FONT_FAMILY
p5.font.size = Pt(10)
p5.font.color.rgb = COLOR_STRUCTURE

add_footer(s1, 1, 7)

# ==========================================
# SLIDE 2: 3 GRANDES PILARES
# ==========================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "Arquitetura Estratégica & Governança do Caso", "Painel Executivo")
add_footer(s2, 2, 7)

pillars = [
    ("03", "PROCESSOS", "FRENTES INTEGRADAS", [
        ("3ª Vara Família", "Divórcio e partilha do casal"),
        ("TJMG (8ª Câm.)", "Agravo do IPTU da Begônias"),
        ("10ª Vara Cível", "Arbitramento de aluguéis")
    ], "Segregação procedimental absoluta"),
    ("02", "ACERVOS", "IMÓVEIS MAPEADOS", [
        ("Rua das Begônias", "Posse e fruição exclusiva de Ana"),
        ("Ed. Sense", "Aquisição autônoma de Sílvio"),
        ("Blindagem", "Bloqueio à meação do Sense")
    ], "Proteção do acervo exclusivo"),
    ("100%", "SUCESSO", "RISCOS NEUTRALIZADOS", [
        ("Astreintes", "Revogadas no TJMG"),
        ("IPTU Begônias", "Dever integral da ocupante"),
        ("Alimentos", "Sem compensação cruzada")
    ], "Zero passivo transferido a Sílvio")
]

card_w = Emu(3450000)
card_h = Emu(4850000)
card_y = Emu(1250000)

for idx, (num, tag, title, bullets, bot_tag) in enumerate(pillars):
    card_x = Emu(594360 + idx * 3750000)
    
    # Outer Box
    box = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, card_x, card_y, card_w, card_h)
    box.fill.solid()
    box.fill.fore_color.rgb = COLOR_CARD_BG
    box.line.color.rgb = COLOR_CARD_BORDER
    
    # Top Accent Strip
    strip = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, card_x, card_y, card_w, Emu(50000))
    strip.fill.solid()
    strip.fill.fore_color.rgb = COLOR_ACCENT
    strip.line.color.rgb = COLOR_ACCENT
    
    tb = s2.shapes.add_textbox(card_x + Emu(200000), card_y + Emu(180000), card_w - Emu(400000), card_h - Emu(360000))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_num = tf.paragraphs[0]
    p_num.text = f"{num}  "
    p_num.font.name = FONT_FAMILY
    p_num.font.size = Pt(28)
    p_num.font.bold = True
    p_num.font.color.rgb = COLOR_TEXT_PRIMARY
    
    p_ttl = tf.add_paragraph()
    p_ttl.text = title
    p_ttl.font.name = FONT_FAMILY
    p_ttl.font.size = Pt(12)
    p_ttl.font.bold = True
    p_ttl.font.color.rgb = COLOR_ACCENT
    p_ttl.space_after = Pt(14)
    
    for h, b in bullets:
        pb = tf.add_paragraph()
        pb.text = f"✔ {h}: {b}"
        pb.font.name = FONT_FAMILY
        pb.font.size = Pt(10)
        pb.font.color.rgb = COLOR_TEXT_PRIMARY
        pb.space_after = Pt(8)
        
    p_bot = tf.add_paragraph()
    p_bot.text = f"● {bot_tag}"
    p_bot.font.name = FONT_FAMILY
    p_bot.font.size = Pt(9.5)
    p_bot.font.bold = True
    p_bot.font.color.rgb = COLOR_STRUCTURE
    p_bot.space_before = Pt(16)

# ==========================================
# SLIDE 3: MATRIZ DE AÇÕES (4 CARDS)
# ==========================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "Matriz de Litigiosidade e Diretrizes RDAA", "Mapa de Ações")
add_footer(s3, 3, 7)

actions = [
    ("3ª VARA DE FAMÍLIA", "Divórcio e Partilha", "Proc. 5026681-10", "Partilha do patrimônio comum e apuração da meação.", "Isolar bens particulares e exigir prestação de contas dos frutos."),
    ("TJMG — 8ª CÂMARA", "AI IPTU Begônias (/006)", "Proc. 1.0000.23.223786-7", "Custeio do IPTU e baixa de protesto da casa residencial.", "Manter dever tributário exclusivo da coproprietária ocupante."),
    ("10ª VARA CÍVEL", "Arbitramento de Aluguéis", "Proc. 5033450-63", "Indenização pela fruição exclusiva da antiga residência.", "Fixar termo inicial na citação e dispensar esbulho físico."),
    ("10ª VARA CÍVEL", "Reconvenção (Ed. Sense)", "Proc. 5033450-63", "Pretensão de meação sobre o apartamento de Sílvio.", "Impor ônus primário integral à reconvinte (art. 373, I).")
]

card_w3 = Emu(2600000)
for idx, (court, action, proc, desc, target) in enumerate(actions):
    card_x = Emu(594360 + idx * 2800000)
    box = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, card_x, card_y, card_w3, card_h)
    box.fill.solid()
    box.fill.fore_color.rgb = COLOR_CARD_BG
    box.line.color.rgb = COLOR_CARD_BORDER
    
    tb = s3.shapes.add_textbox(card_x + Emu(150000), card_y + Emu(160000), card_w3 - Emu(300000), card_h - Emu(320000))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_c = tf.paragraphs[0]
    p_c.text = court
    p_c.font.name = FONT_FAMILY
    p_c.font.size = Pt(8.5)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_ACCENT
    
    p_a = tf.add_paragraph()
    p_a.text = action
    p_a.font.name = FONT_FAMILY
    p_a.font.size = Pt(12)
    p_a.font.bold = True
    p_a.font.color.rgb = COLOR_TEXT_PRIMARY
    
    p_p = tf.add_paragraph()
    p_p.text = proc
    p_p.font.name = FONT_FAMILY
    p_p.font.size = Pt(8.5)
    p_p.font.color.rgb = COLOR_STRUCTURE
    p_p.space_after = Pt(10)
    
    p_d = tf.add_paragraph()
    p_d.text = desc
    p_d.font.name = FONT_FAMILY
    p_d.font.size = Pt(9.5)
    p_d.font.color.rgb = COLOR_TEXT_PRIMARY
    p_d.space_after = Pt(14)
    
    p_t = tf.add_paragraph()
    p_t.text = f"🎯 DIRETRIZ RDAA:\n{target}"
    p_t.font.name = FONT_FAMILY
    p_t.font.size = Pt(9.5)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_TEXT_PRIMARY

# ==========================================
# SLIDE 4: FRENTE 1 IPTU BEGÔNIAS (FLUXO)
# ==========================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "TJMG Mantém IPTU com a Ocupante e Revoga Multa", "AI 1.0000.23.223786-7/006 — TJMG")
add_footer(s4, 4, 7)

# 4 Horizontal flow steps
flow_steps = [
    ("USO EXCLUSIVO", "Ana reside na casa desde 13/03/2023"),
    ("INADIMPLÊNCIA", "IPTU e taxas deixados em aberto"),
    ("PROTESTO INDEVIDO", "Fazenda protestou Sílvio em cartório"),
    ("ORDEM DO TJMG", "Ana deve solver dívida e baixar protesto")
]

flow_w = Emu(2500000)
flow_h = Emu(1500000)
flow_y = Emu(1300000)

for idx, (title, sub) in enumerate(flow_steps):
    fx = Emu(594360 + idx * 2800000)
    f_box = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, fx, flow_y, flow_w, flow_h)
    f_box.fill.solid()
    if idx == 3:
        f_box.fill.fore_color.rgb = COLOR_GREEN_BG
        f_box.line.color.rgb = COLOR_GREEN_TEXT
    else:
        f_box.fill.fore_color.rgb = COLOR_CARD_BG
        f_box.line.color.rgb = COLOR_CARD_BORDER
        
    tb_f = s4.shapes.add_textbox(fx + Emu(100000), flow_y + Emu(150000), flow_w - Emu(200000), flow_h - Emu(300000))
    tff = tb_f.text_frame
    tff.word_wrap = True
    
    pf1 = tff.paragraphs[0]
    pf1.text = f"PASSO {idx+1}: {title}"
    pf1.font.name = FONT_FAMILY
    pf1.font.size = Pt(9.5)
    pf1.font.bold = True
    pf1.font.color.rgb = COLOR_GREEN_TEXT if idx == 3 else COLOR_ACCENT
    
    pf2 = tff.add_paragraph()
    pf2.text = sub
    pf2.font.name = FONT_FAMILY
    pf2.font.size = Pt(9)
    pf2.font.color.rgb = COLOR_TEXT_PRIMARY
    pf2.space_before = Pt(4)

# 2 Lower Contrast Boxes
box_w4 = Emu(5350000)
box_h4 = Emu(3000000)
box_y4 = Emu(3100000)

# Danger Box
b_dan = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(594360), box_y4, box_w4, box_h4)
b_dan.fill.solid()
b_dan.fill.fore_color.rgb = COLOR_RED_BG
b_dan.line.color.rgb = COLOR_RED_TEXT

tb_dan = s4.shapes.add_textbox(Emu(800000), box_y4 + Emu(200000), box_w4 - Emu(400000), box_h4 - Emu(400000))
tfd = tb_dan.text_frame
tfd.word_wrap = True

pd1 = tfd.paragraphs[0]
pd1.text = "✗ TESE REJEITADA DA ADVERSÁRIA"
pd1.font.name = FONT_FAMILY
pd1.font.size = Pt(11)
pd1.font.bold = True
pd1.font.color.rgb = COLOR_RED_TEXT
pd1.space_after = Pt(8)

pd2 = tfd.add_paragraph()
pd2.text = "• Invocou 'violência patrimonial' e suposta dependência econômica.\n• Tentou abater IPTU de pensão alimentícia em atraso.\n• Incompatibilidade: Sílvio é a vítima do protesto; alimentos têm via executiva autônoma."
pd2.font.name = FONT_FAMILY
pd2.font.size = Pt(10)
pd2.font.color.rgb = COLOR_TEXT_PRIMARY

# Victory Box
b_vic = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(6244360), box_y4, box_w4, box_h4)
b_vic.fill.solid()
b_vic.fill.fore_color.rgb = COLOR_ACCENT_LIGHT
b_vic.line.color.rgb = COLOR_ACCENT
b_vic.line.width = Pt(1.5)

tb_vic = s4.shapes.add_textbox(Emu(6450000), box_y4 + Emu(200000), box_w4 - Emu(400000), box_h4 - Emu(400000))
tfv = tb_vic.text_frame
tfv.word_wrap = True

pv1 = tfv.paragraphs[0]
pv1.text = "✔ SOLUÇÃO RDAA ACOLHIDA NO TJMG"
pv1.font.name = FONT_FAMILY
pv1.font.size = Pt(11)
pv1.font.bold = True
pv1.font.color.rgb = COLOR_ACCENT
pv1.space_after = Pt(8)

pv2 = tfv.add_paragraph()
pv2.text = "• Jurisprudência consolidada (TJMG AC 0013168-49 e STJ AREsp 2.462.038).\n• Quem frui o bem com exclusividade suporta integralmente os tributos.\n• Resultado: Mantida obrigação de Ana; astreintes de R$ 10 mil revogadas."
pv2.font.name = FONT_FAMILY
pv2.font.size = Pt(10)
pv2.font.color.rgb = COLOR_TEXT_PRIMARY

# ==========================================
# SLIDE 5: FRENTE 2 ARBITRAMENTO (SANEADOR)
# ==========================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Ajuste do Saneador: Fato Gerador e Piso na Citação", "Ação nº 5033450-63.2025.8.13.0702 — 10ª Vara Cível")
add_footer(s5, 5, 7)

# 2 Large pillars
card_w5 = Emu(5350000)
card_h5 = Emu(4850000)

# Col 1: Fato Gerador
b_fg = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(594360), card_y, card_w5, card_h5)
b_fg.fill.solid()
b_fg.fill.fore_color.rgb = COLOR_CARD_BG
b_fg.line.color.rgb = COLOR_CARD_BORDER

tb_fg = s5.shapes.add_textbox(Emu(800000), card_y + Emu(200000), card_w5 - Emu(400000), card_h5 - Emu(400000))
tffg = tb_fg.text_frame
tffg.word_wrap = True

pfg1 = tffg.paragraphs[0]
pfg1.text = "1. DESMISTIFICAÇÃO DO ESBULHO FÍSICO"
pfg1.font.name = FONT_FAMILY
pfg1.font.size = Pt(12)
pfg1.font.bold = True
pfg1.font.color.rgb = COLOR_ACCENT
pfg1.space_after = Pt(12)

pfg2 = tffg.add_paragraph()
pfg2.text = "• Equívoco no Saneador: Juízo exigiu prova de que Ana impedia fisicamente o acesso de Sílvio ao imóvel.\n\n• Correção RDAA: A ruptura conjugal gera impossibilidade prática de coabitação. O direito indenizatório independe de agressão ou esbulho material.\n\n• Tese STJ (REsp 1.699.013/DF): O fato gerador decorre do uso exclusivo somado à inequívoca oposição do outro coproprietário."
pfg2.font.name = FONT_FAMILY
pfg2.font.size = Pt(10)
pfg2.font.color.rgb = COLOR_TEXT_PRIMARY

# Col 2: Termo Inicial
b_ti = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(6244360), card_y, card_w5, card_h5)
b_ti.fill.solid()
b_ti.fill.fore_color.rgb = COLOR_CARD_BG
b_ti.line.color.rgb = COLOR_CARD_BORDER

tb_ti = s5.shapes.add_textbox(Emu(6450000), card_y + Emu(200000), card_w5 - Emu(400000), card_h5 - Emu(400000))
tfti = tb_ti.text_frame
tfti.word_wrap = True

pti1 = tfti.paragraphs[0]
pti1.text = "2. CONSOLIDAÇÃO DO TERMO INICIAL"
pti1.font.name = FONT_FAMILY
pti1.font.size = Pt(12)
pti1.font.bold = True
pti1.font.color.rgb = COLOR_ACCENT
pti1.space_after = Pt(12)

pti2 = tfti.add_paragraph()
pti2.text = "• Piso Mínimo Incontroverso: Fixação expressa da data da citação válida como termo inicial dos aluguéis, sem necessidade de instrução probatória adicional.\n\n• Retroatividade a 13/03/2023: Preservada a faculdade de demonstrar oposição prévia desde a separação de fato através dos autos do divórcio.\n\n• Estabilização (CPC, art. 357, §1º): Definição prévia antes da abertura de prazo para especificação de perícia avaliatória."
pti2.font.name = FONT_FAMILY
pti2.font.size = Pt(10)
pti2.font.color.rgb = COLOR_TEXT_PRIMARY

# ==========================================
# SLIDE 6: FRENTE 3 SENSE VERTICAL
# ==========================================
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "Blindagem do Apartamento Sense Vertical Living", "Defesa na Reconvenção — 10ª Vara Cível")
add_footer(s6, 6, 7)

# Danger Side
b_s_dan = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(594360), card_y, Emu(5100000), card_h)
b_s_dan.fill.solid()
b_s_dan.fill.fore_color.rgb = COLOR_CARD_BG
b_s_dan.line.color.rgb = COLOR_CARD_BORDER

tb_sd = s6.shapes.add_textbox(Emu(800000), card_y + Emu(200000), Emu(4700000), card_h - Emu(400000))
tfsd = tb_sd.text_frame
tfsd.word_wrap = True

psd1 = tfsd.paragraphs[0]
psd1.text = "⚠ RISCO DE INVERSÃO PROBATÓRIA"
psd1.font.name = FONT_FAMILY
psd1.font.size = Pt(12)
psd1.font.bold = True
psd1.font.color.rgb = COLOR_STRUCTURE
psd1.space_after = Pt(12)

psd2 = tfsd.add_paragraph()
psd2.text = "• Pretensão de Ana: Incluir o Ed. Sense na partilha e cobrar aluguéis de Sílvio.\n\n• Risco Identificado: Presunção do art. 1.660 do CC operar como inversão automática de ônus em prejuízo do reconvindo.\n\n• Ambiguidade Judicial: Juízo atribuiu a Sílvio prova impeditiva (art. 373, II), sugerindo presunção precoce de comunicabilidade."
psd2.font.name = FONT_FAMILY
psd2.font.size = Pt(10)
psd2.font.color.rgb = COLOR_TEXT_PRIMARY

# Shield Center
shield = s6.shapes.add_shape(MSO_SHAPE.OVAL, Emu(5800000), Emu(3300000), Emu(600000), Emu(600000))
shield.fill.solid()
shield.fill.fore_color.rgb = COLOR_TEXT_PRIMARY
shield.line.color.rgb = COLOR_ACCENT

# Victory Side
b_s_vic = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(6500000), card_y, Emu(5100000), card_h)
b_s_vic.fill.solid()
b_s_vic.fill.fore_color.rgb = COLOR_ACCENT_LIGHT
b_s_vic.line.color.rgb = COLOR_ACCENT
b_s_vic.line.width = Pt(1.5)

tb_sv = s6.shapes.add_textbox(Emu(6700000), card_y + Emu(200000), Emu(4700000), card_h - Emu(400000))
tfsv = tb_sv.text_frame
tfsv.word_wrap = True

psv1 = tfsv.paragraphs[0]
psv1.text = "🛡 BLINDAGEM TÉCNICA RDAA"
psv1.font.name = FONT_FAMILY
psv1.font.size = Pt(12)
psv1.font.bold = True
psv1.font.color.rgb = COLOR_ACCENT
psv1.space_after = Pt(12)

psv2 = tfsv.add_paragraph()
psv2.text = "• Primazia do Art. 373, I: Incumbe à reconvinte comprovar que o imóvel foi adquirido na constância e com esforço comum.\n\n• Presunção Inoperante: O art. 1.660 do CC não supre a inércia probatória primária da autora reconvinte.\n\n• Lastro Exclusivo de Reserva: Sílvio detém extratos bancários e contratos atestando aquisição autônoma fora da comunhão."
psv2.font.name = FONT_FAMILY
psv2.font.size = Pt(10)
psv2.font.color.rgb = COLOR_TEXT_PRIMARY

# ==========================================
# SLIDE 7: TIMELINE & CRONOGRAMA
# ==========================================
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "Cronograma de Providências Imediatas", "Roadmap Estratégico")
add_footer(s7, 7, 7)

steps = [
    ("ETAPA 1", "JULGAMENTO NO TJMG", "Distribuir memoriais na 8ª Câmara Cível para confirmar que o IPTU é dever exclusivo de Ana.", COLOR_ACCENT),
    ("ETAPA 2", "PERÍCIA DE ALUGUEL", "Apresentar quesitos na 10ª Vara Cível para arbitrar o valor de mercado da residência Begônias.", COLOR_TEXT_PRIMARY),
    ("ETAPA 3", "BAIXA DO PROTESTO", "Fiscalizar cumprimento da ordem judicial no 1º Tabelionato de Protestos de Uberlândia.", COLOR_TEXT_PRIMARY),
    ("ETAPA 4", "BLINDAGEM DO SENSE", "Excluir formalmente o apartamento da partilha na 3ª Vara de Família com prova documental.", COLOR_TEXT_PRIMARY)
]

step_w7 = Emu(2600000)
for idx, (tag, title, desc, col) in enumerate(steps):
    sx = Emu(594360 + idx * 2800000)
    box = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, sx, card_y, step_w7, card_h)
    box.fill.solid()
    if idx == 0:
        box.fill.fore_color.rgb = COLOR_ACCENT_LIGHT
        box.line.color.rgb = COLOR_ACCENT
        box.line.width = Pt(1.5)
    else:
        box.fill.fore_color.rgb = COLOR_CARD_BG
        box.line.color.rgb = COLOR_CARD_BORDER
        
    tb = s7.shapes.add_textbox(sx + Emu(150000), card_y + Emu(200000), step_w7 - Emu(300000), card_h - Emu(400000))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_t = tf.paragraphs[0]
    p_t.text = tag
    p_t.font.name = FONT_FAMILY
    p_t.font.size = Pt(10)
    p_t.font.bold = True
    p_t.font.color.rgb = col
    
    p_h = tf.add_paragraph()
    p_h.text = title
    p_h.font.name = FONT_FAMILY
    p_h.font.size = Pt(12)
    p_h.font.bold = True
    p_h.font.color.rgb = COLOR_TEXT_PRIMARY
    p_h.space_after = Pt(10)
    
    p_d = tf.add_paragraph()
    p_d.text = desc
    p_d.font.name = FONT_FAMILY
    p_d.font.size = Pt(9.5)
    p_d.font.color.rgb = COLOR_STRUCTURE

prs.save(OUTPUT_PPTX)
print(f"PPTX atualizado com sucesso em: {OUTPUT_PPTX}")
