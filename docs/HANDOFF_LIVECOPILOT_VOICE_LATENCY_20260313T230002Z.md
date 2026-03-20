# Handoff Livecopilot Voice Latency 20260313T230002Z

## Objetivo
Instrumentar e medir a latencia ponta a ponta da trilha de voz antes de otimizar.

## Mudancas aplicadas
- Frontend `app/static/app.js`
  - adicionados marcadores de tempo para:
    - inicio da fala
    - `transcription_completed`
    - envio para `/realtime/respond`
    - resposta HTTP recebida
    - `voice_output_received`
    - `voice_output_play_requested`
    - `voice_output_play_started`
- Backend `app/api/routes.py`
  - `/realtime/respond` agora devolve:
    - `latency_breakdown.build_livecopilot_reply_ms`
    - `latency_breakdown.process_ingest_ms`
    - `latency_breakdown.connector_ms`
    - `latency_breakdown.voice_output_ms`
    - `latency_breakdown.request_total_ms`
  - `voice_backend_response_completed` persiste esses campos no log
- Contrato de eventos:
  - `VoiceEventRequest` agora aceita e persiste campos extras de latencia
- Publicacao:
  - bundle novo `app.js?v=20260313T225637Z`

## Medicao real mais recente disponivel
Sessao usada: `logs/voice_sessions/20260313T2250557_rt-1773442854`

Consulta de referencia:
- `Verifica se o serviço do banco de dados está em pé.`

Tempos observados:
- `speech_started` -> `transcription_completed`: ~`5724 ms`
- `transcription_completed` -> `voice_transcript_sent_to_backend`: ~`127 ms`
- backend `/realtime/respond`: ~`4501 ms`
- `voice_backend_response_received` -> `voice_output_play_started`: ~`71 ms`
- total `speech_started` -> `play_started`: ~`11575 ms`
- total `transcription_completed` -> `play_started`: ~`5851 ms`

## Conclusao atual
- O playback no browser nao e o gargalo principal.
- O backend unificado consome a maior parte do tempo depois da transcricao final.
- A etapa ate a transcricao final tambem pesa bastante para frases mais longas.
- A nova instrumentacao permite separar no proximo teste:
  - custo do `build_livecopilot_reply`
  - custo de conector
  - custo do `voice_output`

## Proximo passo
Gerar uma nova sessao real com o bundle `v=20260313T225637Z` e reler a pasta mais recente em `logs/voice_sessions` para extrair:
- latencia total ponta a ponta
- latencia ate `transcription_completed`
- latencia backend total
- latencia do `voice_output`
- latencia ate `play_started`
- gargalo preciso com base no `latency_breakdown`
