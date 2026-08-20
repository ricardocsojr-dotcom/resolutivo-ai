# Referência: Categorias de Prazo e Fluxo da Planilha

Fonte: Manual de Tratamento de Prazos — Resolutivo Back-Office Jurídico (mai/2026)

---

## Estrutura da planilha diária

| Coluna | Função |
|---|---|
| PJ | Número interno do projeto/processo no sistema |
| Prazo | Categoria do prazo (sempre começa com "2 …") |
| Prazo Fatal | Data limite — ordenar por esta coluna para garantir urgência |
| Tarefa | Tipo: elaboração de peça / cumprimento de tarefa / audiência |
| Adv | Status de distribuição: Interno · Possível Aguarda · Prazo Ag. Distrib. · Novo Prazo · Ric · Ale |
| Número do processo | Número judicial — usado para solicitar guias e localizar documentos |
| Prazo Interno? | Sim = controle interno, não exige ação imediata; Não = prazo externo |
| Autor / Réu | Partes (consulta rápida) |
| Descrição da situação | Pendente / Cumprido / outro status |
| Texto Tramitação | Campo crítico — contém decisões, orientações, valor de guia, menção a "AGUARDA" |
| Responsável do Processo | Advogado responsável — define para quem encaminhar |

### Hierarquia de status (coluna Adv)

1. **"Interno"** — Prazo Interno? = Sim. Monitorar, não agir imediatamente.
2. **"Possível Aguarda"** — Texto Tramitação contém "AGUARDA" isolado. Processo depende de terceiro (juiz, cliente). Monitorar até nova tramitação.
3. **Status anterior mantido** — Se o dia anterior já tinha "Ric", "Ale" ou outro responsável manual, manter. Não redirecionar sem confirmação.
4. **"Prazo Ag. Distrib."** — Sem histórico anterior ou status vazio. Aguardar definição da controladoria.
5. **"Novo Prazo"** — Sem histórico algum. Analisar e distribuir com urgência.

---

## Categorias de prazo e ações obrigatórias

### 2 ANÁLISE PROCESSUAL
Novo andamento ou marcação de prazo. Não exige peça — é revisão.
- Ler Texto Tramitação
- Atualizar advogado responsável
- Classificar como Interno se não exigir ação imediata

### 2 SOLICITAÇÃO DE SUBSÍDIO
Necessidade de documentos/informações do cliente para preparar peça ou ação.
- Conferir Número do Processo e Texto Tramitação
- Preparar pedido ao cliente com lista de documentos, motivo e prazo
- Manter status "Novo Prazo" até retorno
- Ver `references/comunicacao-modelo.md` para modelo de subsídio

### 2 RETORNO DO SUBSÍDIO
Controle de retorno dos subsídios solicitados.
- Verificar se documentos recebidos parecem completos
- Se incompletos: pedir complementação
- Se completos: alterar status para responsável (Ric / Ale) e encaminhar para elaboração de peça

### 2 SOLICITAR EMISSÃO DE GUIA
Emissão de guia de custas, preparo ou taxa antes de recurso ou distribuição.
- Verificar se guia já foi solicitada no Texto Tramitação
- Se não: solicitar à área financeira ou ao cliente com número do processo e finalidade
- Se Prazo Fatal próximo (menos de uma semana): **URGENTE**
- Controlar retorno até comprovante juntado nos autos
- Se Texto Tramitação indica guia já solicitada: mover para Possível Aguarda

### 2 PROVIDÊNCIAS AUDIÊNCIA
Providências antes de audiência — iniciar **um mês antes**.
- Verificar data, horário e modalidade (presencial / híbrida / videoconferência)
- Se outra cidade: avaliar contratação de preposto ou correspondente
- Providenciar: procuração, carta de preposição, substabelecimento, link ou endereço
- Informar cliente com antecedência

### 2 JUNTAR CP/SUB/AVISAR TESTEMUNHA
Carta de preposição, substabelecimento, procuração ou aviso de testemunha — geralmente **uma semana antes** da audiência.
- Verificar se já existe nos autos
- Se não: pedir ao cliente
- Conferir se testemunha precisa ser avisada
- Verificar se Prazo Fatal coincide com a data da audiência

### 2 CUMPRIMENTO DE OBRIGAÇÃO DE FAZER
Determinação judicial com prazo (liminar, juntada de documento, suspensão de apontamento).
- Prioridade máxima
- Ler Texto Tramitação para entender a obrigação exata
- Contatar cliente ou responsável interno
- Providenciar cumprimento, anexar comprovantes e protocolar
- Risco de multa ou afronta à determinação judicial

### Peças processuais (2 MANIFESTAÇÃO CÍVEL, 2 CONTESTAÇÃO CÍVEL, 2 AGRAVO DE INSTRUMENTO CÍVEL, etc.)
- Encaminhar ao advogado de produção indicado em Responsável do Processo
- Destacar prazo fatal, documentos necessários e pendências
- Não é atribuição do backoffice redigir — apenas distribuir com antecedência suficiente

---

## Regras de prioridade

**Urgente** (agir hoje):
- Prazo Fatal próximo (até 3 dias)
- Guia pendente com prazo iminente
- Cumprimento de obrigação de fazer
- Audiência com providências pendentes
- Cliente aguardando resposta sensível
- Risco de multa, preclusão ou descumprimento

**Delegável à controladoria/backoffice** (não exige advogado):
- Cadastrar processo / lançar prazo
- Solicitar guia / acompanhar emissão
- Confirmar juntada / localizar documento nos autos
- Pedir substabelecimento, procuração ou carta de preposição
- Organizar link/endereço de audiência
- Cobrar documento já solicitado
- Monitorar Possível Aguarda / Interno

**Postergável** (sai do foco imediato):
- Prazo Interno sem vencimento próximo
- Aguarda sem urgência identificada
- Follow-up sem data definida
- Leitura não urgente

---

## Comunicação com Flavia

Flavia Almeida Forti da Fonseca não acessa a planilha diariamente.

- Filtrar todas as linhas onde Responsável do Processo = Flavia
- Gerar resumo diário: Número do Processo · Categoria · Prazo Fatal · observações do Texto Tramitação
- Ordenar do mais próximo ao mais distante
- Audiências e guias: comunicar com pelo menos 15 dias de antecedência
- Enviar por e-mail ou registrar em sistema
