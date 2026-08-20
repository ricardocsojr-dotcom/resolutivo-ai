# Matriz de validação com peças anonimizadas

A validação usa somente contextos sintéticos/anonimizados, sem nomes reais,
números de processos reais, documentos reais ou consulta externa. Os textos são
entradas explícitas para testar engenharia do gerador, não conteúdo jurídico
para uso em caso concreto.

| Caso | Tipo representado | `nivel_peca` | `nivel_risco` | Cobertura técnica |
|---|---|---|---|---|
| `C-manifestacao` | manifestação simples | C | baixo | redação direta, parágrafos curtos, pedidos e assinatura |
| `B-contestacao` | contestação intermediária | B | medio | redação por blocos, títulos hierárquicos, alíneas, citação longa, nota de rodapé, documentos, tabela |
| `A-apelacao-visual` | recurso composto | A | alto | redação por blocos, múltiplas sequências, alíneas aninhadas, citação, tabela, figura local, documentos, semantic blocks e assinaturas |

## Critérios objetivos

Cada candidato deve: ser gerado sem erro; abrir com `python-docx`; passar pelo gate
estrutural e estilométrico; preservar o arquivo anterior quando um bloqueio for
introduzido; manter IDs semânticos presentes quando declarados; separar o estado
por matéria; registrar a rota declarada no manifesto; e produzir métricas locais
de contexto.

A validação não conclui se uma tese é correta, se um pedido é cabível, se uma
prova é autêntica, se um precedente é aplicável ou se o risco declarado é
materialmente adequado. Esses pontos continuam sob julgamento de Ricardo.

O `nivel_peca` A/B/C é declarado para definir o modo de produção da peça e
não é confundido com `nivel_risco`. Nenhum dos dois é inferido do vault, da
extensão do texto ou de palavras livres do contexto. A redação por blocos só é
válida nos casos A e B; o caso C usa redação direta.
