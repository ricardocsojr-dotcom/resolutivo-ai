# Metodologia de classificação de risco e provisão — RDAA

Este documento consolida a metodologia definida por Ricardo para o setor
Resolutivo. Tem duas camadas que trabalham juntas, não uma no lugar da outra:

- **Camada A — árvore institucional (mecânica)**: regras de transição de
  classificação conforme o estágio processual (b.1 a b.9, incluindo as
  exceções b.3.1, b.7.1, b.8 e b.9). É o padrão que o escritório já usa no
  dia a dia para classificar rapidamente.
- **Camada B — critério de auditoria (qualitativo, CPC 25/NBC TG 25)**: exige
  que a classificação reflita a força real das provas, da jurisprudência e da
  fase processual — não apenas o estágio mecânico do processo.

O papel do double-check é justamente comparar as duas: aplicar a árvore
mecânica para saber "onde o processo está" e depois perguntar, com base nas
provas e no andamento reais, se aquele valor mecânico ainda reflete a
probabilidade de perda de verdade. Divergência entre as duas camadas não é
erro automático — é o achado que deve ser reportado ao usuário para decisão.

---

## Camada A — árvore institucional (b.1 a b.9)

### b.1) Classificação inicial (processos passivos)
- Classificação: **Risco Possível**.
- Valor contingenciado: **valor da causa**.
- Justificativa: no início não há decisão judicial definitiva; o valor
  inicial representa risco potencial, não uma estimativa refinada.

### b.2) Correção monetária
- O valor contingenciado é corrigido pelo índice do TJMG.
- Juros: pendente de definição institucional — se o usuário pedir para
  aplicar juros, sinalize `[VERIFICAR: critério de juros ainda não definido
  pelo escritório]` em vez de arbitrar uma taxa.

### b.3) Após sentença
| Resultado | Classificação | Valor contingenciado | Até quando |
|---|---|---|---|
| Improcedente | Possível (mantém) | Valor da causa | Até trânsito em julgado ou reversão em recurso |
| Procedente em parte | Possível (mantém) | Valor da condenação, se líquido | — |
| Totalmente procedente | Possível (mantém) | Valor da condenação, se líquido | — |

#### b.3.1) Exceção — Juizado Especial (sentença desfavorável)
- Eleva **diretamente para Provável** — não aguarda acórdão, ao contrário da
  regra geral do b.3.
- Justificativa: o escopo recursal dos Juizados Especiais é restrito (apenas
  recurso inominado à Turma Recursal, sem acesso a tribunal superior
  ordinário), o que reduz a margem de reversão em comparação com o processo
  em vara comum.
- **Nota de governança**: processos anteriormente provisionados como
  Provável apenas por sentença desfavorável em vara comum podem exigir
  reclassificação sob esta regra refinada. A reclassificação é prática
  normal do CPC 25, com efeito contábil positivo (redução de passivo) —
  desde que o racional esteja documentado. A determinação sobre mudança de
  estimativa (CPC 23, efeito prospectivo) versus correção de erro é da
  contabilidade, fora do escopo jurídico deste skill.

### b.4) Quando não há recurso
| Situação | Classificação | Valor contingenciado |
|---|---|---|
| Depósito do valor da condenação | Remoto (até encerramento/arquivamento) | — |
| Garantia do débito sem pagamento | Provável (mantém) | Ajustado para o valor em discussão |

### b.5) Quando há recurso interposto (aguardando acórdão)
| Resultado do acórdão | Classificação | Valor contingenciado |
|---|---|---|
| 100% de êxito no recurso | Possível (mantém), depois **Remoto** após trânsito em julgado | Valor da condenação |
| Procedência mantida | **Provável** | Atualizado conforme o acórdão |

### b.6) Trânsito em julgado e arquivamento
| Desfecho | Classificação | Observação |
|---|---|---|
| Sem condenação | Remoto | — |
| Com condenação | Provável (mantém) | Valor da condenação |
| Depósito do valor | Remoto | Até encerramento e arquivamento |
| Garantia do débito sem pagamento | Provável (mantém) | Valor ajustado para o valor em discussão |
| Arquivamento do processo | **Remoto, valor zerado** | Reportar em relatório apartado |

### b.7) Exceção — processos com pedido mandatório de pagamento
Aplica-se a: **cumprimento de sentença, execução de título extrajudicial,
execução fiscal e ação monitória** — porque já nascem com obrigação de
pagamento definida, ao contrário de uma ação de conhecimento comum.

- **Classificação inicial**: Provável (não Possível — é a exceção à regra
  do b.1). Valor contingenciado: valor líquido do pedido inicial.
- **Depósito do valor**: Remoto, até encerramento/arquivamento.
- **Garantia do débito sem pagamento**: Provável (mantém). Valor ajustado
  para o valor em discussão.

#### b.7.1) Exceção — ação monitória
- Inicia como **Possível** (título ainda não constituído).
- Escalona para **Provável** em caso de revelia, ou segue a árvore comum de
  ação de conhecimento (b.1 em diante) se houver embargos.

### b.8) Acordo com parcelamento
Aplica-se a processos passivos resolvidos por acordo, com pagamento
parcelado. Uma vez que o acordo formaliza um cronograma de pagamento
definido, a incerteza típica do CPC 25 se dissolve para o valor acordado —
o item sai do regime de contingência jurídica e passa a ser tratado como
obrigação financeira ordinária, salvo quebra do acordo.

- **Durante o cumprimento ativo do parcelamento**: Classificação **Remoto**.
  Não é objeto de provisão jurídica específica — a contabilidade absorve a
  previsão de gasto das parcelas em seu próprio fluxo, como obrigação
  contratual ordinária, não como passivo contingente.
- **Quebra do acordo**: o contingenciamento só é constituído a partir da
  notícia de quebra. A partir desse evento, a contingência é calculada com
  base na multa (cláusula penal) específica prevista no instrumento daquele
  caso particular — não um percentual ou valor genérico entre casos. Esta é
  a aplicação prática da cláusula resolutiva: a contingência residual é
  classificada de forma independente, a partir do risco de inadimplemento
  já concretizado.
- **Valor a contingenciar após a quebra**: o saldo remanescente das
  parcelas não pagas — equivalente ao valor integral original da
  condenação/débito, descontado o que já foi efetivamente pago.
  **Exceção**: se a parte exequente apresentar um cálculo de saldo menor
  que o calculado internamente, prevalece o valor menor. Em outras
  palavras, adotar sempre o valor menos oneroso ao cliente entre o cálculo
  interno e o cálculo apresentado pela parte contrária.

### b.9) Ação declaratória de inexistência de débito
Caso particular: o cliente é **autor** no processo, mas é **economicamente
passivo** — a posição processual não define, sozinha, a lógica de provisão.

| Cenário | Tratamento |
|---|---|
| Débito já registrado em passivo (contas a pagar suspenso) | Provisão cobre apenas os acessórios: sucumbência, custas, diferenças de correção monetária — evitando duplicidade, já que o principal já está reconhecido no passivo. |
| Débito não registrado no passivo | O valor integral do débito entra na árvore de risco como exposição passiva, seguindo b.1–b.7 normalmente. |

### Resumo das três categorias (definição operacional da árvore)
- **Possível**: potencial condenação, sem certeza suficiente.
- **Provável**: alta chance de condenação, valor contingenciado.
- **Remoto**: chances baixas de condenação, ou valor já garantido em juízo.

---

## Camada B — critério de auditoria (CPC 25 / NBC TG 25)

A classificação final não deve ser um rótulo sem lastro. Toda classificação
deve vir acompanhada de fundamento objetivo e rastreável — nunca "risco
possível" ou "risco provável" sem explicar por quê.

- **Risco provável**: perda mais provável que vitória. Indicadores: decisão
  desfavorável relevante, prova documental robusta contra o cliente, laudo
  pericial desfavorável, jurisprudência consolidada contrária, baixa
  viabilidade recursal, fase processual avançada com pouca margem de
  reversão. Havendo estimativa confiável, indicar valor como **provisão
  recomendada**.
- **Risco possível**: incerteza material, sem predominância clara de perda
  ou êxito. Indicadores: tese defensiva plausível, jurisprudência dividida,
  necessidade de produção de prova, ausência de decisão de mérito, riscos
  relevantes ainda não consolidados. Em regra, não se recomenda provisão
  contábil, mas o caso deve ser monitorado como **passivo contingente**
  (conforme materialidade definida pelo cliente/auditoria).
- **Risco remoto**: possibilidade de perda baixa. Indicadores: tese
  defensiva forte, vício processual relevante, ilegitimidade, prescrição,
  decadência, ausência de prova mínima, precedente vinculante favorável,
  decisão favorável relevante. Em regra, sem provisão nem divulgação como
  passivo contingente, salvo política interna mais conservadora do cliente.

**Como aplicar o double-check**: depois de obter a classificação mecânica
(Camada A) a partir do estágio processual, releia as provas e o andamento
disponíveis com os olhos da Camada B. Se os indicadores qualitativos
apontarem para uma classificação diferente da mecânica (ex.: a árvore diria
"possível" porque ainda não houve sentença, mas há laudo pericial
desfavorável e jurisprudência consolidada contra o cliente), reporte a
divergência com o fundamento específico — não troque silenciosamente um
valor pelo outro.

---

## Os quatro campos financeiros (nunca usar só "valor da causa")

| Campo | Definição |
|---|---|
| Valor da causa | Valor formal da petição inicial — nem sempre reflete a exposição econômica real |
| Valor econômico envolvido | Montante total discutido no processo, atualizado quando possível |
| Valor de contingência | Estimativa do impacto financeiro no cenário jurídico mais provável (ou ponderado) |
| Valor provisionável | Parcela que, por risco provável e estimativa confiável, deve ir para avaliação contábil de provisão |

Nos **processos passivos**, considerar conforme o caso: principal discutido,
atualização monetária, juros, multa contratual/legal, honorários
sucumbenciais, custas, despesas processuais, solidariedade, limitação do
pedido, depósitos judiciais, garantias prestadas, acordos prováveis,
possibilidade de redução parcial da condenação.

Nos **processos ativos**, tratar a expectativa de recuperação com cautela:
não registrar como ativo contingente reconhecido enquanto o ingresso do
benefício não for praticamente certo. Para fins gerenciais, pode-se indicar
o valor econômico potencial, separado do valor provisionável e acompanhado
da classificação de risco de êxito.

Se o valor não puder ser estimado com segurança, **declare a limitação
expressamente** (motivo + informação necessária para mensurar) em vez de
usar um valor arbitrário.

---

## Os 17 campos mínimos por processo

1. Identificação do processo
2. Partes
3. Natureza da demanda
4. Objeto resumido
5. Fase processual
6. Último andamento relevante
7. Pedidos com impacto econômico
8. Valor da causa
9. Valor econômico atualizado
10. Valor de contingência sugerido
11. Classificação de risco
12. Fundamento da classificação
13. Depósitos, garantias ou bloqueios existentes
14. Próximos prazos ou eventos relevantes
15. Providência recomendada
16. Data-base da análise
17. Responsável pela avaliação

Campos adicionais recomendados (não obrigatórios, mas valiosos para auditoria
em massa): **escopo de materialidade** (a análise cobre todos os processos
ou só acima de um valor/área/contrato/fase/relevância?) e **fato gerador da
demanda** (evento jurídico/econômico que originou o litígio — inadimplemento
contratual, falha de serviço, cobrança de multa, execução de título,
disputa societária, responsabilidade civil, relação de consumo, relação
trabalhista, controvérsia regulatória).

## Parâmetros de qualidade da informação

a. **Completude** — número do processo, partes, natureza, juízo, fase,
   pedidos relevantes, valor da causa, valor atualizado, garantias,
   depósitos, decisões relevantes, próximos prazos.
b. **Objetividade** — evitar histórico excessivo; registrar só o que
   influencia risco, valor, estratégia ou obrigação de divulgação contábil.
c. **Rastreabilidade** — toda conclusão relevante deve remeter a uma
   decisão, documento, prova, laudo, contrato, tese jurídica, entendimento
   jurisprudencial ou evento processual identificável.
d. **Atualidade** — refletir o estágio mais recente, com data-base explícita.
e. **Consistência** — processos semelhantes recebem tratamento semelhante,
   salvo justificativa expressa para distinção.
f. **Separação fato / avaliação / recomendação** — o relatório deve deixar
   claro o que já ocorreu no processo, qual é a avaliação jurídica da
   equipe, e qual é a providência sugerida. Não misturar as três coisas na
   mesma frase.
g. **Utilidade financeira** — sempre que possível, indicar o valor
   econômico efetivamente exposto, não só o valor da causa.

## Eventos que exigem revisão da contingência

Sentença, acórdão, decisão em recurso, laudo pericial, saneamento, audiência
relevante, bloqueio patrimonial, homologação de acordo, alteração do valor
executado, depósito judicial, trânsito em julgado, início de cumprimento de
sentença, mudança relevante de jurisprudência, quebra de acordo com
parcelamento (ver b.8).

## Fronteira entre jurídico e contábil

Cabe ao jurídico (este skill) indicar: classificação de risco, fundamento,
valor econômico envolvido, valor de contingência sugerido e as limitações da
análise. A decisão sobre reconhecer provisão, divulgar em nota explicativa
ou apenas monitorar é do cliente/contabilidade, conforme sua política
contábil e o CPC 25/NBC TG 25. **Não usurpar essa decisão** — o relatório
entrega insumo para ela, não a substitui.

## Controle de versão

| Versão | Data | Alterações |
|---|---|---|
| 1.1 | Julho de 2026 | Absorvidas formalmente as exceções b.3.1 (Juizado Especial), b.7.1 (ação monitória) e b.9 (ação declaratória de inexistência de débito), antes discutidas mas não registradas neste arquivo. Registrado o b.8 (acordo com parcelamento) como ponto em aberto. |
| 1.2 | Julho de 2026 | Fechado o critério do b.8 (acordo com parcelamento): Remoto durante cumprimento ativo (contabilidade absorve a previsão de gasto); contingenciamento só é constituído na quebra do acordo, com base na multa específica do caso; valor = saldo remanescente das parcelas não pagas, ou o cálculo menor apresentado pela parte exequente, prevalecendo sempre o valor menos oneroso ao cliente. b.8 movido para dentro da árvore institucional (b.1 a b.9), deixando de ser ponto em aberto. |
