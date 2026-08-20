# Catálogo auditável de skills e referências externas

## Regra de governança

Nenhuma skill externa entra no fluxo por volume ou por reputação. Cada item precisa de origem, licença conhecida, finalidade, compatibilidade com o RDAA, dependências, risco de sobreposição, status de teste e decisão de integração. O catálogo é informativo e não ativa skills automaticamente.

## Itens integrados

| Identificador | Origem | Finalidade | Acionamento | Dependências | Status |
|---|---|---|---|---|---|
| `estilo-flavia-rdaa` | Arquivo enviado por Ricardo | Camada opcional de estilo para peça já redigida | `estilo_alvo: flavia` ou pedido explícito | Perfil local em Markdown e fluxo RDAA | Integrado com guardas RDAA |
| `converter-arquivo-grande` | Arquivo enviado por Ricardo | Extração local antes da leitura de arquivo extenso | Arquivo grande ou pedido explícito | Ferramentas já disponíveis, sem instalação automática | Integrado com custo zero |
| `previsao-condenacao-rdaa` | Arquivo enviado por Ricardo | Análise de provisão pré-sentença sob demanda | `modo: previsao_condenacao` e pedido explícito | Script local de liquidação. Fontes externas opcionais | Integrado como módulo isolado |
| `data-storytelling-rdaa` | Derivada de arquivo enviado por Ricardo | Referência de narrativa visual para A/B | Legal Design autorizado | Nenhuma | Integrada como referência, não como skill autônoma |

## Itens consultivos

| Identificador | Origem | Aprendizado aproveitado | Limite |
|---|---|---|---|
| `aas-core-patterns` | https://github.com/sickn33/agentic-awesome-skills | Catálogo, seleção explícita, manifestos e plano antes da alteração | Não importar catálogo, MCP, Workbench ou Node |
| `awesome-legal-skills-patterns` | https://github.com/lawve-ai/awesome-legal-skills | Curadoria por domínio, licença e status | Não importar lista em massa |
| `claude-for-legal-patterns` | https://github.com/anthropics/claude-for-legal | Perfil operacional, cold start e invariantes de plugin | Não adicionar entrevista, marketplace ou conectores obrigatórios |
| `docx-declarative-components` | https://github.com/dolanmiu/docx | Componentes declarativos e documentação de DOCX | Não trocar `python-docx` nem introduzir Node |
| `lex-intel-visual-design-patterns` | https://github.com/fbmoulin/lex-intel-visual-design | Componentes visuais tipados e testes sem banco | Não importar SaaS, banco, exportação ou paleta externa |

## Regras de segurança

A skill Flávia não prova autoria ou identidade pessoal. O perfil é um corpus de compatibilidade e a fidelidade factual e jurídica prevalece sobre estilo. A skill de previsão não decide risco nem cria probabilidade. O conversor não substitui conferência da fonte original. O data storytelling não transforma dados ausentes em conclusões.

Todos os itens passam pelo candidato temporário, pela revisão RDAA e pela publicação protegida quando produzirem conteúdo para um DOCX. Nenhum item autoriza consulta automática ao vault, CNJ, DataJud, DJEN ou Jusbrasil.
