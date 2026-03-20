# Handoff Livecopilot Voice Session Trace

data:
- 2026-03-13T20:38:25Z

objetivo da rodada:
- criar rastreabilidade por sessao da trilha de voz
- salvar frontend, backend, transcricoes, respostas e erros em arquivos simples
- diagnosticar por evidencia o caso real de "transcreve mas nao responde"

causa encontrada do problema atual:
- o backend publicado nao era o gargalo principal
- `POST /realtime/respond` no dominio publicado respondeu `200` com payload valido
- o problema estava no frontend publicado servido em `/static/app.js`
- evidencia:
  - no handler `conversation.item.input_audio_transcription.completed`, o JS antigo so fazia:
    - `pushInteraction('voz->consulta', text)`
    - atualizacao de status
  - ele nao chamava `submitVoiceTranscriptToBackend(text)`
  - ele ainda dependia de `response.output_audio_transcript.*` da sessao Realtime
- efeito observado:
  - a UI mostrava a transcricao em "Consultas e Transcricoes"
  - "Resposta Atual" seguia vazia

correcao minima aplicada:
- cache bust do frontend principal em `app/templates/index.html`
  - novo script:
    - `/static/app.js?v=20260313T203315Z`
- restart do servico:
  - `livecopilot-web8000.service`
- validacao objetiva:
  - `GET /` publicado passou a apontar para o asset versionado
  - `GET /static/app.js?v=20260313T203315Z`
    - `200`
    - `cf-cache-status: MISS`
  - `POST /api/voice/events`
    - `200`
    - devolvendo `session_dir`

rastreabilidade por sessao implementada:
- raiz:
  - `/lab/projects/livecopilot/logs/voice_sessions`
- indice:
  - `/lab/projects/livecopilot/logs/voice_sessions/session_index.json`
- naming:
  - `<timestamp>_<session_id>/`
- arquivos por sessao:
  - `session_meta.json`
  - `frontend_events.jsonl`
  - `backend_events.jsonl`
  - `transcripts.jsonl`
  - `responses.jsonl`
  - `errors.jsonl`
  - `summary.md`

conteudo por arquivo:
- `session_meta.json`
  - sessao, URL, transporte, modelo, voz, diagnosticos do navegador, `user_agent`
- `frontend_events.jsonl`
  - `voice_session_started`
  - `voice_session_stopped`
  - `transcription_completed`
  - `voice_transcript_sent_to_backend`
  - `voice_backend_response_received`
  - `voice_backend_response_rendered`
  - `voice_error`
- `backend_events.jsonl`
  - `voice_backend_request_received`
  - `voice_backend_response_completed`
  - `voice_backend_response_failed`
- `transcripts.jsonl`
  - transcricao final por sessao
- `responses.jsonl`
  - resposta resumida, backend/conector, status HTTP
- `errors.jsonl`
  - falha resumida por lado `frontend/backend`
- `summary.md`
  - ultimo evento bem-sucedido
  - primeiro ponto de falha ou silencio
  - hipotese principal

sessao smoke criada:
- `/lab/projects/livecopilot/logs/voice_sessions/20260313T203810Z_voice-session-trace-smoke`
- leitura do resumo:
  - ultimo evento bem-sucedido:
    - `voice_backend_response_completed`
  - sem erro registrado
  - como nao houve navegador real, faltou o evento de renderizacao da UI

como usar nas proximas rodadas:
- sempre abrir primeiro a sessao mais recente em:
  - `/lab/projects/livecopilot/logs/voice_sessions`
- ordem recomendada:
  - `summary.md`
  - `session_meta.json`
  - `frontend_events.jsonl`
  - `backend_events.jsonl`
  - `transcripts.jsonl`
  - `responses.jsonl`
  - `errors.jsonl`
- criterio de diagnostico:
  - se ha `transcription_completed` e nao ha `voice_transcript_sent_to_backend`, o problema esta no cliente antes do fetch
  - se ha `voice_transcript_sent_to_backend` e nao ha `voice_backend_request_received`, o problema esta na chamada HTTP/rede
  - se ha `voice_backend_response_completed` e nao ha `voice_backend_response_rendered`, o problema esta na renderizacao da UI

limitacoes restantes:
- ainda falta a validacao visual final em navegador com microfone
- nao ha captura de audio bruto nesta rodada
- limpeza automatica de sessao antiga ainda nao foi implementada
