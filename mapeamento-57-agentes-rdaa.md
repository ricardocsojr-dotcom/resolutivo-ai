# Mapeamento: 57 Agents Advocacia (ASV Digital/Bravy) × plugin Resolutivo.AI

Comparação de cada um dos 57 agentes do pacote contra o que já existe no plugin
**Resolutivo.AI** (`resolutivo-ai`) (skills `buscar-jurisprudencia`, `consultar-processo`,
`redigir-peca`, `backoffice-diario`, agente `monitor-processos`) e nas skills
RDAA já instaladas (`contencioso-rdaa`, `dano-moral-rct`, `revisor-rdaa`,
`backoffice-juridico`, `jusbrasil-jurisprudencia`, `perfil-csv`).

Veredito usado em cada linha:
- **GAP** — não existe nada equivalente hoje; vale construir.
- **PARCIAL** — existe algo próximo, mas o agente cobre uma fatia que o atual não cobre bem; vale absorver como melhoria em vez de criar peça nova.
- **REDUNDANTE** — já coberto pelo que existe; não vale duplicar.
- **FORA DE ESCOPO?** — área do direito (trabalhista, família, criminal, tributário, previdenciário, imobiliário, M&A) que o RDAA pode ou não praticar. Confirmar com Ricardo antes de decidir.

## 1 · Prazos & Acompanhamento

| # | Agente | Veredito | Observação |
|---|--------|----------|------------|
| 01 | Monitor DJE/DJEN | REDUNDANTE | Coberto por `backoffice-diario` + agente `monitor-processos`. A classificação de urgência (dobro Fazenda/Defensoria) é mais detalhada no pacote — vale só enriquecer o `monitor-processos` existente com essa tabela. |
| 02 | Lembrete de prazo | **GAP** | Nada hoje calcula data fatal + gera régua D-7/D-3/D-1/D-0 + .ics. É o gap mais concreto da categoria — prazo perdido é o maior risco operacional do escritório. |
| 03 | Andamento processual | REDUNDANTE | `consultar-processo` já lê DataJud/CNJ e interpreta status. |
| 04 | Intimação | PARCIAL | `backoffice-juridico` interpreta andamento, mas não gera a minuta de resposta padrão (ciência/manifestação/prorrogação) nem detecta vício formal. Vale absorver como variação do `redigir-peca`. |
| 05 | Ciência | GAP (baixo valor) | Nicho — pode virar só um template dentro de `redigir-peca`, não precisa de agente/skill própria. |

## 2 · Petições & Documentos

| # | Agente | Veredito | Observação |
|---|--------|----------|------------|
| 06 | Petição inicial cível | REDUNDANTE | `redigir-peca` + `contencioso-rdaa` já cobrem. |
| 07 | Contestação cível | REDUNDANTE | Idem. |
| 08 | Recurso (genérico) | PARCIAL | `redigir-peca` redige, mas não tem árvore de decisão "qual recurso cabe" (admissibilidade). Vale um checklist adicional, não um agente novo. |
| 09 | Parecer jurídico | **GAP** | `contencioso-rdaa` é focado em peça de litígio; formato consultivo (parecer, não-contencioso) não existe hoje. |
| 10 | Procuração | GAP (baixo valor) | Não coberto, mas é template puro — baixo retorno para virar skill dedicada. |

## 3 · Pesquisa Jurídica

| # | Agente | Veredito | Observação |
|---|--------|----------|------------|
| 11 | Jurisprudência STJ/STF | REDUNDANTE | `buscar-jurisprudencia` já cobre Jusbrasil + DataJud. |
| 12 | Doutrina | GAP, mas arriscado | Nada cita doutrina hoje — porém não há MCP/fonte de doutrina conectada (sem Jusbrasil doutrina, sem base de livros). Implementar sem fonte verificável = risco real de citar autor/obra/página inventados. Só vale se houver fonte confiável para plugar. |
| 13 | Lei e súmula | PARCIAL | `buscar-jurisprudencia` foca em ementas, não em vigência/conflito de normas (LINDB) nem súmula isolada. |
| 14 | Tese repetitiva | **GAP** | Uso estratégico de Tema STJ/STF (afetação, suspensão, distinguishing) não existe hoje e tem valor real em qualquer carteira de processos repetitivos. |
| 15 | Ementário | GAP moderado | Poderia alimentar o NotebookLM como base de conhecimento interno — hoje não há esse pipeline de captura. |

## 4 · Atendimento ao Cliente

| # | Agente | Veredito | Observação |
|---|--------|----------|------------|
| 16 | Triagem novo caso | **GAP** | Intake + viabilidade + conflito de interesse (EAOAB art. 17) não existe hoje. Valor real. |
| 17 | Orientação inicial | GAP | Consulta ao cliente em linguagem simples — não coberto; sobrepõe um pouco com `legal-design-rdaa` (plain language) mas esse é para documentos, não para conversa com cliente. |
| 18 | Onboarding cliente | PARCIAL | `backoffice-juridico` cobre parte operacional; falta o pacote formal (contrato honorários + procuração + termo LGPD + cadastro). |
| 19 | Follow-up cliente | PARCIAL | `backoffice-juridico` já "manda e-mail pro cliente"; falta a régua sistemática (mensal/trimestral/VIP) e protocolo de retenção. |

## 5 · Contratos & Compliance

| # | Agente | Veredito | Observação |
|---|--------|----------|------------|
| 20 | Revisão de cláusula | FORA DE ESCOPO? | `Resolutivo.AI` é plugin de litígio, não de contratos comerciais. Confirmar se o Resolutivo faz esse tipo de trabalho. |
| 21 | Comparação de contratos | FORA DE ESCOPO? | Idem. |
| 22 | LGPD/Direito Digital | PARCIAL | `dano-moral-rct` cobre dano moral por vazamento como consequência, não o parecer/compliance LGPD em si. Só vale se o escritório atender esse tipo de demanda. |
| 23 | Due diligence | FORA DE ESCOPO? | M&A/societário — confirmar se é praticado. |

## 6 · Operação do Escritório

| # | Agente | Veredito | Observação |
|---|--------|----------|------------|
| 24 | Cobrança de honorários | **GAP** | Nada cobre a cobrança do próprio escritório aos clientes (regra é diferente de cobrança de terceiros). |
| 25 | Agenda de audiência | PARCIAL | `backoffice-juridico` menciona audiências no gatilho, mas não tem o checklist de preparação D-7/D-1 nem carta de preposição. |
| 26 | Resumo de processo (case briefing) | **GAP** | `consultar-processo` lê movimentação (metadados via DataJud); não sumariza o conteúdo integral de autos grandes (200+ páginas). Capacidade diferente e valiosa ao assumir caso de outro advogado. |
| 27 | Backup do escritório | FORA DE ESCOPO | É política de TI genérica, não conhecimento jurídico. Baixa prioridade para um plugin jurídico. |

## 7 · Peças por área do direito (28–57)

| # | Agente | Veredito | Observação |
|---|--------|----------|------------|
| 28 | Apelação cível | REDUNDANTE/PARCIAL | Dentro do escopo cível; `redigir-peca` já cobre recurso em geral — a tabela de prazos/efeitos específica poderia enriquecer, não duplicar. |
| 29 | Agravo de instrumento | REDUNDANTE/PARCIAL | Idem. |
| 30 | Ação de cobrança | REDUNDANTE/PARCIAL | Idem, dentro do escopo cível. |
| 31–33 | Trabalhista (reclamação, defesa, verbas rescisórias) | FORA DE ESCOPO? | Confirmar se RDAA atua em trabalhista. |
| 34–38 | Família e Sucessões (divórcio, alimentos, inventário, guarda) | FORA DE ESCOPO? | Idem. |
| 39–40 | Criminal (resposta a acusação, habeas corpus) | FORA DE ESCOPO? | Idem. |
| 41–42 | Tributário (MS, embargos execução fiscal) | FORA DE ESCOPO? | Idem. |
| 43–45 | Empresarial (recuperação judicial, contrato social, acordo de acionistas) | FORA DE ESCOPO? (provável dentro) | `contencioso-rdaa` já se descreve como "cível **e empresarial** estratégico" — então pode estar dentro do escopo real. Confirmar. |
| 46 | CDC prática abusiva | PARCIAL | RDAA é "cível e consumerista" (README do plugin) — overlap direto com `contencioso-rdaa`/`dano-moral-rct`. Enriquecimento, não peça nova. |
| 47–48 | Imobiliário (despejo, renovatória) | FORA DE ESCOPO? | Confirmar. |
| 49–50 | Usucapião (extra/judicial) | FORA DE ESCOPO? | Confirmar. |
| 51–53 | Previdenciário (aposentadoria, BPC, auxílio-doença) | FORA DE ESCOPO? | Confirmar. |
| 54 | Cumprimento de sentença | **GAP** | Fase final de qualquer ação cível que o escritório ganha — hoje `contencioso-rdaa` cobre a ação, não a execução. Gap real e certamente usado. |
| 55 | Impugnação ao cumprimento | **GAP** | Idem — defesa na execução. |
| 56 | Cálculo judicial de atualização | **GAP** | Nada hoje calcula atualização monetária/juros (Selic/IPCA/TR). Overlap parcial com a skill `perfil-csv` (que já converte tabelas de parcelas/cálculo para o formato interno) — os dois podem se conectar: este agente calcularia, `perfil-csv` formataria a saída. |
| 57 | Minuta de contrato de serviços | PARCIAL | Relacionado ao próprio contrato de honorários do escritório (usado dentro de `18-onboarding-cliente`) — não é peça de litígio, é documento interno do RDAA. |

## Conclusão — prioridades se fossem construir 5 coisas

1. **Lembrete de prazo com régua D-7/D-3/D-1/D-0 + .ics** (02) — maior risco operacional coberto.
2. **Cumprimento de sentença + Impugnação ao cumprimento** (54+55) — fase que falta no fluxo atual de litígio.
3. **Cálculo judicial de atualização monetária** (56) — plugável no `perfil-csv` já existente.
4. **Triagem de novo caso** (16) — intake/viabilidade/conflito de interesse, zero cobertura hoje.
5. **Resumo de processo / case briefing de autos grandes** (26) — diferente de `consultar-processo`, resolve "peguei processo no meio".

## Pendência: confirmar escopo de área com Ricardo

Categoria 5 inteira (contratos comerciais/M&A) e a maior parte da categoria 7
(31–53, exceto 43–46) dependem de uma resposta simples: **o RDAA atua em
trabalhista, família, criminal, tributário, previdenciário e imobiliário, ou
o foco real é cível/consumerista/empresarial?** Isso muda se vale portar ~25
dos 57 agentes ou descartá-los de saída.

## Ressalva de licença

O pacote é "uso permitido para clientes ASV Digital/Bravy — não redistribuir
sem autorização". Qualquer coisa aproveitada daqui deve ser **reescrita do
zero** (persona, estrutura, conteúdo jurídico) e ligada às MCPs reais do
projeto (CNJ, JusIA, NotebookLM) — não copiar o `.md` literal para dentro do
plugin.
