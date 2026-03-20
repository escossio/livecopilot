# Handoff Livecopilot Voice Transcript Serialization

data:
- 2026-03-13T21:42:28Z

objetivo da rodada:
- corrigir o bug provado de concorrencia entre transcricoes finais sucessivas
- fazer a menor mudanca possivel no frontend de voz
- manter a instrumentacao existente

bug provado de entrada:
- sessao usada como evidencia:
  - `logs/voice_sessions/20260313T2127019_rt-1773437817`
- falha observada:
  - `voice_error`
  - mensagem:
    - `transcricao ignorada porque ja existe request em andamento`
- leitura correta:
  - uma nova `conversation.item.input_audio_transcription.completed` chegava enquanto o request anterior ainda estava em andamento
  - o frontend descartava a nova consulta valida

arquivos lidos:
- `app/static/app.js`
- `STATUS.md`
- `docs/HANDOFF_LIVECOPILOT_VOICE_WEBRTC_PRETRANSCRIPTION_DIAG_20260313T212927Z.md`
- `logs/voice_sessions/20260313T2127019_rt-1773437817/*`

backups criados antes da edicao:
- `app/static/app.js.bak.20260313T214133Z`
- `app/templates/index.html.bak.20260313T214133Z`

o que foi alterado:
- `app/static/app.js`
  - adicionada a memoria `pendingTranscript`
  - ajuste minimo em `submitVoiceTranscriptToBackend(text)`:
    - se `requestInFlight=false`:
      - envia normal
    - se `requestInFlight=true` e o texto for diferente do request atual:
      - guarda em `pendingTranscript`
      - mantem apenas a mais recente
    - no `finally` do request atual:
      - se houver `pendingTranscript`
      - emite `voice_transcript_dequeued`
      - envia a pendente automaticamente
  - requests paralelos continuam proibidos
  - duplicates identicos ao request atual continuam ignorados
- `app/templates/index.html`
  - cache-bust para publicar o bundle corrigido:
    - `/static/app.js?v=20260313T214133Z`

novos eventos frontend:
- `voice_transcript_queued`
- `voice_transcript_replaced_in_queue`
- `voice_transcript_dequeued`

before:
- nova transcricao final durante request em andamento
  - era descartada
  - gerava `voice_error`

after:
- nova transcricao final durante request em andamento
  - entra como pendente unica
  - pode substituir a pendente anterior
  - e despachada quando o request atual termina

validacao executada:
- `node --check app/static/app.js`
  - `OK`
- `./.venv/bin/python -m unittest -v tests/test_livecopilot_interface_api.py`
  - `Ran 7 tests` -> `OK`
- `systemctl restart livecopilot-web8000.service`
  - `active`
- `GET https://livecopilot.escossio.dev.br/health`
  - `200 OK`
- `GET https://livecopilot.escossio.dev.br/`
  - referencia `app.js?v=20260313T214133Z`
- `GET https://livecopilot.escossio.dev.br/static/app.js?v=20260313T214133Z`
  - contem:
    - `pendingTranscript`
    - `voice_transcript_queued`
    - `voice_transcript_replaced_in_queue`
    - `voice_transcript_dequeued`

limitacao desta rodada:
- nao foi possivel gerar aqui uma nova sessao real com microfone
- o host continua sem browser local com suporte de microfone/playwright

estado ao encerrar:
- a causa do descarte cego foi removida do codigo
- ainda falta a prova final em sessao real nova com:
  - `voice_transcript_queued`
  - `voice_transcript_dequeued`
  - `voice_backend_response_rendered`

como validar na proxima sessao real:
- abrir `https://livecopilot.escossio.dev.br/`
- garantir `app.js?v=20260313T214133Z`
- falar duas vezes em sequencia curta, com a segunda fala chegando antes da primeira resposta terminar
- abrir a pasta mais recente em `logs/voice_sessions`
- procurar por:
  - `transcription_completed`
  - `voice_transcript_queued` ou `voice_transcript_replaced_in_queue`
  - `voice_transcript_dequeued`
  - `voice_backend_response_received`
  - `voice_backend_response_rendered`
- criterio de sucesso:
  - nao deve mais aparecer `transcricao ignorada porque ja existe request em andamento`
  - a transcricao mais recente deve acabar sendo enviada e renderizada

risco residual:
- a correcao nao fecha a investigacao pre-transcription antiga
- a fila e deliberadamente limitada a uma unica pendente; transcricoes intermediarias podem ser sobrescritas pela mais recente por design
