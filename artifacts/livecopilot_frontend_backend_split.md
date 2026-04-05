# Livecopilot frontend/backend split

## Objetivo

- Separar o Livecopilot em duas camadas lógicas:
  - frontend estático dedicado
  - backend FastAPI focado em API, realtime e WebSocket
- Manter Apache como borda de publicação
- Preservar o domínio e o comportamento atual da aplicação

## O que virou frontend

- `web/index.html`
- `web/project-status/index.html`
- `web/static/app.js`
- `web/static/style.css`
- `web/static/project_status.js`
- `web/static/project_status.css`

## O que ficou no backend

- `GET /health`
- `GET /status`
- `POST /api/chat`
- `POST /api/realtime/session`
- `POST /api/voice/events`
- `POST /realtime/ingest`
- `GET /realtime/session/{conversation_id}`
- `GET /realtime/sessions`
- `GET /realtime/metrics`
- `POST /realtime/respond`
- `GET /api/panel/summary`
- `GET /api/panel/recent`
- `GET /panel/cache`
- `GET /api/knowledge/*`
- `GET /api/question-bank/*`
- `GET /api/certifications/*`
- `GET /ws`
- `GET /project-status-data` como apoio operacional consumido pelo frontend

## Roteamento do Apache

- `/` -> frontend estático
- `/project-status` -> frontend estático
- `/static/*` -> frontend estático
- `/health` -> backend FastAPI
- `/status` -> backend FastAPI
- `/project-status-data` -> backend FastAPI
- `/api/*` -> backend FastAPI
- `/realtime/*` -> backend FastAPI
- `/ws` -> backend FastAPI com WebSocket
- `/panel/*` -> backend FastAPI por compatibilidade

## Validação esperada

- `GET /` abre a UI estática
- `GET /project-status` abre a tela de status estática
- `GET /api/chat` responde via backend
- `GET /health` e `GET /status` respondem via backend
- `GET /realtime/respond` continua íntegro
- `GET /ws` continua disponível via WebSocket

## Rollback

- Reverter `app/main.py` e `livecopilot.conf` pelos backups criados nesta rodada
- Repointar a raiz do Apache para o backend se houver regressão
- Remover o diretório `web/` se a separação precisar ser desfeita
