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
  <title>Caso Sílvio Luiz Afonso — Apresentação Estratégica RDAA</title>
  <style>
    :root {{
      --rd-background: #FFFFFF;
      --rd-text: #000000;
      --rd-structure: #63666A;
      --rd-accent: #F7A800;
      --rd-card-bg: #F8F9FA;
      --rd-card-border: #E2E8F0;
      --rd-accent-light: #FFF9EE;
      --rd-accent-hover: #D99000;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: #111827;
      color: var(--rd-text);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      overflow-x: hidden;
      padding: 20px;
    }}

    /* Presentation Deck Frame (16:9) */
    .deck-container {{
      width: 100%;
      max-width: 1200px;
      aspect-ratio: 16 / 9;
      background-color: var(--rd-background);
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.45);
      border-radius: 8px;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    /* Slides */
    .slide {{
      display: none;
      width: 100%;
      height: 100%;
      padding: 44px 56px 40px 56px;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      background-color: var(--rd-background);
    }}

    .slide.active {{
      display: flex;
      animation: fadeIn 0.25s ease-in-out;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(4px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Slide Header */
    .slide-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 2px solid #F1F5F9;
      padding-bottom: 14px;
      margin-bottom: 20px;
    }}

    .header-titles {{
      display: flex;
      align-items: flex-start;
      gap: 14px;
    }}

    .header-bar {{
      width: 5px;
      height: 42px;
      background-color: var(--rd-accent);
      border-radius: 2px;
      flex-shrink: 0;
    }}

    .header-category {{
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1.2px;
      color: var(--rd-accent);
      text-transform: uppercase;
      margin-bottom: 2px;
    }}

    .header-title {{
      font-size: 22px;
      font-weight: 800;
      color: var(--rd-text);
      letter-spacing: -0.3px;
      text-transform: uppercase;
    }}

    .header-logo {{
      height: 38px;
      object-fit: contain;
    }}

    /* Slide Content Body */
    .slide-body {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}

    /* Slide Footer */
    .slide-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid var(--rd-card-border);
      padding-top: 10px;
      font-size: 11px;
      color: var(--rd-structure);
      letter-spacing: 0.5px;
      font-weight: 500;
    }}

    .page-indicator {{
      font-weight: 700;
      color: var(--rd-text);
    }}

    /* Controls Bar below presentation */
    .controls-bar {{
      width: 100%;
      max-width: 1200px;
      margin-top: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: #9CA3AF;
      font-size: 13px;
    }}

    .nav-buttons {{
      display: flex;
      gap: 10px;
    }}

    .btn-nav {{
      background-color: #1F2937;
      color: #F3F4F6;
      border: 1px solid #374151;
      padding: 8px 16px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 13px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}

    .btn-nav:hover {{
      background-color: #374151;
      color: #FFFFFF;
      border-color: var(--rd-accent);
    }}

    .btn-nav:disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}

    .dots-container {{
      display: flex;
      gap: 8px;
    }}

    .dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background-color: #4B5563;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .dot.active {{
      background-color: var(--rd-accent);
      transform: scale(1.25);
    }}

    /* SLIDE 1: COVER */
    .cover-content {{
      display: flex;
      flex-direction: column;
      height: 100%;
      justify-content: space-between;
    }}

    .cover-top {{
      display: flex;
      justify-content: flex-end;
    }}

    .cover-logo {{
      height: 52px;
    }}

    .cover-center {{
      display: flex;
      gap: 28px;
      align-items: stretch;
      margin: auto 0;
    }}

    .cover-bar {{
      width: 7px;
      background-color: var(--rd-accent);
      border-radius: 3px;
      flex-shrink: 0;
    }}

    .cover-eyebrow {{
      font-size: 13px;
      font-weight: 700;
      color: var(--rd-accent);
      letter-spacing: 2px;
      text-transform: uppercase;
      margin-bottom: 8px;
    }}

    .cover-title {{
      font-size: 38px;
      font-weight: 800;
      color: var(--rd-text);
      line-height: 1.15;
      letter-spacing: -0.5px;
      margin-bottom: 12px;
    }}

    .cover-subtitle {{
      font-size: 18px;
      color: var(--rd-structure);
      font-weight: 400;
      line-height: 1.4;
      margin-bottom: 24px;
      max-width: 820px;
    }}

    .cover-meta {{
      font-size: 12.5px;
      color: var(--rd-structure);
      line-height: 1.8;
    }}

    .cover-meta strong {{
      color: var(--rd-text);
    }}

    /* SLIDE 2: CARDS & DASHBOARD */
    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      margin-bottom: 18px;
    }}

    .kpi-card {{
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-top: 4px solid var(--rd-accent);
      border-radius: 6px;
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
    }}

    .kpi-num {{
      font-size: 20px;
      font-weight: 800;
      color: var(--rd-accent);
      margin-bottom: 2px;
    }}

    .kpi-sub {{
      font-size: 10.5px;
      font-weight: 700;
      color: var(--rd-structure);
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-bottom: 10px;
    }}

    .kpi-list {{
      list-style: none;
      font-size: 12px;
      line-height: 1.5;
      color: var(--rd-text);
    }}

    .kpi-list li {{
      margin-bottom: 5px;
      padding-left: 14px;
      position: relative;
    }}

    .kpi-list li::before {{
      content: "•";
      color: var(--rd-accent);
      font-weight: bold;
      position: absolute;
      left: 0;
    }}

    .summary-box {{
      background-color: var(--rd-accent-light);
      border: 1px solid #FDE68A;
      border-left: 5px solid var(--rd-accent);
      border-radius: 6px;
      padding: 16px 20px;
    }}

    .summary-title {{
      font-size: 13px;
      font-weight: 700;
      color: #B45309;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-bottom: 8px;
    }}

    .summary-text {{
      font-size: 12.5px;
      line-height: 1.55;
      color: var(--rd-text);
    }}

    .summary-text p {{
      margin-bottom: 6px;
    }}
    .summary-text p:last-child {{
      margin-bottom: 0;
    }}

    /* SLIDE 3: TABLE */
    .table-responsive {{
      width: 100%;
      border-collapse: collapse;
      font-size: 11.5px;
      border: 1px solid var(--rd-card-border);
      border-radius: 6px;
      overflow: hidden;
    }}

    .table-responsive th {{
      background-color: #0F172A;
      color: #FFFFFF;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      padding: 10px 12px;
      text-align: left;
      font-size: 11px;
    }}

    .table-responsive td {{
      padding: 9px 12px;
      border-bottom: 1px solid var(--rd-card-border);
      vertical-align: top;
      line-height: 1.4;
      color: var(--rd-text);
    }}

    .table-responsive tr:nth-child(even) td {{
      background-color: var(--rd-card-bg);
    }}

    .table-proc {{
      font-weight: 700;
      color: var(--rd-text);
      white-space: nowrap;
    }}

    .badge {{
      display: inline-block;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
    }}

    .badge-active {{
      background-color: #FEF3C7;
      color: #B45309;
      border: 1px solid #FCD34D;
    }}

    .badge-favorable {{
      background-color: #ECFDF5;
      color: #047857;
      border: 1px solid #A7F3D0;
    }}

    /* SLIDE 4 & 6: TWO COLUMNS */
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 22px;
      height: 100%;
    }}

    .col-card {{
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-radius: 6px;
      padding: 20px 22px;
      display: flex;
      flex-direction: column;
    }}

    .col-card.accent-card {{
      background-color: var(--rd-accent-light);
      border: 1.5px solid var(--rd-accent);
    }}

    .col-title {{
      font-size: 13px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .col-title.orange {{
      color: #B45309;
    }}

    .col-title.gray {{
      color: var(--rd-structure);
    }}

    .point-item {{
      margin-bottom: 12px;
      font-size: 12px;
      line-height: 1.5;
    }}

    .point-item strong {{
      color: var(--rd-text);
      display: block;
      margin-bottom: 2px;
      font-size: 12px;
    }}

    .point-item span {{
      color: #374151;
    }}

    /* SLIDE 5: 3 VERTICAL ADJUSTMENT CARDS */
    .grid-3-vert {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      height: 100%;
    }}

    .adj-card {{
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-radius: 6px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    .adj-header {{
      background-color: #0F172A;
      color: var(--rd-accent);
      padding: 12px 14px;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      line-height: 1.3;
    }}

    .adj-body {{
      padding: 14px 16px;
      font-size: 11.5px;
      line-height: 1.45;
      display: flex;
      flex-direction: column;
      gap: 10px;
      flex: 1;
    }}

    .adj-sec-title {{
      font-size: 10.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .adj-sec-title.gray {{ color: var(--rd-structure); }}
    .adj-sec-title.dark {{ color: var(--rd-text); }}
    .adj-sec-title.orange {{ color: #B45309; }}

    /* SLIDE 7: TIMELINE */
    .timeline-container {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      justify-content: center;
      height: 100%;
    }}

    .timeline-row {{
      display: flex;
      background-color: var(--rd-card-bg);
      border: 1px solid var(--rd-card-border);
      border-radius: 6px;
      overflow: hidden;
      align-items: stretch;
    }}

    .timeline-tag {{
      width: 120px;
      background-color: #0F172A;
      color: #FFFFFF;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 1px;
      flex-shrink: 0;
    }}

    .timeline-tag.highlight {{
      background-color: var(--rd-accent);
      color: #000000;
    }}

    .timeline-info {{
      padding: 12px 18px;
      flex: 1;
    }}

    .timeline-title {{
      font-size: 12.5px;
      font-weight: 800;
      color: var(--rd-text);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 3px;
    }}

    .timeline-desc {{
      font-size: 11.5px;
      color: var(--rd-structure);
      line-height: 1.4;
    }}
  </style>
</head>
<body>

  <!-- DECK CONTAINER -->
  <div class="deck-container">

    <!-- SLIDE 1: COVER -->
    <div class="slide active" id="slide-1">
      <div class="cover-content">
        <div class="cover-top">
          <img src="{logo_uri}" alt="Romano Donadel" class="cover-logo">
        </div>
        <div class="cover-center">
          <div class="cover-bar"></div>
          <div>
            <div class="cover-eyebrow">Relatório Estratégico Contencioso</div>
            <h1 class="cover-title">CASO SÍLVIO LUIZ AFONSO</h1>
            <div class="cover-subtitle">Panorama Integrado das Frentes Processuais, Gestão de Passivo Tributário e Blindagem Patrimonial Ativa</div>
            <div class="cover-meta">
              <p><strong>CLIENTE:</strong> Sílvio Luiz Afonso &nbsp;|&nbsp; <strong>PARTE ADVERSA:</strong> Ana Lúcia de Oliveira Afonso</p>
              <p><strong>PATROCÍNIO:</strong> Romano Donadel Advogados Associados &nbsp;|&nbsp; <strong>DATA:</strong> Setembro de 2026</p>
            </div>
          </div>
        </div>
        <div class="slide-footer">
          <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
          <span class="page-indicator">01 / 07</span>
        </div>
      </div>
    </div>

    <!-- SLIDE 2: RESUMO EXECUTIVO -->
    <div class="slide" id="slide-2">
      <div class="slide-header">
        <div class="header-titles">
          <div class="header-bar"></div>
          <div>
            <div class="header-category">Governança Processual</div>
            <h2 class="header-title">Resumo Executivo & Visão Global</h2>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="grid-3">
          <div class="kpi-card">
            <div class="kpi-num">03 FRENTES</div>
            <div class="kpi-sub">Gestão Coordenada</div>
            <ul class="kpi-list">
              <li>Divórcio & Partilha (3ª Vara Família)</li>
              <li>Arbitramento de Aluguel (10ª Vara Cível)</li>
              <li>Execução de Alimentos autônoma</li>
            </ul>
          </div>
          <div class="kpi-card">
            <div class="kpi-num">02 IMÓVEIS</div>
            <div class="kpi-sub">Imóveis Objeto</div>
            <ul class="kpi-list">
              <li>Rua das Begônias, 108 (Posse de Ana)</li>
              <li>Ed. Sense Vertical Living (Particular)</li>
              <li>Prevenção contra confusão de acervos</li>
            </ul>
          </div>
          <div class="kpi-card">
            <div class="kpi-num">100% BLINDADO</div>
            <div class="kpi-sub">Vitórias Estratégicas</div>
            <ul class="kpi-list">
              <li>Astreintes de R$ 10k afastadas no TJMG</li>
              <li>Bloqueio à compensação cruzada</li>
              <li>Ônus da prova mantido na reconvinte</li>
            </ul>
          </div>
        </div>
        <div class="summary-box">
          <div class="summary-title">Diretriz Estratégica RDAA — Síntese da Posição Patrimonial</div>
          <div class="summary-text">
            <p><strong>1. Segregação Absoluta:</strong> A responsabilidade pelo IPTU e o protesto lavrado contra Sílvio decorrem do uso exclusivo exercido por Ana Lúcia. O escritório neutralizou no TJMG as alegações de "violência patrimonial" e repeliu tentativas de compensação com alimentos.</p>
            <p><strong>2. Fruição Indenizável:</strong> A fixação de aluguéis respalda-se no REsp 1.699.013/DF (STJ): o dever independe de esbulho ou impedimento físico, bastando a impossibilidade prática de coabitação e a oposição manifesta.</p>
            <p><strong>3. Blindagem na Reconvenção:</strong> Exigência de que a reconvinte comprove aquisição na constância e recursos comuns (CPC, art. 373, I), desarmando inversões indevidas contra o patrimônio particular do cliente.</p>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
        <span class="page-indicator">02 / 07</span>
      </div>
    </div>

    <!-- SLIDE 3: TABELA ANALÍTICA -->
    <div class="slide" id="slide-3">
      <div class="slide-header">
        <div class="header-titles">
          <div class="header-bar"></div>
          <div>
            <div class="header-category">Mapa de Litigiosidade</div>
            <h2 class="header-title">Matriz Comparativa das Ações em Curso</h2>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <table class="table-responsive">
          <thead>
            <tr>
              <th>Ação / Processo</th>
              <th>Juízo Competente</th>
              <th>Objeto Controvertido</th>
              <th>Status / Posição Atual</th>
              <th>Diretriz de Atuação RDAA</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="table-proc">Divórcio e Partilha<br><span style="font-size:10px; color:#64748B;">5026681-10.2023.8.13.0702</span></td>
              <td>3ª Vara de Família<br>Uberlândia/MG</td>
              <td>Partilha do patrimônio comum e meação.</td>
              <td><span class="badge badge-active">Instrução</span> Perícia contábil pendente.</td>
              <td>Segregar acervo particular e exigir prestação de contas dos frutos.</td>
            </tr>
            <tr>
              <td class="table-proc">AI IPTU Begônias (/006)<br><span style="font-size:10px; color:#64748B;">1.0000.23.223786-7</span></td>
              <td>TJMG — 8ª Câmara Cível Especializada</td>
              <td>Custeio do IPTU e baixa do protesto em nome de Sílvio.</td>
              <td><span class="badge badge-favorable">Liminar Parcial</span> Multa revogada; dever mantido.</td>
              <td>Sustentar enriched sem causa de Ana (TJMG, AC 0013168-49).</td>
            </tr>
            <tr>
              <td class="table-proc">Arbitramento Aluguéis<br><span style="font-size:10px; color:#64748B;">5033450-63.2025.8.13.0702</span></td>
              <td>10ª Vara Cível<br>Uberlândia/MG</td>
              <td>Indenização pela fruição exclusiva da residência.</td>
              <td><span class="badge badge-active">Saneador</span> Pedido art. 357, §1º protocolado.</td>
              <td>Consolidar termo inicial na citação/separação e afastar requisito de esbulho.</td>
            </tr>
            <tr>
              <td class="table-proc">Reconvenção (Ed. Sense)<br><span style="font-size:10px; color:#64748B;">5033450-63.2025.8.13.0702</span></td>
              <td>10ª Vara Cível<br>Uberlândia/MG</td>
              <td>Pretensão de meação sobre apartamento de Sílvio.</td>
              <td><span class="badge badge-active">Saneamento</span> Ônus do art. 373, I com Ana.</td>
              <td>Bloquear presunção automática do art. 1.660 CC; exigir prova documental de aporte.</td>
            </tr>
            <tr>
              <td class="table-proc">Execução de Alimentos<br><span style="font-size:10px; color:#64748B;">5072971-49.2024.8.13.0702</span></td>
              <td>Vara de Família<br>Uberlândia/MG</td>
              <td>Pensão alimentícia de 4,5 salários mínimos.</td>
              <td><span class="badge badge-active">Execução</span> Via autônoma de rito próprio.</td>
              <td>Manter autonomia procedimental estrita; impedir compensação cruzada com dívidas reais.</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
        <span class="page-indicator">03 / 07</span>
      </div>
    </div>

    <!-- SLIDE 4: FRENTE 1 IPTU BEGONIAS -->
    <div class="slide" id="slide-4">
      <div class="slide-header">
        <div class="header-titles">
          <div class="header-bar"></div>
          <div>
            <div class="header-category">Agravo de Instrumento nº 1.0000.23.223786-7/006 — TJMG</div>
            <h2 class="header-title">Frente I — Imóvel Begônias, Passivo de IPTU e Protesto</h2>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="grid-2">
          <div class="col-card">
            <div class="col-title gray">⚖ Dinâmica dos Fatos & Decisão Agravada</div>
            <div class="point-item">
              <strong>Ocupação Exclusiva desde a Separação:</strong>
              <span>Ana Lúcia reside com exclusividade na Rua das Begônias nº 108 desde 13/03/2023, sem remunerar Sílvio e sem honrar tributos municipais.</span>
            </div>
            <div class="point-item">
              <strong>Protesto em Nome de Sílvio:</strong>
              <span>A inadimplência de IPTU gerou lançamento em dívida ativa e protesto indevido da Fazenda Pública contra o nome do cliente.</span>
            </div>
            <div class="point-item">
              <strong>Tutela de Urgência no 1º Grau:</strong>
              <span>A 3ª Vara de Família acolheu pedido de Sílvio, ordenando que a ocupante pague o IPTU e dê baixa no protesto em 15 dias sob pena de astreintes.</span>
            </div>
            <div class="point-item">
              <strong>Inconformismo de Ana Lúcia:</strong>
              <span>Recorreu ao TJMG invocando tese de vulnerabilidade, "violência patrimonial" e descabida compensação com débitos alimentares.</span>
            </div>
          </div>
          <div class="col-card accent-card">
            <div class="col-title orange">🛡 Defesa Técnica RDAA & Desfecho no TJMG</div>
            <div class="point-item">
              <strong>Encargos da Posse Exclusiva:</strong>
              <span>Jurisprudência mansa do TJMG (AC 0013168-49.2018.8.13.0148) e STJ (AREsp 2.462.038/SP): tributos e conservação cabem ao coproprietário ocupante.</span>
            </div>
            <div class="point-item">
              <strong>Rejeição de "Violência Patrimonial":</strong>
              <span>Demostrada a inadequação do art. 7º da Lei Maria da Penha para justificar inadimplência tributária quando a parte protestada é o ex-marido.</span>
            </div>
            <div class="point-item">
              <strong>Impossibilidade de Compensação:</strong>
              <span>Alimentos possuem via executiva própria (rito de prisão/penhora) e não admitem confusão com obrigações propter rem.</span>
            </div>
            <div class="point-item">
              <strong>Vitória Liminar no TJMG:</strong>
              <span>O TJMG afastou apenas a multa diária de R$ 200,00, mantendo íntegro o dever da agravante de arcar com o passivo de IPTU.</span>
            </div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
        <span class="page-indicator">04 / 07</span>
      </div>
    </div>

    <!-- SLIDE 5: FRENTE 2 ARBITRAMENTO -->
    <div class="slide" id="slide-5">
      <div class="slide-header">
        <div class="header-titles">
          <div class="header-bar"></div>
          <div>
            <div class="header-category">Ação Ordinária nº 5033450-63.2025.8.13.0702 — 10ª Vara Cível</div>
            <h2 class="header-title">Frente II — Arbitramento de Aluguéis & Ajuste do Saneador</h2>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="grid-3-vert">
          <div class="adj-card">
            <div class="adj-header">01. Fruição Exclusiva vs. Esbulho Físico</div>
            <div class="adj-body">
              <div>
                <div class="adj-sec-title gray">Equívoco no Saneador</div>
                <p>O juízo impôs a Sílvio provar que Ana estaria "impedindo ou inviabilizando na prática o uso pelo coproprietário".</p>
              </div>
              <div>
                <div class="adj-sec-title dark">Correção RDAA</div>
                <p>A jurisprudência não exige esbulho físico, violência ou expulsão material. A animosidade e impossibilidade fática de coabitação bastam.</p>
              </div>
              <div>
                <div class="adj-sec-title orange">Precedente STJ</div>
                <p><strong>REsp 1.699.013/DF:</strong> O fato gerador indenizatório é a fruição exclusiva concomitante à inequívoca oposição do outro coproprietário.</p>
              </div>
            </div>
          </div>
          <div class="adj-card">
            <div class="adj-header">02. Delimitação do Termo Inicial</div>
            <div class="adj-body">
              <div>
                <div class="adj-sec-title gray">Equívoco no Saneador</div>
                <p>O juiz fixou genericamente "marco temporal da privação", sem qualificar juridicamente qual ato constitui a ré em mora.</p>
              </div>
              <div>
                <div class="adj-sec-title dark">Piso Garantido</div>
                <p>Fixação expressa da data da citação válida como piso mínimo inquestionável para incidência dos aluguéis indenizatórios.</p>
              </div>
              <div>
                <div class="adj-sec-title orange">Marco Anterior</div>
                <p>Resguardo da pretensão desde 13/03/2023 (separação), condicionada a certidões de oposição inequívoca já juntadas ao divórcio.</p>
              </div>
            </div>
          </div>
          <div class="adj-card">
            <div class="adj-header">03. Rito do Art. 357, §1º do CPC</div>
            <div class="adj-body">
              <div>
                <div class="adj-sec-title gray">Estratégia Processual</div>
                <p>Uso de Manifestação de Esclarecimentos e Ajustes (art. 357, §1º) em vez de Embargos de Declaração hostis.</p>
              </div>
              <div>
                <div class="adj-sec-title dark">Benefício Prático</div>
                <p>Estabilização do saneamento antes da especificação de provas, balizando com clareza o objeto da perícia avaliatória.</p>
              </div>
              <div>
                <div class="adj-sec-title orange">Prevenção Recursal</div>
                <p>Requerimento subsidiário com esteio no art. 1.022 para resguardar formalidades caso o juízo decline dos esclarecimentos.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
        <span class="page-indicator">05 / 07</span>
      </div>
    </div>

    <!-- SLIDE 6: FRENTE 3 RECONVENCAO -->
    <div class="slide" id="slide-6">
      <div class="slide-header">
        <div class="header-titles">
          <div class="header-bar"></div>
          <div>
            <div class="header-category">Defesa Patrimonial Ativa — 10ª Vara Cível</div>
            <h2 class="header-title">Frente III — Defesa na Reconvenção: Edifício Sense</h2>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="grid-2">
          <div class="col-card">
            <div class="col-title gray">⚠ O Risco da Inversão Precoce do Ônus</div>
            <div class="point-item">
              <strong>Pretensão Reconvencional Extensiva:</strong>
              <span>Ana Lúcia formulou pedido de inclusão do apartamento no Edifício Sense Vertical Living na comunhão, postulando aluguéis de Sílvio.</span>
            </div>
            <div class="point-item">
              <strong>Ambiguidade na Decisão de Saneamento:</strong>
              <span>O saneador atribuiu a Sílvio o ônus de provar fato impeditivo (CPC, art. 373, II), criando risco de inversão probatória não dita.</span>
            </div>
            <div class="point-item">
              <strong>Ameaça do Art. 1.660 do Código Civil:</strong>
              <span>Risco de o magistrado aplicar a presunção relativa de comunhão de bens como presunção absoluta, dispensando Ana de provar a aquisição na constância.</span>
            </div>
          </div>
          <div class="col-card accent-card">
            <div class="col-title orange">🛡 A Blindagem Técnica RDAA</div>
            <div class="point-item">
              <strong>Primazia do Art. 373, I do CPC:</strong>
              <span>Incumbe exclusivamente à reconvinte o encargo de comprovar que o bem integra o acervo partilhável e foi adquirido com recursos comuns.</span>
            </div>
            <div class="point-item">
              <strong>Presunção Inoperante sem Fato Constitutivo:</strong>
              <span>A presunção do art. 1.660 do CC não tem o condão de suprir a inércia probatória inicial da reconvinte.</span>
            </div>
            <div class="point-item">
              <strong>Coexistência Regrada de Encargos:</strong>
              <span>O ônus imposto a Sílvio (art. 373, II) atua como prova subsidiária impeditiva, sem afastar a premissa de que a autora da reconvenção prove seu direito.</span>
            </div>
            <div class="point-item">
              <strong>Comprovação Documental de Reserva:</strong>
              <span>Sílvio possui lastro bancário e documental integral atestando aquisição autônoma com recursos próprios.</span>
            </div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
        <span class="page-indicator">06 / 07</span>
      </div>
    </div>

    <!-- SLIDE 7: TIMELINE & CRONOGRAMA -->
    <div class="slide" id="slide-7">
      <div class="slide-header">
        <div class="header-titles">
          <div class="header-bar"></div>
          <div>
            <div class="header-category">Roadmap Estratégico RDAA</div>
            <h2 class="header-title">Cronograma de Ações & Providências Críticas</h2>
          </div>
        </div>
        <img src="{logo_uri}" alt="Romano Donadel" class="header-logo">
      </div>
      <div class="slide-body">
        <div class="timeline-container">
          <div class="timeline-row">
            <div class="timeline-tag highlight">ETAPA 01</div>
            <div class="timeline-info">
              <div class="timeline-title">Julgamento Colegiado no TJMG (AI nº /006)</div>
              <div class="timeline-desc">Acompanhar pauta da 8ª Câmara Cível Especializada; distribuir memoriais e sustentar a confirmação definitiva da obrigação de Ana arcar com o passivo de IPTU e custas de protesto.</div>
            </div>
          </div>
          <div class="timeline-row">
            <div class="timeline-tag">ETAPA 02</div>
            <div class="timeline-info">
              <div class="timeline-title">Especificação de Provas na 10ª Vara Cível</div>
              <div class="timeline-desc">Apresentar quesitos para perícia de arbitramento do valor locatício da casa da Begônias e juntar documentação do divórcio consolidando oposição inequívoca desde 13/03/2023.</div>
            </div>
          </div>
          <div class="timeline-row">
            <div class="timeline-tag">ETAPA 03</div>
            <div class="timeline-info">
              <div class="timeline-title">Fiscalização da Baixa do Protesto Municipal</div>
              <div class="timeline-desc">Notificar a Procuradoria Fiscal e o 1º Tabelionato de Protestos de Uberlândia quanto à ordem judicial, resguardando certidão negativa de débitos em nome de Sílvio.</div>
            </div>
          </div>
          <div class="timeline-row">
            <div class="timeline-tag">ETAPA 04</div>
            <div class="timeline-info">
              <div class="timeline-title">Instrução Pericial na Partilha (3ª Vara de Família)</div>
              <div class="timeline-desc">Preservar o isolamento do Edifício Sense Vertical Living do plano de partilha e exigir compensação formal de todas as dívidas tributárias pagas pelo cliente.</div>
            </div>
          </div>
        </div>
      </div>
      <div class="slide-footer">
        <span>CONFIDENCIAL | ROMANO DONADEL ADVOGADOS</span>
        <span class="page-indicator">07 / 07</span>
      </div>
    </div>

  </div>

  <!-- CONTROLS -->
  <div class="controls-bar">
    <div class="nav-buttons">
      <button class="btn-nav" id="prevBtn" onclick="changeSlide(-1)">◀ Anterior</button>
      <button class="btn-nav" id="nextBtn" onclick="changeSlide(1)">Próximo ▶</button>
    </div>
    <div class="dots-container" id="dotsContainer"></div>
    <div>Navegue com [◀] ou [▶] no teclado</div>
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
        if (idx + 1 === currentSlide) {{
          dot.classList.add('active');
        }} else {{
          dot.classList.remove('active');
        }}
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

print(f"Apresentação HTML criada com sucesso em: {HTML_OUTPUT}")
