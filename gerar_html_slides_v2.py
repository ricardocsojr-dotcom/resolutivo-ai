import base64
import os

LOGO_PATH = "C:/Projetos/resolutivo-ai/skills/romano-donadel-slide-style/assets/logo_romano_donadel.png"
HTML_OUTPUT = "C:/Projetos/resolutivo-ai/Apresentacao_Caso_Silvio_Afonso_Romano_Donadel.html"

with open(LOGO_PATH, "rb") as f:
    logo_b64 = f.read()
logo_uri = f"data:image/png;base64,{base64.b64encode(logo_b64).decode('utf-8')}"

# SVG Icons embedded cleanly
SVG_SCALE = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>'
SVG_SHIELD = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>'
SVG_HOME = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
SVG_BUILDING = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="20" x="4" y="2" rx="2" ry="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M8 10h.01"/><path d="M16 10h.01"/><path d="M8 14h.01"/><path d="M16 14h.01"/></svg>'
SVG_ALERT = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>'
SVG_CHECK = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#047857" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
SVG_CROSS = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#B91C1C" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
SVG_ARROW_RIGHT = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>'

html_code = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Caso Sílvio Luiz Afonso — Estratégia Visual RDAA</title>
  <style>
    :root {{
      --rd-background: #FFFFFF;
      --rd-text: #000000;
      --rd-structure: #63666A;
      --rd-accent: #F7A800;
      --rd-card-bg: #F8F9FA;
      --rd-card-border: #E5E7EB;
      --rd-accent-light: #FFF9EE;
      --rd-success-bg: #ECFDF5;
      --rd-success-text: #047857;
      --rd-danger-bg: #FEF2F2;
      --rd-danger-text: #B91C1C;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      background-color: #0F172A;
      color: var(--rd-text);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      overflow: hidden;
      padding: 16px;
    }}

    /* STRICT 16:9 CONTAINER FITTED TO VIEWPORT WITHOUT SCROLL */
    .deck-frame {{
      width: min(94vw, 1200px);
      aspect-ratio: 16 / 9;
      height: auto;
      max-height: 84vh;
      background-color: var(--rd-background);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
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
      padding: 30px 44px 22px 44px;
      flex-direction: column;
      justify-content: space-between;
      overflow: hidden;
      background-color: var(--rd-background);
    }}

    .slide.active {{
      display: flex;
      animation: slideIn 0.2s ease-out;
    }}

    @keyframes slideIn {{
      from {{ opacity: 0; transform: scale(0.99); }}
      to {{ opacity: 1; transform: scale(1); }}
    }}

    /* HEADER */
    .slide-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 2px solid #F1F5F9;
      padding-bottom: 12px;
      margin-bottom: 16px;
      flex-shrink: 0;
    }}

    .header-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .accent-bar {{
      width: 4px;
      height: 36px;
      background-color: var(--rd-accent);
      border-radius: 2px;
    }}

    .action-category {{
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 1.2px;
      color: var(--rd-accent);
      text-transform: uppercase;
      margin-bottom: 2px;
    }}

    .action-title {{
      font-size: 19px;
      font-weight: 900;
      color: var(--rd-text);
      text-transform: uppercase;
      letter-spacing: -0.2px;
    }}

    .header-logo {{
      height: 32px;
      object-fit: contain;
    }}

    /* SLIDE BODY CONTAINER */
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
      font-weight: 600;
      letter-spacing: 0.5px;
      flex-shrink: 0;
    }}

    .page-indicator {{
      color: var(--rd-text);
      font-weight: 800;
    }}

    /* CONTROLS UNDER DECK */
    .nav-bar {{
      width: min(94vw, 1200px);
      margin-top: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: #94A3B8;
      font-size: 12px;
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
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 9.5px;
      font-weight: 800;
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
      border: 1px solid #A7F3D0;
    }}

    .badge-dark {{
      background-color: #0F172A;
      color: #FFFFFF;
    }}

    /* SLIDE 1: CAPA */
    .cover-layout {{
      display: flex;
      flex-direction: column;
      height: 100%;
      justify-content: space-between;
    }}

    .cover-hero {{
      display: flex;
      align-items: center;
      gap: 32px;
      margin: auto 0;
    }}

    .cover-accent-pillar {{
      width: 6px;
      height: 190px;
      background-color: var(--rd-accent);
      border-radius: 3px;
      flex-shrink: 0;
    }}

    .cover-headline {{
      font-size: 34px;
      font-weight: 900;
      color: var(--rd-text);
      line-height: 1.15;
      letter-spacing: -0.5px;
      margin-bottom: 8px;
    }}

    .cover-subheadline {{
      font-size: 16px;
      color: var(--rd-structure);
      margin-bottom: 24px;
      font-weight: 500;
    }}

    .cover-pills {{
      display: flex;
      gap: 12px;
    }}

    .cover-pill {{
      display: flex;
      align-items: center;
      gap: 8px;
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      color: var(--rd-structure);
    }}

    .cover-pill strong {{
      color: var(--rd-text);
    }}

    /* SLIDE 2: 3 BIG PILLARS */
    .grid-3-pillars {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      height: 100%;
    }}

    .pillar-card {{
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-top: 4px solid var(--rd-accent);
      border-radius: 6px;
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .pillar-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 8px;
    }}

    .pillar-num {{
      font-size: 26px;
      font-weight: 900;
      color: var(--rd-text);
      line-height: 1;
    }}

    .pillar-title {{
      font-size: 13px;
      font-weight: 800;
      text-transform: uppercase;
      color: var(--rd-text);
      margin-bottom: 10px;
    }}

    .mini-bullet-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .mini-bullet {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11.5px;
      font-weight: 600;
      color: var(--rd-structure);
    }}

    .mini-bullet strong {{
      color: var(--rd-text);
    }}

    .pillar-bottom-tag {{
      margin-top: 12px;
      padding: 6px 10px;
      background-color: #FFFFFF;
      border: 1px solid var(--rd-card-border);
      border-radius: 4px;
      font-size: 10.5px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    /* SLIDE 3: PROCESS CHEVRON MATRIX */
    .grid-4-process {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      height: 100%;
    }}

    .proc-card {{
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-radius: 6px;
      padding: 14px 14px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .proc-tag {{
      font-size: 10px;
      font-weight: 800;
      color: var(--rd-accent);
      text-transform: uppercase;
      margin-bottom: 4px;
    }}

    .proc-name {{
      font-size: 12.5px;
      font-weight: 800;
      color: var(--rd-text);
      line-height: 1.25;
      margin-bottom: 8px;
    }}

    .proc-action {{
      background-color: #FFFFFF;
      border: 1px solid var(--rd-card-border);
      border-left: 3px solid var(--rd-accent);
      padding: 6px 8px;
      border-radius: 3px;
      font-size: 11px;
      font-weight: 700;
      color: var(--rd-text);
      margin-top: 6px;
    }}

    /* SLIDE 4: FLOWCHART DIAGRAM (IPTU) */
    .flow-container {{
      display: flex;
      align-items: center;
      gap: 12px;
      height: 130px;
      margin-bottom: 12px;
    }}

    .flow-step {{
      flex: 1;
      height: 100%;
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-radius: 6px;
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      text-align: center;
    }}

    .flow-step.step-victory {{
      background-color: var(--rd-success-bg);
      border-color: #A7F3D0;
    }}

    .flow-icon {{
      margin: 0 auto 6px auto;
      color: var(--rd-structure);
    }}

    .flow-label {{
      font-size: 11.5px;
      font-weight: 800;
      color: var(--rd-text);
      margin-bottom: 3px;
    }}

    .flow-sub {{
      font-size: 10px;
      color: var(--rd-structure);
      font-weight: 600;
    }}

    .flow-arrow {{
      color: var(--rd-accent);
      flex-shrink: 0;
    }}

    .cards-2-contrast {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      flex: 1;
    }}

    .contrast-box {{
      padding: 12px 16px;
      border-radius: 6px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}

    .contrast-danger {{
      background-color: var(--rd-danger-bg);
      border: 1px solid #FECACA;
    }}

    .contrast-success {{
      background-color: var(--rd-accent-light);
      border: 1.5px solid var(--rd-accent);
    }}

    .contrast-head {{
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .contrast-val {{
      font-size: 12.5px;
      font-weight: 700;
      line-height: 1.4;
    }}

    /* SLIDE 5: 2 COMPARATIVE PILLARS (SANEADOR) */
    .grid-2-large {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      height: 100%;
    }}

    .large-card {{
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-radius: 6px;
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .large-card-top {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
    }}

    .icon-badge {{
      width: 36px;
      height: 36px;
      border-radius: 6px;
      background-color: #FFFFFF;
      border: 1px solid var(--rd-card-border);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--rd-accent);
    }}

    .large-card-title {{
      font-size: 13.5px;
      font-weight: 800;
      color: var(--rd-text);
      text-transform: uppercase;
    }}

    .compare-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 10px;
      background-color: #FFFFFF;
      border: 1px solid var(--rd-card-border);
      border-radius: 4px;
      font-size: 11.5px;
      font-weight: 700;
      margin-bottom: 6px;
    }}

    /* SLIDE 6: SENSE VERTICAL SHIELD */
    .shield-layout {{
      display: grid;
      grid-template-columns: 1fr 80px 1fr;
      gap: 12px;
      align-items: center;
      height: 100%;
    }}

    .side-box {{
      height: 100%;
      border-radius: 6px;
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .side-danger {{
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-top: 4px solid #EF4444;
    }}

    .side-victory {{
      background-color: var(--rd-accent-light);
      border: 1.5px solid var(--rd-accent);
      border-top: 4px solid var(--rd-accent);
    }}

    .center-barrier {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 6px;
      text-align: center;
    }}

    .barrier-shield {{
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background-color: #0F172A;
      color: var(--rd-accent);
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .barrier-text {{
      font-size: 9px;
      font-weight: 800;
      color: var(--rd-structure);
      text-transform: uppercase;
    }}

    /* SLIDE 7: TIMELINE */
    .timeline-steps {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      height: 100%;
      align-items: stretch;
    }}

    .step-col {{
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-radius: 6px;
      padding: 16px 14px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
    }}

    .step-col.active-step {{
      border: 2px solid var(--rd-accent);
      background-color: var(--rd-accent-light);
    }}

    .step-circle {{
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background-color: #0F172A;
      color: #FFFFFF;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 800;
      margin-bottom: 10px;
    }}

    .step-col.active-step .step-circle {{
      background-color: var(--rd-accent);
      color: #000000;
    }}

    .step-headline {{
      font-size: 12px;
      font-weight: 800;
      color: var(--rd-text);
      text-transform: uppercase;
      margin-bottom: 8px;
      line-height: 1.3;
    }}

    .step-item {{
      font-size: 11px;
      color: var(--rd-structure);
      font-weight: 600;
      line-height: 1.4;
    }}
  </style>
</head>
<body>

  <!-- 16:9 DECK FRAME -->
  <div class="deck-frame">

    <!-- SLIDE 1: CAPA EXECUTIVA -->
    <div class="slide active" id="slide-1">
      <div class="cover-layout">
        <div style="display: flex; justify-content: flex-end;">
          <img src="{logo_uri}" alt="Romano Donadel" class="header-logo" style="height: 38px;">
        </div>
        <div class="cover-hero">
          <div class="cover-accent-pillar"></div>
          <div>
            <div class="badge badge-gold" style="margin-bottom: 8px;">Diretriz Estratégica RDAA</div>
            <h1 class="cover-headline">CASO SÍLVIO LUIZ AFONSO</h1>
            <div class="cover-subheadline">Panorama Estratégico, Gestão de Passivo Tributário e Blindagem de Meação</div>
            <div class="cover-pills">
              <div class="cover-pill">
                {SVG_SCALE}
                <span>CLIENTE: <strong>Sílvio Luiz Afonso</strong></span>
              </div>
              <div class="cover-pill">
                {SVG_SHIELD}
                <span>PATROCÍNIO: <strong>Romano Donadel Advogados</strong></span>
              </div>
              <div class="cover-pill">
                <span>DATA: <strong>Setembro / 2026</strong></span>
              </div>
            </div>
          </div>
        </div>
        <div class="slide-footer">
          <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS ASSOCIADOS</span>
          <span class="page-indicator">SLIDE 01 / 07</span>
        </div>
      </div>
    </div>

    <!-- SLIDE 2: RESUMO EXECUTIVO (3 PILARES) -->
    <div class="slide" id="slide-2">
      <div class="slide-header">
        <div class="header-left">
          <div class="accent-bar"></div>
          <div>
            <div class="action-category">Painel Executivo</div>
            <div class="action-title">Arquitetura Estratégica & Governança do Caso</div>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="grid-3-pillars">
          <!-- Pilar 1 -->
          <div class="pillar-card">
            <div>
              <div class="pillar-header">
                <div class="pillar-num">03</div>
                <span class="badge badge-dark">Processos</span>
              </div>
              <div class="pillar-title">Frentes Integradas</div>
              <ul class="mini-bullet-list">
                <li class="mini-bullet">{SVG_CHECK} <strong>3ª Vara Família:</strong> Divórcio & Partilha</li>
                <li class="mini-bullet">{SVG_CHECK} <strong>TJMG (8ª Câm.):</strong> Agravo IPTU Begônias</li>
                <li class="mini-bullet">{SVG_CHECK} <strong>10ª Vara Cível:</strong> Arbitramento Aluguel</li>
              </ul>
            </div>
            <div class="pillar-bottom-tag">
              <span style="color: var(--rd-accent);">●</span> Segregação procedimental absoluta
            </div>
          </div>

          <!-- Pilar 2 -->
          <div class="pillar-card">
            <div>
              <div class="pillar-header">
                <div class="pillar-num">02</div>
                <span class="badge badge-gold">Acervos</span>
              </div>
              <div class="pillar-title">Imóveis Mapeados</div>
              <ul class="mini-bullet-list">
                <li class="mini-bullet">{SVG_HOME} <strong>Rua das Begônias:</strong> Fruição de Ana</li>
                <li class="mini-bullet">{SVG_BUILDING} <strong>Ed. Sense:</strong> Particular de Sílvio</li>
                <li class="mini-bullet">{SVG_SHIELD} <strong>Prevenção:</strong> Bloqueio à meação do Sense</li>
              </ul>
            </div>
            <div class="pillar-bottom-tag">
              <span style="color: #047857;">●</span> Proteção do acervo exclusivo
            </div>
          </div>

          <!-- Pilar 3 -->
          <div class="pillar-card">
            <div>
              <div class="pillar-header">
                <div class="pillar-num">100%</div>
                <span class="badge badge-green">Sucesso</span>
              </div>
              <div class="pillar-title">Riscos Neutralizados</div>
              <ul class="mini-bullet-list">
                <li class="mini-bullet">{SVG_CHECK} <strong>Astreintes:</strong> Revogadas no TJMG</li>
                <li class="mini-bullet">{SVG_CHECK} <strong>IPTU:</strong> Dever integral da ocupante</li>
                <li class="mini-bullet">{SVG_CHECK} <strong>Alimentos:</strong> Sem compensação cruzada</li>
              </ul>
            </div>
            <div class="pillar-bottom-tag">
              <span style="color: var(--rd-accent);">●</span> Zero passivo transferido a Sílvio
            </div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
        <span class="page-indicator">SLIDE 02 / 07</span>
      </div>
    </div>

    <!-- SLIDE 3: MATRIZ DE LITIGIOSIDADE (CHEVRONS) -->
    <div class="slide" id="slide-3">
      <div class="slide-header">
        <div class="header-left">
          <div class="accent-bar"></div>
          <div>
            <div class="action-category">Mapa de Ações</div>
            <div class="action-title">Matriz de Litigiosidade e Diretrizes RDAA</div>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="grid-4-process">
          <!-- Card 1 -->
          <div class="proc-card">
            <div>
              <div class="proc-tag">3ª Vara de Família</div>
              <div class="proc-name">Ação de Divórcio e Partilha</div>
              <span class="badge badge-dark">Proc. 5026681</span>
              <p style="font-size: 11px; color: var(--rd-structure); margin-top: 8px;">Definição de meação e inventário de bens.</p>
            </div>
            <div class="proc-action">
              🎯 <strong>Alvo RDAA:</strong> Isolar bens particulares e exigir contas.
            </div>
          </div>

          <!-- Card 2 -->
          <div class="proc-card">
            <div>
              <div class="proc-tag">TJMG — 8ª Câmara</div>
              <div class="proc-name">AI IPTU Begônias (/006)</div>
              <span class="badge badge-green">Liminar Parcial</span>
              <p style="font-size: 11px; color: var(--rd-structure); margin-top: 8px;">Custeio de IPTU e baixa de protesto da casa.</p>
            </div>
            <div class="proc-action">
              🎯 <strong>Alvo RDAA:</strong> Manter dever tributário exclusivo de Ana.
            </div>
          </div>

          <!-- Card 3 -->
          <div class="proc-card">
            <div>
              <div class="proc-tag">10ª Vara Cível</div>
              <div class="proc-name">Arbitramento de Aluguéis</div>
              <span class="badge badge-gold">Art. 357, §1º</span>
              <p style="font-size: 11px; color: var(--rd-structure); margin-top: 8px;">Indenização pela posse exclusiva da residência.</p>
            </div>
            <div class="proc-action">
              🎯 <strong>Alvo RDAA:</strong> Consolidar termo na citação e prova fática.
            </div>
          </div>

          <!-- Card 4 -->
          <div class="proc-card">
            <div>
              <div class="proc-tag">10ª Vara Cível</div>
              <div class="proc-name">Reconvenção (Ed. Sense)</div>
              <span class="badge badge-dark">Art. 373, I CPC</span>
              <p style="font-size: 11px; color: var(--rd-structure); margin-top: 8px;">Pretensão de meação sobre apartamento de Sílvio.</p>
            </div>
            <div class="proc-action">
              🎯 <strong>Alvo RDAA:</strong> Impor ônus primário integral à reconvinte.
            </div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
        <span class="page-indicator">SLIDE 03 / 07</span>
      </div>
    </div>

    <!-- SLIDE 4: FRENTE 1 IPTU BEGONIAS (FLUXO + CONTRASTE) -->
    <div class="slide" id="slide-4">
      <div class="slide-header">
        <div class="header-left">
          <div class="accent-bar"></div>
          <div>
            <div class="action-category">AI 1.0000.23.223786-7/006 — TJMG</div>
            <div class="action-title">TJMG Mantém IPTU com a Ocupante e Revoga Multa</div>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <!-- Flowchart -->
        <div class="flow-container">
          <div class="flow-step">
            <div class="flow-icon">{SVG_HOME}</div>
            <div class="flow-label">Uso Exclusivo</div>
            <div class="flow-sub">Ana reside desde 13/03/2023</div>
          </div>
          <div class="flow-arrow">{SVG_ARROW_RIGHT}</div>
          <div class="flow-step">
            <div class="flow-icon">{SVG_ALERT}</div>
            <div class="flow-label">Inadimplemento</div>
            <div class="flow-sub">IPTU não pago pela ocupante</div>
          </div>
          <div class="flow-arrow">{SVG_ARROW_RIGHT}</div>
          <div class="flow-step">
            <div class="flow-icon" style="color: #DC2626;">{SVG_CROSS}</div>
            <div class="flow-label">Protesto Indevido</div>
            <div class="flow-sub">Fazenda protestou Sílvio</div>
          </div>
          <div class="flow-arrow">{SVG_ARROW_RIGHT}</div>
          <div class="flow-step step-victory">
            <div class="flow-icon" style="color: #047857;">{SVG_CHECK}</div>
            <div class="flow-label">Ordem Judicial TJMG</div>
            <div class="flow-sub">Ana deve pagar e baixar protesto</div>
          </div>
        </div>

        <!-- 2 Contrast Cards -->
        <div class="cards-2-contrast">
          <div class="contrast-box contrast-danger">
            <div class="contrast-head" style="color: #B91C1C;">
              {SVG_CROSS} Tese Rejeitada da Adversária
            </div>
            <div class="contrast-val">
              Alegou "violência patrimonial" e tentou abater IPTU de alimentos atrasados.
            </div>
            <div style="font-size: 11px; color: #7F1D1D; margin-top: 4px;">
              ✗ Tese sem aderência: Sílvio é a vítima do protesto; alimentos têm via própria.
            </div>
          </div>
          <div class="contrast-box contrast-success">
            <div class="contrast-head" style="color: #B45309;">
              {SVG_CHECK} Solução RDAA Acolhida no TJMG
            </div>
            <div class="contrast-val">
              Jurisprudência vincula o encargo tributário à fruição direta (TJMG AC 0013168-49).
            </div>
            <div style="font-size: 11px; color: #78350F; margin-top: 4px;">
              ✓ Resultado: Obrigação de pagamento mantida para Ana; astreintes de R$ 10k revogadas.
            </div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
        <span class="page-indicator">SLIDE 04 / 07</span>
      </div>
    </div>

    <!-- SLIDE 5: FRENTE 2 ARBITRAMENTO DE ALUGUÉIS (SANEADOR) -->
    <div class="slide" id="slide-5">
      <div class="slide-header">
        <div class="header-left">
          <div class="accent-bar"></div>
          <div>
            <div class="action-category">Ação nº 5033450-63.2025.8.13.0702 — 10ª Vara Cível</div>
            <div class="action-title">Ajuste do Saneador: Fato Gerador e Piso na Citação</div>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="grid-2-large">
          <!-- Card 1: Fato Gerador -->
          <div class="large-card">
            <div>
              <div class="large-card-top">
                <div class="icon-badge">{SVG_SCALE}</div>
                <div class="large-card-title">1. Desmistificação do "Esbulho Físico"</div>
              </div>
              <div class="compare-row">
                <span style="color: var(--rd-structure);">Exigência do Saneador:</span>
                <span style="color: #B91C1C;">Prova de ato material impeditivo</span>
              </div>
              <div class="compare-row" style="background-color: var(--rd-accent-light); border-color: var(--rd-accent);">
                <span style="color: var(--rd-text);">Padrão STJ (REsp 1.699.013):</span>
                <span style="color: #047857;">Posse exclusiva + oposição expressa</span>
              </div>
            </div>
            <div style="font-size: 11.5px; color: var(--rd-structure); line-height: 1.4;">
              💡 <strong>RDAA:</strong> A animosidade e ruptura do casal tornam a coabitação impossível. O dever indenizatório independe de expulsão física.
            </div>
          </div>

          <!-- Card 2: Termo Inicial -->
          <div class="large-card">
            <div>
              <div class="large-card-top">
                <div class="icon-badge">{SVG_CHECK}</div>
                <div class="large-card-title">2. Consolidação do Marco Inicial</div>
              </div>
              <div class="compare-row">
                <span style="color: var(--rd-structure);">Marco Mínimo Incontroverso:</span>
                <span class="badge badge-green">Data da Citação Válida</span>
              </div>
              <div class="compare-row" style="background-color: var(--rd-accent-light); border-color: var(--rd-accent);">
                <span style="color: var(--rd-text);">Marco Pretendido (Divórcio):</span>
                <span class="badge badge-gold">13/03/2023 (Separação)</span>
              </div>
            </div>
            <div style="font-size: 11.5px; color: var(--rd-structure); line-height: 1.4;">
              💡 <strong>RDAA:</strong> Piso garantido sem ônus adicional probatório. Direito reservado de retroagir se a oposição prévia restar comprovada.
            </div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
        <span class="page-indicator">SLIDE 05 / 07</span>
      </div>
    </div>

    <!-- SLIDE 6: FRENTE 3 EDIFÍCIO SENSE (ESCUDO) -->
    <div class="slide" id="slide-6">
      <div class="slide-header">
        <div class="header-left">
          <div class="accent-bar"></div>
          <div>
            <div class="action-category">Defesa na Reconvenção — 10ª Cível</div>
            <div class="action-title">Blindagem do Apartamento Sense Vertical Living</div>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="shield-layout">
          <!-- Pretensão da Ré -->
          <div class="side-box side-danger">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="badge badge-dark">Pretensão de Ana</span>
                <span style="color: #B91C1C;">{SVG_ALERT}</span>
              </div>
              <div style="font-size: 13px; font-weight: 800; color: var(--rd-text); margin-bottom: 6px;">Inclusão no Acervo Comum</div>
              <p style="font-size: 11px; color: var(--rd-structure); line-height: 1.4;">Invocou o art. 1.660 do CC para presumir comunicabilidade e cobrar aluguéis de Sílvio.</p>
            </div>
            <div style="font-size: 11px; color: #B91C1C; font-weight: 700; background: #FFF; padding: 6px 8px; border-radius: 4px;">
              ⚠ Tentativa de inversão prematura de ônus
            </div>
          </div>

          <!-- Escudo Central -->
          <div class="center-barrier">
            <div class="barrier-shield">{SVG_SHIELD}</div>
            <div class="barrier-text">FILTRO RDAA</div>
          </div>

          <!-- Solução RDAA -->
          <div class="side-box side-victory">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="badge badge-gold">Blindagem RDAA</span>
                <span style="color: #047857;">{SVG_CHECK}</span>
              </div>
              <div style="font-size: 13px; font-weight: 800; color: var(--rd-text); margin-bottom: 6px;">Primazia do Art. 373, I do CPC</div>
              <p style="font-size: 11px; color: var(--rd-text); line-height: 1.4;">Ana tem o ônus primário de comprovar que o imóvel foi adquirido com recursos comuns.</p>
            </div>
            <div style="font-size: 11px; color: #047857; font-weight: 700; background: #FFF; padding: 6px 8px; border-radius: 4px; border: 1px solid #A7F3D0;">
              ✓ Sílvio detém lastro bancário exclusivo de reserva
            </div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
        <span class="page-indicator">SLIDE 06 / 07</span>
      </div>
    </div>

    <!-- SLIDE 7: CRONOGRAMA & ROADMAP -->
    <div class="slide" id="slide-7">
      <div class="slide-header">
        <div class="header-left">
          <div class="accent-bar"></div>
          <div>
            <div class="action-category">Roadmap Estratégico</div>
            <div class="action-title">Cronograma de Providências Imediatas</div>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="timeline-steps">
          <!-- Passo 1 -->
          <div class="step-col active-step">
            <div>
              <div class="step-circle">1</div>
              <div class="step-headline">Julgamento no TJMG</div>
              <div class="step-item">Distribuir memoriais na 8ª Câmara Cível para manter a exclusividade do IPTU sob responsabilidade de Ana.</div>
            </div>
            <span class="badge badge-gold">Em Pauta</span>
          </div>

          <!-- Passo 2 -->
          <div class="step-col">
            <div>
              <div class="step-circle">2</div>
              <div class="step-headline">Quesitos de Perícia</div>
              <div class="step-item">Indicar assistente técnico na 10ª Vara Cível para fixar locativo de mercado da Rua das Begônias.</div>
            </div>
            <span class="badge badge-dark">10ª Cível</span>
          </div>

          <!-- Passo 3 -->
          <div class="step-col">
            <div>
              <div class="step-circle">3</div>
              <div class="step-headline">Baixa de Protesto</div>
              <div class="step-item">Fiscalizar cumprimento da ordem judicial no 1º Tabelionato de Protestos de Uberlândia.</div>
            </div>
            <span class="badge badge-dark">Extrajudicial</span>
          </div>

          <!-- Passo 4 -->
          <div class="step-col">
            <div>
              <div class="step-circle">4</div>
              <div class="step-headline">Blindagem do Sense</div>
              <div class="step-item">Excluir formalmente o apartamento da partilha na 3ª Vara de Família mediante prova documental autônoma.</div>
            </div>
            <span class="badge badge-dark">Partilha</span>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
        <span class="page-indicator">SLIDE 07 / 07</span>
      </div>
    </div>

  </div>

  <!-- NAVIGATION CONTROLS -->
  <div class="nav-bar">
    <div class="nav-btns">
      <button class="nav-btn" id="prevBtn" onclick="changeSlide(-1)">◀ Anterior</button>
      <button class="nav-btn" id="nextBtn" onclick="changeSlide(1)">Próximo ▶</button>
    </div>
    <div class="dots" id="dotsContainer"></div>
    <div style="font-size: 11px;">[◀ / ▶] no teclado ou clique nas bolinhas</div>
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
    f.write(html_code)

print(f"Novo HTML ultra visual gerado em: {HTML_OUTPUT}")
