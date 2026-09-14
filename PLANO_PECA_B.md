# Plano de Extrema Produtividade para Peça Tipo B 

## Objetivo
Reduzir o tempo de execução e iteração do nível B para 50% do nível A, garantindo qualidade técnica com menor profundidade exploratória e mais resiliência contra loops mecânicos (QA). 

## Eixos Estruturais

### 1. Orçamento Diferenciado e Foco (Planner)
- **Como é no A:** Busca exaustiva, compilação de múltiplos precedentes, `critic` avaliza o draft (longo).
- **Ajuste para B:** O `planner` será instruído (via flag em `roteamento.json` ou instrução de pacote) a realizar busca **direta e limitada** (max 2 precedentes fundamentais, sem devaneio doutrinário).
- **Sem fase `critic`:** O B já pula o `criticizing`, ganhando velocidade.

### 2. Paralelização e Extração Inteligente
- O novo estágio `intake_ready` com `PyMuPDF` já resolve o gargalo de OCR que afetava todos os níveis (inclusive B). Um arquivo PDF longo é extraído 10x mais rápido que chamadas `vision_analyze` segmentadas. 
- A compilação do contexto do cofre (`vault_context_ready`) pode operar de forma leve para nível B (apenas metadados essenciais, sem full-text fetch de casos análogos pesados).

### 3. Cache de Fases (Reaproveitamento)
- Com a correção que fizemos `_check_duplicate_attempt`, o motor já entende se uma tentativa é duplicata cega. 
- Para subir a produtividade de retomadas: O comando `cli resume` deve habilitar **Skip-Cache**: se o QA falhar apenas na formatação (ex: numeração de tópicos errada), a próxima rodada do `validator` ou `writer` não deve re-planejar ou reescrever a peça toda. O motor já persiste os outputs no `RDAAState` via artefatos.

### 4. Revisão Automática Anti-Gargalo (Auto-Fix de QA)
- **Problema Atual:** Falhas ortográficas ou estilísticas de quebra de linha reprovam no `qa_passed` e estouram disjuntor, travando a matéria para o humano arrumar a formatação.
- **Solução proposta (Auto-QA Fix):** Antes de entregar o DOCX, se a falha no gate de QA for **estritamente formativa (ex: layout de alíneas, falta de negrito em pedidos)**, o `production_worker` (ou `QA Gate`) executa uma rotina automática e determinística em Markdown via script local, regerando o DOCX na hora. Se for insanável (falta de elemento da petição), reprova e segue para disjuntor.

