# Resolutivo.AI — Servidor MCP e Plugin Jurídico RDAA

Servidor MCP remoto e plugin de contencioso cível e consumerista do **Romano Donadel Advogados Associados (RDAA)**.

O projeto disponibiliza tanto o funcionamento tradicional em formato de plugin (Claude Code / Codex) quanto um **Servidor MCP Remoto (Model Context Protocol)** compatível com o **Google Gemini (Connected Apps)**, Claude Desktop, Cursor, MCP Inspector e qualquer cliente compatível com MCP.

---

## 1. Arquitetura do Servidor MCP Remoto

O servidor é construído sobre o SDK oficial do Model Context Protocol em Python (`FastMCP` + `Starlette`), adotando transporte **Streamable HTTP** de alta performance:

```
resolutivo-ai/
├── src/
│   ├── server.py                  # Ponto de entrada FastMCP, rotas /health, /mcp e OAuth 2.1
│   ├── auth/                      # Módulo de Autenticação e Segurança
│   │   ├── middleware.py          # Middleware Starlette (Bearer / OAuth / Dev)
│   │   ├── oauth_provider.py      # Provedor OAuth 2.1 (RFC 8414 /.well-known, /oauth/authorize, /oauth/token)
│   │   └── security.py            # JWT, sanitização de logs (sem PII/segredos)
│   ├── tools/                     # Ferramentas determinísticas executáveis
│   │   ├── cnj_tools.py           # DataJud e DJEN (consultar_processo, buscar_publicacoes, etc.)
│   │   ├── calculo_tools.py       # Motor aritmético de correção monetária e juros
│   │   ├── provisao_tools.py      # Liquidação determinística de pedidos e provisão
│   │   ├── revisor_tools.py       # Classificação de peças, esqueleto e linter de estilo
│   │   └── base_tools.py          # Utilitários de conversão e formatação de parcelas
│   ├── prompts/                   # Catálogo de MCP Prompts estruturados
│   │   └── prompts_registry.py    # redigir_peca, revisar_peca, conselho_deliberativo, etc.
│   └── resources/                 # Catálogo de MCP Resources (textos canônicos e checklists)
│       └── resources_registry.py  # rdaa://perfil/escritorio, rdaa://regras/redacao, etc.
├── Dockerfile                     # Imagem de produção otimizada (Python 3.12-slim)
├── render.yaml                    # Configuração para deploy no Render
├── Procfile                       # Suporte para Railway e Heroku
├── cloudbuild.yaml                # Suporte para Google Cloud Run
└── tests/                         # Suíte de 91 testes automatizados (pytest)
```

---

## 2. Relação entre as Skills Originais e o Protocolo MCP

As funcionalidades do plugin foram devidamente auditadas e convertidas de acordo com sua natureza:

### 2.1 Ferramentas MCP (`Tools` — Código Executável Determinístico)

| Ferramenta MCP | Skill de Origem | O que faz |
|----------------|-----------------|-----------|
| `consultar_processo` | `consultar-processo` | Consulta dados cadastrais, partes e 10 últimos movimentos no DataJud. |
| `buscar_processos_por_parte` | `consultar-processo` | Pesquisa processos no DataJud por nome da parte e polo (ATIVO/PASSIVO). |
| `buscar_processos_por_assunto` | `consultar-processo` | Pesquisa processos no DataJud por matéria/assunto jurídico. |
| `listar_tribunais` | `consultar-processo` | Lista siglas de tribunais válidos e seus respectivos índices no DataJud. |
| `buscar_publicacoes_djen` | `backoffice-diario` | Consulta publicações e intimações no Diário de Justiça Eletrônico Nacional (PJe). |
| `buscar_publicacoes_dje_cnj` | `backoffice-diario` | Filtra movimentações de publicação no DJe diretamente nos autos do DataJud. |
| `calcular_atualizacao_judicial`| `calculo-judicial` | Motor determinístico de correção monetária e juros moratórios com tabelas oficiais. |
| `listar_indices_disponiveis` | `calculo-judicial` | Lista índices cadastrados no manifesto e seu status de validação. |
| `liquidar_pedidos_provisao` | `previsao-condenacao-rdaa` | Soma aritmética de parcelas e ponderação de risco de condenação (Decimal). |
| `classificar_tipo_peca` | `revisor-rdaa` | Classifica o nível da peça (Tier A, B, C), rito e permissão de blocos. |
| `validar_esqueleto_peca` | `esqueleto-peca` | Valida objetivamente requisitos estruturais do esqueleto contra o CPC. |
| `verificar_estilo_rdaa` | `revisor-rdaa` | Linter estilométrico objetivo (proibição de travessões, pontuação fora de lista, etc.). |
| `converter_tabela_perfil` | `perfil-csv` | Converte tabela de parcelas em formato CSV padronizado. |

### 2.2 Prompts MCP (`Prompts` — Raciocínio, Persona e Orquestração)

| Prompt MCP | Skill de Origem | Finalidade |
|------------|-----------------|------------|
| `redigir_peca` | `redigir-peca` / `contencioso-rdaa` | Conduz a redação completa no padrão RDAA conforme o nível (A/B/C). |
| `revisar_peca` | `revisor-rdaa` | Orquestra a revisão da peça contra os Checklists 1, 2 e 3 do escritório. |
| `analisar_risco_processual`| `analise-provisao-rdaa` | Guia a classificação de risco (provável/possível/remoto) sob CPC 25 / NBC TG 25. |
| `conselho_deliberativo` | `conselho-rdaa` | Conduz o conselho deliberativo ACH com 5 conselheiros especializados. |
| `critico_adversarial` | `critico-rdaa` | Teste de estresse adversarial da tese jurídica antes do protocolo. |
| `gerar_briefing_andamentos`| `briefing-andamentos` | Estrutura o briefing matinal executivo de casos críticos. |
| `organizar_prazos_backoffice`| `backoffice-juridico` | Transforma intimações em esteira de tarefas com responsáveis e minutas. |
| `redigir_dano_moral_rct` | `dano-moral-rct` | Redige fundamentação de dano moral no estilo autoral RCT/RDAA. |
| `aplicar_legal_design` | `legal-design-rdaa` | Orienta criação de linhas do tempo, matrizes de confronto e plain language. |
| `aplicar_estilo_flavia` | `estilo-flavia-rdaa` | Camada de estilo textual adaptada ao perfil da Dra. Flávia. |

### 2.3 Recursos MCP (`Resources` — Conhecimento Normativo e Checklists)

| URI do Recurso | Conteúdo Disponibilizado |
|----------------|--------------------------|
| `rdaa://perfil/escritorio` | Identidade, setores e governança do escritório Romano Donadel (`CLAUDE.md`). |
| `rdaa://regras/redacao` | Núcleo Único de Escrita e regras de redação forense (`redacao-rdaa.md`). |
| `rdaa://checklists/revisao/juridico` | Checklist 1 — Aspectos Jurídicos e Estratégicos. |
| `rdaa://checklists/revisao/visual` | Checklist 2 — Visual Law e Formatação. |
| `rdaa://checklists/revisao/estilometria` | Checklist 3 — Estilometria e Vícios de Linguagem. |
| `rdaa://provisao/metodologia` | Metodologia da árvore de risco e provisionamento contábil. |
| `rdaa://indices/manifest` | Manifesto oficial de índices monetários e fontes primárias. |
| `rdaa://slide-style/guia` | Guia de identidade visual e paleta para apresentações executivas. |

---

## 3. Funcionalidades Bloqueadas, Pendentes ou com Dependências Específicas

1. **Jusbrasil (`buscar-jurisprudencia`)**:
   - *Status*: Mantida como fluxo via extensão do Chrome / navegador logado.
   - *Motivo*: O Jusbrasil não fornece API REST pública oficial headless sem autenticação proprietária de navegador.
2. **NotebookLM Interno**:
   - *Status*: Requer configuração de ambiente (`NOTEBOOKLM_MCP_PATH` apontando para o CLI local).
3. **Vault Obsidian**:
   - *Status*: Mantido inerte por governança institucional do escritório (gravação e leitura apenas quando explicitamente solicitado).

---

## 4. Como Executar Localmente

### 4.1 Instalação das Dependências

```bash
# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 4.2 Execução do Servidor

```bash
# Modo Streamable HTTP (padrão em http://localhost:8000/mcp com health check em /health)
python -m src.server --port 8000 --transport streamable-http

# Modo STDIO (para clientes locais como Claude Desktop)
python -m src.server --transport stdio
```

### 4.3 Verificação de Saúde

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "service": "resolutivo-ai-mcp",
  "version": "3.0.0",
  "auth_mode": "none",
  "mcp_endpoint": "/mcp",
  "capabilities": {
    "tools": true,
    "prompts": true,
    "resources": true,
    "streamable_http": true
  }
}
```

---

## 5. Como Testar com o MCP Inspector

O [MCP Inspector](https://github.com/modelcontextprotocol/inspector) permite inspecionar interativamente todas as ferramentas, prompts e recursos:

```bash
# 1. Inicie o servidor localmente (AUTH_MODE=none no .env)
python -m src.server --port 8000 --transport streamable-http

# 2. Em outro terminal, inicie o MCP Inspector:
npx @modelcontextprotocol/inspector
```

No MCP Inspector:
- Selecione o transporte: **Streamable HTTP** ou **SSE**.
- URL: `http://localhost:8000/mcp` (ou `http://localhost:8000/sse` se modo SSE).
- Clique em **Connect** para explorar as 13 ferramentas, 10 prompts e 8 recursos.

---

## 6. Conexão com o Google Gemini (Connected Apps)

Para conectar o servidor MCP ao **Google Gemini** como um aplicativo conectado personalizado:

### 6.1 URLs para Cadastro no Gemini

Após realizar o deploy (ex: `https://resolutivo-ai.onrender.com`):

* **MCP Server URL**: `https://resolutivo-ai.onrender.com/mcp`
* **Authorization URL**: `https://resolutivo-ai.onrender.com/oauth/authorize`
* **Token URL**: `https://resolutivo-ai.onrender.com/oauth/token`
* **Scopes**: `mcp:all`

### 6.2 Configuração de Credenciais OAuth 2.1

1. Defina as variáveis de ambiente no servidor:
   - `AUTH_MODE=oauth`
   - `SERVER_BASE_URL=https://resolutivo-ai.onrender.com`
   - `OAUTH_CLIENT_ID=<defina-um-id-ex-gemini-client>`
   - `OAUTH_CLIENT_SECRET=<defina-um-segredo-forte>`
   - `JWT_SECRET=<defina-uma-chave-jwt-segura>`
2. No painel de configuração de conexões do Gemini:
   - Insira o **Client ID** e **Client Secret** configurados.
   - O Gemini realizará o fluxo PKCE padrão (S256) automaticamente.

---

## 7. Instruções de Deploy

### 7.1 Deploy no Render

1. Crie um novo **Web Service** no Render conectado ao seu repositório GitHub.
2. O arquivo [`render.yaml`](file:///c:/Projetos/resolutivo-ai/render.yaml) já contém a configuração necessária:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m src.server --host 0.0.0.0 --port $PORT --transport streamable-http`
   - **Health Check Path**: `/health`
3. Configure as variáveis de ambiente no painel do Render (`AUTH_MODE`, `SERVER_BASE_URL`, etc.).

### 7.2 Deploy no Google Cloud Run

```bash
# Build e deploy direto com gcloud
gcloud run deploy resolutivo-ai-mcp \
  --source . \
  --region southamerica-east1 \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars AUTH_MODE=oauth,SERVER_BASE_URL=https://<sua-url-cloud-run>.run.app
```

### 7.3 Deploy no Railway / Heroku

O projeto já inclui [`Procfile`](file:///c:/Projetos/resolutivo-ai/Procfile):
```
web: python -m src.server --host 0.0.0.0 --port $PORT --transport streamable-http
```

---

## 8. Exemplos Práticos de Uso

### 8.1 Chamada: Consulta de Processo (`consultar_processo`)

**Entrada:**
```json
{
  "numero_processo": "1002345-67.2023.8.26.0100",
  "tribunal": "TJSP"
}
```

**Resposta:**
```json
{
  "status": "success",
  "processos": [
    {
      "numero_processo": "10023456720238260100",
      "tribunal": "TJSP",
      "classe": "Procedimento Comum Cível",
      "assuntos": ["Indenização por Dano Moral", "Inclusão Indevida em Cadastro de Inadimplentes"],
      "orgao_julgador": "2ª Vara Cível do Foro Central",
      "partes": [
        {"tipo": "ATIVO", "nome": "MARIA DA SILVA"},
        {"tipo": "PASSIVO", "nome": "BANCO EXEMPLO S.A."}
      ],
      "movimentos_recentes": [
        {"data": "2024-02-15T14:30:00", "descricao": "Conclusos para Despacho"}
      ]
    }
  ]
}
```

### 8.2 Chamada: Liquidação de Pedidos (`liquidar_pedidos_provisao`)

**Entrada:**
```json
{
  "pedidos_json": "[{\"pedido\": \"Tarifas\", \"tipo\": \"material\", \"valor_unitario\": 100.0, \"periodicidade\": \"mensal\", \"data_inicio\": \"2022-01-01\", \"data_fim\": \"2022-03-01\", \"risco\": \"provavel\"}, {\"pedido\": \"Dano moral\", \"tipo\": \"moral\", \"valor_unitario\": 8000.0, \"periodicidade\": \"unico\", \"risco\": \"possivel\"}]"
}
```

**Resposta:**
```json
{
  "status": "success",
  "total_pedidos": 2,
  "total_liquidado": 8300.0,
  "total_provisao_ponderada": 4300.0,
  "linhas": [
    {
      "pedido": "Tarifas",
      "tipo": "material",
      "valor_liquidado": 300.0,
      "risco_percentual": 100.0,
      "provisao_ponderada": 300.0
    },
    {
      "pedido": "Dano moral",
      "tipo": "moral",
      "valor_liquidado": 8000.0,
      "risco_percentual": 50.0,
      "provisao_ponderada": 4000.0
    }
  ]
}
```

### 8.3 Chamada: Linter de Estilo Forense (`verificar_estilo_rdaa`)

**Entrada:**
```json
{
  "texto_peca": "A parte autora — ora requerente — requer a procedência."
}
```

**Resposta:**
```json
{
  "status": "REPROVADO",
  "total_paragrafos_analisados": 1,
  "total_violacoes": 1,
  "violacoes": [
    "Paragrafo 0: travessao proibido na peca final, sem excecao — reescrever com virgula, ponto ou conectivo: 'A parte autora — ora requerente — requer a procedência.'"
  ]
}
```

---

## 9. Execução de Testes Automatizados

O projeto conta com suíte completa de testes unitários e de integração:

```bash
pytest
```

Output:
```
======================= 91 passed in 19.70s =======================
```

---

## 10. Licença e Direitos

Projeto proprietário desenvolvido para uso exclusivo do **Romano Donadel Advogados Associados (RDAA)**.
Responsável Técnico: Ricardo Cesar Souza de Oliveira Junior (`ricardocsojr@gmail.com`).
