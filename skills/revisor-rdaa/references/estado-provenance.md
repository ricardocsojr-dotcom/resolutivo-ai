# Contrato conservador de estado e provenance RDAA

## Princípio

O estado automático registra somente informações já presentes no contexto estruturado da peça ou em resultados explícitos do fluxo. Ele não interpreta a redação para inventar fatos, não confirma a validade de uma fonte e não transforma uma citação sem origem em fonte confirmada.

Toda informação derivada automaticamente recebe `origem: contexto_json` e um status que distingue informação fornecida de fonte efetivamente verificada.

## Separação por caso

Cada execução deve possuir um `matter_id`. A prioridade para derivá-lo é:

1. `matter_id` fornecido explicitamente no contexto;
2. número do processo normalizado;
3. nome do arquivo de saída, apenas como fallback operacional.

O estado de casos diferentes não pode compartilhar o mesmo `matter_state.json`. O diretório padrão passa a ser `.rdaa-run/<matter_id>/` quando o publicador opera em um diretório comum.

## `matter_state.json`

```json
{
  "schema_version": "3",
  "matter_id": "0000000-00.0000.8.26.0001",
  "created_at": "...",
  "updated_at": "...",
  "facts": [
    {
      "id": "F-001",
      "campo": "numero_processo",
      "valor": "0000000-00.0000.8.26.0001",
      "origem": "contexto_json",
      "status": "informado"
    }
  ],
  "theses": [],
  "citations": [],
  "decisions": [],
  "pending": [],
  "hypotheses": [],
  "requests": [],
  "risks": [],
  "rules": [],
  "semantic_reviews": [],
  "metrics": {},
  "nivel_peca": "A|B|C|ausente em contexto legado",
  "modo_redacao": "direta|blocos|molde_controlado",
  "redacao_por_blocos": true,
  "modelo_estrutura": {}
}
```

Os campos estruturados do contexto, como processo, partes, endereçamento e data, podem entrar em `facts`. Teses, hipóteses, pedidos, riscos, decisões e regras só entram quando existirem explicitamente no JSON; o sistema não deve inferi-las dos parágrafos da peça.

`nivel_peca` define o modo de produção e é independente de `declared_risk_level`, que representa somente a rota de risco. O tipo C usa redação direta. Os tipos A e B podem usar redação por blocos. Nenhum desses campos dispara consulta automática ao vault.

Quando `modelo_estrutura` existe, ele deve conter pelo menos `modelo_id` e `versao`. A seleção é operacional e não prova pertinência jurídica.

`semantic_reviews` guarda o resultado do comparador objetivo de IDs,
referências, identidade processual e duplicidades. `metrics.context_packs` guarda
somente contagens locais de tamanho e uso dos pacotes por tarefa; não registra o
conteúdo integral do contexto.

## `provenance.jsonl`

Cada linha é um registro independente:

```json
{
  "schema_version": "3",
  "id": "P-001",
  "tipo": "nota_rodape|citacao|documento|figura",
  "fonte": "texto ou caminho informado",
  "localizacao": "contexto.bloco[3].nota_rodape",
  "trecho": "...",
  "status": "informada|pendente|sem_fonte",
  "origem": "contexto_json",
  "recorded_at": "..."
}
```

`informada` significa que a origem foi fornecida no contexto. Não significa que a fonte foi verificada externamente. `pendente` significa que o fluxo precisa de confirmação ou busca. `sem_fonte` significa que existe um trecho com aparência de citação, mas o contexto não trouxe origem.

## Estado confirmado e estado candidato

Quando o publicador recebe contexto, ele avalia o candidato em `.rdaa-run/<matter_id>/candidate/`. Essa pasta pode conter fatos, provenance, rota e revisão semântica do candidato, mas não representa publicação confirmada.

`matter_state.json` e `provenance.jsonl` na raiz da matéria representam o último estado confirmado. Se o candidato for rejeitado, esses arquivos não são substituídos. O `run_manifest.json` da raiz registra a tentativa, o hash do candidato, `candidate_status: REJECTED` e `confirmed_state_status: PRESERVED`.

Somente depois de QA, revisão semântica, esqueleto, Visual Law e publicação atômica o estado candidato é promovido para a raiz. O manifesto então registra `candidate_status: APPROVED`, `confirmed_state_status: CONFIRMED`, o hash confirmado, o backup e os arquivos promovidos.

A separação evita que uma peça rejeitada altere fatos, teses, decisões, provenance ou nível confirmado da matéria. A contagem existente de `publish_attempts` e `blocked_attempts` continua registrando tentativas sem modificar o rollback.

## Revisão semântica objetiva

Quando o estado da matéria existe, `semantica_rdaa.py review` compara IDs e
referências. Referência impossível ou conflito objetivo de identidade pode
bloquear o publicador. Alertas que dependem de julgamento jurídico permanecem
pendências e exigem conferência humana.

## O que não será derivado automaticamente

O sistema não deverá inferir autoria, validade jurídica, tese, risco processual, autenticidade documental, atualidade legislativa ou pertinência jurisprudencial a partir de texto livre. Esses elementos continuam sob responsabilidade das skills jurídicas e da revisão correspondente.
