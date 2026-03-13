# Livecopilot Interface V1

## O que e
V1 funcional da interface web do Livecopilot reaproveitando a pagina HTML original do projeto:
- texto via backend do proprio Livecopilot
- voz como canal alternativo de entrada via OpenAI Realtime API
- exibicao clara de resposta, transcricao e estado da interacao

Pagina reaproveitada:
- `app/templates/index.html`

## O que foi reaproveitado
- pagina HTML original do projeto
- `app/static/style.css`
- backend FastAPI existente em `app/main.py`
- rotas e estado conversacional ja existentes em `app/api/routes.py`
- fluxo de resposta do backend ja existente em `/realtime/respond`

## O que foi criado/adaptado
- rota explicita de texto:
  - `POST /api/chat`
- rota minima de sessao efemera para voz:
  - `POST /api/realtime/session`
- helper de integracao com OpenAI Realtime:
  - `app/services/realtime_openai.py`
- frontend adaptado em:
  - `app/static/app.js`
  - `app/templates/index.html`

## Desenho da V1

### Arquitetura correta da interface
- a pagina HTML e uma janela de acesso ao proprio sistema Livecopilot
- o motor logico de consulta/resposta fica no backend do Livecopilot
- texto e a entrada de referencia para esse motor
- voz nao define um segundo produto conversacional
- voz e o caminho "falar em vez de digitar":
  - capturar audio
  - transcrever
  - exibir a consulta/transcricao na UI
  - convergir para a mesma logica de consulta do Livecopilot

Em termos de contrato:
- rota principal de consulta:
  - `POST /api/chat`
- rota auxiliar da voz:
  - `POST /api/realtime/session`
  - ela existe para abrir a sessao efemera e a captura/transcricao via Realtime API
  - nao substitui o papel do backend logico do Livecopilot

### Texto
Fluxo:
1. usuario digita no campo de texto
2. frontend chama `POST /api/chat`
3. backend reaproveita a mesma logica central do Livecopilot, compartilhada com `/realtime/respond`
4. frontend renderiza:
   - resposta atual
   - pontos de apoio
   - log da interacao
   - estado da interacao
   - contexto resumido do backend

### Voz
Fluxo:
1. frontend chama `POST /api/realtime/session`
2. backend cria sessao efemera usando `client.realtime.client_secrets.create(...)`
3. frontend abre WebRTC direto com a OpenAI Realtime API
4. audio do microfone vai direto para a OpenAI
5. frontend recebe eventos realtime e renderiza:
   - status da sessao
   - transcricao da fala como entrada de consulta
   - resposta/transcricao do Livecopilot

Leitura correta desta V1:
- a trilha de voz existe para permitir falar em vez de digitar
- a UI deve deixar claro que a fala e uma entrada alternativa para a mesma janela de consulta do sistema
- esta frente nao abre uma arquitetura paralela de resposta "so para voz"

Observacao importante:
- esta V1 nao usa upload tradicional de audio
- esta V1 nao cria proxy proprio de audio
- o backend so emite o segredo efemero e a configuracao minima da sessao

## Rotas HTTP da V1
- `GET /`
  - entrega a interface HTML
- `GET /status`
  - informa capacidades do backend, inclusive disponibilidade da trilha Realtime
- `POST /api/chat`
  - entrada principal de consulta do Livecopilot
- `POST /api/realtime/session`
  - cria sessao efemera para o browser conectar via WebRTC na OpenAI Realtime API
  - rota auxiliar da entrada por voz
- rotas antigas mantidas e reaproveitadas:
  - `POST /ingest`
  - `POST /realtime/respond`
  - `POST /realtime/ingest`

## Como usar hoje

### Rodar localmente
```bash
uvicorn app.main:app --reload
```

Abrir:
- `http://127.0.0.1:8000/`

### Texto
1. digite no campo `Entrada por texto`
2. clique em `Enviar texto`
3. a resposta volta do backend em `/api/chat`
4. a UI mostra resposta, pontos de apoio, status e contexto do backend

### Voz
Pre-requisitos:
- `OPENAI_API_KEY` configurada
- navegador com suporte a WebRTC e permissao de microfone

Passos:
1. abrir a pagina
2. clicar `Iniciar voz`
3. o frontend pede uma sessao efemera em `/api/realtime/session`
4. o browser negocia WebRTC diretamente com `https://api.openai.com/v1/realtime/calls`
5. falar no microfone
6. acompanhar transcricao/status/resposta na interface
7. interpretar a fala como uma consulta alternativa ao mesmo Livecopilot

## Dependencias da Realtime API
- backend:
  - `OPENAI_API_KEY`
  - SDK Python `openai`
- frontend:
  - `navigator.mediaDevices.getUserMedia(...)`
  - `RTCPeerConnection`
  - data channel para eventos realtime
- endpoint oficial usado pelo browser:
  - `https://api.openai.com/v1/realtime/calls`

## Validacao executada nesta rodada
- contrato do frontend:
  - `node --check app/static/app.js` -> `OK`
- contrato da API da interface:
  - `./.venv/bin/python -m unittest -v tests/test_livecopilot_interface_api.py` -> `Ran 2 tests` -> `OK`
- gate local completo:
  - `./scripts/unit_test_gate.sh` -> `Ran 197 tests in 105.823s` -> `OK`
- smoke local de texto:
  - `GET /status` -> `200`
  - `POST /api/chat` -> `200`
  - evidencia: resposta real retornada pelo backend com `backend=semantic_api`
- checagem de erro/control flow da voz:
  - `POST /api/realtime/session` -> `503`
  - evidencia concreta do ambiente atual:
    - `OPENAI_API_KEY ausente para Realtime API`

## Validacao final da voz em ambiente atual
- tentativa desta rodada:
  - validar ponta a ponta:
    - sessao efemera
    - WebRTC
    - microfone
    - transcricao/resposta na UI
- resultado:
  - validacao real **nao concluida** neste ambiente
- evidencia objetiva:
  - artefato:
    - `docs/coverage/livecopilot_interface_voice_validation_20260313T052938Z.json`
  - `GET /status`:
    - `realtime_api_enabled=true`
    - `realtime_api_key_present=false`
  - `POST /api/realtime/session`:
    - `503`
    - erro: `OPENAI_API_KEY ausente para Realtime API`
  - ambiente grafico:
    - sem `DISPLAY`
    - sem `WAYLAND_DISPLAY`
    - `XDG_SESSION_TYPE=tty`
    - nenhum binario de navegador encontrado

## Como reproduzir o teste real quando o ambiente estiver pronto
Pre-requisitos minimos:
- `OPENAI_API_KEY` exportada no shell do backend
- navegador com suporte a WebRTC
- permissao de microfone
- sessao com display grafico

Passos:
1. subir o backend:
   - `uvicorn app.main:app --reload`
2. confirmar:
   - `GET /status`
   - `realtime_api_key_present=true`
3. testar sessao efemera:
   - `POST /api/realtime/session`
   - esperar `200`
4. abrir `http://127.0.0.1:8000/`
5. clicar `Iniciar voz`
6. permitir o microfone
7. falar uma frase curta
8. confirmar:
   - sessao criada
   - conexao WebRTC estabelecida
   - transcricao do usuario na UI
   - resposta/transcricao do assistente na UI

## Limitacoes atuais
- a validacao de voz ponta a ponta ficou bloqueada neste ambiente pela ausencia de `OPENAI_API_KEY` e pela falta de navegador grafico utilizavel
- sem chave valida, a V1 so consegue provar o contrato do endpoint e o caminho de erro controlado
- a convergencia total "voz -> transcricao -> mesma resposta logica do `/api/chat`" ainda precisa de validacao real em ambiente com credencial e microfone
- a V1 nao implementa autenticacao de usuario
- a V1 nao implementa memoria sofisticada de sessao
- a V1 nao faz redesign amplo de frontend
- a V1 nao cria websocket proprio para audio

## Proximo passo natural
Quando esta frente for retomada:
- validar WebRTC ponta a ponta em ambiente com `OPENAI_API_KEY` e navegador com microfone
- endurecer o tratamento de eventos realtime observados em navegador real
- confirmar em ambiente real a UX final de voz como canal alternativo da mesma consulta do Livecopilot
