# HANDOFF_FIX_WEBSOCKET_RUNTIME_20260313T170303Z

status final
- concluido

comandos executados
- `sed -n '1,80p' requirements.txt`
- `/lab/projects/livecopilot/.venv/bin/pip install websockets`
- `systemctl restart livecopilot-web8000.service`
- `systemctl is-active livecopilot-web8000.service`
- `curl -i http://127.0.0.1:8000/status`
- `/lab/projects/livecopilot/.venv/bin/python` para validar `websockets`/`uvicorn`
- `/lab/projects/livecopilot/.venv/bin/python` com `websockets.connect('ws://127.0.0.1:8000/ws')`
- `curl -i -N ... http://127.0.0.1:8000/ws`
- `journalctl -u livecopilot-web8000.service -n 60 --no-pager`

arquivos tocados
- `requirements.txt`
- `STATUS.md`
- `docs/HANDOFF_FIX_WEBSOCKET_RUNTIME_20260313T170303Z.md`

o que foi alterado
- instalado `websockets==16.0` no `.venv`
- registrado `websockets==16.0` em `requirements.txt`
- reiniciado o servico `livecopilot-web8000.service`

o que foi validado
- `/status` continua `200 OK`
- `/ws` passou a aceitar conexao WebSocket real
- logs apos restart mostram `WebSocket /ws [accepted]` e `connection open`
- os avisos antigos de backend ausente nao apareceram na janela de logs apos a correcao

o que falta
- validar visualmente no navegador a desaparicao da enxurrada de erros da UI
- corrigir em rodada separada o erro de logging ao receber mensagem no `/ws`:
  - `KeyError: "Attempt to overwrite 'message' in LogRecord"`

se precisa aprovacao
- nao

se houve erro
- houve um novo gargalo identificado apos a correcao principal:
  - o upgrade WebSocket funciona, mas o handler quebra ao logar mensagem recebida por usar a chave reservada `message` no `extra` do logger
