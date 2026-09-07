# Evidence Chain — Manifest

Todo artefato ou decisão gerada por esta skill vira uma entrada em `evidence/log.jsonl`
(append-only, **nunca versionado no Git** — contém dados de cliente).

## Schema

```json
{
  "ts": "2026-07-02T14:30:00Z",
  "event": "peca_protocolada | prazo_ciencia | decisao | calculo_emitido | ...",
  "case_id": "identificador interno do caso",
  "actor": "quem executou",
  "payload": { "resumo do artefato/decisão" },
  "prev_hash": "SHA-256 da entrada anterior",
  "hash": "SHA-256 desta entrada (com prev_hash incluído)"
}
```

## Regras

1. **Append-only** — nunca editar ou apagar entradas; correção = nova entrada `event: "retificacao"`.
2. **Hash-chained** — `hash = sha256(json_da_entrada_sem_hash + prev_hash)`; primeira entrada usa `prev_hash: "genesis"`.
3. **Verificação** — qualquer alteração retroativa quebra a cadeia e é detectável.
4. **LGPD** — o log contém dados pessoais de clientes: mesmo regime de sigilo do prontuário do caso.

> Por que isso importa no escritório: em discussão sobre responsabilidade profissional
> (prazo perdido, tese não recomendada), o log prova **o que foi feito, quando e por quem**.
