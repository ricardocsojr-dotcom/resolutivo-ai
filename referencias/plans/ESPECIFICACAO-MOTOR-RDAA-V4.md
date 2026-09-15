# Especificação do Motor RDAA V4

## 1. Objetivo e arquitetura

O Resolutivo.AI será uma linha de produção local operada oficialmente pelo Codex, governada por um único motor LangGraph e alimentada por Combos do OmniRoute via HTTP.

```text
Ricardo -> Codex oficial -> LangGraph -> pacote mínimo da etapa
        -> API HTTP OmniRoute -> Combo -> saída estruturada
        -> LangGraph -> QA/publicação -> Cérebro-Ricar -> OpenViking
```

- Codex é a interface e o único agente operacional.
- LangGraph é o único motor e decide todas as transições.
- OmniRoute recebe o nome do Combo como `model` e resolve modelo, conta e fallback.
- `planner`, `writer`, `critic`, `validator`, `research` e `reader` são papéis lógicos/nós, não CLIs.
- Não chamar `codex exec`, `claude`, `agy` ou Hermes como workers.
- Scripts determinísticos fazem QA, cálculo, DOCX, hashes, publicação e sincronização.
- Cérebro-Ricar é a memória institucional canônica; OpenViking é índice derivado.

## 2. Princípios não negociáveis

- Uma única implementação do motor.
- Nenhuma resposta de modelo ou cliente escolhe a próxima fase.
- Cada etapa recebe somente o contexto necessário, nunca o histórico bruto por padrão.
- Skills contêm inteligência, método e limites; Python controla execução e estado.
- Cada matéria usa exclusivamente `.rdaa-run/<matter_id>/`.
- Falha de persistência, contrato, HTTP, hash, QA ou gate bloqueia o fluxo.
- O RDAA não cria fallback próprio; fallback pertence ao Combo.
- Ricardo é a única autoridade para gates, retomada e aborto.
- Jusbrasil é a única fonte jurisprudencial externa autorizada, salvo decisão expressa.

## 3. Estrutura final

```text
orquestracao/
  engine.py       # grafo, condições e transições
  cli.py          # interface local usada pelo Codex
  contracts.py    # estado, pacotes, recibos e erros
  omniroute.py    # único cliente HTTP
  prompts.py      # pacote mínimo e prompt por papel
  roteamento.json # fases, papéis e Combos
services/
  memoria.py
  pesquisa.py
  publicacao.py
  qa.py
tests/
  unit/
  contract/
  e2e/
  acceptance/
```

Não manter dois `langgraph_engine.py`, dispatcher paralelo, proxy que avance fases nem adaptadores de Claude/Codex/Agy.

## 4. Papéis e Combos

| Papel lógico | Função | Combo inicial sugerido |
|---|---|---|
| `planner` | organizar contexto e esqueleto | `RJ-Planejamento` |
| `writer_heavy` | redação premium | `RJ-Escrita-Pesada` |
| `writer_light` | redação simples/desenvolvida | `RJ-Escrita-Leve` |
| `critic` | vulnerabilidades, sem correção | Combo crítico ou `RJ-Leitura` |
| `validator` | validação e correção objetiva | `RJ-Revisao-Final` |
| `research` | pesquisa autorizada | `RJ-Pesquisa` |
| `reader` | leitura e extração | `RJ-Leitura` |

Os nomes dos Combos ficam somente em `roteamento.json`. O motor não codifica nomes de GPT, Claude, Gemini, contas ou conexões.

Contrato de rota por papel:

```json
{
  "role": "writer",
  "transport": "omniroute_http",
  "target_type": "combo",
  "model": "RJ-Escrita-Pesada",
  "endpoint": "/v1/responses",
  "timeout_seconds": 600,
  "output_contract": "draft_v1"
}
```

## 5. Cliente HTTP OmniRoute

Endpoint padrão configurável:

```text
http://localhost:20128/v1/responses
```

Requisição conceitual:

```json
{
  "model": "RJ-Escrita-Pesada",
  "input": [
    {"role": "system", "content": "regras e contrato da etapa"},
    {"role": "user", "content": "pacote mínimo da matéria"}
  ]
}
```

Requisitos:

- API key somente por variável de ambiente;
- nunca persistir segredo;
- timeout e limites de entrada/saída;
- resposta estruturada e validada;
- registrar status HTTP e request ID;
- retentar apenas falha transitória autorizada, sem mudar Combo;
- quota, indisponibilidade ou resposta inválida contam como falha da etapa;
- duas falhas consecutivas abrem o disjuntor.

## 6. Pacote mínimo

- Planner: fatos, fontes autorizadas, pendências, teses candidatas e regras de planejamento.
- Writer: esqueleto aprovado e hash, fatos/fontes selecionados, decisões e núcleo RDAA.
- Critic: rascunho, fatos/fontes necessários, teses, pedidos e contrato adversarial.
- Validator: rascunho, esqueleto, fontes, crítica aplicável e checklist RDAA.

Cada pacote deve ser materializado em `packages/` e hasheado antes do envio.

## 7. Rotas

### Nível C

```text
intake_ready -> drafting -> draft_ready -> candidate_ready -> qa_passed
-> release_ready -> published -> vault_registered
```

Redação por Combo leve; sem Cérebro-Ricar, esqueleto ou crítica; QA, publicação e Cérebro obrigatórios.

### Nível B

```text
intake_ready -> vault_context_ready -> sources_ready -> skeleton_ready
-> awaiting_skeleton_approval -> skeleton_approved -> drafting -> draft_ready
-> validating -> candidate_ready -> qa_passed -> release_ready
-> published -> vault_registered
```

Combos de planejamento/redação B e revisão final; Cérebro-Ricar read-only e gate do esqueleto.

### Nível A

```text
intake_ready -> vault_context_ready -> sources_ready -> council_ready
-> skeleton_ready -> awaiting_skeleton_approval -> skeleton_approved
-> drafting -> draft_ready -> criticizing -> critique_ready -> validating
-> candidate_ready -> qa_passed -> release_ready
-> awaiting_release_approval -> published -> vault_registered
```

Combos de planejamento, escrita pesada, crítica e revisão final; gates de esqueleto e publicação; mudança de tese, pedido ou estratégia abre decisão para Ricardo.

## 8. Estado canônico

```text
.rdaa-run/<matter_id>/
  langgraph.sqlite
  run_manifest.json
  matter_state.json
  provenance.jsonl
  artifacts/
  packages/
  approvals/
  receipts/
  logs/
  candidate/
```

- SQLite: checkpoint autoritativo do grafo.
- Manifesto: projeção auditável da execução.
- Matter state: fatos, teses, decisões e pendências confirmadas.
- Provenance: ledger append-only.
- Artefatos e pacotes: imutáveis e hasheados.
- Approvals: gates vinculados a hashes.
- Receipts: HTTP, publicação, Cérebro e OpenViking.

Falha de persistência bloqueia e preserva o último estado confirmado. `matter_id` deve coincidir no diretório, SQLite, manifesto e estado. Rejeitar path absoluto indevido, `..`, separador, symlink externo e ID divergente. Nunca derivar a matéria do nome do DOCX.

## 9. Recibo OmniRoute

```json
{
  "role": "writer",
  "transport": "omniroute_http",
  "requested_combo": "RJ-Escrita-Pesada",
  "endpoint": "/v1/responses",
  "request_id": "...",
  "resolved_provider": null,
  "resolved_model": null,
  "fallback_used": null,
  "prompt_path": "packages/writer-001.json",
  "prompt_sha256": "...",
  "output_path": "artifacts/draft-001.md",
  "output_sha256": "...",
  "started_at": "...",
  "finished_at": "...",
  "duration_ms": 0,
  "http_status": 200,
  "outcome": "ok"
}
```

O motor calcula hashes. Provider, modelo resolvido e fallback só são registrados quando a resposta ou log correlacionado fornecer prova; caso contrário permanecem `null`.

## 10. Gates, revisão e disjuntor

- Aprovação registra gate, autoridade, artefato, SHA-256 e data.
- Alteração do artefato invalida a aprovação.
- `needs_revision` retorna ao writer uma única vez automaticamente.
- Nova revisão pausa para Ricardo.
- `escalate` abre gate e não muda mérito.
- Duas falhas consecutivas pausam a matéria.
- `resume` e `abort` exigem `authority: ricardo` e motivo.
- O motor nunca muda o Combo como fallback próprio.
- Crítica é alerta; tese, pedido e estratégia dependem de Ricardo.

## 11. Interface do Codex

CLI local fina, sem chamar outras IAs por CLI:

```text
rdaa start
rdaa status
rdaa next
rdaa approve
rdaa reject
rdaa resume
rdaa abort
rdaa audit
```

As inferências acontecem internamente nos nós via HTTP. Não expor avanço arbitrário. Importação de artefato manual, se necessária, exige comando específico que valide fase, contrato, caminho e hash.

O Codex apresenta gates e transmite a decisão de Ricardo. Não escreve diretamente em SQLite ou JSON.

## 12. QA e publicação

1. Gerar DOCX candidato em staging.
2. Validar contexto, identidade e hash.
3. Executar QA estrutural, estilístico, semântico e visual aplicável.
4. Rejeitar estrutura inválida, referência impossível e conflito de identidade.
5. Preservar arquivo anterior em falha.
6. Criar backup recuperável.
7. Publicar por substituição atômica.
8. Gerar recibo.
9. Atualizar estado confirmado somente após publicação real.

Nível A exige aprovação de publicação vinculada ao hash do candidato.

## 13. Cérebro e OpenViking

- Cérebro-Ricar é memória institucional canônica.
- OpenViking é índice derivado.
- `.rdaa-run` é estado transacional.
- Skills são inteligência, não memória.
- Em divergência, prevalece o Cérebro-Ricar.

Peças B/A consultam o Cérebro-Ricar no Cérebro em modo read-only; o material entra como `informada`, não como tese aprovada ou fonte externamente verificada.

Após publicar: registrar no Cérebro, obter recibo com hash, registrar no manifesto, sincronizar OpenViking e guardar recibo. Falha no Cérebro impede `vault_registered`. Falha no OpenViking cria pendência reexecutável sem desfazer o Cérebro.

## 14. Skills

Cada `SKILL.md` deve conter somente gatilhos, objetivo, método, fontes, critérios, limites, escalonamentos e contrato do conteúdo. Remover comandos, controle de fase, staging, persistência, chamadas a CLIs, referências ao dispatcher e marcadores substituídos.

## 15. Migração

1. Definir contratos e mapear papéis para Combos.
2. Consolidar `orquestracao/engine.py` com nós, arestas, condições e interrupts reais.
3. Remover `phase_idx` e transições manuais paralelas.
4. Implementar cliente HTTP, validação e recibos.
5. Implementar persistência, hashes, gates, revisão e disjuntor.
6. Integrar QA, DOCX, publicação, Cérebro e OpenViking.
7. Migrar consumidores.
8. Remover dispatcher, proxy, segundo motor e integrações de IA por CLI.
9. Limpar skills e documentação.
10. Remover testes antigos somente após cobertura equivalente.

## 16. Testes obrigatórios

- Matter ID, state dir, papel e Combo por fase.
- Pacote mínimo e hashes.
- Gate válido, inválido e expirado.
- Revisão, escalonamento, disjuntor, resume e abort.
- Persistência atômica.
- `/v1/responses` com nome exato do Combo.
- Sucesso, timeout, quota, HTTP/JSON inválido e contrato incompatível.
- Confirmação de que a API key nunca é persistida.
- E2E C/B/A, incluindo os dois gates de A.
- Reinício em gates e duas matérias simultâneas.
- Publicação rejeitada, Cérebro indisponível e OpenViking indisponível.
- Confirmação de que nenhuma CLI de IA foi chamada.

Testes usam servidor HTTP falso e diretórios temporários. Aceitação local usa matéria sintética e Combos reais, sem Cérebro/OneDrive/produção. Executar `py -3.14 -m pytest -q` integralmente.

## 17. Critérios de conclusão

- Codex é a única interface oficial.
- Nenhuma CLI de IA é chamada.
- Existe um único LangGraph e as transições pertencem ao grafo.
- Cada papel usa o Combo da rota e recebe pacote mínimo.
- Respostas, artefatos e hashes são validados.
- Gates estão vinculados a hashes.
- Disjuntor e retomada humana estão testados.
- Publicação protegida está integrada.
- Cérebro é canônico e OpenViking derivado.
- Skills não contêm mecânica.
- Documentação não aponta para legado.
- Suíte e ensaios sintéticos C/B/A passam.
- Revisão independente não encontra bloqueador funcional.

## 18. Ordem obrigatória

```text
contratos -> roteamento por Combos -> LangGraph único -> HTTP OmniRoute
-> persistência/gates/disjuntor -> QA/publicação -> Cérebro/OpenViking
-> consumidores -> remoção do legado -> skills/documentação
-> testes integrais -> revisão independente
```

Não remover proteção ou teste antes de sua substituição estar comprovada.
