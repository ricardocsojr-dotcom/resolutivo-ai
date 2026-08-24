# Walkthrough: Servidor MCP Remoto Resolutivo.AI

A transformação do plugin **Resolutivo.AI** em um servidor **MCP Remoto (Model Context Protocol)** foi concluída com sucesso, preservando 100% das regras e funcionalidades do plugin e disponibilizando transporte **Streamable HTTP** (`/mcp`), verificação de saúde (`/health`), autenticação modular (OAuth 2.1 e Bearer) e suporte a deploy conteinerizado.

---

## 1. O que foi Implementado

### 1.1 Núcleo do Servidor MCP (`src/`)
* **Transporte**: Streamable HTTP no endpoint `/mcp` com Starlette ASGI e SDK oficial `FastMCP`.
* **Health Check**: Endpoint `/health` respondendo status, versão e capacidades.
* **Autenticação Modular**:
  - **Modo Desenvolvimento** (`AUTH_MODE=none`): Sem atrito para testes locais e MCP Inspector.
  - **Modo Bearer** (`AUTH_MODE=bearer`): Validação de API Key estática.
  - **Modo OAuth 2.1** (`AUTH_MODE=oauth`): Endpoints `/.well-known/oauth-authorization-server`, `/oauth/authorize` e `/oauth/token` com suporte a PKCE (`S256`) e JWT, 100% compatível com o cadastro de **Connected Apps do Google Gemini**.
* **Segurança e Privacidade**: Filtro de sanitização de logs eliminando PII, números de processos, CPFs, tokens e segredos do `stdout`.

### 1.2 Catálogo MCP Completo

#### 13 Ferramentas MCP (`Tools`)
1. `consultar_processo`: Consulta processo por número CNJ no DataJud.
2. `buscar_processos_por_parte`: Pesquisa processos por nome da parte e polo (ATIVO/PASSIVO).
3. `buscar_processos_por_assunto`: Busca processos por matéria jurídica.
4. `listar_tribunais`: Relação de todos os tribunais e índices suportados no DataJud.
5. `buscar_publicacoes_djen`: Busca publicações oficiais no DJEN via Comunica PJe.
6. `buscar_publicacoes_dje_cnj`: Localiza publicações de DJe diretamente nos movimentos processuais.
7. `calcular_atualizacao_judicial`: Motor aritmético de correção monetária e juros moratórios com tabelas oficiais.
8. `listar_indices_disponiveis`: Catálogo de índices e status de aprovação.
9. `liquidar_pedidos_provisao`: Liquidação aritmética de pedidos e provisionamento ponderado por risco (Decimal).
10. `classificar_tipo_peca`: Validação de nível de complexidade (Tier A, B, C) e regras de redação.
11. `validar_esqueleto_peca`: Validação objetiva de esqueleto estrutural contra o CPC.
12. `verificar_estilo_rdaa`: Linter estilométrico objetivo (proibição de travessões, pontuação fora de lista, aberturas defensivas).
13. `converter_tabela_perfil`: Normalização de tabela de parcelas/custas para formato CSV perfil.

#### 10 Prompts MCP (`Prompts`)
* `redigir_peca`, `revisar_peca`, `analisar_risco_processual`, `conselho_deliberativo`, `critico_adversarial`, `gerar_briefing_andamentos`, `organizar_prazos_backoffice`, `redigir_dano_moral_rct`, `aplicar_legal_design`, `aplicar_estilo_flavia`.

#### 8 Recursos MCP (`Resources`)
* `rdaa://perfil/escritorio`, `rdaa://regras/redacao`, `rdaa://checklists/revisao/juridico`, `rdaa://checklists/revisao/visual`, `rdaa://checklists/revisao/estilometria`, `rdaa://provisao/metodologia`, `rdaa://indices/manifest`, `rdaa://slide-style/guia`.

---

## 2. Árvore de Arquivos Criados e Alterados

```
resolutivo-ai/
├── src/
│   ├── __init__.py                                 [NOVO]
│   ├── server.py                                   [NOVO] Ponto de entrada FastMCP / Starlette
│   ├── auth/                                       [NOVO]
│   │   ├── __init__.py                             [NOVO]
│   │   ├── middleware.py                           [NOVO] Middleware de autenticação e CORS
│   │   ├── oauth_provider.py                       [NOVO] Endpoints OAuth 2.1 RFC 8414
│   │   └── security.py                             [NOVO] JWT, variáveis de ambiente e sanitização
│   ├── tools/                                      [NOVO]
│   │   ├── __init__.py                             [NOVO]
│   │   ├── cnj_tools.py                            [NOVO] DataJud e DJEN
│   │   ├── calculo_tools.py                        [NOVO] Motor de cálculo judicial
│   │   ├── provisao_tools.py                       [NOVO] Liquidação determinística
│   │   ├── revisor_tools.py                        [NOVO] Classificação, esqueleto e estilo
│   │   └── base_tools.py                           [NOVO] Conversor CSV perfil
│   ├── prompts/                                    [NOVO]
│   │   ├── __init__.py                             [NOVO]
│   │   └── prompts_registry.py                     [NOVO] 10 Prompts estruturados
│   └── resources/                                  [NOVO]
│       ├── __init__.py                             [NOVO]
│       └── resources_registry.py                   [NOVO] 8 Recursos normativos
├── tests/
│   ├── conftest.py                                 [NOVO] Configuração de fixtures pytest
│   ├── test_mcp_server.py                          [NOVO] Testes de /health, /mcp e metadados
│   ├── test_mcp_tools.py                           [NOVO] Testes de execução real das ferramentas
│   ├── test_mcp_auth.py                            [NOVO] Testes de OAuth 2.1, PKCE e Bearer
│   ├── test_qa_engineering.py                      [ALTERADO] Correção de fixtures
│   └── ... (demais testes preservados)
├── skills/formatar-peca/scripts/anotar_decisao.py  [ALTERADO] Suporte a pypdfium2/fitz com doc.close()
├── Dockerfile                                      [NOVO] Imagem de produção
├── .dockerignore                                   [NOVO]
├── .env.example                                    [NOVO] Variáveis de ambiente sem credenciais
├── requirements.txt                                [NOVO] Dependências raiz do servidor
├── render.yaml                                     [NOVO] Manifesto de deploy Render
├── Procfile                                        [NOVO] Configuração Railway/Heroku
├── cloudbuild.yaml                                 [NOVO] Configuração Google Cloud Run
├── pytest.ini                                      [NOVO]
└── README.md                                       [ALTERADO] Documentação completa do servidor MCP
```

---

## 3. Validação e Testes Automatizados

### Resultado da Suíte de Testes
Execução completa via `pytest`:

```
======================= 91 passed, 2 warnings in 19.70s =======================
```

Todos os 91 testes (testes do servidor MCP, ferramentas, OAuth, fluxos legados de QA e engenharia) passaram com 100% de sucesso.

### Validação das Rotas HTTP em Execução Local
* **GET `/health`**: Retornou HTTP 200 `{"status": "healthy", "service": "resolutivo-ai-mcp", "version": "3.0.0", "mcp_endpoint": "/mcp", "capabilities": {...}}`
* **GET `/.well-known/oauth-authorization-server`**: Retornou HTTP 200 com os metadados OAuth 2.1 RFC 8414.

---

## 4. Como Conectar ao Google Gemini

### URLs para Cadastro no Gemini Connected Apps
Ao hospedar a aplicação (ex: no Render, Cloud Run ou Railway):
- **MCP Server URL**: `https://<seu-dominio>/mcp`
- **Authorization URL**: `https://<seu-dominio>/oauth/authorize`
- **Token URL**: `https://<seu-dominio>/oauth/token`
- **Scopes**: `mcp:all`

### Credenciais
- **Client ID**: Valor definido na variável de ambiente `OAUTH_CLIENT_ID`
- **Client Secret**: Valor definido na variável de ambiente `OAUTH_CLIENT_SECRET`
