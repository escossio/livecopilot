# Handoff Fix Realtime API Key 20260313T160451Z

## status final
- concluido

## comandos executados
- `sed -n '1,240p' app/core/config.py`
- `systemctl cat livecopilot-web8000.service`
- `systemctl show livecopilot-web8000.service -p Environment -p EnvironmentFiles -p MainPID`
- `tr '\0' '\n' </proc/<pid>/environ | rg '^OPENAI_API_KEY='`
- `./scripts/with-semantic-env.sh`
- `curl -sS http://127.0.0.1:8000/status`
- `curl -i -sS -X POST http://127.0.0.1:8000/api/realtime/session -H 'Content-Type: application/json' --data '{"mode":"generic"}'`
- `systemctl restart livecopilot-web8000.service`
- `curl -i -sS http://127.0.0.1:8000/status`
- `curl -i -sS -X POST http://127.0.0.1:8000/api/realtime/session -H 'Content-Type: application/json' --data '{"mode":"generic"}'`
- `curl -i -sS http://10.45.0.3:8000/status`
- `curl -i -sS -X POST http://10.45.0.3:8000/api/realtime/session -H 'Content-Type: application/json' --data '{"mode":"generic"}'`
- `journalctl -u livecopilot-web8000.service -n 50 --no-pager -o short-iso`
- `./.venv/bin/python -m unittest -v tests/test_livecopilot_interface_api.py`
- `./scripts/unit_test_gate.sh`

## arquivos tocados
- `app/core/config.py`
- `STATUS.md`
- `docs/HANDOFF_FIX_REALTIME_API_KEY_20260313T160451Z.md`

## o que foi alterado
- o backend passou a carregar o arquivo canonico `/etc/livecopilot-semantic.env` quando presente
- o servico web foi reiniciado para subir com a chave disponivel
- checkpoint e handoff atualizados

## causa do problema
- `OPENAI_API_KEY` existia no host, mas nao no ambiente do processo web
- o projeto tinha loader de `.env`, porem nao havia `.env` no repositorio e o servico nao usava `EnvironmentFile`
- existia um ambiente canonico externo ja usado por scripts (`/etc/livecopilot-semantic.env`), mas o backend web nao o lia

## como a chave passou a ser carregada
- `app/core/config.py` agora carrega:
  - `/etc/livecopilot-semantic.env` quando presente
  - depois `.env` local como override opcional
- validacao sanitizada:
  - antes: `realtime_api_key_present=false`
  - depois: `realtime_api_key_present=true`

## validacao
- `GET /status`:
  - `200 OK`
  - `realtime_api_key_present=true`
- `POST /api/realtime/session`:
  - antes: `503` com `OPENAI_API_KEY ausente para Realtime API`
  - depois: `200 OK` com payload de sessao efemera compatível com Realtime API
- `journalctl`:
  - `POST /api/realtime/session HTTP/1.1" 200 OK` em `127.0.0.1`
  - `POST /api/realtime/session HTTP/1.1" 200 OK` em `10.45.0.3`
- testes:
  - `tests/test_livecopilot_interface_api.py` -> `OK`
  - `./scripts/unit_test_gate.sh` -> `Ran 197 tests` -> `OK`

## estado visual da interface
- a UI deixa de exibir `OPENAI_API_KEY ausente para Realtime API`, porque o backend nao retorna mais esse erro
- a proxima etapa visual esperada passa a ser criacao de sessao/conexao de voz
- observacao:
  - a confirmacao visual do DOM nao foi feita com navegador grafico nesta sessao; a inferencia foi feita pelo contrato real do endpoint consumido pela UI

## o que falta
- opcional: validar ponta a ponta WebRTC + microfone em navegador grafico

## se precisa aprovacao
- nao

## se houve erro
- sim, erro inicial reproduzido antes da correcao:
  - `503 Service Unavailable`
  - `OPENAI_API_KEY ausente para Realtime API`
