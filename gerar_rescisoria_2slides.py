import base64

LOGO_PATH = "C:/Projetos/resolutivo-ai/skills/romano-donadel-slide-style/assets/logo_romano_donadel.png"
OUTPUT = "C:/Projetos/resolutivo-ai/rescisoria_trivale_minare_2slides.html"

with open(LOGO_PATH, "rb") as f:
    logo_uri = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Rescisória Trivale x Minare — Mecanismo e Erro de Fato</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap" rel="stylesheet">
<style>
  :root {{
    --rd-text: #63666A;
    --rd-black: #000000;
    --rd-accent: #F7A800;
    --rd-accent-light: #FFF8EB;
    --rd-bg: #FFFFFF;
    --rd-card: #F8FAFC;
    --rd-border: #E2E8F0;
    --rd-green: #047857;
    --rd-green-bg: #ECFDF5;
    --rd-green-border: #A7F3D0;
    --rd-red: #B91C1C;
    --rd-red-bg: #FEF2F2;
    --rd-red-border: #FECACA;
    --rd-neutral-bg: #EEF1F4;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Lato', sans-serif;
    background: #14181F;
    color: var(--rd-text);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    min-height: 100vh; overflow: hidden; padding: 16px;
  }}
  .deck-frame {{
    width: min(95vw, 1280px);
    aspect-ratio: 16 / 9;
    height: auto; max-height: 86vh;
    background: var(--rd-bg);
    box-shadow: 0 25px 60px rgba(0,0,0,0.55);
    border-radius: 8px;
    position: relative; overflow: hidden;
    display: flex; flex-direction: column;
  }}
  .slide {{
    display: none; width: 100%; height: 100%;
    padding: 30px 48px 22px 48px;
    flex-direction: column; justify-content: space-between;
    overflow: hidden; background: var(--rd-bg);
  }}
  .slide.active {{ display: flex; animation: fadeIn 0.2s ease-out; }}
  @keyframes fadeIn {{ from {{ opacity:0; transform: scale(0.995); }} to {{ opacity:1; transform: scale(1); }} }}

  .slide-header {{
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 2px solid #F1F5F9; padding-bottom: 12px; margin-bottom: 18px; flex-shrink: 0;
  }}
  .header-left {{ display: flex; align-items: center; gap: 12px; }}
  .accent-bar {{ width: 5px; height: 40px; background: var(--rd-accent); border-radius: 2px; }}
  .eyebrow {{
    font-size: 10.5px; font-weight: 900; letter-spacing: 1.2px; color: var(--rd-accent);
    text-transform: uppercase; margin-bottom: 3px;
  }}
  .action-title {{
    font-size: 21px; font-weight: 900; color: var(--rd-black);
    text-transform: uppercase; letter-spacing: -0.3px; line-height: 1.2; max-width: 900px;
  }}
  .header-logo {{ height: 32px; object-fit: contain; }}

  .slide-body {{ flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 20px; overflow: hidden; }}

  .slide-footer {{
    display: flex; justify-content: space-between; align-items: center;
    border-top: 1px solid var(--rd-border); padding-top: 8px;
    font-size: 10px; color: var(--rd-text); font-weight: 700; letter-spacing: 0.5px; flex-shrink: 0;
  }}
  .page-indicator {{ color: var(--rd-black); font-weight: 900; }}

  .nav-bar {{
    width: min(95vw, 1280px); margin-top: 10px;
    display: flex; justify-content: space-between; align-items: center;
    color: #9CA3AF; font-size: 12px; font-weight: 600;
  }}
  .nav-btns {{ display: flex; gap: 8px; }}
  .nav-btn {{
    background: #1E293B; color: #F8FAFC; border: 1px solid #334155;
    padding: 6px 14px; border-radius: 5px; font-weight: 700; font-size: 12px;
    font-family: 'Lato', sans-serif; cursor: pointer; transition: all .15s;
  }}
  .nav-btn:hover {{ background: #334155; border-color: var(--rd-accent); color: #fff; }}
  .nav-btn:disabled {{ opacity: .35; cursor: not-allowed; }}
  .dots {{ display: flex; gap: 7px; }}
  .dot {{ width: 9px; height: 9px; border-radius: 50%; background: #475569; cursor: pointer; transition: .2s; }}
  .dot.active {{ background: var(--rd-accent); transform: scale(1.3); }}

  /* ===== SLIDE 1: MECANISMO (fluxo operacional + cadeia documental) ===== */
  .flow-block-title {{
    font-size: 12px; font-weight: 900; color: var(--rd-black);
    text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 10px;
    display: flex; align-items: center; gap: 8px;
  }}
  .flow-block-title .n {{
    width: 22px; height: 22px; border-radius: 50%; background: var(--rd-black); color: var(--rd-accent);
    font-size: 11px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  }}
  .flow-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; }}
  .flow-card {{
    background: var(--rd-card); border: 1.5px solid var(--rd-border); border-radius: 6px;
    padding: 14px 15px; margin-right: 26px; position: relative;
  }}
  .flow-card:last-child {{ margin-right: 0; }}
  .flow-card::after {{
    content: '➔'; position: absolute; right: -24px; top: 50%; transform: translateY(-50%);
    color: var(--rd-accent); font-size: 18px; font-weight: 900;
  }}
  .flow-card:last-child::after {{ content: ''; }}
  .flow-card .actor {{
    display: inline-block; font-size: 9px; font-weight: 900; color: var(--rd-black);
    background: var(--rd-accent-light); border: 1px solid #FCD34D; padding: 1px 7px; border-radius: 3px; margin-bottom: 6px;
  }}
  .flow-card .title {{ font-size: 12px; font-weight: 900; color: var(--rd-black); margin-bottom: 5px; text-transform: uppercase; }}
  .flow-card .desc {{ font-size: 10.5px; color: var(--rd-text); line-height: 1.4; }}

  .doc-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; }}
  .doc-card {{
    background: var(--rd-bg); border: 1.5px solid var(--rd-black); border-radius: 6px;
    padding: 13px 14px; margin-right: 22px; position: relative;
  }}
  .doc-card:last-child {{ margin-right: 0; }}
  .doc-card::after {{
    content: '⟶'; position: absolute; right: -20px; top: 50%; transform: translateY(-50%);
    color: var(--rd-black); font-size: 15px;
  }}
  .doc-card:last-child::after {{ content: ''; }}
  .doc-card .step-tag {{ font-size: 9px; font-weight: 900; color: var(--rd-accent); text-transform: uppercase; margin-bottom: 4px; }}
  .doc-card .title {{ font-size: 11.5px; font-weight: 900; color: var(--rd-black); text-transform: uppercase; margin-bottom: 4px; }}
  .doc-card .proves {{ font-size: 10px; color: var(--rd-text); line-height: 1.35; }}

  /* IDEIA CENTRAL — bloco autônomo, escala próxima ao título, isolado do texto de apoio */
  .core-idea-block {{
    display: flex; align-items: flex-start; gap: 14px;
  }}
  .core-idea-mark {{
    width: 6px; align-self: stretch; background: var(--rd-accent); border-radius: 3px; flex-shrink: 0;
  }}
  .core-idea-text {{
    font-size: 19px; font-weight: 900; color: var(--rd-black);
    line-height: 1.25; letter-spacing: -0.2px;
  }}
  .support-text {{
    font-size: 11px; font-weight: 400; color: var(--rd-text); line-height: 1.4;
    margin-top: 6px; padding-left: 20px;
  }}

  /* ===== SLIDE 2: ERRO DE FATO (decomposição — parte-todo) ===== */
  .decomp-anchor-row {{ display: flex; align-items: baseline; gap: 12px; }}
  .decomp-anchor-label {{
    font-size: 12.5px; font-weight: 700; color: var(--rd-text); text-transform: uppercase; letter-spacing: 0.4px;
  }}
  .decomp-anchor-val {{ font-size: 26px; font-weight: 900; color: var(--rd-black); }}

  .bar-track {{
    width: 100%; height: 64px; border-radius: 8px; overflow: hidden;
    display: flex; border: 2px solid var(--rd-black); margin-top: 10px;
  }}
  .bar-seg {{ height: 100%; display: flex; align-items: center; justify-content: center; position: relative; }}
  .bar-seg.pago {{ background: var(--rd-green-bg); border-right: 3px solid #FFFFFF; }}
  .bar-seg.dup {{ background: var(--rd-neutral-bg); border-right: 3px solid #FFFFFF; }}
  .bar-seg.aberto {{ background: var(--rd-red-bg); }}
  .bar-seg-label {{ font-size: 13px; font-weight: 900; white-space: nowrap; }}
  .bar-seg.pago .bar-seg-label {{ color: var(--rd-green); }}
  .bar-seg.aberto .bar-seg-label {{ color: var(--rd-red); }}
  .bar-seg.dup .bar-seg-label {{ color: #64748B; font-size: 9px; }}

  .callouts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
  .callout {{ padding: 13px 16px; border-radius: 6px; }}
  .callout.pago {{ background: var(--rd-green-bg); border-left: 5px solid var(--rd-green); }}
  .callout.aberto {{ background: var(--rd-red-bg); border-left: 5px solid var(--rd-red); }}
  .callout-title {{ font-size: 11px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 4px; }}
  .callout.pago .callout-title {{ color: var(--rd-green); }}
  .callout.aberto .callout-title {{ color: var(--rd-red); }}
  .callout-val {{ font-size: 20px; font-weight: 900; color: var(--rd-black); margin-bottom: 4px; }}
  .callout-desc {{ font-size: 11px; color: var(--rd-text); line-height: 1.4; }}

  .nota-dup {{ font-size: 10px; color: #94A3B8; font-weight: 700; margin-top: 2px; }}
</style>
</head>
<body>

<div class="deck-frame">

  <!-- SLIDE 1: MECANISMO — CADEIA DE RECEBÍVEIS -->
  <div class="slide active" id="slide-1">
    <div class="slide-header">
      <div class="header-left">
        <div class="accent-bar"></div>
        <div>
          <div class="eyebrow">Mecanismo — Ação Rescisória nº 1.0000.26.447718-3/000</div>
          <div class="action-title">Cada Repasse Deixa um Rastro Documental Completo</div>
        </div>
      </div>
      <img src="{logo_uri}" class="header-logo" alt="Romano Donadel">
    </div>

    <div class="slide-body">
      <div>
        <div class="flow-block-title"><span class="n">1</span>Fluxo Operacional — o dinheiro</div>
        <div class="flow-row">
          <div class="flow-card">
            <span class="actor">Minare (loja)</span>
            <div class="title">Venda no cartão</div>
            <div class="desc">Cliente final paga na Minare com o cartão da rede Valecard.</div>
          </div>
          <div class="flow-card">
            <span class="actor">Trivale (rede)</span>
            <div class="title">Apuração</div>
            <div class="desc">Trivale registra a transação e desconta a taxa (MDR).</div>
          </div>
          <div class="flow-card">
            <span class="actor">Trivale → Minare</span>
            <div class="title">Repasse</div>
            <div class="desc">Valor líquido transferido por TED/DOC, individual ou agrupado.</div>
          </div>
          <div class="flow-card">
            <span class="actor">Trivale (documenta)</span>
            <div class="title">Registro</div>
            <div class="desc">Extrato de Conveniada lista quais títulos aquele repasse quitou.</div>
          </div>
        </div>
      </div>

      <div>
        <div class="flow-block-title"><span class="n">2</span>Cadeia Documental — a prova, título a título</div>
        <div class="doc-row">
          <div class="doc-card">
            <div class="step-tag">Etapa 1</div>
            <div class="title">Título de venda</div>
            <div class="proves">Prova que a obrigação existiu — é o que o laudo listou como "em aberto".</div>
          </div>
          <div class="doc-card">
            <div class="step-tag">Etapa 2</div>
            <div class="title">Extrato de Conveniada</div>
            <div class="proves">Prova que aquele título foi liquidado — valor bruto e líquido.</div>
          </div>
          <div class="doc-card">
            <div class="step-tag">Etapa 3</div>
            <div class="title">Agrupamento bancário</div>
            <div class="proves">Quando aplicável: vários títulos pagos num único lote.</div>
          </div>
          <div class="doc-card">
            <div class="step-tag">Etapa 4</div>
            <div class="title">TED / DOC</div>
            <div class="proves">Prova bancária final: o valor efetivamente saiu e chegou.</div>
          </div>
        </div>
      </div>

      <div class="core-idea-block">
        <div class="core-idea-mark"></div>
        <div>
          <div class="core-idea-text">A quitação só está provada quando as 4 etapas se conectam.</div>
          <div class="support-text">Título, extrato, agrupamento (quando houver) e comprovante bancário — nenhuma etapa isolada basta.</div>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS ASSOCIADOS</span>
      <span class="page-indicator">SLIDE 01 / 02</span>
    </div>
  </div>

  <!-- SLIDE 2: ERRO DE FATO — DECOMPOSIÇÃO PARTE-TODO -->
  <div class="slide" id="slide-2">
    <div class="slide-header">
      <div class="header-left">
        <div class="accent-bar"></div>
        <div>
          <div class="eyebrow">Erro de Fato — CPC, art. 966, VIII e §1º</div>
          <div class="action-title">Dentro da Dívida Apontada, Quanto Já Foi Pago?</div>
        </div>
      </div>
      <img src="{logo_uri}" class="header-logo" alt="Romano Donadel">
    </div>

    <div class="slide-body">
      <div>
        <div class="decomp-anchor-row">
          <span class="decomp-anchor-label">Valor que a sentença tratou como devido:</span>
          <span class="decomp-anchor-val">R$ 150.730,93</span>
        </div>

        <!-- UMA barra = O total devido. Ela se divide — nunca é comparada a outro total. -->
        <div class="bar-track">
          <div class="bar-seg pago" style="width: 85.2%;">
            <span class="bar-seg-label">✓ JÁ PAGO — R$ 128.370,50</span>
          </div>
          <div class="bar-seg dup" style="width: 2.5%;">
            <span class="bar-seg-label">AJUSTE</span>
          </div>
          <div class="bar-seg aberto" style="width: 12.3%;">
            <span class="bar-seg-label">R$ 18.523,21</span>
          </div>
        </div>
        <div class="nota-dup">Faixa cinza (R$ 3.837,22): valor contado duas vezes no laudo — não é dívida nem pagamento, é erro de soma já descontado nos números ao lado.</div>
      </div>

      <div class="callouts">
        <div class="callout pago">
          <div class="callout-title">Dentro do valor devido: já pago</div>
          <div class="callout-val">R$ 128.370,50</div>
          <div class="callout-desc">85% do que a sentença tratou como dívida já tinha comprovante nos autos — título, extrato e TED/DOC — antes mesmo da sentença.</div>
        </div>
        <div class="callout aberto">
          <div class="callout-title">Dentro do valor devido: realmente em aberto</div>
          <div class="callout-val">R$ 18.523,21</div>
          <div class="callout-desc">Única fração que sobra como dívida real depois de descontar o que já foi pago. A Trivale não contesta esse valor.</div>
        </div>
      </div>

      <div class="core-idea-block">
        <div class="core-idea-mark"></div>
        <div>
          <div class="core-idea-text">85% do valor tratado como dívida já estava pago e documentado.</div>
          <div class="support-text">A sentença nunca cruzou o título com o comprovante — isso é erro de fato (CPC, art. 966, VIII), não rediscussão de mérito.</div>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS ASSOCIADOS</span>
      <span class="page-indicator">SLIDE 02 / 02</span>
    </div>
  </div>

</div>

<div class="nav-bar">
  <div class="nav-btns">
    <button class="nav-btn" id="prevBtn" onclick="changeSlide(-1)">◀ Anterior</button>
    <button class="nav-btn" id="nextBtn" onclick="changeSlide(1)">Próximo ▶</button>
  </div>
  <div class="dots" id="dotsContainer"></div>
  <div>Navegue com [◀ / ▶] ou barra de espaço</div>
</div>

<script>
  let currentSlide = 1;
  const totalSlides = 2;
  function init() {{
    const c = document.getElementById('dotsContainer');
    c.innerHTML = '';
    for (let i = 1; i <= totalSlides; i++) {{
      const d = document.createElement('div');
      d.className = `dot ${{i === 1 ? 'active' : ''}}`;
      d.onclick = () => goToSlide(i);
      c.appendChild(d);
    }}
    updateUI();
  }}
  function changeSlide(dir) {{ goToSlide(currentSlide + dir); }}
  function goToSlide(t) {{
    if (t < 1 || t > totalSlides) return;
    document.getElementById(`slide-${{currentSlide}}`).classList.remove('active');
    currentSlide = t;
    document.getElementById(`slide-${{currentSlide}}`).classList.add('active');
    updateUI();
  }}
  function updateUI() {{
    document.getElementById('prevBtn').disabled = currentSlide === 1;
    document.getElementById('nextBtn').disabled = currentSlide === totalSlides;
    document.querySelectorAll('.dot').forEach((d, i) => d.classList.toggle('active', i + 1 === currentSlide));
  }}
  document.addEventListener('keydown', (e) => {{
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') changeSlide(1);
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') changeSlide(-1);
  }});
  init();
</script>
</body>
</html>
"""

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

print("Deck de 2 slides gerado em:", OUTPUT)
