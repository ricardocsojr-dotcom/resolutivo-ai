# Plano de correções — diagnóstico cruzado (Claude Code + Antigravity)

> **Status:** Fases 1 e 2 aplicadas e verificadas (suíte completa passando — 69 testes).
> Fase 3 (gate de escalonamento) e Fase 4 (arquitetura) seguem pendentes.
> Durante a Fase 2, surgiu e foi corrigido um achado adicional não previsto
> neste plano original: o gate de estilo (`verificar_estilo.py`) bloqueava
> 100% das peças reais por contradição entre `construir_peca.py` (exige
> "(Assinado Eletronicamente)") e a regra de aposto explicativo (proibia
> qualquer parênteses não-curto). Também foram endurecidas, a pedido do
> Ricardo, as regras de travessão (zero-tolerância) e ponto-e-vírgula
> (permitido só em lista/alínea) — ver commits/mudanças em
> `verificar_estilo.py`, `redacao-rdaa.md` e `checklist-3-estilometria.md`.

## Escopo deste documento

Este é um documento de orquestração, não de execução. Ele descreve **o que fazer, onde, e por quê** para cada achado confirmado ou plausível no diagnóstico cruzado do Resolutivo.AI. Nenhuma correção foi aplicada até o momento da escrita deste plano.

Cada item traz: arquivo, causa raiz, o que fazer, e como validar que a correção funcionou. Quem for executar (Ricardo, sócio, ou uma sessão de Claude Code/Antigravity autorizada) pode seguir a lista sem precisar re-investigar o problema.

Convergência: os achados abaixo foram confirmados por duas análises independentes (Claude Code e Antigravity), lendo o mesmo código-fonte.

---

## Fase 1 — Bugs confirmados (prioridade técnica antes de uso real)

### 1.1 Mapeamento de tribunal por NPU quebrado

**Arquivo:** `servers/cnj-server.py`, função `buscar_publicacoes_dje_cnj`, por volta da linha 358-377

**Causa raiz:**
- O padrão oficial de NPU do CNJ é `NNNNNNN-DD.AAAA.J.TR.OOOO`. Removendo separadores, isso corresponde a: posições `13` = segmento de Justiça (1 dígito), `14-15` = código do tribunal (2 dígitos), `16-19` = código de origem (4 dígitos).
- O código atual faz `codigo_tribunal = num_limpo[13:17]`, uma janela de 4 dígitos que mistura o segmento, o tribunal e o primeiro dígito da origem (ex.: gera `"8260"` em vez do tribunal real).
- O dicionário `CODIGO_TRIBUNAL` usa chaves de 4 dígitos inventadas (`"8026"` → TJSP) que não existem na tabela oficial do CNJ. O código real de TJSP é `26` dentro do segmento `8` (Justiça Estadual).

**Impacto real (com escopo correto):** este bug só é acionado quando alguém chama `buscar_publicacoes_dje_cnj` explicitamente — a consulta CNJ/DataJud/DJEN não é automática no fluxo normal de redação, conforme já definido no `CLAUDE.md`. Não é risco de prazo passando batido silenciosamente no dia a dia. É risco de retorno errado quando a consulta é pedida sob demanda.

**O que fazer:**
1. Trocar `num_limpo[13:17]` por `num_limpo[13:16]` (segmento + tribunal, 3 dígitos) ou separar em duas variáveis: `segmento = num_limpo[13]`, `tribunal_codigo = num_limpo[14:16]`.
2. Reconstruir `CODIGO_TRIBUNAL` usando a tabela oficial de códigos de tribunal do CNJ (segmento 8 = Justiça Estadual, segmento 4 = Justiça Federal, etc.), indexada por `(segmento, tribunal_codigo)` ou por tribunal_codigo dentro de cada segmento — não por uma string de 4 dígitos fabricada.
3. Fonte da tabela oficial: Resolução CNJ nº 65/2008 (tabela de códigos de segmento e tribunal do Judiciário), ou a tabela pública do próprio DataJud.

**Como validar:** escrever um teste com pelo menos 5 NPUs reais de tribunais diferentes (TJSP, TJMG, TRF1, STJ, TST) e confirmar que a função identifica o tribunal correto para cada um.

---

### 1.2 Estouro de precisão no `quantize()` do motor de cálculo

**Arquivo:** `skills/calculo-judicial/scripts/calculo_motor.py`, por volta da linha 436-483

**Causa raiz:**
- O cálculo principal (fator de correção, juros, total) roda dentro de `with localcontext() as context: context.prec = 50`, que termina na linha ~468.
- As funções `_money_text` e `_decimal_text`, que chamam `.quantize()` para formatar os valores finais, são executadas **depois** desse bloco `with`, já fora dele — ou seja, no contexto Decimal padrão de 28 dígitos de precisão.
- Se o fator acumulado ou algum valor intermediário tiver mais de 28 dígitos significativos (períodos longos, séries de fator acumulado), `.quantize()` levanta `decimal.InvalidOperation` em vez de truncar, travando o cálculo numa entrada legítima.

**O que fazer:**
1. Mover as chamadas de `_money_text`/`_decimal_text` para dentro do mesmo `with localcontext(prec=50)`, **ou**
2. Abrir um novo `localcontext(prec=50)` especificamente ao redor da montagem do dicionário `result` (linhas ~470-498), já que ele também chama essas funções de formatação.
3. Confirmar que não há nenhum outro ponto no arquivo onde `Decimal.quantize()`/operações aritméticas ocorrem fora de um contexto de precisão explícita.

**Como validar:** criar um caso de teste com um período longo (ex.: 10+ anos) e um índice de fator acumulado que force um coeficiente com mais de 28 dígitos, e confirmar que o cálculo completa sem `InvalidOperation`.

---

## Fase 2 — Robustez (riscos plausíveis, sem urgência de incêndio, mas devem entrar antes de uso real de cada módulo)

### 2.1 Provisão calculada em `float`, não `Decimal`

**Arquivo:** `skills/previsao-condenacao-rdaa/scripts/liquidar_pedidos.py`, por volta da linha 81-94

**Causa raiz:** a soma de `total_liquidado` e `total_provisao` é feita com `float` nativo, com `round()` aplicado a cada passo. Isso é inconsistente com o padrão já estabelecido em `calculo_motor.py` (que usa `Decimal` corretamente) e sujeito ao erro clássico de ponto flutuante binário (`0.1 + 0.2 != 0.3`).

**O que fazer:** reescrever a aritmética monetária do script usando `Decimal`, seguindo o mesmo padrão de `calculo_motor.py` — inputs convertidos para `Decimal` na entrada, nunca `float` intermediário, `quantize()` só na formatação final (dentro do contexto de precisão correto, ver item 1.2 para não repetir o mesmo erro aqui).

**Como validar:** teste somando uma lista de pedidos com valores que tipicamente quebram float (ex.: múltiplos de 0.1, 0.2, 0.3) e conferir que o total bate exatamente com o cálculo manual em `Decimal`.

---

### 2.2 Escrita em disco não-atômica em dois pontos

**Arquivos:**
- `skills/formatar-peca/scripts/construir_peca.py`, linha 1522 (`doc.save(output_path)`)
- `skills/revisor-rdaa/scripts/seguro.py`, linha ~53 (função `restaurar()`, usa `shutil.copy2` direto)

**Causa raiz:** todo o resto do plugin usa o padrão de escrever em arquivo temporário no mesmo diretório e depois `Path.replace()` (que é atômico no mesmo filesystem). Esses dois pontos gravam direto no destino final. Se o processo for interrompido (crash, kill, queda de energia) no meio da gravação, o arquivo de destino fica truncado ou corrompido — no caso de `seguro.py`, isso é particularmente grave porque é justamente a função de recuperação de emergência que fica vulnerável.

**Distinção importante:** isso não afeta a publicação final protegida (`publicar_docx.py`), que já usa substituição atômica corretamente. O risco está no gerador isolado (candidato ainda não publicado) e na função de restore.

**O que fazer:**
1. Em `construir_peca.py`: trocar `doc.save(output_path)` por `doc.save(tmp_path)` seguido de `tmp_path.replace(output_path)`, usando um arquivo temporário no mesmo diretório de `output_path`.
2. Em `seguro.py`, função `restaurar()`: trocar o `shutil.copy2(backup, destino)` direto pelo mesmo padrão — copiar para um temporário no diretório de `destino` e depois `Path.replace()`.

**Como validar:** teste simulando interrupção (ex.: matar o processo no meio da gravação, ou mockar uma exceção após a escrita parcial) e confirmar que o arquivo original permanece intacto em vez de corrompido.

---

### 2.3 Merge many-to-many sem proteção no diagnóstico de base

**Arquivo:** `skills/correcao-base-rdaa/scripts/diagnosticar_base.py`, por volta da linha 171-174

**Causa raiz:** o merge assume que existe exatamente uma linha com `Sufixo == '00'` por `Ficha`. Se a base tiver duplicidade nesse campo (exatamente o tipo de sujeira que esse script existe para detectar), o merge do Pandas duplica silenciosamente as linhas associadas, inflando a contagem de "recursos com origem arquivada" que vai direto para o Plano de Ação entregue.

**O que fazer:** antes do merge, validar unicidade de `Sufixo == '00'` por `Ficha` (ex.: `df[df['EhOrigem']].groupby(COL_FICHA).size()` e checar se algum grupo tem mais de 1). Se houver duplicidade, não seguir silenciosamente — reportar como um item de inconsistência do próprio diagnóstico, ou falhar explicitamente com uma mensagem clara.

**Como validar:** criar uma fixture com uma `Ficha` duplicada em `Sufixo == '00'` e confirmar que o script não duplica contagens — ou que reporta a duplicidade como achado, em vez de mascará-la.

---

### 2.4 Hash de confirmação nunca comparado

**Arquivo:** `skills/revisor-rdaa/scripts/publicar_docx.py`, por volta da linha 146-221

**Causa raiz:** `confirmed_hash` é calculado e persistido no manifesto após a substituição atômica, mas nunca comparado com `candidate_hash`. O invariante "o arquivo publicado é bit-a-bit idêntico ao candidato aprovado" está documentado no manifesto, mas não é verificado em código — hoje é uma promessa, não uma garantia ativa.

**O que fazer:** logo após calcular `confirmed_hash`, comparar com `candidate_hash`. Se divergirem, tratar como falha de publicação (reverter para o backup, não deixar o manifesto registrar sucesso).

**Como validar:** teste forçando uma divergência artificial (ex.: mockar uma escrita corrompida) e confirmar que o publicador detecta e rejeita.

---

## Fase 3 — Governança (melhoria de baixo custo, alto valor)

### 3.1 Gate explícito de escalonamento manual

**Escopo:** `skills/esqueleto-peca/` (e possivelmente referenciado por `skills/redigir-peca/`)

**Motivação:** esse gap apareceu por dois ângulos independentes de análise (comparação estrutural com padrões de skills jurídicas de referência, e a auditoria interna). O RDAA tem a classificação A/B/C, mas não tem um checklist explícito que trave o fluxo automatizado e exija decisão humana antes de seguir.

**O que fazer:** criar um arquivo de referência Markdown curto (20-30 linhas) em `skills/esqueleto-peca/references/`, listando condições de parada obrigatória — por exemplo (a decidir com Ricardo, estes são só exemplos de ponto de partida, não regras definitivas):
- Prazo fatal sem instrução clara do cliente/caso.
- Tese nova sem precedente interno aprovado.
- Valor de causa acima de um teto a definir.

O esqueleto deve consultar esse checklist antes de prosseguir com a redação por blocos, e travar pedindo decisão explícita do Ricardo quando alguma condição bater.

**Restrição importante:** esse gate não deve decidir mérito, tese, ou risco jurídico — ele só impede que o sistema siga automaticamente sem uma decisão expressa nas situações declaradas como sensíveis. Os gatilhos específicos precisam ser aprovados por Ricardo antes de virar regra — este documento não os aprova, só recomenda o mecanismo.

**Como validar:** rodar o fluxo de esqueleto com um caso de teste que bate uma das condições e confirmar que ele para e pede decisão, em vez de prosseguir.

---

## Fase 4 — Arquitetura (sem pressa, requer decisão de proporcionalidade)

Estes itens **não são bugs**. São observações de que parte da engenharia foi dimensionada para um cenário de operação diferente do atual (um único operador ativo, você e seu sócio construindo). Não devem virar remoção automática — cada um preserva uma garantia real (reversibilidade, rastreabilidade, resistência a falha) que precisa ser avaliada contra o custo de manutenção, não contra o número de usuários isoladamente.

| Elemento | O que preservar | O que pode simplificar |
|---|---|---|
| Candidato, gate, hash, publicação protegida (`publicar_docx.py`, `qa_gate.py`) | Núcleo de segurança — não mexer | — |
| Homologação por caso dourado (`promover_indice_aprovado.py`) | Núcleo de segurança do cálculo — não mexer | — |
| `seguro.py` vs `manutencao_rdaa.py` | A garantia de backup/restore em si | Duplicação: os dois reimplementam backup/restore de formas diferentes no mesmo skill. Escolher um, deletar o outro, depois de aplicar a correção de atomicidade da Fase 2.2 |
| Pipeline de 4 estágios de índice (`preparar_fonte_candidata.py` → `normalizar_indice_candidato.py` → `registrar_indice_candidato.py` → `promover_indice_aprovado.py`) | O gate de homologação por caso dourado | Só considerar simplificar depois que a homologação estiver completa e as travas estiverem bem compreendidas — não mexer nisso no meio da Fase 1-3 |
| Versionamento de schema e estado local (`estado_rdaa.py`, `contexto_rdaa.py`, `semantica_rdaa.py`) | Rastreabilidade por matéria | Avaliar depois das fases anteriores — decisão de proporcionalidade, não urgência |

**Recomendação:** não tocar na Fase 4 nesta rodada. Ela mistura duas frentes (correção de bug vs. redesenho arquitetural) e o risco de introduzir um bug novo numa simplificação apressada é maior que o ganho imediato.

---

## Ordem de execução recomendada

1. Fase 1 completa (dois bugs confirmados) — com teste de validação para cada um antes de seguir.
2. Fase 2 completa (quatro itens de robustez) — podem ser feitos em paralelo entre si, são independentes.
3. Fase 3 (gate de escalonamento) — depende de uma conversa curta com Ricardo sobre quais gatilhos específicos entram na v1 do checklist.
4. Fase 4 — não entra nesta rodada. Revisitar depois que 1-3 estiverem em produção e estáveis.

## Nota de governança

Este plano não altera nenhum arquivo do plugin. Ele existe para que quem for executar (Ricardo, sócio, ou uma sessão de IA autorizada) tenha o diagnóstico completo sem precisar re-investigar cada achado do zero. Cada correção listada acima deve ser aplicada com o teste de validação correspondente antes de ser considerada concluída.
