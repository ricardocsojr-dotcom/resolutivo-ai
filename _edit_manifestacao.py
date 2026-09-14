#!/usr/bin/env python3
"""Edita a manifestação preservando estilos OOXML existentes."""
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from copy import deepcopy
import re, shutil, os

SRC = r'C:\Users\ricar\AppData\Local\hermes\attachments\Manifestação - Revelia e Julgamento Antecipado.docx'
OUT = r'C:\Users\ricar\Desktop\Produção Jurídica\2026-09-14\1001667-36.2026.8.13.0040\Manifestação - Revelia e Julgamento Antecipado.docx'
WORK = r'C:\Users\ricar\Desktop\resolutivo-ai-lab\_edit_manifestacao.docx'

shutil.copy2(SRC, WORK)
doc = Document(WORK)

# ── helper: substitui texto de todos os runs, preservando formatação ──
def replace_text(p, new_text):
    """Preserva formatação do primeiro run, zera os demais."""
    runs = [r for r in p.runs if r.text.strip() or r._r.getparent().tag.endswith('}p')]
    if not runs:
        # sem runs de texto (parágrafo vazio com imagem)
        return
    runs[0].text = new_text
    for r in runs[1:]:
        r.text = ''

def insert_paragraph_after(doc, ref_p, text, style_name):
    """Insere novo parágrafo após ref_p, copiando numeração do estilo indicado."""
    # Cria novo elemento w:p
    new_p = OxmlElement('w:p')
    # Copia pPr do estilo alvo (busca um parágrafo existente com esse estilo)
    for p in doc.paragraphs:
        if p.style.name == style_name and p._p.pPr is not None:
            new_pPr = deepcopy(p._p.pPr)
            new_p.insert(0, new_pPr)
            break
    # Adiciona run com texto
    new_r = OxmlElement('w:r')
    new_t = OxmlElement('w:t')
    new_t.set(qn('xml:space'), 'preserve')
    new_t.text = text
    new_r.append(new_t)
    new_p.append(new_r)
    # Insere após o parágrafo de referência
    ref_p._p.addnext(new_p)
    return new_p

paras = doc.paragraphs

# ═══════════════════════════════════════════════════════════════════════
# 1. ABERTURA — trocar título da peça + dois-pontos
# ═══════════════════════════════════════════════════════════════════════
p8 = paras[8]
old_abertura = p8.text
# Substituir "MANIFESTAÇÃO SOBRE A CITAÇÃO" → "MANIFESTAÇÃO SOBRE O DECURSO DE PRAZO:"
new_abertura = old_abertura.replace(
    "MANIFESTAÇÃO SOBRE A CITAÇÃO",
    "MANIFESTAÇÃO SOBRE O DECURSO DE PRAZO"
)
# Os dois-pontos pertencem ao parágrafo introdutório, após a frase de abertura,
# e não ao título da manifestação.
new_abertura = new_abertura.replace(
    "MANIFESTAÇÃO SOBRE O DECURSO DE PRAZO:, pelas razões a seguir expostas.",
    "MANIFESTAÇÃO SOBRE O DECURSO DE PRAZO, pelas razões a seguir expostas:"
)
replace_text(p8, new_abertura)

# ═══════════════════════════════════════════════════════════════════════
# 2. INSERIR título DECURSO DO PRAZO após imagem (para 14)
# ═══════════════════════════════════════════════════════════════════════
# Encontra o parágrafo da imagem (para 14 =图片)
p14 = paras[14]
# Inserir novo título "II. DECURSO DO PRAZO PARA CONTESTAÇÃO" após a imagem
insert_paragraph_after(doc, p14, 'II. DECURSO DO PRAZO PARA CONTESTAÇÃO', 'RDAA Título 1')
# Recarrega parágrafos (inserção via XML muda a lista)
paras = doc.paragraphs

# ═══════════════════════════════════════════════════════════════════════
# 3. BODY — Regularidade da Citação (parágrafos 12, 15→16, 17→18, 19→20)
# ═══════════════════════════════════════════════════════════════════════
# Mantém parágrafo 12 (após imagem) como está — já é bom
# Para 16 (após inserção do título DECURSO) → era body 15 (original)
# Para 18 → era body 17
# Para 20 → era body 19

# Re-textar body de regularidade (mantém o parágrafo 12 original, ajusta os seguintes)
# Body 1 (original para 15, agora 16): reescrever
replace_text(paras[15],
    "Constata-se que a finalidade precípua do ato de comunicação processual restou plenamente "
    "atingida. O Réu obteve ciência inequívoca e pessoal acerca da existência da lide e do "
    "prazo fixado para o exercício do contraditório, não se cogitando de entrega a terceiro ou "
    "de vício de identificação do recebedor.")
replace_text(paras[17],
    "Nos moldes preconizados pelo CPC, arts. 238 e 239, a citação perfaz pressuposto processual "
    "de validade, cuja concretização por via postal atende aos requisitos do art. 248, § 1º, do "
    "mesmo diploma legal quando entregue diretamente ao citando mediante aposição de assinatura.")
replace_text(paras[19],
    "O ato citatório revela-se, portanto, formal e materialmente válido, gerando a plenitude de "
    "seus efeitos. Tendo o próprio destinatário subscrito o documento postal comprobatório, não "
    "remanesce nulidade a ser pronunciada nem motivo para renovação da diligência.")

# ═══════════════════════════════════════════════════════════════════════
# 4. DECURSO DO PRAZO — body após o novo título inserido
# ═══════════════════════════════════════════════════════════════════════
# O corpo original de DECURSO (era para 22-23 original, agora shiftou +1 por inserção)
# Para 23 era body 22 original: "Regularmente cientificado..."
replace_text(paras[23],
    "Regularmente citado, o Réu permaneceu inerte e deixou transcorrer integralmente o prazo "
    "para apresentação de contestação, encerrado em 19 de agosto de 2026, conforme certidão "
    "lançada nos autos.")
# Para 25 original era body "Diante da consumação..." → reescrever para flare
replace_text(paras[25],
    "A inércia defensiva não passa de simples irregularidade sem consequência. O Réu foi chamado "
    "ao processo de forma válida, recebeu pessoalmente a comunicação e, mesmo assim, não "
    "apresentou contestação.")

# ═══════════════════════════════════════════════════════════════════════
# 5. REVELIA — body (parágrafos 27, 29 → reescrever conforme Flávia)
# ═══════════════════════════════════════════════════════════════════════
replace_text(paras[27],
    "Diante da consumação do prazo in albis, impõe-se a declaração formal da revelia do "
    "Demandado, com incidência do efeito material contemplado pelo CPC, art. 344, "
    "presumindo-se verdadeiras as alegações de fato deduzidas pela Autora.")
replace_text(paras[29],
    "Tal presunção de veracidade confere higidez ao quadro fático delineado na exordial, "
    "atuando de maneira harmônica com o lastro probatório documental já acostado aos autos para "
    "subsidiar o provimento jurisdicional pretendido.")

# ═══════════════════════════════════════════════════════════════════════
# 6. JULGAMENTO ANTECIPADO — body (parágrafos 33, 35, 37 → manter como Flávia)
# ═══════════════════════════════════════════════════════════════════════
# Para 33 era body original 33 "Operada a revelia..." → manter ou reescrever
# A orientação da Flávia fala em substituir "item 12" — que era o 4º body do JULGAMENTO
# Vamos reescrever os 4 body paragraphs do JULGAMENTO conforme Flávia

# Para 33: revelia deve produzir efeitos... (CPC art. 346, preclusão)
replace_text(paras[33],
    "A revelia deve produzir seus efeitos processuais próprios, inclusive aqueles previstos no "
    "CPC, art. 346, bem como ser reconhecida a preclusão temporal e consumativa quanto às "
    "matérias defensivas, alegações de fato, impugnações e requerimentos probatórios que "
    "deveriam ter sido deduzidos no momento processual oportuno, não se admitindo que eventual "
    "ingresso tardio do Réu nos autos importe reabertura de fases processuais já superadas.")

# Para 35: embora ao revel assegurado...
replace_text(paras[35],
    "Com efeito, embora ao revel seja assegurado o direito de intervir no processo em qualquer "
    "fase, recebendo-o no estado em que se encontrar, tal prerrogativa não autoriza a "
    "restituição de oportunidades processuais já preclusas, tampouco permite que a revelia "
    "seja posteriormente neutralizada mediante apresentação extemporânea de defesa ou "
    "formulação tardia de pretensões probatórias.")

# Para 37: no caso concreto...
replace_text(paras[37],
    "No caso concreto, estando os fatos constitutivos do direito da Autora suficientemente "
    "expostos e documentalmente demonstrados, e incidindo sobre as alegações fáticas não "
    "impugnadas a presunção decorrente da revelia, mostra-se desnecessária a dilação probatória, "
    "devendo o feito ser submetido a julgamento antecipado do mérito, nos termos do art. 355, "
    "II, do CPC.")

# Para 39: ressalte-se + caso subsidiário (4º body)
replace_text(paras[39],
    "Ressalte-se que a presunção decorrente da revelia recai sobre os fatos narrados pela "
    "Autora, cabendo ao Juízo, a partir deles, proceder à respectiva qualificação jurídica. "
    "Assim, reconhecida como verdadeira a base fática não impugnada e estando presentes os "
    "elementos necessários à solução da controvérsia, inexiste razão para instrução mediante "
    "produção de prova destinada justamente a demonstrar fatos que, por força da inércia "
    "processual do Réu, já se encontram submetidos aos efeitos do art. 344 do CPC.")

# ═══════════════════════════════════════════════════════════════════════
# 7. PEDIDOS — body introdutório (para 43) + alíneas (45-53)
# ═══════════════════════════════════════════════════════════════════════
replace_text(paras[43],
    "Diante do exposto, a Autora requer:")

# A) validez da citação + decurso (substitui 2 primeiras alíneas)
replace_text(paras[45],
    "seja reconhecida a validade da citação do Réu, realizada por carta com aviso de recebimento, "
    "considerando que o AR foi assinado pelo próprio destinatário, conforme evento 8;")
replace_text(paras[47],
    "seja certificado o decurso do prazo para contestação findo em 19 de agosto de 2026, "
    "conforme certidão lançada nos autos;")

# C) revelia + 344
replace_text(paras[49],
    "seja decretada a revelia do Réu, com a incidência dos efeitos materiais previstos no "
    "art. 344 do CPC, reputando-se verdadeiras as alegações de fato formuladas na petição "
    "inicial e não validamente impugnadas;")

# D) efeitos processuais 346
replace_text(paras[51],
    "sejam igualmente aplicados os efeitos processuais da revelia, especialmente aqueles "
    "previstos no art. 346 do CPC, na extensão legalmente cabível;")

# E) preclusão + julgamento antecipado (substitui penúltima alínea)
# Preciso de mais 2 alíneas — inserir após para 53
# Primeiro reescrever o que já existe (era d) julgamento antecipado)
replace_text(paras[53],
    "seja reconhecida a preclusão quanto à apresentação de defesa, impugnação específica dos "
    "fatos, alegação de matérias defensivas disponíveis e formulação de requerimentos "
    "probatórios que deveriam ter sido apresentados tempestivamente, ressalvadas apenas as "
    "matérias cognoscíveis de ofício e as hipóteses expressamente admitidas pela legislação "
    "processual;")

# Inserir 2 novas alíneas antes da última (subsid) = D julgamento + E subsidiária
# Para 53 era a última alínea existente antes do vazio; agora precisa de 2 mais
# Estrutura atual: 45(A), 47(B), 49(C), 51(D), 53(E-preclusão) → precisa: F(julgamento), G(subsid)

# Inserir F) julgamento antecipado após para 53
p_f = insert_paragraph_after(doc, paras[53],
    "reconhecida a suficiência do conjunto probatório já produzido e a incidência dos efeitos "
    "materiais da revelia, seja proferido julgamento antecipado do mérito, nos termos do "
    "art. 355, II, do CPC, com apreciação integral dos pedidos formulados pela Autora;",
    'RDAA Alínea')

# Recarrega parágrafos
paras = doc.paragraphs

# Encontrar o índice do parágrafo recém-inserido (F)
idx_f = None
for i, p in enumerate(paras):
    if 'reconhecida a suficiência' in p.text:
        idx_f = i
        break

# Inserir G) subsidiária após F
if idx_f:
    p_f_para = paras[idx_f]
    insert_paragraph_after(doc, p_f_para,
        "subsidiariamente, se por hipótese este d. Juízo entenda necessária alguma dilação "
        "probatória, sejam fixados os pontos controvertidos e delimitada a prova a ser "
        "realizada, promovendo-se o regular saneamento do feito.",
        'RDAA Alínea')

# ═══════════════════════════════════════════════════════════════════════
# 8. Remover alíneas antigas que ficaram sobressalentes
# ═══════════════════════════════════════════════════════════════════════
# Após inserções, podem ter ficado alíneas antigas "d)" e "e)" duplicadas
# Precisamos remover: "seja proferido o julgamento antecipado do mérito, na forma do CPC, art. 355, inciso I"
# e "subsidiariamente, caso este d. Juízo..." originais

paras = doc.paragraphs
to_remove = []
for i, p in enumerate(paras):
    if p.style.name == 'RDAA Alínea':
        txt = p.text.strip()
        if txt.startswith('seja proferido o julgamento antecipado do mérito, na forma do CPC, art. 355, inciso I'):
            to_remove.append(i)
        elif txt.startswith('subsidiariamente, caso este d. Juízo entenda necessária'):
            to_remove.append(i)

# Remover de trás para frente
for idx in sorted(to_remove, reverse=True):
    p_el = paras[idx]._p
    p_el.getparent().remove(p_el)

# ═══════════════════════════════════════════════════════════════════════
# 9. Salvar e verificar
# ═══════════════════════════════════════════════════════════════════════
doc.save(WORK)

# Reabrir e verificar estrutura
doc2 = Document(WORK)
print(f"Total parágrafos: {len(doc2.paragraphs)}")
for i, p in enumerate(doc2.paragraphs):
    if p.text.strip():
        style = p.style.name
        pics = len(p._p.findall('.//' + qn('w:drawing')))
        print(f"{i:02d} [{style}] pic={pics} | {p.text[:80]}...")

# Copiar para destino final
os.makedirs(os.path.dirname(OUT), exist_ok=True)
shutil.copy2(WORK, OUT)
print(f"\nSalvo em: {OUT}")
