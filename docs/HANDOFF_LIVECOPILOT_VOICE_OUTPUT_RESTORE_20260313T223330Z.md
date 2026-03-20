# Handoff Livecopilot Voice Output Restore

data:
- 2026-03-13T22:33:30Z

objetivo da rodada:
- restaurar o audio de saida pelo caminho correto do backend unificado
- sem reativar a fala direta da sessao Realtime

causa de entrada ja provada:
- a sessao Realtime publicada estava em:
  - `output_modalities=["text"]`
  - `create_response=false`
  - `interrupt_response=false`
- o backend tinha TTS em codigo
- mas o frontend mandava `voice_output_enabled=false`
- e nao tocava `payload.voice_output`

arquivos lidos:
- `app/static/app.js`
- `app/api/routes.py`
- `app/services/voice_output.py`
- `app/services/realtime_openai.py`
- `app/templates/index.html`
- `STATUS.md`
- `docs/HANDOFF_LIVECOPILOT_VOICE_OUTPUT_DIAG_20260313T222747Z.md`

backups criados antes da edicao:
- `app/static/app.js.bak.20260313T223330Z`
- `app/services/voice_output.py.bak.20260313T223330Z`
- `app/templates/index.html.bak.20260313T223330Z`
- `tests/test_livecopilot_interface_api.py.bak.20260313T223330Z`

o que foi alterado:

1) frontend de voz
- arquivo:
  - `app/static/app.js`
- mudancas:
  - `submitVoiceTranscriptToBackend()` passou a enviar:
    - `voice_output_enabled: true`
  - adicionada funcao de playback do retorno do backend
  - reaproveitado o elemento:
    - `<audio id="remote-audio" autoplay></audio>`
  - fluxo novo:
    - recebe `payload.voice_output`
    - le `audio_base64` + `mime_type`
    - limpa `srcObject`
    - define `src` como `data:<mime>;base64,...`
    - chama `play()`

2) backend de TTS
- arquivo:
  - `app/services/voice_output.py`
- mudancas:
  - `voice_output` agora inclui:
    - `audio_base64`
    - `mime_type`
  - isso transforma o payload do backend em algo reproduzivel no browser

3) publicacao do bundle
- arquivo:
  - `app/templates/index.html`
- novo cache-bust:
  - `/static/app.js?v=20260313T223330Z`

4) teste de contrato
- arquivo:
  - `tests/test_livecopilot_interface_api.py`
- teste novo:
  - confirma que `/realtime/respond` pode devolver `voice_output` com:
    - `voice_status=ready`
    - `audio_base64`
    - `mime_type`

eventos novos frontend:
- `voice_output_received`
- `voice_output_play_requested`
- `voice_output_play_started`
- `voice_output_play_failed`

before:
- o backend unificado gerava apenas texto utilizavel na UI
- o audio de saida nao era pedido pelo frontend
- a UI nao tocava o `voice_output`

after:
- o frontend pede explicitamente TTS do backend unificado
- o backend retorna audio embutido no payload
- a UI tenta reproduzir esse audio
- o texto segue sendo renderizado mesmo que o audio falhe

fallback quando autoplay/play falha:
- a resposta textual continua visivel
- a UI mostra mensagem explicita:
  - audio nao iniciou automaticamente
- o frontend registra:
  - `voice_output_play_failed`

validacao executada:
- `node --check app/static/app.js`
  - `OK`
- `./.venv/bin/python -m unittest -v tests/test_livecopilot_interface_api.py`
  - `Ran 8 tests` -> `OK`
- `systemctl restart livecopilot-web8000.service`
  - `active`
- `GET https://livecopilot.escossio.dev.br/`
  - referencia `app.js?v=20260313T223330Z`
- `GET https://livecopilot.escossio.dev.br/static/app.js?v=20260313T223330Z`
  - contem:
    - `voice_output_enabled: true`
    - `voice_output_received`
    - `voice_output_play_requested`
    - `voice_output_play_started`
    - `voice_output_play_failed`
- `GET https://livecopilot.escossio.dev.br/health`
  - `200 OK`

evidencia funcional do backend unificado:
- `POST https://livecopilot.escossio.dev.br/realtime/respond`
  - com `voice_output_enabled=true`
  - retornou:
    - `voice_output.voice_status = ready`
    - `voice_output.audio_output_available = true`
    - `voice_output.audio_bytes = 77568`
    - `voice_output.audio_base64 = presente`
    - `voice_output.mime_type = audio/mpeg`

o que ainda falta provar em navegador real:
- se Android / iPhone / notebook deixam `play()` acontecer sem bloqueio
- isso deve aparecer na proxima sessao real como:
  - `voice_output_received`
  - `voice_output_play_requested`
  - `voice_output_play_started`
  - ou `voice_output_play_failed`

limites remanescentes:
- nao houve browser local com microfone nesta sessao para validar a ponta visual/sonora
- alguns navegadores podem exigir gesto de usuario mais proximo do `play()`

proximo passo recomendado:
- executar uma sessao real curta com voz no bundle `v=20260313T223330Z`
- abrir a pasta mais recente em `logs/voice_sessions`
- confirmar se o audio:
  - iniciou (`voice_output_play_started`)
  - ou falhou por autoplay (`voice_output_play_failed`)
