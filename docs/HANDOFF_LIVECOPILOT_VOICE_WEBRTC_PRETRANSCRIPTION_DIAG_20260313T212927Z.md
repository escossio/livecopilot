# Handoff Livecopilot Voice WebRTC Pre-Transcription Diag

data:
- 2026-03-13T21:29:27Z

objetivo da rodada:
- instrumentar a etapa frontend/WebRTC anterior a `transcription_completed`
- publicar a instrumentacao sem alterar backend logico nem `/realtime/respond`
- deixar a proxima sessao real capaz de provar onde o fluxo morre

contexto consolidado antes desta rodada:
- a sessao falha de referencia foi:
  - `logs/voice_sessions/20260313T2114139_rt-1773437052`
- nela houve:
  - `POST /api/realtime/session` -> `200`
  - `WebSocket /ws` aceito
  - `POST /api/voice/events` -> `200` para `voice_session_started`
  - depois apenas `voice_session_stopped`
- nela nao houve:
  - `transcription_completed`
  - `voice_transcript_sent_to_backend`
  - `voice_backend_response_received`
  - `voice_backend_response_rendered`
  - `voice_error`
- conclusao valida:
  - o fluxo morria antes da transcricao final no frontend/WebRTC

arquivos lidos:
- `app/static/app.js`
- `app/services/realtime_openai.py`
- `app/api/routes.py`
- `STATUS.md`
- `docs/HANDOFF_LIVECOPILOT_VOICE_SESSION_TRACE_20260313T203825Z.md`
- `docs/HANDOFF_LIVECOPILOT_VOICE_OBSERVABILITY_20260313T202558Z.md`
- `logs/voice_sessions/20260313T2114139_rt-1773437052/*`

backups criados antes da edicao:
- `app/static/app.js.bak.20260313T212419Z`
- `app/templates/index.html.bak.20260313T212419Z`

o que foi alterado:
- `app/static/app.js`
  - telemetria nova de pre-transcription:
    - `voice_session_open_requested`
    - `voice_session_open_response_received`
    - `rtc_peer_connection_created`
    - `rtc_offer_created`
    - `rtc_local_description_set`
    - `rtc_remote_description_received`
    - `rtc_remote_description_set`
    - `rtc_track_received`
    - `rtc_connection_state_changed`
    - `rtc_ice_connection_state_changed`
    - `rtc_signaling_state_changed`
    - `rtc_peer_connection_error`
    - `rtc_datachannel_created`
    - `rtc_datachannel_opened`
    - `rtc_datachannel_closed`
    - `rtc_datachannel_error`
    - `rtc_message_received`
    - `rtc_message_parse_failed`
    - `realtime_event_received`
    - `realtime_error_event`
    - `microphone_access_requested`
    - `microphone_access_granted`
    - `microphone_access_failed`
    - `microphone_track_state`
    - `voice_stop_requested`
    - `voice_session_auto_stopped`
  - payload resumido dos eventos realtime:
    - tipo bruto
    - ids principais quando existirem
    - trecho de texto quando houver
    - erro resumido quando houver
  - rastreio de motivo de encerramento:
    - manual
    - auto-stop por `connectionState`
    - auto-stop por `iceConnectionState`
    - auto-stop por `datachannel`
    - auto-stop por erro realtime
    - auto-stop por fim da track do microfone
- `app/templates/index.html`
  - cache-bust para servir o bundle novo:
    - `/static/app.js?v=20260313T212419Z`

publicacao validada:
- `systemctl restart livecopilot-web8000.service`
- `systemctl is-active livecopilot-web8000.service`
  - `active`
- `node --check app/static/app.js`
  - `OK`
- `GET https://livecopilot.escossio.dev.br/`
  - referencia `app.js?v=20260313T212419Z`
- `GET https://livecopilot.escossio.dev.br/static/app.js?v=20260313T212419Z`
  - contem os novos eventos de instrumentacao

limitacao objetiva desta rodada:
- nao foi possivel executar aqui um teste real em navegador com microfone
- evidencias:
  - nenhum `chromium`, `chrome` ou `firefox` instalado no host
  - `playwright` ausente

sessao real adicional observada no periodo:
- `logs/voice_sessions/20260313T2127019_rt-1773437817`
- ela serviu como contraste funcional:
  - houve `transcription_completed`
  - houve `voice_transcript_sent_to_backend`
  - houve `voice_backend_response_received`
  - houve `voice_backend_response_rendered`
- problema capturado nessa sessao:
  - novas transcricoes finais chegaram enquanto havia request em andamento
  - erro frontend observado:
    - `transcricao ignorada porque ja existe request em andamento`
- isso prova uma segunda falha real:
  - concorrencia entre transcricoes sucessivas apos a transcricao final
- isso nao prova a causa da sessao falha `rt-1773437052`

estado da causa principal ao encerrar esta rodada:
- ainda nao provada para a sessao que morria antes de `transcription_completed`
- agora a instrumentacao publicada e suficiente para provar:
  - se o data channel abre
  - se o peer connection estabiliza
  - se chegam eventos realtime com nome diferente do esperado
  - se ha erro silencioso
  - se houve `voice_stop_requested` manual
  - se houve `voice_session_auto_stopped`

como conduzir a proxima captura:
- abrir `https://livecopilot.escossio.dev.br/`
- garantir que a pagina carregou `app.js?v=20260313T212419Z`
- fazer um teste curto com voz
- depois abrir a pasta mais recente em `logs/voice_sessions`
- ordem de leitura:
  - `summary.md`
  - `session_meta.json`
  - `frontend_events.jsonl`
  - `backend_events.jsonl`
  - `transcripts.jsonl`
  - `responses.jsonl`
  - `errors.jsonl`

o que procurar primeiro na proxima sessao:
- `voice_session_open_requested`
- `voice_session_open_response_received`
- `rtc_peer_connection_created`
- `rtc_datachannel_opened`
- `rtc_connection_state_changed`
- `rtc_message_received`
- `realtime_event_received`
- se apareceu:
  - `input_audio_buffer.speech_started`
  - `input_audio_buffer.speech_stopped`
  - `conversation.item.input_audio_transcription.completed`
  - algum tipo alternativo de transcricao
  - `realtime_error_event`
  - `voice_stop_requested`
  - `voice_session_auto_stopped`

criterio de leitura:
- se o data channel nao abrir:
  - gargalo em negociacao WebRTC/data channel
- se abrir e nao chegar nenhuma `rtc_message_received`:
  - gargalo na sessao realtime antes dos eventos
- se chegarem mensagens mas sem evento de transcricao:
  - verificar nome real dos tipos recebidos
- se houver `voice_session_auto_stopped`:
  - usar `provider_event_type` e `response_summary` como motivo concreto
- se houver `voice_stop_requested` com `provider_event_type=manual`:
  - houve encerramento manual

resumo curto:
- a rodada entregou instrumentacao publicada e auditavel
- a causa pre-transcription ainda nao foi provada por falta de uma sessao real nova com o bundle instrumentado
- a proxima sessao real ja deve responder exatamente onde o fluxo morre
