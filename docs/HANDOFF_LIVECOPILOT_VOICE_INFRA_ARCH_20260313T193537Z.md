# HANDOFF_LIVECOPILOT_VOICE_INFRA_ARCH_20260313T193537Z

status final
- concluido

arquivos lidos
- `docs/HANDOFF_LIVECOPILOT_PUBLIC_DEPLOYMENT_20260313T191538Z.md`
- `docs/PROJECT_CONTRACT.md`
- `docs/PROJECT_STAGE_INDEX.md`
- `docs/project_status_state.json`
- `docs/LIVECOPILOT_INTERFACE_V1.md`
- `docs/HANDOFF_LIVECOPILOT_INTERFACE_ARCHITECTURE_ALIGNMENT_20260313T054615Z.md`
- `docs/continuity/PROJECT_BRAIN_QUERY.md`
- `app/static/app.js`
- `app/api/routes.py`
- `app/main.py`
- `app/services/pipeline.py`
- `app/services/state.py`
- `app/services/context.py`
- `app/services/suggestions.py`
- `app/services/knowledge_search.py`

arquitetura atual encontrada
- texto entra por `POST /api/chat` e converge para `_build_livecopilot_reply()`
- `_build_livecopilot_reply()` usa `process_ingest()` como motor logico atual do backend
- `process_ingest()` atualiza `ConversationState`, roda sugestoes e preenche `knowledge_context`
- voz publicada entra por `POST /api/realtime/session`, mas depois segue browser -> OpenAI Realtime API via WebRTC
- a voz atual usa o backend para sessao efemera, nao para processar a resposta final

gaps encontrados
- texto e voz ainda nao convergem de fato apos a transcricao
- a voz atual nao reaproveita `_build_livecopilot_reply()` depois que o texto da fala fica pronto
- nao existia conector explicito para responder perguntas sobre estado real do projeto usando fontes locais canonicas

arquitetura recomendada
- `voz -> transcricao -> entrada unificada -> roteador de intencao -> conectores read-only controlados -> resposta`
- `texto -> entrada unificada -> roteador de intencao -> conectores read-only controlados -> resposta`
- ponto de convergencia backend recomendado: `_build_livecopilot_reply()`
- manter WebRTC/Realtme como camada de captura/transcricao, nao como motor logico paralelo

conectores iniciais recomendados
- `project_state_connector`
- `project_brain_connector` read-only
- `knowledge_search_connector`
- `runtime_health_connector`

decisao do menor MVP
- implementar apenas `project_state_connector`
- usar somente leitura local de:
  - `STATUS.md`
  - `docs/project_status_state.json`
  - `docs/PROJECT_STAGE_INDEX.md`
  - `docs/HANDOFF_*.md`
- integrar no caminho unificado do backend sem tocar em Apache, backend operacional externo ou automacao mutavel

o que foi alterado
- criado `app/services/project_state_connector.py`
- integrado o conector em `app/api/routes.py`
- adicionado teste de contrato em `tests/test_livecopilot_interface_api.py`
- registrado checkpoint em `STATUS.md`

validacao
- `./.venv/bin/python -m unittest -v tests/test_livecopilot_interface_api.py`
- smoke local do conector com perguntas sobre status, checkpoint, handoff e publicacao

o que falta
- fazer a trilha de voz publicada chamar o caminho unificado do backend depois da transcricao final
- definir o contrato minimo do roteador de intencao para crescer alem do `project_state_connector`
- decidir a proxima integracao read-only entre `project_state_connector` e `project_brain_query` ou health/status local

se precisa aprovacao
- nao para este MVP
- sim antes de qualquer frente que envolva comandos mutaveis, shell remoto ou automacao operacional

se houve erro
- nao houve erro de implementacao
- gap arquitetural principal confirmado: a voz publicada ainda responde direto pela OpenAI Realtime API e nao pelo motor do backend
