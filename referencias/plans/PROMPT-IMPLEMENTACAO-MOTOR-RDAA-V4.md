# Prompt de implementação do Motor RDAA V4

```text
Trabalhe exclusivamente em C:\Users\ricar\Desktop\resolutivo-ai-lab.

Implemente integralmente C:\Users\ricar\Desktop\resolutivo-ai-lab\referencias\plans\ESPECIFICACAO-MOTOR-RDAA-V4.md.

Antes de editar, leia AGENTS.md, CLAUDE.md, HERMES.md, a especificação inteira, orquestracao/roteamento.json, skills/redigir-peca/SKILL.md, os motores atuais e os testes relacionados. Não produza outro plano: implemente código e testes.

Arquitetura obrigatória:

- Codex é a interface oficial e o único agente operacional.
- LangGraph é o único motor.
- O motor chama Combos do OmniRoute diretamente por HTTP.
- Não chamar codex exec, claude, agy, Hermes ou qualquer CLI de IA.
- Planner, writer, critic, validator, research e reader são papéis/nós, não agentes externos.
- Cada papel mapeia para um Combo em roteamento.json.
- Envie o nome exato do Combo no campo model.
- O motor não escolhe o modelo interno nem implementa fallback próprio.

Corrija o estado atual:

- consolide as duas implementações em orquestracao/engine.py;
- faça testes e produção importarem o mesmo motor;
- substitua phase_idx/update_state manual por nós, arestas, condições e interrupts reais;
- remova avanço arbitrário sem artefato, contrato, hash e resultado válidos;
- vincule gates a artefato e hash;
- corrija a seleção papel -> Combo;
- migre executar_motor.py, registrar_cerebro.py, hooks, QA e publicação;
- remova proxy e legado apenas após paridade;
- restaure cobertura equivalente aos testes de governança removidos.

Crie somente os componentes necessários:

- orquestracao/engine.py
- orquestracao/cli.py
- orquestracao/contracts.py
- orquestracao/omniroute.py
- orquestracao/prompts.py
- services necessários, reutilizando scripts existentes sempre que possível

OmniRoute:

- endpoint padrão http://localhost:20128/v1/responses, configurável;
- API key somente por variável de ambiente;
- cliente HTTP único;
- timeout, limites e validação da resposta;
- servidor HTTP falso nos testes;
- recibo com Combo solicitado, request ID, HTTP, duração, prompt/output e hashes;
- provider/modelo/fallback ficam null quando não houver prova;
- nunca persista credenciais;
- nenhuma rede real em testes unitários ou E2E.

Estado:

- use exclusivamente .rdaa-run/<matter_id>;
- nunca derive matter_id do output;
- SQLite é checkpoint; manifesto, matter_state e provenance são obrigatórios;
- escrita crítica atômica e falha fechada;
- rejeite .., path indevido, symlink externo e identidade divergente;
- workers/modelos nunca alteram estado diretamente.

Gates e governança:

- aprovação somente por Ricardo, vinculada ao hash;
- alteração invalida aprovação;
- uma revisão automática, segunda pausa;
- duas falhas consecutivas abrem disjuntor;
- resume/abort exigem Ricardo e motivo;
- mudança de tese, pedido ou estratégia abre gate;
- nenhum fallback próprio do RDAA.

Memória:

- Cérebro-Ricar é memória canônica;
- OpenViking é índice derivado;
- falha no Cérebro impede conclusão;
- falha no OpenViking vira pendência reexecutável sem desfazer Cérebro;
- não acesse Cérebro real, OneDrive ou matéria real durante implementação/testes.

Skills e documentação:

- remova comandos, controle de fase, persistência, CLIs e referências ao dispatcher das skills;
- preserve inteligência jurídica, método, fontes, limites e estilo;
- atualize AGENTS.md, CLAUDE.md, HERMES.md e README.md;
- declare Codex como interface, LangGraph como motor, Cérebro como memória e OpenViking como índice.

Testes obrigatórios:

- rotas C/B/A completas;
- papel -> Combo e pacote mínimo;
- HTTP sucesso, timeout, quota e resposta inválida;
- credencial nunca persistida;
- artefato/hash inválido;
- gates e invalidação por alteração;
- disjuntor, resume, abort e limite de revisão;
- reinício e concorrência entre matérias;
- falha de persistência e publicação;
- Cérebro/OpenViking indisponíveis;
- teste que falha se qualquer CLI de IA for chamada.

Use diretórios temporários e matéria sintética. Preserve mudanças existentes fora do escopo. Não faça push, merge ou publicação real. Não remova controle/teste antes da substituição comprovada.

Execute py -3.14 -m pytest -q e não declare conclusão sem suíte integral verde.

Na entrega informe arquivos criados/alterados/removidos, arquitetura implementada, Combos por papel, controles migrados, resultado exato dos testes, pendências e confirmação de que nenhuma CLI de IA, matéria real, memória real, push, merge ou publicação real foi usada.
```
