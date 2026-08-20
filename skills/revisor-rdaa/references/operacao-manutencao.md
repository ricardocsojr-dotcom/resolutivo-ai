# Operação e manutenção do estado local RDAA

## Princípio de segurança

A manutenção é local, reversível e conservadora. Nenhum estado de matéria ou
backup é apagado automaticamente pelo fluxo de redação ou publicação.

> Diagnóstico pode ser automático; destruição de estado exige comando explícito.

## Diretórios

| Diretório | Conteúdo | Regra |
|---|---|---|
| `.rdaa-run/<matter_id>/` | estado, provenance, manifesto e métricas da matéria | nunca misturar matérias; limpeza é explícita |
| `.rdaa-backups/` | cópias anteriores dos DOCX publicados | nunca apagar automaticamente; restauração exige arquivo indicado |

Quando o publicador recebe `--state-dir` explícito, ele usa exatamente essa pasta.
Quando não recebe, cria o diretório padrão da matéria. Isso evita ambiguidades
em restauração e testes.

## Diagnóstico

O diagnóstico deve informar existência, tamanho, datas, status do manifesto,
número de tentativas, bloqueios, rodadas, registros de provenance e métricas.
Ele não deve imprimir o texto integral da peça ou de fontes quando um resumo for
suficiente.

## Limpeza

A limpeza segura deve ser somente uma simulação por padrão. A ação efetiva exige
`--apply` e pode operar apenas sobre uma matéria ou sobre backups selecionados.
O comando deve:

1. recusar diretórios que não tenham a estrutura esperada;
2. preservar a matéria mais recente quando houver retenção por idade;
3. mover itens para uma quarentena local, em vez de excluir diretamente;
4. gerar um manifesto da limpeza com lista de itens movidos;
5. nunca tocar em `.rdaa-backups` sem seleção explícita.

A quarentena pode ser restaurada antes de uma exclusão manual externa. O plugin
não deve esvaziá-la automaticamente.

## Restauração

A restauração exige indicar explicitamente o backup e o destino. Antes da troca,
o destino atual deve ser copiado para um novo backup, quando existir. A cópia
deve ser atômica e o resultado deve ser validado como arquivo existente.

O teste de restauração usa arquivos temporários, calcula hashes antes/depois e
não altera a matéria real nem o backup original.

## Limites

O plugin não decide se um estado é juridicamente relevante, se um backup é a
versão correta ou se uma matéria pode ser encerrada. Essas decisões continuam
humanas. A retenção por idade é apenas um filtro operacional declarado.
