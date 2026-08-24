"""Registro de Prompts MCP para redação, revisão, estratégia e governança jurídica."""

from mcp.server.fastmcp import FastMCP

def register_prompts(mcp: FastMCP) -> None:
    """Registra todos os prompts instrucionais do Resolutivo.AI no servidor MCP."""

    @mcp.prompt()
    def redigir_peca(
        tipo_peca: str,
        nivel_peca: str = "B",
        fatos_processo: str = "",
        tese_juridica: str = "",
        pedidos: str = "",
    ) -> str:
        """
        Orquestra a redação de uma peça forense no padrão RDAA (Núcleo Único de Escrita).

        Args:
            tipo_peca: Tipo da peça (ex: 'Contestação', 'Apelação', 'Agravo de Instrumento', 'Petição Inicial').
            nivel_peca: Nível de complexidade: 'A' (Premium), 'B' (Desenvolvida) ou 'C' (Simples em parágrafos curtos).
            fatos_processo: Fatos explícitos fornecidos pelo cliente/autos (nunca inventados).
            tese_juridica: Fundamentação jurídica e teses centrais.
            pedidos: Pedidos específicos a formular.
        """
        return f"""Você atuará como o Advogado Sênior de Contencioso Cível do escritório Romano Donadel Advogados Associados (RDAA).
Sua missão é redigir uma peça processual do tipo: {tipo_peca.upper()} (Nível de Produção: {nivel_peca.upper()}).

DIRETRIZES OBRIGATÓRIAS DE REDAÇÃO (NÚCLEO ÚNICO RDAA):
1. Linguagem direta, ordem direta, sem arcaísmos, floreios ou redundâncias.
2. Tese fundida na primeira frase de cada parágrafo (um parágrafo = uma ideia central; extensão ideal de 3 a 7 linhas).
3. Citações legislativas no formato padrão: 'CPC, art. 373, inciso II'.
4. Citações jurisprudenciais com aterrissagem literal e ementa completa (nunca paráfrase).
5. Títulos objetivos: NUNCA comece títulos ou subtítulos com 'Da', 'Do', 'De', 'Dos' ou 'Das'.
6. Sem travessões (—): use vírgulas, pontos ou conectivos.
7. Ponto-e-vírgula permitido APENAS em itens de listas/pedidos numerados; proibido em prosa corrida.
8. Sem aberturas defensivas repetitivas ('não se pretende', 'o que não se discute').
9. Pedidos estruturados em cascata com parágrafo introdutório.

FATOS FORNECIDOS:
{fatos_processo or '[Fatos a serem informados pelo usuário]'}

TESE JURÍDICA:
{tese_juridica or '[Teses a serem informadas pelo usuário]'}

PEDIDOS:
{pedidos or '[Pedidos a serem formulados]'}

Redija a peça completa preservando estritamente os fatos fornecidos e aplicando o estilo técnico e incisivo do RDAA."""

    @mcp.prompt()
    def revisar_peca(texto_peca: str) -> str:
        """
        Executa a revisão completa da peça aplicando os 3 checklists estruturais do RDAA.

        Args:
            texto_peca: Texto integral da peça a ser revisada.
        """
        return f"""Você atuará como o Revisor Técnico do RDAA.
Avalie a peça processual fornecida abaixo contra os 3 Checklists Oficiais do escritório:

1. CHECKLIST 1 (JURÍDICO E ESTRATÉGICO):
   - Admissibilidade, tempestividade e competência corretas.
   - Fatos separados de avaliações e sem acréscimo de elementos não documentados.
   - Fundamento legal explícito no primeiro período.
   - Pedidos claros, em cascata, correspondentes às teses.

2. CHECKLIST 2 (VISUAL E FORMATAÇÃO):
   - Estrutura hierárquica sem poluição.
   - Títulos sem preposição inicial ('Da/Do/De').
   - Destaques exclusivamente em negrito (sem sublinhados).

3. CHECKLIST 3 (ESTILOMETRIA E LINGUAGEM):
   - Proibição absoluta de travessões (—).
   - Ausência de ponto-e-vírgula fora de listas numeradas.
   - Sem aberturas defensivas reiteradas ('não se busca', 'a questão não está em').
   - Parágrafos objetivos de 3 a 7 linhas.

PEÇA A REVISAR:
{texto_peca}

Apresente um relatório objetivo de conformidade contendo:
- [APROVADO] / [RESSALVAS] / [BLOQUEIO]
- Tabela de inconformidades encontradas com localização do parágrafo e sugestão exata de correção."""

    @mcp.prompt()
    def analisar_risco_processual(
        fase_processual: str,
        jurisprudencia_dominante: str,
        provas_existentes: str,
        pedidos_economicos: str,
    ) -> str:
        """
        Analisa o risco de contingência e critérios de provisionamento sob CPC 25 / NBC TG 25.

        Args:
            fase_processual: Fase atual dos autos (ex: Inicial, Instrução, Sentença desfavorável, Apelação).
            jurisprudencia_dominante: Entendimento pacificado dos tribunais (STJ/TJ).
            provas_existentes: Provas documentais, periciais e testemunhais constantes nos autos.
            pedidos_economicos: Valores ou obrigações pleiteadas.
        """
        return f"""Você atuará como Especialista em Auditoria e Risco Processual do RDAA.
Aplique a metodologia da árvore de risco (b.1 a b.7) e o padrão CPC 25 / NBC TG 25 para os dados informados:

FASE PROCESSUAL: {fase_processual}
JURISPRUDÊNCIA / PRECEDENTES: {jurisprudencia_dominante}
CONJUNTO PROBATÓRIO: {provas_existentes}
PEDIDOS ECONÔMICOS: {pedidos_economicos}

REGRAS DE CLASSIFICAÇÃO:
- PROVÁVEL (>50% de probabilidade de perda): Exige provisionamento contábil e valor de contingência.
- POSSÍVEL (20% a 50% de probabilidade de perda): Divulgação em notas explicativas, sem provisão contábil imediata.
- REMOTO (<20% de probabilidade de perda): Sem provisão e sem necessidade de notas explicativas.

Separe expressamente:
1. Avaliação técnica do risco com base em precedentes e provas.
2. Sugestão de classificação contábil (Provável/Possível/Remoto).
3. Providência processual e estratégica recomendada (acordo, garantia, recurso especial)."""

    @mcp.prompt()
    def conselho_deliberativo(
        decisao_a_tomar: str,
        alternativas: str,
        cenario_fatico: str,
    ) -> str:
        """
        Submete uma decisão jurídica complexa à metodologia ACH (Análise de Hipóteses Concorrentes) com 5 conselheiros especializados.

        Args:
            decisao_a_tomar: O dilema ou escolha estratégica a ser avaliada.
            alternativas: Hipóteses ou caminhos disponíveis (A, B, C...).
            cenario_fatico: Elementos fáticos, processuais e econômicos relevantes.
        """
        return f"""Você coordenará o Conselho de Decisão Estratégica do RDAA aplicando o método ACH.

DILEMA: {decisao_a_tomar}
ALTERNATIVAS: {alternativas}
CENÁRIO: {cenario_fatico}

Execute o debate estruturado com as 5 perspectivas do conselho:
1. Conselheiro Cético / Red Team: Identifica os pontos cegos e riscos de cada alternativa.
2. Conselheiro Pragmatico: Avalia viabilidade prática, custo e tempo de tramitação.
3. Conselheiro Precedentalista: Foca na posição firme dos tribunais superiores (STJ/STF).
4. Conselheiro Financeiro: Avalia impacto econômico, sucumbência e custo-benefício de acordo vs litígio.
5. Conselheiro Síntese (ACH): Monta a matriz de inconsistência e define a recomendação final fundamentada."""

    @mcp.prompt()
    def critico_adversarial(tese_proposta: str, peca_tipo: str) -> str:
        """
        Executa teste de estresse da tese jurídica simulando os argumentos do adversário e do juízo.

        Args:
            tese_proposta: Argumentação jurídica desenvolvida.
            peca_tipo: Tipo de peça processual.
        """
        return f"""Você atuará como o Advogado da Parte Contrária e Juiz da Causa simulando um teste adversarial para a peça {peca_tipo}.

TESE PROPOSTA:
{tese_proposta}

Aponte de forma implacável:
1. Qual é a contra-argumentação mais provável da parte contrária?
2. Quais são as brechas probatórias ou premissas frágeis da tese?
3. Onde um juiz cético indeferiria o pedido?
4. Reformulação recomendada para blindar o argumento antes do protocolo."""

    @mcp.prompt()
    def gerar_briefing_andamentos(planilha_andamentos_texto: str) -> str:
        """
        Gera o Radar Estratégico e briefing de casos críticos a partir de planilha ou lista de andamentos.

        Args:
            planilha_andamentos_texto: Dados ou extrato dos andamentos do dia.
        """
        return f"""Você atuará como o Gestor de Backoffice Forense do RDAA.
Analise a relação de andamentos abaixo e elabore o briefing matinal executivo:

ANDAMENTOS:
{planilha_andamentos_texto}

Estruture a resposta em:
1. Casos Críticos (Prazos Fatais e Decisões Desfavoráveis Imediatas).
2. Publicações Relevantes e Despachos de Mero Expediente.
3. Quadro de Providências Imediatas (Processo, Providência, Responsável, Prazo Fatal)."""

    @mcp.prompt()
    def organizar_prazos_backoffice(publicacoes_texto: str) -> str:
        """
        Transforma intimações soltas em rotinas claras com responsável e mensagens prontas para clientes/parceiros.

        Args:
            publicacoes_texto: Texto bruto de intimações ou andamentos.
        """
        return f"""Você atuará como Coordenador Operacional do RDAA.
Processe as seguintes publicações e monte a esteira de providências:

PUBLICAÇÕES:
{publicacoes_texto}

Gere para cada caso:
- Resumo executivo da intimação (1 linha).
- Prazo em dias e sugestão de data fatal.
- Minuta pronta de mensagem para WhatsApp ou e-mail com cliente solicitando subsídios/documentos."""

    @mcp.prompt()
    def redigir_dano_moral_rct(
        fato_violador: str,
        perfil_consumidor: str,
        capacidade_economica_reu: str,
    ) -> str:
        """
        Redige a fundamentação de dano moral consumerista no estilo autoral RDAA/RCT.

        Args:
            fato_violador: Ocorrência que causou o dano (ex: negativação indevida, perda de tempo útil, golpe bancário).
            perfil_consumidor: Condição da vítima.
            capacidade_economica_reu: Porte econômico da instituição infratora.
        """
        return f"""Redija o capítulo de Indenização por Danos Morais no estilo autoral RDAA (Ricardo Cesar / RCT):

FATO VIOLADOR: {fato_violador}
PERFIL DA VÍTIMA: {perfil_consumidor}
PORTE DO RÉU: {capacidade_economica_reu}

Diretrizes:
- Sem citações doutrinárias enciclopédicas genéricas.
- Aplicação das funções pedagógica, punitiva e compensatória.
- Destaque ao desvio produtivo e perda de tempo útil do consumidor.
- Precedentes específicos do STJ (ementas literais completas)."""

    @mcp.prompt()
    def aplicar_legal_design(conteudo_juridico: str, tipo_elemento: str = "linha_do_tempo") -> str:
        """
        Estrutura elementos de Visual Law e Plain Language (linha do tempo, matriz de confronto, tabela comparativa).

        Args:
            conteudo_juridico: Fatos ou cláusulas a transformar.
            tipo_elemento: Tipo de recurso visual ('linha_do_tempo', 'matriz_confronto', 'fluxograma', 'destaque').
        """
        return f"""Converta o conteúdo jurídico fornecido em um recurso claro de Legal Design ({tipo_elemento}):

CONTEÚDO:
{conteudo_juridico}

Regras:
1. Texto pesquisável e legível.
2. Linha do tempo sequencial e sem repetições.
3. Manter rigor técnico sem rebuscamento.
4. Fornecer em formato de tabela ou blocos de texto Markdown prontos para transposição ao DOCX."""

    @mcp.prompt()
    def aplicar_estilo_flavia(texto_peca: str) -> str:
        """
        Aplica a camada de adaptação estilométrica ao tom da Dra. Flávia.

        Args:
            texto_peca: Peça redigida.
        """
        return f"""Adapte a seguinte peça processual ao estilo textual da Dra. Flávia (RDAA), preservando 100% da substância, fatos e pedidos:

PEÇA:
{texto_peca}

Ajuste a cadência para enfatizar a clareza didática, precisão de termos e transições elegantes entre parágrafos, mantendo os checklists RDAA intactos."""
