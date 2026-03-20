# Handoff Livecopilot Voice Output Diag

data:
- 2026-03-13T22:27:47Z

objetivo da rodada:
- descobrir quem deveria gerar o audio de saida no runtime publicado
- provar se esse caminho esta ativo ou desligado

pergunta central respondida:
- no estado atual, nenhum componente esta efetivamente falando a resposta

provas principais:

1) sessao Realtime publicada
- `POST https://livecopilot.escossio.dev.br/api/realtime/session`
- contrato real retornado:
  - `output_modalities: ["text"]`
  - `turn_detection.create_response: false`
  - `turn_detection.interrupt_response: false`
  - `audio.output.voice: "alloy"`
- leitura:
  - a sessao ainda sabe qual voz usaria
  - mas esta configurada para responder em texto apenas
  - e tambem para nao gerar resposta propria

2) frontend
- existe `<audio id="remote-audio" autoplay></audio>`
- existe `remoteAudioEl.srcObject = event.streams[0]`
- nao existe:
  - `play()`
  - tratamento de autoplay bloqueado
  - caminho de playback para audio retornado do backend
- leitura:
  - a UI aceita uma track remota WebRTC
  - mas nao existe caminho ativo de audio vindo do backend unificado

3) backend unificado /realtime/respond
- o frontend envia:
  - `voice_output_enabled: false`
- o backend ainda chama:
  - `synthesize_voice_output_realtime_controlled(...)`
- porem o runtime publicado em `/status` mostra:
  - `voice_output_enabled_default=false`
  - `voice_output_provider=external`
  - `voice_output_model=gpt-4o-mini-tts`
  - `silent_mode_default=true`
- leitura:
  - o TTS backend existe em codigo
  - mas esta desabilitado por default
  - e ainda recebe override explicito para `false`
  - alem disso, o frontend nao consome `payload.voice_output`

conclusao principal:
- A) a sessao realtime foi configurada para nao falar mais

observacao complementar importante:
- tambem ha um segundo bloqueio consistente:
  - existe TTS/backend previsto
  - mas ele nao esta sendo chamado de forma efetiva para reproduzir audio na UI

resposta objetiva por item:
- quem hoje e o responsavel pelo audio de saida?
  - teoricamente poderia ser a Realtime session ou o TTS backend
  - na pratica, nenhum dos dois esta ativo para falar
- o contrato real publicado da sessao realtime:
  - `output_modalities=["text"]`
  - `create_response=false`
  - `interrupt_response=false`
  - `audio.output.voice="alloy"`
- existe `voice/audio.output.voice` configurado?
  - sim
- isso basta para falar?
  - nao, porque `output_modalities` esta em `text`
- existe TTS depois do `/realtime/respond`?
  - existe em codigo
  - mas esta desabilitado por default e por override do frontend
  - e a UI nao toca esse retorno

causa mais provavel:
- a ausencia de audio e consequencia esperada da configuracao atual do sistema
- nao parece ser falha aleatoria de navegador/dispositivo

menor correcao recomendada:
- manter a arquitetura atual de backend unificado como fonte da resposta
- reativar somente o caminho de TTS apos `/realtime/respond`
- isso implica:
  - parar de forcar `voice_output_enabled: false` no fluxo de voz
  - fazer o frontend consumir e tocar `payload.voice_output`

alternativa menos alinhada com a arquitetura atual:
- fazer a propria Realtime session voltar a falar
- isso exigiria revisar:
  - `output_modalities`
  - `create_response`
- mas reabre a disputa de responsabilidade entre Realtime e backend unificado
