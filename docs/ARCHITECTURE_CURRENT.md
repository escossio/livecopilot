# Livecopilot Architecture Current

## Visão geral

O Livecopilot está dividido em três camadas operacionais:

1. frontend estático dedicado
2. backend FastAPI apenas para API, realtime e WebSocket
3. Apache como borda de publicação e reverse proxy

A publicação externa segue:

- Internet -> Cloudflared -> Apache -> frontend estático ou backend FastAPI

## Camadas

### Frontend estático

- Origem local: `/lab/projects/livecopilot/web`
- Responsabilidade: entregar a interface principal e a tela de status
- Não depende de renderização de template pelo FastAPI
- Consome o backend publicado pelo Apache

### Backend FastAPI

- Serviço: `livecopilot-semantic-api.service`
- Porta local: `127.0.0.1:8099`
- Responsabilidade: API, realtime, WebSocket e dados operacionais
- Mantém `project-status-data` como endpoint de apoio para o frontend

### Apache

- Borda local do Livecopilot: `127.0.0.1:8080`
- Responsabilidade: servir arquivos estáticos e proxyar rotas dinâmicas para o backend
- Não executa a aplicação
- `:80` do host Debian permanece com o vhost padrão e não é a borda do Livecopilot

### Cloudflared

- Publica o vhost do Livecopilot para o domínio externo
- Encaminha o tráfego para o Apache
- Não altera a divisão entre frontend e backend

## Fluxo de publicação

1. O usuário acessa o domínio público do Livecopilot.
2. O tráfego entra pelo Cloudflared.
3. O Cloudflared encaminha para o Apache.
4. O Apache serve o frontend estático ou repassa a chamada ao backend FastAPI.
5. O backend responde as rotas de API, realtime, WebSocket e apoio operacional.

## Mapa de rotas atual

- `/` -> frontend estático
- `/project-status` -> frontend estático
- `/static/*` -> frontend estático
- `/health` -> backend FastAPI
- `/status` -> backend FastAPI
- `/project-status-data` -> backend FastAPI
- `/api/*` -> backend FastAPI
- `/realtime/*` -> backend FastAPI
- `/ws` -> backend FastAPI com WebSocket
- `/panel/*` -> backend FastAPI por compatibilidade operacional

## Serviços e portas

- Apache: `127.0.0.1:8080`
- Backend FastAPI: `127.0.0.1:8099`
- Cloudflared: túnel para o hostname público do Livecopilot
- Vhost do Livecopilot: `livecopilot.escossio.dev.br`

## Arquivos e serviços-chave

- `/etc/apache2/sites-available/livecopilot.conf`
- `/etc/cloudflared/livecopilot-config.yml`
- `/etc/systemd/system/livecopilot-semantic-api.service`
- `/lab/projects/livecopilot/web/*`
- `/lab/projects/livecopilot/app/main.py`
- `/lab/projects/livecopilot/app/api/routes.py`

## Frontend x backend

### Frontend

- HTML, CSS e JS estáticos em `web/`
- `index.html` como entrada principal
- `project-status/index.html` como tela operacional de status

### Backend

- rotas de saúde e status operacional
- rotas de chat, realtime e voz
- rotas de painel e conhecimento
- endpoint `project-status-data` como payload operacional para a UI

## Rollback

- Restaurar `app/main.py` e `livecopilot.conf` a partir dos backups da rodada de separação
- Reverter o Apache para proxyar a raiz ao backend, se necessário
- Manter `web/` como fonte estática ou removê-lo apenas em um rollback completo

## Observações operacionais

- O documento canônico anterior era uma visão de arquitetura em transição; esta é a referência atual.
- O backend continua responsivo para `/api/*`, `/realtime/*`, `/ws`, `/health` e `/status`.
- A borda operacional validada nesta rodada fica em `127.0.0.1:8080` com o host `livecopilot.escossio.dev.br`.
