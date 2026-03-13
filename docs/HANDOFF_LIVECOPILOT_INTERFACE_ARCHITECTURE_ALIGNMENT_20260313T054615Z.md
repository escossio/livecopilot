# Handoff: Livecopilot Interface Architecture Alignment

## O que esta pronto
- a pagina `app/templates/index.html` segue como a janela web do Livecopilot
- `POST /api/chat` permanece como fluxo principal de consulta/resposta
- a UI agora explicita que voz e um canal alternativo de entrada
- a documentacao da interface registra de forma clara a convergencia texto/voz para o mesmo motor logico

## O que foi testado
- `node --check app/static/app.js`
- `./.venv/bin/python -m unittest -v tests/test_livecopilot_interface_api.py`
- smoke local de `GET /` e `POST /api/chat`

## O que nao retrabalhar agora
- nao abrir uma arquitetura paralela de resposta so para voz
- nao trocar a trilha de voz para upload tradicional
- nao redesenhar a interface inteira

## Proximo passo natural
- validar em ambiente real a trilha `POST /api/realtime/session` + WebRTC + microfone, confirmando a UX de voz como "falar em vez de digitar" para consultar o mesmo Livecopilot
