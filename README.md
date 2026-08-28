# Resolutivo.AI — Plugin Jurídico RDAA

Plugin de Claude Code para o contencioso cível e consumerista do
**Romano Donadel Advogados Associados (RDAA)**.

Reúne, como skills, todo o fluxo de trabalho do setor Resolutivo: redação e
revisão de peças, cálculo judicial determinístico, análise de risco e
provisão, pesquisa jurisprudencial autorizada, Legal Design e backoffice
operacional. As regras de negócio, personalidade do assistente e o que cada
skill pode ou não fazer automaticamente estão em [`CLAUDE.md`](CLAUDE.md) —
leitura obrigatória antes de mexer em qualquer skill.

## Instalação

```
/plugin marketplace add ricardocsojr-dotcom/resolutivo-ai
/plugin install resolutivo-ai
```

## Estrutura

```
resolutivo-ai/
├── CLAUDE.md              # Regras do escritório, o que é automático e o que não é
├── skills/                # Cada pasta é uma skill (SKILL.md + scripts/ + references/)
├── referencias/indices/   # Tabelas de índice usadas pela skill calculo-judicial
├── roteamento-ia.md       # Como o trabalho se divide entre Claude Code, Codex e Gemini
├── requirements.txt       # Dependências Python dos scripts das skills (docx, xlsx, pdf, etc.)
└── tests/                 # Suíte pytest dos scripts determinísticos das skills
```

Não há servidor MCP remoto hospedado por este repositório — o que existe é
só o plugin, instalado localmente em cada CLI (Claude Code e Codex instalam
o pacote inteiro; Gemini usa a camada de handoff descrita em
`roteamento-ia.md`).

## Rodando os testes

```bash
pip install -r requirements.txt
pytest
```

## Licença

Projeto proprietário, uso exclusivo do **Romano Donadel Advogados
Associados (RDAA)**. Responsável técnico: Ricardo Cesar Souza de Oliveira
Junior (`ricardocsojr@gmail.com`).
