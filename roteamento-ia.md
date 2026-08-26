# Roteamento de IA por nível de peça — RDAA

> Referência de como distribuir o trabalho entre as assinaturas de IA que o
> escritório já paga (Claude, Gemini, ChatGPT), configurada uma vez no
> OmniRoute (login OAuth por assinatura, não chave de API) para não exigir
> troca manual de janela/CLI a cada etapa. O nível da peça é sempre declarado
> por Ricardo — nenhum roteamento reclassifica ou troca a rota sozinho.

## Tabela de roteamento

| Nível | Leitura documental | Planejamento e primeira redação | Revisão e entrega |
|---|---|---|---|
| C | Gemini quando houver volume; Codex/GPT em caso simples | Gemini | Codex/GPT, com revisão rápida `revisor-rdaa` e formatação |
| B | Gemini | **Claude** | Codex/GPT audita fatos, formata e produz Visual Law determinístico |
| A | Gemini | **Claude** | Codex/GPT audita; Claude retorna somente se houver achado material |

## Regras

1. Claude é responsável por planejamento, primeira redação B/A e jurisprudência quando Ricardo a autorizar expressamente — é onde a engenharia do plugin (skills, gates, publicação protegida) foi calibrada e testada.
2. Gemini e Codex/GPT são responsáveis por leitura documental de volume, OCR/preparação local, conferência de fatos, formatação e Visual Law com dados verificáveis.
3. **Nenhuma rota é fallback de limite.** Se um provedor falhar ou atingir cota, o fluxo pausa e Ricardo decide — nunca troca de assinatura silenciosamente.
4. Para infográficos jurídicos: SVG/HTML/Word determinístico. Imagem generativa é só decorativa, nunca contém fato, data, valor, prova ou tese.

## Protocolo de exceção

Se qualquer modelo encontrar fato incerto, documento ausente, contradição relevante ou risco de alteração de pedido:

1. não completa a peça por inferência;
2. abre uma pendência na matéria e pausa o estágio;
3. solicita segunda análise independente de outro modelo, limitada ao ponto e às referências documentais;
4. apresenta as duas análises a Ricardo;
5. somente Ricardo decide. A decisão não retoma a matéria automaticamente.

Não há terceira análise automática, pesquisa externa automática nem correção silenciosa.

## Fontes externas

DataJud, DJEN, Jusbrasil, NotebookLM e web continuam bloqueados por padrão, independente de qual modelo estiver ativo — ver `CLAUDE.md`. Jurisprudência é tarefa do Claude e exige autorização registrada para a matéria.

## Configuração prática no OmniRoute

O OmniRoute não tem um motor de regras que leia "isso é nível C" e escolha
provedor sozinho — quem decide a etapa continua sendo você (ou o Claude,
seguindo instrução). O que ele oferece é **combo**: grupo nomeado de
modelo + estratégia. É nisso que a tabela acima se apoia.

### 1. Criar os combos (Dashboard → Combos → Create)

Cada combo com **um único modelo** e estratégia **Priority** — sem 2º/3º
alvo de fallback. Isso é o que garante a regra "nenhuma rota é fallback de
limite": o OmniRoute não tem um botão dedicado pra desligar fallback
automático, então o jeito de conseguir esse comportamento é não dar a ele
nenhum alvo de reserva. Se o provedor do combo bater cota, a requisição
falha e aparece como erro — não troca de assinatura escondido.

| Combo | Estratégia | Provedor (conectado via OAuth de assinatura) | Uso |
|---|---|---|---|
| `rdaa-leitura` | Priority (um só, sem fallback) | Gemini (Gemini CLI) | Leitura documental de volume — nível B/A |
| `rdaa-planejamento` | Priority (um só, sem fallback) | Claude (Claude Code) | Planejamento e 1ª redação — nível B/A |
| `rdaa-revisao` | Priority (um só, sem fallback) | Codex/GPT (Codex CLI) | Auditoria de fatos, formatação, Visual Law — B/A |
| `rdaa-tipo-c` | Round Robin (divide custo entre os dois) | Codex/GPT + Gemini | Fluxo inteiro do tipo C — peça simples e padronizada, sem esqueleto/pesquisa |

`rdaa-tipo-c` é a única exceção à regra "um modelo só, sem fallback": aqui
os dois provedores foram escolhidos deliberadamente para dividir o mesmo
trabalho (não é fallback de emergência, é balanceamento de custo entre
assinaturas que você já paga). Nada de DeepSeek ou outro provedor gratuito
entrou nessa composição.

### 2. Conectar os provedores (Dashboard → Providers)

Login OAuth de assinatura em cada um — não usar chave de API avulsa
(`GEMINI_API_KEY`/API key da OpenAI cobra separado da assinatura já paga):
- Connect Claude Code → OAuth
- Connect Codex → OAuth (porta 1455)
- Connect Gemini CLI → OAuth do Google

### 3. Apontar o Claude Code pro OmniRoute

- Base URL: `http://localhost:20128/v1`
- API Key: copiada de Dashboard → Endpoints

### 4. Trocar de combo dentro da mesma janela

Sem abrir outro app: `/model rdaa-leitura` antes de pedir leitura de
volume, `/model rdaa-planejamento` pra planejar/redigir B/A,
`/model rdaa-revisao` pra auditoria/formatação. O gatilho da troca continua
sendo você — o OmniRoute só evita precisar trocar de programa pra isso.

## Nota de origem

Esta tabela nasceu de uma arquitetura anterior que usava o Hermes como
dispatcher automático entre Claude Code, Codex e Antigravity — descartada
por experiência de uso ruim. A lógica de divisão de trabalho por nível foi
preservada; o mecanismo de execução mudou para OmniRoute (uma interface só,
roteamento configurado por baixo) em vez de um coordenador separado.
