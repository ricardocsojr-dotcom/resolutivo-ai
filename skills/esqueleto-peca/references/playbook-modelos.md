# Playbook de modelos de estrutura RDAA

## Finalidade

Este playbook organiza modelos de estrutura aprovados. Ele não é um catálogo de teses e não autoriza a aplicação automática de fatos, fontes, pedidos, prazos, valores ou conclusões jurídicas.

Nenhum modelo substitui o contexto da matéria, a declaração do nível ou a aprovação do esqueleto. A seleção do modelo é uma decisão operacional que deve ser registrada.

## Níveis de peça

| Tipo | Uso do modelo |
|---|---|
| A | Peça premium. O modelo pode orientar ou acelerar a estrutura, mas a peça pode usar todo o conjunto de recursos aprovado para o caso |
| B | Peça baseada no processo existente. O modelo pode organizar melhor, explicar, desenvolver, ilustrar ou aplicar Legal Design quando útil |
| C | Peça muito simples. Em regra não usa modelo complexo nem redação por blocos |

A redação por blocos é exclusiva dos tipos A e B. O gerador ainda pode usar objetos técnicos internos para montar qualquer DOCX.

## Modos de modelo

| Modo | Regra |
|---|---|
| `referencia` | O modelo serve como inspiração de ordem e apresentação. A redação é nova |
| `estrutura_orientadora` | O modelo define blocos esperados, campos e dependências. Alterações ficam visíveis no esqueleto |
| `molde_controlado` | O modelo é editado por substituições, acréscimos e remoções limitadas. Requer diff e revisão antes da publicação |

## Contrato mínimo

Cada modelo local deve declarar identidade, versão, tipo de peça, níveis recomendados, modo, blocos, variáveis, dependências, recursos visuais e provenance.

```json
{
  "modelo_id": "manifestacao-complexa-v1",
  "nome": "Manifestação complexa",
  "versao": 1,
  "tipo_peca": "manifestacao",
  "niveis_recomendados": ["B"],
  "modo": "estrutura_orientadora",
  "blocos": [
    {"id": "contexto", "funcao": "contextualizacao", "obrigatorio": true},
    {"id": "fundamentos", "funcao": "desenvolvimento", "obrigatorio": true},
    {"id": "pedidos", "funcao": "pedido", "obrigatorio": true}
  ],
  "variaveis": [],
  "dependencias": [],
  "recursos_visuais": [],
  "provenance": {"origem": "modelo_local", "versao": 1}
}
```

## Regras de seleção

O índice do catálogo pode ser consultado para encontrar modelos pelo tipo de peça e pelo nível declarado. A íntegra do modelo só deve entrar no contexto depois de `modelo_id` e `versao` serem selecionados.

O playbook não deve inferir que um modelo é juridicamente pertinente. Se o modelo exigir informação ausente, registre pendência ou `[PONTO A CONFERIR]`. Se o tipo C receber um modelo que imponha redação por blocos, o contrato deve bloquear o candidato.

Este playbook (seleção de modelo estrutural) não consulta vault nenhum. O Ementário do Resolutivo é consultado automaticamente pelo `redigir-peca` nos tipos B/A (fora deste playbook, passo 9 de `redigir-peca/SKILL.md`) — o que ele traz é material a avaliar, não um modelo aprovado. A aprovação de um modelo anterior não aprova o caso atual.

## Validação e diff

Modelos devem ser validados com fixtures anonimizadas, verificação estrutural, verificação semântica, Visual Law quando houver recurso visual e publicação protegida. O Modo Molde exige comparação entre modelo, candidato e versão publicada.

Toda adoção futura de biblioteca externa para diff ou composição deve ser opcional e precedida de teste com DOCX representativo do RDAA. A compatibilidade não pode ser concluída apenas pela leitura do README do projeto.
