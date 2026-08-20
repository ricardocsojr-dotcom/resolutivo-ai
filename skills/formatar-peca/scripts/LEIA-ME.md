
## Atualização 2026-07-19 (v3) — tabela de assinaturas

Confirmado com o Ricardo, contra peça real assinada: a assinatura é sempre
uma grade 2x2 sem bordas com os 4 advogados (Wanderley/Flávia na linha de
cima, Alessandra/Ricardo Cesar embaixo), não uma coluna única de 3.
Corrigido:

- `SIGNATARIOS` agora tem 4 entradas, incluindo Ricardo Cesar Souza de
  Oliveira Junior (OAB/MG 208.090).
- `_inserir_tabela_assinaturas()` reescrita: `doc.add_table(rows=2, cols=2)`
  em vez de 1 coluna por N linhas; cada célula com nome (negrito), OAB,
  e-mail (sublinhado, azul-link `#0563C1`) e observação opcional em itálico;
  alinhamento à esquerda (não mais centralizado); largura de coluna =
  metade da largura útil (4819 twips).
- `verificar_formatacao.py` (Item 7a) atualizado para exigir 2 colunas x 2
  linhas e os 4 nomes, em vez de 1 coluna e 3 nomes.

Validado por render (LibreOffice → PDF → PNG) comparado com a imagem da
peça real assinada enviada pelo Ricardo — bate.
