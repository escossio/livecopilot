# Handoff Livecopilot Voice Observability

data:
- 2026-03-13T20:25:58Z

objetivo da rodada:
- adicionar observabilidade estruturada na trilha de voz
- reduzir o troubleshooting do "nao responde nada" a eventos auditaveis ponta a ponta
- manter o fluxo atual sem criar pipeline paralelo e sem gravar audio bruto

arquitetura mantida:
- captura/transcricao continua via browser -> OpenAI Realtime API por WebRTC
- a transcricao final continua convergindo para o backend unificado via `POST /realtime/respond`
- `_build_livecopilot_reply()` segue como motor logico unico para texto e voz

o que foi instrumentado:
- frontend em `app/static/app.js`
  - eventos:
    - `voice_session_started`
    - `voice_session_stopped`
    - `transcription_completed`
    - `voice_transcript_sent_to_backend`
    - `voice_backend_response_received`
    - `voice_backend_response_rendered`
    - `voice_error`
  - campos:
    - `session_id`
    - `conversation_id`
    - `ts`
    - `transcript_excerpt`
    - `http_status`
    - `response_summary`
    - `error_message`
    - `provider_event_type`
- backend em `app/api/routes.py`
  - endpoint novo:
    - `POST /api/voice/events`
  - observabilidade de `/realtime/respond`:
    - `voice_backend_request_received`
    - `voice_backend_response_completed`
    - `voice_backend_response_failed`

persistencia minima:
- path:
  - `/lab/projects/livecopilot/var/voice_observability/voice_events.ndjson`
- formato:
  - NDJSON/JSONL
- politica minima:
  - retencao documentada de `7` dias
- fora do escopo:
  - audio bruto

diagnostico obtido nesta rodada:
- smoke local confirmou que:
  - `POST /api/voice/events` grava evento no NDJSON
  - `POST /realtime/respond` grava request e response no NDJSON
  - o backend unificado responde normalmente no fluxo de voz
- exemplo validado:
  - pergunta: `o backend do Livecopilot esta saudavel?`
  - backend selecionado: `infra_status_connector`
  - latencia observada no smoke: `3146 ms`

leitura atual do problema "nao responde nada":
- ainda nao houve reproducao visual em navegador real nesta rodada
- com os achados atuais, o silencio nao parece estar no motor logico do backend
- os pontos mais provaveis remanescentes ficaram no cliente:
  - transcricao final nao emitida
  - transcricao emitida mas nao enviada
  - resposta recebida mas nao renderizada

validacoes executadas:
- `node --check app/static/app.js`
- `./.venv/bin/python -m unittest -v tests/test_livecopilot_interface_api.py tests/test_infra_status_connector.py`
- smoke local com `TestClient` para:
  - `POST /api/voice/events`
  - `POST /realtime/respond`

proximo passo recomendado:
- reiniciar/redeploy o runtime publicado para servir o frontend instrumentado e o endpoint novo
- executar teste manual E2E com navegador + microfone
- correlacionar:
  - console do navegador
  - `voice_events.ndjson`
  - logs JSON do backend
