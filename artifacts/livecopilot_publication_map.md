# Livecopilot publication map

## Topologia atual

- Internet -> Cloudflared -> Apache -> FastAPI
- Apache continua como borda de publicação e reverse proxy
- O frontend estático agora é servido a partir de `/lab/projects/livecopilot/web`
- O backend FastAPI segue escutando em `127.0.0.1:8099` via `livecopilot-semantic-api.service`
- O vhost do Livecopilot responde em `127.0.0.1:8080` com `Host: livecopilot.escossio.dev.br`

## Responsabilidades por camada

- `web/`: frontend estático dedicado
- `app/api/routes.py`: backend funcional com `/health`, `/status`, `/api/*`, `/realtime/*`, `/panel/cache` e suporte operacional
- `app/main.py`: bootstrap do FastAPI, `WebSocket` em `/ws` e endpoint de apoio `/project-status-data`
- Apache: serve arquivos estáticos, publica `/` e encaminha rotas dinâmicas ao backend

## Roteamento no Apache

- `/` -> frontend estático em `web/index.html`
- `/project-status` -> frontend estático em `web/project-status/index.html`
- `/static/*` -> arquivos estáticos locais em `web/static/*`
- `/health` -> backend FastAPI em `127.0.0.1:8099`
- `/status` -> backend FastAPI em `127.0.0.1:8099`
- `/project-status-data` -> backend FastAPI em `127.0.0.1:8099`
- `/api/*` -> backend FastAPI em `127.0.0.1:8099`
- `/realtime/*` -> backend FastAPI em `127.0.0.1:8099`
- `/ws` -> backend FastAPI com suporte a WebSocket
- `/panel/*` -> backend FastAPI, mantido por compatibilidade operacional
- `:80` continua com o vhost padrão do Debian; a borda do Livecopilot fica em `:8080`

## Rollback simples

- Restaurar `app/main.py` a partir do backup em `backups/20260404-livecopilot-split/main.py.bak`
- Restaurar `/etc/apache2/sites-available/livecopilot.conf` a partir do backup correspondente
- Remover ou ignorar `web/` e voltar o Apache a proxyar a raiz para o backend
- Reiniciar `livecopilot-semantic-api.service` e recarregar Apache

## Observação

- `/project-status-data` continua sendo dado de apoio do backend, porque a tela estática ainda consome o estado operacional do projeto.
- A validação desta rodada foi feita na borda `127.0.0.1:8080` com o host `livecopilot.escossio.dev.br`.
