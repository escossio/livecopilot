# Handoff Fix API Chat 20260313T121730Z

## status final
- concluido

## comandos executados
- `ps -ef | grep -E 'uvicorn|gunicorn|livecopilot|python' | grep -v grep`
- `ss -lntp | grep 8000 || true`
- `curl -i -sS -X POST http://127.0.0.1:8000/api/chat -H 'Content-Type: application/json' --data '{"message":"teste de diagnostico"}'`
- `curl -i -sS http://127.0.0.1:8000/openapi.json`
- `systemctl status livecopilot-web8000.service --no-pager -l`
- `journalctl -u livecopilot-web8000.service -n 120 --no-pager -o short-iso`
- `systemctl restart livecopilot-web8000.service`
- `curl -i -sS http://127.0.0.1:8000/`
- `curl -i -sS -X POST http://127.0.0.1:8000/api/chat -H 'Content-Type: application/json' --data '{"text":"como configurar probes no kubernetes","mode":"generic","conversation_id":"diag-chat-001"}'`
- `curl -i -sS http://10.45.0.3:8000/`
- `curl -i -sS -X POST http://10.45.0.3:8000/api/chat -H 'Content-Type: application/json' --data '{"text":"smoke interface publicado","mode":"generic","conversation_id":"smoke-published-001"}'`
- `./.venv/bin/python -m unittest -v tests/test_livecopilot_interface_api.py`
- `./scripts/unit_test_gate.sh`

## arquivos tocados
- `STATUS.md`
- `docs/HANDOFF_FIX_API_CHAT_20260313T121730Z.md`

## o que foi alterado
- nenhuma alteracao de codigo no app
- correcao minima operacional: restart do servico `livecopilot-web8000.service`
- registro de checkpoint e handoff com evidencias

## causa raiz
- o processo publicado em `8000` estava desatualizado em relacao ao codigo atual
- a rota `/api/chat` existia em `app/api/routes.py`, mas nao estava registrada na instancia servida pelo `uvicorn`
- evidencia objetiva:
  - `POST /api/chat` retornava `404`
  - `openapi.json` exposto antes do restart nao listava `/api/chat`
  - o servico estava no ar desde `2026-03-10`

## validacao
- depois do restart:
  - `openapi.json` passou a listar `/api/chat`
  - `GET /` em `127.0.0.1:8000` e `10.45.0.3:8000` retornou `200`
  - `POST /api/chat` em `127.0.0.1:8000` retornou `200` com payload completo de resposta
  - `POST /api/chat` em `10.45.0.3:8000` retornou `200`
- testes:
  - `tests/test_livecopilot_interface_api.py` -> `OK`
  - `./scripts/unit_test_gate.sh` -> `Ran 197 tests` -> `OK`

## o que falta
- nada para restaurar `/api/chat`
- opcional futuro: endurecer o procedimento de deploy para garantir restart/reload do servico publicado

## se precisa aprovacao
- nao

## se houve erro
- sim, erro inicial reproduzido:
  - `HTTP/1.1 404 Not Found`
  - body: `{"detail":"Not Found"}`
