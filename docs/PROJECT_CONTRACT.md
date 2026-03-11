# Project Contract: Livecopilot

## Propósito do sistema
Livecopilot existe para atuar como **copiloto silencioso de conversação técnica em tempo real**.

No estado atual, o produto não é um assistente falado como missão primária. O valor central é:
- ouvir/receber contexto da conversa técnica;
- interpretar o contexto;
- consultar primeiro a memória técnica local do sistema;
- exibir em tela sugestões úteis e discretas durante a conversa.

## Missão operacional principal
Durante conversas técnicas reais, o sistema deve ajudar o usuário sem interromper sua fala, entregando na UI:
- termos relevantes;
- conceitos;
- possíveis respostas;
- complementos úteis;
- pistas contextuais.

A missão não é substituir a fala do usuário. É reduzir latência cognitiva com suporte técnico silencioso.

## Fluxo principal do produto
Fluxo governante (estado atual + contrato operacional):
1. Entrada de conversa em tempo real (texto incremental/manual e/ou chunks vindo de camada externa de áudio/compreensão).
2. Atualização do contexto curto da conversa (`ConversationState` + sessões realtime).
3. Consulta prioritária à base local (semantic cache/memória operacional).
4. Se insuficiente, uso de camada externa controlada (hoje: APIs/modelos externos acoplados ao caminho semântico e embeddings; sem ingestão automática cega).
5. Ranking/filtragem com sinais de relevância prática e diversidade.
6. Exibição silenciosa na interface web local.
7. Possível incorporação de novo conhecimento no banco somente via curadoria explícita.

## Componentes core
Componentes que definem o produto hoje:
- Realtime/UI local: `app/templates/index.html`, `app/static/app.js`, `app/static/style.css`, websocket/snapshot.
- Orquestração de contexto e sugestão: `app/services/context.py`, `app/services/suggestions.py`.
- Busca técnica local: `app/services/knowledge_search.py`.
- Pilar complementar de lacunas/perguntas: `app/services/question_bank_search.py`.
- Ingestão de conversa e estado: pipeline de `process_ingest`, sessões realtime e snapshot.

Garantia explícita:
- a saída principal atual é visual/silenciosa em tela;
- a UI web local faz parte do core do produto.

## Componentes de suporte
Componentes importantes, porém de suporte ao core:
- Camada de captura/compreensão de áudio plugável (`audio_capture.py`, `transcription.py`), podendo ser local ou externa, com preferência operacional atual por API/modelo externo devido à limitação real de hardware local.
- Continuidade e memória operacional (`project_runs`, `project_facts`, `project_memory_chunks`).
- Project Brain (`scripts/project_brain_query.py` e wrapper).
- Automações de round/closeout/continuity.
- Avaliações offline e calibração de ranking.

Garantias explícitas:
- Project Brain é motor de apoio ao copiloto, não o produto inteiro.
- Continuidade e memória sustentam o sistema, mas não definem sozinhas sua missão.

## Política de conhecimento em camadas
Hierarquia mandatória:
1. **Cache/memória local do sistema**:
   - `project_runs`
   - `project_facts`
   - `project_memory_chunks`
   - knowledge base
   - question bank
   - contexto recente da conversa
2. **Se insuficiente**:
   - busca externa controlada
3. **Se relevante e confiável**:
   - curadoria
   - incorporação ao banco
   - indexação para uso futuro

Definições contratuais:
- o banco local é tratado como **cache semântico operacional**, não como fronteira completa do conhecimento;
- o sistema deve reconhecer insuficiência do cache local e não fingir completude.

## Política de resposta sob incerteza
Quando a base local não sustentar resposta sólida:
- declarar limitação de contexto/confiabilidade;
- responder de forma conservadora e útil;
- priorizar pedido de clarificação e/ou sugestão de próxima ação verificável;
- quando apropriado, acionar camada externa controlada;
- nunca inventar precisão.

## Fontes de conhecimento e curadoria
Dois conjuntos complementares e obrigatórios:
- **Knowledge base**: literatura, explicação, referência técnica.
- **Question bank**: cenários, perguntas, lacunas, gatilhos de estudo e recuperação contextual.

Regra de incorporação:
- ingestão externa não é automática;
- requer avaliação de relevância, confiança e curadoria antes de promoção.

## 5. Invariantes do sistema
1. A missão principal é apoio cognitivo em conversações técnicas em tempo real, no formato de copiloto silencioso.
2. A saída principal atual do produto é visual e exibida na UI web local; essa interface faz parte do core.
3. O sistema não é chatbot principal e não usa resposta falada realtime como padrão do produto.
4. A camada local (memória operacional + banco semântico + knowledge base + question bank) é sempre a primeira consulta.
5. O banco local é cache semântico operacional, não enciclopédia completa; insuficiência de contexto local deve ser reconhecida explicitamente.
6. Busca externa, quando usada, é complementar e controlada; persistência de conhecimento externo não é automática e exige curadoria/relevância.
7. O caminho principal de acesso ao banco deve usar `DATABASE_URL` com role de aplicação; `postgres` fica restrito a tarefas administrativas.
8. `peer auth` e `runuser` não fazem parte do fluxo principal do app.
9. Smokes operacionais permanecem invariantes de sanidade antes/depois de mudanças relevantes.
10. Mudanças no núcleo devem ser pequenas, reversíveis e com evidência comparável.
11. A camada de transcrição/compreensão de áudio é plugável, com preferência operacional atual por API/modelo externo.

### Regressão arquitetural (sinal vermelho)
- Transformar o Livecopilot em chatbot principal.
- Trocar a UI silenciosa por resposta falada como padrão.
- Tratar o banco como base completa e remover a política de insuficiência.
- Reintroduzir `postgres`/`peer`/`runuser` no caminho principal do app.
- Abrir automação/autonomia fora do escopo do produto principal.

## Regras de evolução
Toda frente nova deve passar pela pergunta de controle de escopo:
**“Isso aproxima ou afasta o Livecopilot da missão de copiloto silencioso de conversação técnica em tempo real?”**

Critérios de aceite para evolução:
- reforça utilidade em conversa ao vivo;
- mantém ou melhora sinal útil em tela;
- não desloca o produto para automação periférica como objetivo central;
- preserva política de camadas e curadoria.

## Regras de calibração/ranking
- calibrar ranking por evidência (smokes + evals), sem tuning arbitrário.
- preservar legibilidade do porquê de ranqueamento (`score`, sinais, debug).
- priorizar relevância prática e diversidade de contexto.
- mudanças de ranking não podem quebrar o fluxo principal de resposta silenciosa em tempo real.

## Dívidas técnicas aceitas
1. Captura/transcrição local ainda simplificada/mock no caminho principal local.
2. Dependência de APIs/modelos externos para partes semânticas/compreensão no estado atual.
3. Modos de continuidade/Project Brain ainda exigem disciplina operacional (wrappers/smokes).
4. Parte da busca externa controlada permanece parcial e orientada por integrações existentes, não por coleta aberta automática.

## Critérios de encerramento de frentes
Uma frente pode ser encerrada quando:
- mantém missão central intacta;
- preserva invariantes deste contrato;
- tem validação operacional objetiva (incluindo smokes aplicáveis);
- registra checkpoint no `STATUS.md`;
- deixa handoff curto e auditável.

## Evoluções futuras fora do escopo atual
1. Resposta falada em tempo real (voz de saída).
2. Pilha robusta de captura/transcrição local em hardware dedicado.
3. Expansão de busca externa online além das integrações controladas atuais.
4. Automação avançada que não melhore diretamente o copiloto silencioso de conversa.

## Origem metodológica (obrigatória)
A base metodológica do sistema é:
- análise de vagas/mercado para detectar demanda real de habilidades;
- extração de tópicos/tecnologias para direcionar cobertura;
- uso de perguntas/certificações/cenários para revelar lacunas;
- busca e curadoria de literatura antes da ativação no banco;
- princípio operacional: **saber o que não sabe**;
- ideia complementar: **não uma base estática, mas uma máquina que aprende pela revelação da própria ignorância**.

## Modos secundários (não missão principal)
São modos de suporte, não o centro do produto:
- query operacional via CLI (incluindo Project Brain);
- bootstrap/new chat context;
- continuidade entre rodadas;
- avaliação offline;
- calibração de ranking.

Eles devem continuar servindo ao core realtime silencioso, não competir com ele.
