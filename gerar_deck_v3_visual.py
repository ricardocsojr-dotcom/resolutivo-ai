import base64
import os

LOGO_PATH = "C:/Projetos/resolutivo-ai/skills/romano-donadel-slide-style/assets/logo_romano_donadel.png"
HTML_OUTPUT = "C:/Projetos/resolutivo-ai/Apresentacao_Caso_Silvio_Afonso_Romano_Donadel.html"

with open(LOGO_PATH, "rb") as f:
    logo_b64 = f.read()
logo_uri = f"data:image/png;base64,{base64.b64encode(logo_b64).decode('utf-8')}"

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Caso Sílvio Luiz Afonso — Estratégia Visual RDAA</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap" rel="stylesheet">
  <style>
    :root {{
      --rd-background: #FFFFFF;
      --rd-text-dark: #0F172A;
      --rd-structure: #63666A;
      --rd-accent: #F7A800;
      --rd-accent-light: #FFF8EB;
      --rd-card-bg: #F8FAFC;
      --rd-card-border: #E2E8F0;
      --rd-card-dark: #0F172A;
      --rd-card-dark-text: #F8FAFC;
      --rd-success-bg: #ECFDF5;
      --rd-success-text: #047857;
      --rd-success-border: #A7F3D0;
      --rd-danger-bg: #FEF2F2;
      --rd-danger-text: #B91C1C;
      --rd-danger-border: #FECACA;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Lato', sans-serif;
      background-color: #090D16;
      color: var(--rd-text-dark);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      overflow: hidden;
      padding: 16px;
    }}

    /* STRICT 16:9 VIEWPORT FITTED FRAME */
    .deck-frame {{
      width: min(95vw, 1220px);
      aspect-ratio: 16 / 9;
      height: auto;
      max-height: 85vh;
      background-color: var(--rd-background);
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.65);
      border-radius: 8px;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    .slide {{
      display: none;
      width: 100%;
      height: 100%;
      padding: 28px 44px 20px 44px;
      flex-direction: column;
      justify-content: space-between;
      overflow: hidden;
      background-color: var(--rd-background);
    }}

    .slide.active {{
      display: flex;
      animation: fadeIn 0.22s ease-out;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: scale(0.995); }}
      to {{ opacity: 1; transform: scale(1); }}
    }}

    /* HEADER */
    .slide-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #F1F5F9;
      padding-bottom: 12px;
      margin-bottom: 14px;
      flex-shrink: 0;
    }}

    .header-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .accent-bar {{
      width: 5px;
      height: 38px;
      background: linear-gradient(to bottom, var(--rd-accent), #E69500);
      border-radius: 2px;
    }}

    .action-category {{
      font-size: 10px;
      font-weight: 900;
      letter-spacing: 1.4px;
      color: var(--rd-accent);
      text-transform: uppercase;
      margin-bottom: 2px;
    }}

    .action-title {{
      font-size: 20px;
      font-weight: 900;
      color: var(--rd-text-dark);
      text-transform: uppercase;
      letter-spacing: -0.3px;
    }}

    .header-logo {{
      height: 34px;
      object-fit: contain;
    }}

    /* BODY */
    .slide-body {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      overflow: hidden;
      gap: 12px;
    }}

    /* FOOTER */
    .slide-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid var(--rd-card-border);
      padding-top: 8px;
      font-size: 10px;
      color: var(--rd-structure);
      font-weight: 700;
      letter-spacing: 0.6px;
      flex-shrink: 0;
    }}

    .page-indicator {{
      color: var(--rd-text-dark);
      font-weight: 900;
    }}

    /* NAVIGATION CONTROLS */
    .nav-bar {{
      width: min(95vw, 1220px);
      margin-top: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: #94A3B8;
      font-size: 12px;
      font-weight: 600;
    }}

    .nav-btns {{
      display: flex;
      gap: 8px;
    }}

    .nav-btn {{
      background-color: #1E293B;
      color: #F8FAFC;
      border: 1px solid #334155;
      padding: 6px 14px;
      border-radius: 5px;
      font-weight: 700;
      font-size: 12px;
      font-family: 'Lato', sans-serif;
      cursor: pointer;
      transition: all 0.15s;
    }}

    .nav-btn:hover {{
      background-color: #334155;
      border-color: var(--rd-accent);
      color: #FFFFFF;
    }}

    .nav-btn:disabled {{
      opacity: 0.35;
      cursor: not-allowed;
    }}

    .dots {{
      display: flex;
      gap: 7px;
    }}

    .dot {{
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background-color: #475569;
      cursor: pointer;
      transition: 0.2s;
    }}

    .dot.active {{
      background-color: var(--rd-accent);
      transform: scale(1.3);
    }}

    /* BADGES */
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 9px;
      border-radius: 4px;
      font-size: 9.5px;
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .badge-gold {{
      background-color: var(--rd-accent-light);
      color: #B45309;
      border: 1px solid #FCD34D;
    }}

    .badge-green {{
      background-color: var(--rd-success-bg);
      color: var(--rd-success-text);
      border: 1px solid var(--rd-success-border);
    }}

    .badge-danger {{
      background-color: var(--rd-danger-bg);
      color: var(--rd-danger-text);
      border: 1px solid var(--rd-danger-border);
    }}

    .badge-dark {{
      background-color: #0F172A;
      color: #FFFFFF;
    }}

    /* SLIDE 1: CAPA EDITORIAL DE ALTO IMPACTO */
    .cover-layout {{
      display: flex;
      height: 100%;
      gap: 40px;
      align-items: stretch;
    }}

    .cover-left-column {{
      width: 42%;
      background: linear-gradient(145deg, #0F172A 0%, #1E293B 100%);
      border-radius: 6px;
      padding: 32px 28px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      color: #FFFFFF;
      position: relative;
      overflow: hidden;
    }}

    .cover-left-column::after {{
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 6px;
      background-color: var(--rd-accent);
    }}

    .cover-kpi-stack {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .cover-kpi-item {{
      border-left: 3px solid var(--rd-accent);
      padding-left: 12px;
    }}

    .cover-kpi-val {{
      font-size: 24px;
      font-weight: 900;
      color: #FFFFFF;
      line-height: 1.1;
    }}

    .cover-kpi-lbl {{
      font-size: 11px;
      font-weight: 700;
      color: #94A3B8;
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }}

    .cover-right-column {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 10px 0;
    }}

    .cover-headline-block {{
      margin: auto 0;
    }}

    .cover-headline {{
      font-size: 38px;
      font-weight: 900;
      color: var(--rd-text-dark);
      line-height: 1.1;
      letter-spacing: -0.8px;
      margin-bottom: 12px;
    }}

    .cover-subheadline {{
      font-size: 16.5px;
      font-weight: 400;
      color: var(--rd-structure);
      line-height: 1.45;
      margin-bottom: 24px;
    }}

    .cover-pills-row {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .cover-meta-pill {{
      display: flex;
      align-items: center;
      gap: 8px;
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      padding: 8px 14px;
      border-radius: 5px;
      font-size: 11.5px;
      font-weight: 700;
    }}

    /* SLIDE 2: BENTO GRID EXECUTIVO */
    .bento-grid {{
      display: grid;
      grid-template-columns: 1.2fr 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 14px;
      height: 100%;
    }}

    .bento-card {{
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-radius: 6px;
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
    }}

    .bento-card.dark {{
      background-color: #0F172A;
      color: #FFFFFF;
      border-color: #1E293B;
    }}

    .bento-card.highlight {{
      background-color: var(--rd-accent-light);
      border: 1.5px solid var(--rd-accent);
    }}

    .bento-huge-num {{
      font-size: 42px;
      font-weight: 900;
      line-height: 1;
      color: var(--rd-accent);
      margin-bottom: 4px;
    }}

    .bento-title {{
      font-size: 13.5px;
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }}

    .bento-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 12px;
      font-weight: 700;
    }}

    .bento-list li {{
      display: flex;
      align-items: center;
      gap: 7px;
    }}

    /* SLIDE 3 & 4: DIAGRAMA DE FLUXO SVG (STYLE ARCHITECTURE-DIAGRAM) */
    .diagram-canvas {{
      width: 100%;
      height: 100%;
      background: #FFFFFF;
      border: 1px solid var(--rd-card-border);
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 12px;
    }}

    /* SLIDE 5: 2X2 DECISION MATRIX */
    .matrix-2x2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 14px;
      height: 100%;
    }}

    .matrix-quad {{
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-radius: 6px;
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .matrix-quad.winner {{
      background-color: var(--rd-accent-light);
      border: 2px solid var(--rd-accent);
    }}

    .matrix-quad.error {{
      background-color: var(--rd-danger-bg);
      border: 1px solid var(--rd-danger-border);
    }}

    .matrix-quad.success {{
      background-color: var(--rd-success-bg);
      border: 1.5px solid var(--rd-success-border);
    }}

    .quad-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}

    .quad-title {{
      font-size: 13px;
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }}

    .quad-body {{
      font-size: 12.5px;
      font-weight: 700;
      line-height: 1.45;
    }}

    /* SLIDE 6: DEFENSE IN DEPTH / BARREIRA */
    .barrier-grid {{
      display: grid;
      grid-template-columns: 1.1fr 70px 1.4fr;
      gap: 14px;
      align-items: center;
      height: 100%;
    }}

    .barrier-col {{
      height: 100%;
      border-radius: 6px;
      padding: 22px 24px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .shield-separator {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }}

    .shield-badge {{
      width: 52px;
      height: 52px;
      border-radius: 50%;
      background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
      color: var(--rd-accent);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 20px rgba(15, 23, 42, 0.3);
    }}

    /* SLIDE 7: CHEVRONS TIMELINE */
    .chevron-timeline {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      height: 100%;
      align-items: stretch;
    }}

    .chevron-box {{
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-radius: 6px;
      padding: 18px 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
    }}

    .chevron-box.active {{
      background-color: var(--rd-accent-light);
      border: 2px solid var(--rd-accent);
    }}

    .step-badge {{
      width: 30px;
      height: 30px;
      border-radius: 50%;
      background-color: #0F172A;
      color: #FFFFFF;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
      font-weight: 900;
      margin-bottom: 12px;
    }}

    .chevron-box.active .step-badge {{
      background-color: var(--rd-accent);
      color: #0F172A;
    }}

    .step-title {{
      font-size: 13px;
      font-weight: 900;
      color: var(--rd-text-dark);
      text-transform: uppercase;
      line-height: 1.3;
      margin-bottom: 8px;
    }}

    .step-desc {{
      font-size: 12px;
      color: var(--rd-structure);
      font-weight: 700;
      line-height: 1.45;
    }}
  </style>
</head>
<body>

  <!-- 16:9 DECK FRAME -->
  <div class="deck-frame">

    <!-- SLIDE 1: CAPA EDITORIAL DE ALTO IMPACTO -->
    <div class="slide active" id="slide-1">
      <div class="cover-layout">
        <div class="cover-left-column">
          <div>
            <div class="badge badge-gold" style="margin-bottom: 20px;">ROMANO DONADEL ADVOGADOS</div>
            <div style="font-size: 12px; font-weight: 900; color: var(--rd-accent); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Núcleo Contencioso Estratégico</div>
            <div style="font-size: 19px; font-weight: 900; color: #FFFFFF; line-height: 1.25;">Defesa Patrimonial & Blindagem de Meação</div>
          </div>
          <div class="cover-kpi-stack">
            <div class="cover-kpi-item">
              <div class="cover-kpi-val">03 FRENTES</div>
              <div class="cover-kpi-lbl">Ações Judiciais Coordenadas</div>
            </div>
            <div class="cover-kpi-item">
              <div class="cover-kpi-val">R$ 0 DE MULTA</div>
              <div class="cover-kpi-lbl">Astreintes Revogadas no TJMG</div>
            </div>
            <div class="cover-kpi-item">
              <div class="cover-kpi-val">100% BLINDADO</div>
              <div class="cover-kpi-lbl">Apartamento Sense Preservado</div>
            </div>
          </div>
        </div>

        <div class="cover-right-column">
          <div style="display: flex; justify-content: flex-end;">
            <img src="{logo_uri}" alt="Romano Donadel" class="header-logo" style="height: 40px;">
          </div>
          <div class="cover-headline-block">
            <div class="badge badge-dark" style="margin-bottom: 12px;">RELATÓRIO EXECUTIVO RDAA</div>
            <h1 class="cover-headline">CASO SÍLVIO LUIZ AFONSO</h1>
            <p class="cover-subheadline">Estratégia Processual Integrada, Responsabilidade Tributária do Imóvel Ocupado e Governança de Acervo</p>
            <div class="cover-pills-row">
              <div class="cover-meta-pill">
                <span>👤 Cliente: <strong>Sílvio Luiz Afonso</strong></span>
              </div>
              <div class="cover-meta-pill">
                <span>⚖ Adversa: <strong>Ana Lúcia de Oliveira Afonso</strong></span>
              </div>
              <div class="cover-meta-pill">
                <span>📅 <strong>Setembro / 2026</strong></span>
              </div>
            </div>
          </div>
          <div class="slide-footer" style="border-top: none; padding-top: 0;">
            <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS ASSOCIADOS</span>
            <span class="page-indicator">SLIDE 01 / 07</span>
          </div>
        </div>
      </div>
    </div>

    <!-- SLIDE 2: BENTO GRID EXECUTIVO (GOVERNANÇA DO CASO) -->
    <div class="slide" id="slide-2">
      <div class="slide-header">
        <div class="header-left">
          <div class="accent-bar"></div>
          <div>
            <div class="action-category">Visão Geral & Governança</div>
            <div class="action-title">Arquitetura Estratégica do Contencioso</div>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="bento-grid">
          <!-- Card 1: Monumental 3 Frentes (Spans 2 rows) -->
          <div class="bento-card dark" style="grid-row: span 2;">
            <div>
              <span class="badge badge-gold">Gestão Coordenada</span>
              <div class="bento-huge-num" style="margin-top: 8px;">03</div>
              <div class="bento-title" style="color: #FFFFFF;">Frentes Processuais</div>
              <p style="font-size: 12px; color: #94A3B8; margin-bottom: 16px;">Segregação absoluta entre débitos reais, alimentos e partilha patrimonial.</p>
              <ul class="bento-list" style="color: #F8FAFC;">
                <li><span style="color: var(--rd-accent);">●</span> <strong>3ª Vara Família:</strong> Divórcio & Partilha</li>
                <li><span style="color: var(--rd-accent);">●</span> <strong>TJMG (8ª Câm.):</strong> Agravo IPTU Begônias</li>
                <li><span style="color: var(--rd-accent);">●</span> <strong>10ª Cível:</strong> Arbitramento Aluguel</li>
              </ul>
            </div>
            <div style="padding-top: 12px; border-top: 1px solid #334155; font-size: 11px; color: #94A3B8;">
              Status: <strong>Controle total das instâncias</strong>
            </div>
          </div>

          <!-- Card 2: Imóveis Mapeados -->
          <div class="bento-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <div>
                <span class="badge badge-dark">Acervos</span>
                <div class="bento-title" style="margin-top: 6px;">02 Imóveis Centrais</div>
              </div>
              <span style="font-size: 20px;">🏠</span>
            </div>
            <div style="font-size: 12px; font-weight: 700; color: var(--rd-text-dark); line-height: 1.4;">
              <div>• <strong>Rua das Begônias:</strong> Fruição exclusiva de Ana</div>
              <div>• <strong>Ed. Sense Vertical:</strong> Particular de Sílvio</div>
            </div>
            <div style="font-size: 11px; color: #047857; font-weight: 900;">✓ Incomunicabilidade blindada</div>
          </div>

          <!-- Card 3: Vitória Liminar TJMG -->
          <div class="bento-card highlight">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <div>
                <span class="badge badge-green">Decisão TJMG</span>
                <div class="bento-title" style="margin-top: 6px; color: #B45309;">Vitória Recursal AI /006</div>
              </div>
              <span style="font-size: 20px;">⚖</span>
            </div>
            <div style="font-size: 12px; font-weight: 700; color: var(--rd-text-dark); line-height: 1.4;">
              <div>• <strong>Astreintes de R$ 10k:</strong> Revogadas</div>
              <div>• <strong>IPTU Begônias:</strong> Obrigação mantida para Ana</div>
            </div>
            <div style="font-size: 11px; color: #B45309; font-weight: 900;">★ Risco financeiro extinto</div>
          </div>

          <!-- Card 4: Saneador Ajustado -->
          <div class="bento-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <div>
                <span class="badge badge-gold">10ª Vara Cível</span>
                <div class="bento-title" style="margin-top: 6px;">Saneador Art. 357, §1º</div>
              </div>
              <span style="font-size: 20px;">📜</span>
            </div>
            <div style="font-size: 12px; font-weight: 700; color: var(--rd-text-dark); line-height: 1.4;">
              <div>• <strong>Fato Gerador:</strong> Dispensa de esbulho físico</div>
              <div>• <strong>Termo Inicial:</strong> Piso garantido na citação</div>
            </div>
            <div style="font-size: 11px; color: var(--rd-accent); font-weight: 900;">➜ Estabilização pré-perícia</div>
          </div>

          <!-- Card 5: Blindagem de Alimentos -->
          <div class="bento-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <div>
                <span class="badge badge-dark">Alimentos</span>
                <div class="bento-title" style="margin-top: 6px;">Segregação Estrita</div>
              </div>
              <span style="font-size: 20px;">🛡</span>
            </div>
            <div style="font-size: 12px; font-weight: 700; color: var(--rd-text-dark); line-height: 1.4;">
              <div>• Bloqueio total a tentativas de compensação</div>
              <div>• Execução de 4,5 SM mantida em via própria</div>
            </div>
            <div style="font-size: 11px; color: #047857; font-weight: 900;">✓ Blindagem patrimonial ativa</div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS ASSOCIADOS</span>
        <span class="page-indicator">SLIDE 02 / 07</span>
      </div>
    </div>

    <!-- SLIDE 3: DIAGRAMA DE FLUXO VETORIAL (MAPA DE LITIGIOSIDADE) -->
    <div class="slide" id="slide-3">
      <div class="slide-header">
        <div class="header-left">
          <div class="accent-bar"></div>
          <div>
            <div class="action-category">Estrutura de Litigância</div>
            <div class="action-title">Mapeamento Dinâmico das Demandas Cruzadas</div>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="diagram-canvas">
          <svg width="100%" height="100%" viewBox="0 0 1080 340" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#F7A800" />
              </marker>
              <marker id="arrow-dark" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748B" />
              </marker>
            </defs>

            <!-- CONNECTOR LINES -->
            <path d="M 180 85 L 260 85" stroke="#CBD5E1" stroke-width="2" marker-end="url(#arrow-dark)" />
            <path d="M 520 85 L 600 85" stroke="#F7A800" stroke-width="2.5" marker-end="url(#arrow)" />
            <path d="M 520 250 L 600 250" stroke="#F7A800" stroke-width="2.5" marker-end="url(#arrow)" />
            <path d="M 180 250 L 260 250" stroke="#CBD5E1" stroke-width="2" marker-end="url(#arrow-dark)" />
            <path d="M 390 135 L 390 195" stroke="#F7A800" stroke-width="2" stroke-dasharray="4 4" />

            <!-- NODE 1: DIVÓRCIO & ALIMENTOS -->
            <rect x="20" y="40" width="160" height="90" rx="6" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.5" />
            <text x="35" y="65" font-family="Lato" font-size="10" font-weight="900" fill="#64748B">VARA DE FAMÍLIA</text>
            <text x="35" y="85" font-family="Lato" font-size="13" font-weight="900" fill="#0F172A">Divórcio & Alimentos</text>
            <text x="35" y="105" font-family="Lato" font-size="10.5" font-weight="700" fill="#64748B">Execução autônoma</text>

            <!-- NODE 2: INCIDENTE IPTU BEGÔNIAS -->
            <rect x="260" y="40" width="260" height="90" rx="6" fill="#FFF8EB" stroke="#F7A800" stroke-width="2" />
            <text x="280" y="65" font-family="Lato" font-size="10" font-weight="900" fill="#B45309">INCIDENTE RECURSAL</text>
            <text x="280" y="85" font-family="Lato" font-size="14" font-weight="900" fill="#0F172A">Agravo nº 1.0000.23.../006</text>
            <text x="280" y="105" font-family="Lato" font-size="11" font-weight="700" fill="#64748B">TJMG — 8ª Câmara Cível Especializada</text>

            <!-- NODE 3: VITÓRIA TJMG -->
            <rect x="600" y="40" width="460" height="90" rx="6" fill="#ECFDF5" stroke="#10B981" stroke-width="2" />
            <text x="625" y="65" font-family="Lato" font-size="10" font-weight="900" fill="#047857">DECISÃO COLEGIADA / LIMINAR</text>
            <text x="625" y="85" font-family="Lato" font-size="14" font-weight="900" fill="#065F46">Astreintes Revogadas + Dever de Pagar Mantido para Ana</text>
            <text x="625" y="105" font-family="Lato" font-size="11" font-weight="700" fill="#047857">★ Inadmissível transferir ônus de posse exclusiva para Sílvio</text>

            <!-- NODE 4: ARBITRAMENTO ALUGUÉIS -->
            <rect x="20" y="200" width="160" height="95" rx="6" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.5" />
            <text x="35" y="225" font-family="Lato" font-size="10" font-weight="900" fill="#64748B">10ª VARA CÍVEL</text>
            <text x="35" y="245" font-family="Lato" font-size="13" font-weight="900" fill="#0F172A">Ação Arbitramento</text>
            <text x="35" y="265" font-family="Lato" font-size="10.5" font-weight="700" fill="#64748B">Aluguel Casa Begônias</text>

            <!-- NODE 5: SANEADOR & RECONVENÇÃO -->
            <rect x="260" y="200" width="260" height="95" rx="6" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.5" />
            <text x="280" y="225" font-family="Lato" font-size="10" font-weight="900" fill="#F7A800">SANEADOR & RECONVENÇÃO</text>
            <text x="280" y="245" font-family="Lato" font-size="13.5" font-weight="900" fill="#0F172A">Ajuste do Art. 357, §1º CPC</text>
            <text x="280" y="265" font-family="Lato" font-size="11" font-weight="700" fill="#64748B">Delimitação de ônus probatório</text>

            <!-- NODE 6: BLINDAGEM ED. SENSE -->
            <rect x="600" y="200" width="460" height="95" rx="6" fill="#F8FAFC" stroke="#0F172A" stroke-width="2" />
            <text x="625" y="225" font-family="Lato" font-size="10" font-weight="900" fill="#0F172A">BLINDAGEM PATRIMONIAL RDAA</text>
            <text x="625" y="245" font-family="Lato" font-size="14" font-weight="900" fill="#0F172A">Ônus Constitutivo Primário Exclusivo de Ana (CPC 373, I)</text>
            <text x="625" y="265" font-family="Lato" font-size="11" font-weight="700" fill="#64748B">★ Art. 1.660 CC não opera sem prova prévia de aquisição onerosa comum</text>
          </svg>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS ASSOCIADOS</span>
        <span class="page-indicator">SLIDE 03 / 07</span>
      </div>
    </div>

    <!-- SLIDE 4: FRENTE 1 IPTU BEGÔNIAS (FLUXO CAUSA-EFEITO & ALTO CONTRASTE) -->
    <div class="slide" id="slide-4">
      <div class="slide-header">
        <div class="header-left">
          <div class="accent-bar"></div>
          <div>
            <div class="action-category">AI 1.0000.23.223786-7/006 — TJMG</div>
            <div class="action-title">TJMG Mantém IPTU com Ocupante e Revoga Multa de R$ 10k</div>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <!-- Flow vector strip -->
        <div style="height: 100px; background: #FFFFFF; border: 1px solid var(--rd-card-border); border-radius: 6px; padding: 10px 16px; display: flex; align-items: center; justify-content: space-between;">
          <div style="text-align: center; flex: 1;">
            <div style="font-size: 10px; font-weight: 900; color: #64748B;">PASSO 1</div>
            <div style="font-size: 13px; font-weight: 900; color: #0F172A;">Fruição Exclusiva</div>
            <div style="font-size: 10.5px; color: #64748B; font-weight: 700;">Ana no imóvel desde 03/2023</div>
          </div>
          <div style="color: var(--rd-accent); font-weight: 900; font-size: 18px;">➔</div>
          <div style="text-align: center; flex: 1;">
            <div style="font-size: 10px; font-weight: 900; color: #64748B;">PASSO 2</div>
            <div style="font-size: 13px; font-weight: 900; color: #0F172A;">Inadimplência</div>
            <div style="font-size: 10.5px; color: #64748B; font-weight: 700;">IPTU e taxas não pagos</div>
          </div>
          <div style="color: var(--rd-accent); font-weight: 900; font-size: 18px;">➔</div>
          <div style="text-align: center; flex: 1;">
            <div style="font-size: 10px; font-weight: 900; color: #DC2626;">PASSO 3</div>
            <div style="font-size: 13px; font-weight: 900; color: #DC2626;">Protesto Indevido</div>
            <div style="font-size: 10.5px; color: #64748B; font-weight: 700;">Nome de Sílvio negativado</div>
          </div>
          <div style="color: var(--rd-accent); font-weight: 900; font-size: 18px;">➔</div>
          <div style="text-align: center; flex: 1.2; background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 4px; padding: 6px;">
            <div style="font-size: 10px; font-weight: 900; color: #047857;">RESULTADO RDAA</div>
            <div style="font-size: 13px; font-weight: 900; color: #065F46;">Ordem de Pagamento</div>
            <div style="font-size: 10.5px; color: #047857; font-weight: 700;">Ana deve pagar e baixar protesto</div>
          </div>
        </div>

        <!-- 2 Contrast Cards -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; flex: 1;">
          <!-- Left: Tese Adversária Rejeitada -->
          <div style="background-color: var(--rd-danger-bg); border: 1.5px solid var(--rd-danger-border); border-radius: 6px; padding: 18px 20px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="badge badge-danger">Tese Adversária Rejeitada</span>
                <span style="font-size: 18px;">✗</span>
              </div>
              <div style="font-size: 14px; font-weight: 900; color: #991B1B; margin-bottom: 8px;">Alegação de Vulnerabilidade & "Violência Patrimonial"</div>
              <p style="font-size: 12px; font-weight: 700; color: #7F1D1D; line-height: 1.45;">
                Ana pleiteou rateio de tributos e compensação com pensão alimentícia. Tese sem aderência legal: Sílvio é quem foi protestado pelo Fisco, e alimentos exigem via executiva própria.
              </p>
            </div>
            <div style="font-size: 11px; font-weight: 900; color: #991B1B; background: #FFFFFF; padding: 6px 10px; border-radius: 4px;">
              Precedente Inaplicável: Ausência de medida protetiva nos autos
            </div>
          </div>

          <!-- Right: Tese RDAA Vencedora -->
          <div style="background-color: var(--rd-accent-light); border: 2px solid var(--rd-accent); border-radius: 6px; padding: 18px 20px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="badge badge-gold">Solução RDAA Acolhida no TJMG</span>
                <span style="font-size: 18px;">★</span>
              </div>
              <div style="font-size: 14px; font-weight: 900; color: #92400E; margin-bottom: 8px;">Encargos Vinculados à Fruição Direta e Exclusiva</div>
              <p style="font-size: 12px; font-weight: 700; color: #78350F; line-height: 1.45;">
                Aplicação da jurisprudência consolidada (TJMG, AC 0013168-49 e STJ, AREsp 2.462.038): despesas de conservação e impostos incidentes sobre o imóvel em uso exclusivo cabem unicamente ao coproprietário ocupante.
              </p>
            </div>
            <div style="font-size: 11px; font-weight: 900; color: #047857; background: #ECFDF5; border: 1px solid #A7F3D0; padding: 6px 10px; border-radius: 4px;">
              ✓ Resultado no TJMG: Dever de Ana mantido e multa cominatória revogada
            </div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS ASSOCIADOS</span>
        <span class="page-indicator">SLIDE 04 / 07</span>
      </div>
    </div>

    <!-- SLIDE 5: FRENTE 2 MATRIZ 2X2 DO SANEADOR -->
    <div class="slide" id="slide-5">
      <div class="slide-header">
        <div class="header-left">
          <div class="accent-bar"></div>
          <div>
            <div class="action-category">Ação Ordinária nº 5033450-63.2025.8.13.0702</div>
            <div class="action-title">Matriz de Decisão: Ajuste do Saneador (Art. 357, §1º)</div>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="matrix-2x2">
          <!-- Quad 1: Equívoco do Saneador -->
          <div class="matrix-quad error">
            <div class="quad-header">
              <span class="quad-title" style="color: #991B1B;">1. Exigência do Saneador</span>
              <span class="badge badge-danger">Vício</span>
            </div>
            <div class="quad-body" style="color: #7F1D1D;">
              Decisão exigiu prova de que Ana estaria <strong>"impedindo ou inviabilizando na prática o uso pelo coproprietário"</strong>, sugerindo necessidade de demonstrar expulsão ou agressão material.
            </div>
            <div style="font-size: 11px; font-weight: 900; color: #B91C1C;">✗ Ônus probatório excessivo e contraproducente</div>
          </div>

          <!-- Quad 2: Tese RDAA / STJ -->
          <div class="matrix-quad winner">
            <div class="quad-header">
              <span class="quad-title" style="color: #92400E;">2. Padrão STJ (REsp 1.699.013/DF)</span>
              <span class="badge badge-gold">Tese RDAA</span>
            </div>
            <div class="quad-body" style="color: #78350F;">
              A impossibilidade fática de coabitação entre ex-cônjuges e a oposição manifesta <strong>bastam para caracterizar o dever indenizatório</strong>. Desnecessário qualquer ato de esbulho físico.
            </div>
            <div style="font-size: 11px; font-weight: 900; color: #92400E;">★ Acolhimento pleiteado via art. 357, §1º do CPC</div>
          </div>

          <!-- Quad 3: Piso Mínimo Garantido -->
          <div class="matrix-quad success">
            <div class="quad-header">
              <span class="quad-title" style="color: #065F46;">3. Piso Mínimo Garantido</span>
              <span class="badge badge-green">Incontroverso</span>
            </div>
            <div class="quad-body" style="color: #047857;">
              <strong>Data da citação válida nos autos</strong> funciona como marco temporal inquestionável de oposição, dispensando qualquer produção de prova adicional por Sílvio.
            </div>
            <div style="font-size: 11px; font-weight: 900; color: #065F46;">✓ Garantia patrimonial mínima assegurada</div>
          </div>

          <!-- Quad 4: Marco Pretendido -->
          <div class="matrix-quad">
            <div class="quad-header">
              <span class="quad-title" style="color: var(--rd-text-dark);">4. Retroatividade Pretendida</span>
              <span class="badge badge-dark">Sub judice</span>
            </div>
            <div class="quad-body" style="color: var(--rd-text-dark);">
              Direito de buscar a incidência dos aluguéis <strong>desde 13/03/2023 (separação de fato)</strong>, condicionado à juntada de notificações e manifestações constantes da ação de divórcio.
            </div>
            <div style="font-size: 11px; font-weight: 900; color: var(--rd-accent);">➜ Fase instrutória preservada</div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS ASSOCIADOS</span>
        <span class="page-indicator">SLIDE 05 / 07</span>
      </div>
    </div>

    <!-- SLIDE 6: FRENTE 3 BLINDAGEM DO SENSE (DEFENSE IN DEPTH) -->
    <div class="slide" id="slide-6">
      <div class="slide-header">
        <div class="header-left">
          <div class="accent-bar"></div>
          <div>
            <div class="action-category">Defesa na Reconvenção — 10ª Vara Cível</div>
            <div class="action-title">Blindagem do Apartamento Sense Vertical Living</div>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="barrier-grid">
          <!-- Coluna 1: O Ataque da Ré -->
          <div class="barrier-col" style="background-color: var(--rd-card-bg); border: 1.5px solid var(--rd-card-border);">
            <div>
              <span class="badge badge-danger">Pretensão de Ana</span>
              <div style="font-size: 16px; font-weight: 900; color: var(--rd-text-dark); margin: 10px 0 6px 0;">Tentativa de Partilha do Sense</div>
              <p style="font-size: 12.5px; font-weight: 700; color: var(--rd-structure); line-height: 1.45;">
                Invocou a presunção legal do art. 1.660 do CC para presumir comunicabilidade e exigir indenização locatícia de Sílvio.
              </p>
            </div>
            <div style="background: #FFFFFF; border: 1px solid var(--rd-card-border); padding: 8px 10px; border-radius: 4px; font-size: 11.5px; font-weight: 900; color: #DC2626;">
              ⚠ Risco de inversão precoce de ônus probatório
            </div>
          </div>

          <!-- Centro: Escudo e Filtro RDAA -->
          <div class="shield-separator">
            <div class="shield-badge">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            </div>
            <div style="font-size: 9.5px; font-weight: 900; color: var(--rd-structure); text-transform: uppercase;">FILTRO RDAA</div>
          </div>

          <!-- Coluna 2: A Blindagem Técnica RDAA -->
          <div class="barrier-col" style="background-color: var(--rd-accent-light); border: 2px solid var(--rd-accent);">
            <div>
              <span class="badge badge-gold">Blindagem Técnica RDAA</span>
              <div style="font-size: 16px; font-weight: 900; color: #92400E; margin: 10px 0 6px 0;">Primazia do Art. 373, I do CPC</div>
              <p style="font-size: 12.5px; font-weight: 700; color: #78350F; line-height: 1.45;">
                O art. 1.660 do CC não opera no vácuo: incumbe com exclusividade à reconvinte provar que o apartamento foi adquirido com patrimônio comum na vigência do casamento.
              </p>
            </div>
            <div style="background: #ECFDF5; border: 1px solid #A7F3D0; padding: 8px 10px; border-radius: 4px; font-size: 11.5px; font-weight: 900; color: #047857;">
              ✓ Sílvio detém prova bancária documental autônoma de reserva
            </div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS ASSOCIADOS</span>
        <span class="page-indicator">SLIDE 06 / 07</span>
      </div>
    </div>

    <!-- SLIDE 7: ROADMAP EM CHEVRONS (LINHA DO TEMPO) -->
    <div class="slide" id="slide-7">
      <div class="slide-header">
        <div class="header-left">
          <div class="accent-bar"></div>
          <div>
            <div class="action-category">Cronograma de Atuação</div>
            <div class="action-title">Roadmap de Providências Imediatas</div>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="chevron-timeline">
          <!-- Passo 1 -->
          <div class="chevron-box active">
            <div>
              <div class="step-badge">1</div>
              <div class="step-title">Julgamento Colegiado TJMG</div>
              <div class="step-desc">Distribuir memoriais na 8ª Câmara Cível para confirmar a obrigação exclusiva do IPTU com a ocupante.</div>
            </div>
            <span class="badge badge-gold">Pauta Iminente</span>
          </div>

          <!-- Passo 2 -->
          <div class="chevron-box">
            <div>
              <div class="step-badge">2</div>
              <div class="step-title">Quesitos de Perícia Locatícia</div>
              <div class="step-desc">Apresentar quesitos técnicos na 10ª Cível para arbitrar o valor do aluguel da casa da Rua das Begônias.</div>
            </div>
            <span class="badge badge-dark">10ª Vara Cível</span>
          </div>

          <!-- Passo 3 -->
          <div class="chevron-box">
            <div>
              <div class="step-badge">3</div>
              <div class="step-title">Fiscalização da Baixa do Protesto</div>
              <div class="step-desc">Notificar a Fazenda Municipal e o Cartório de Protestos para certificar o cumprimento da liminar por Ana.</div>
            </div>
            <span class="badge badge-dark">Extrajudicial</span>
          </div>

          <!-- Passo 4 -->
          <div class="chevron-box">
            <div>
              <div class="step-badge">4</div>
              <div class="step-title">Exclusão do Edifício Sense</div>
              <div class="step-desc">Consolidar a incomunicabilidade na partilha da 3ª Vara de Família mediante prova bancária documental.</div>
            </div>
            <span class="badge badge-dark">Partilha Final</span>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS ASSOCIADOS</span>
        <span class="page-indicator">SLIDE 07 / 07</span>
      </div>
    </div>

  </div>

  <!-- NAVIGATION BAR -->
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
    const totalSlides = 7;

    function init() {{
      const container = document.getElementById('dotsContainer');
      container.innerHTML = '';
      for (let i = 1; i <= totalSlides; i++) {{
        const dot = document.createElement('div');
        dot.className = `dot ${{i === 1 ? 'active' : ''}}`;
        dot.onclick = () => goToSlide(i);
        container.appendChild(dot);
      }}
      updateUI();
    }}

    function changeSlide(direction) {{
      goToSlide(currentSlide + direction);
    }}

    function goToSlide(target) {{
      if (target < 1 || target > totalSlides) return;
      document.getElementById(`slide-${{currentSlide}}`).classList.remove('active');
      currentSlide = target;
      document.getElementById(`slide-${{currentSlide}}`).classList.add('active');
      updateUI();
    }}

    function updateUI() {{
      document.getElementById('prevBtn').disabled = currentSlide === 1;
      document.getElementById('nextBtn').disabled = currentSlide === totalSlides;
      const dots = document.querySelectorAll('.dot');
      dots.forEach((dot, idx) => {{
        dot.classList.toggle('active', idx + 1 === currentSlide);
      }});
    }}

    document.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {{
        changeSlide(1);
      }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
        changeSlide(-1);
      }}
    }});

    init();
  </script>
</body>
</html>
"""

with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Deck v3 (Lato + Visual Law + Diagrams) gerado em: {HTML_OUTPUT}")
