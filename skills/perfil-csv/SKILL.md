---
name: perfil-csv
description: Converte tabelas de parcelas, cálculos, custas, principal, deduções ou honorários para o formato "perfil" (data,valor,tipo,histórico,mostraTipo,t,correção,juros,dtJuros), entregue direto no chat em bloco de texto pronto para Ctrl+C/Ctrl+V — nunca como arquivo para download. Use esta skill sempre que Ricardo enviar/colar uma tabela desses valores e pedir para "converter para o perfil", "gera o perfil", "monta o perfil", "formato perfil" ou qualquer variação equivalente — mesmo que ele não repita as regras de conversão, mesmo que a tabela venha como texto colado, imagem ou planilha anexada. Esta skill NUNCA deve produzir cabeçalho, texto explicativo, arquivo .csv/.txt ou qualquer coisa além do bloco de texto copiável, salvo erro/inconsistência nos dados de entrada.
---

# Conversor para "perfil" (CSV)

Converte qualquer tabela de valores financeiros (parcelas, custas, principal, deduções,
honorários etc.) para o formato CSV fixo exigido pelo sistema "perfil". A saída é sempre
apenas o CSV — sem cabeçalho, sem explicação — porque o usuário copia e cola isso
diretamente em outro sistema.

## Formato de saída (fixo, sempre nesta ordem de colunas)

```
data,valor,tipo,histórico,mostraTipo,t,correção,juros,dtJuros
```

`mostraTipo` e `t` ficam sempre vazios (campos opcionais que o sistema aceita mas raramente
vêm preenchidos). Isso significa que depois do histórico aparecem duas vírgulas seguidas
antes de `correção`.

## Por que usar o script em vez de converter linha por linha "na mão"

As regras de conversão (data BR→ISO, valor BR→decimal com ponto, normalização de S/N) são
mecânicas, mas fáceis de errar silenciosamente em tabelas longas — um valor com milhar mal
convertido ("1.804,00" virando "1.804" em vez de "1804.00") passa despercebido numa lista de
30 linhas. Por isso, em vez de escrever cada linha do CSV manualmente, extraia os dados brutos
da tabela e deixe `scripts/convert_perfil.py` fazer a conversão determinística. O script grita
(stderr + saída não-zero) se algo não bater, em vez de "adivinhar" um formato.

## Fluxo de trabalho

1. **Leia a tabela** que o usuário enviou (texto colado, imagem ou arquivo). Extraia, para
   cada linha, os campos brutos exatamente como aparecem — sem tentar converter nada ainda:
   - `data` — como veio (ex: `14/06/2014`)
   - `valor` — como veio (ex: `1.804,00`, pode ter "R$" na frente)
   - `tipo` — copiado literal (ex: `Principal`, `Custas`, `Deduções`, `Honorários`)
   - `historico` — copiado literal, preservando acentos, maiúsculas e hífens
     (ex: `DEPÓSITO INICIAL - TUTELA`)
   - `correcao` — como veio (`S`/`N`/`s`/`n`)
   - `juros` — como veio (`S`/`N`/`s`/`n`)
   - `dtJuros` — como veio, ou string vazia `""` se a tabela não trouxer essa data

2. **Monte um JSON** (lista de objetos, uma por linha da tabela) com essas chaves exatas:
   `data`, `valor`, `tipo`, `historico`, `correcao`, `juros`, `dtJuros`.

3. **Rode o script**, passando o JSON pelo stdin:
   ```bash
   python3 scripts/convert_perfil.py <<'EOF'
   [
     {"data": "14/06/2014", "valor": "1.804,00", "tipo": "Principal", "historico": "DEPÓSITO INICIAL - TUTELA", "correcao": "S", "juros": "N", "dtJuros": ""}
   ]
   EOF
   ```

4. **Entregue a saída do script direto na mensagem do chat**, dentro de um bloco de
   código (```texto simples, sem precisar rotular como csv```), sem cabeçalho e sem
   nenhum texto antes ou depois — a menos que o script tenha reportado erro (ver abaixo).
   Nunca crie um arquivo `.csv`/`.txt` para download nem use ferramentas de arquivo para
   isso: o usuário quer só selecionar o bloco e dar Ctrl+C/Ctrl+V, sem precisar baixar nada.

## Se o script reportar erro

O script para e lista, linha por linha, o que não bateu (data em formato não reconhecido,
valor não numérico, campo S/N inválido, tipo ou valor vazio). Nesse caso — e só nesse caso —
explique ao usuário qual linha da tabela original tem o problema e o que parece estar errado,
para ele corrigir a fonte. Não tente adivinhar o valor correto.

## Regras que o script já garante (não precisa reconferir na mão)

- Data `DD/MM/YYYY` → `YYYY-MM-DD` (se já vier em ISO, mantém).
- Valor `1.804,00` → `1804.00` (remove separador de milhar, troca vírgula por ponto,
  sempre duas casas decimais). Se já vier em formato `1804.00`, mantém.
- `correção` e `juros`: qualquer caixa de `s`/`n` vira `S`/`N` maiúsculo.
- `dtJuros` vazio permanece vazio, mas a vírgula final da linha é preservada.
- `histórico` com vírgula ou aspas internas é automaticamente colocado entre aspas pelo
  CSV writer, para não quebrar as colunas — sem alterar o conteúdo.

## O que a skill nunca faz

- Nunca cria arquivo `.csv`/`.txt` para download — a entrega é sempre um bloco de código
  dentro da própria mensagem do chat, para copiar e colar direto.
- Nunca inclui a linha de cabeçalho, a menos que o usuário peça explicitamente.
- Nunca explica o que foi feito quando a conversão deu certo — só entrega o CSV.
- Nunca reordena, resume ou remove linhas da tabela original.
- Nunca corrige valores/tipos "de acordo com o palpite" — em caso de dúvida, é erro (ver acima).
