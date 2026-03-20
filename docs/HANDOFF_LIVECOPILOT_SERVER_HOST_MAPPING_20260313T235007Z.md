# Handoff Livecopilot Server Host Mapping 20260313T235007Z

## Objetivo
Permitir checks de hosts nomeados no alvo `server` com whitelist explicita, sem shell livre, sem descoberta dinamica e mantendo o pipeline unificado.

## O que foi implementado
- `app/services/infra_status_connector.py`
  - whitelist explicita de hosts permitidos
  - parser de perguntas de servidor agora reconhece aliases nomeados como `agt01`, `debian2-1` e `llm`
  - `agt01` passou a ser host permitido
  - hosts nomeados nao permitidos retornam `warn` claro
- `tests/test_infra_status_connector.py`
  - cobertura para host permitido, host nao permitido e alias nomeado
- `tests/test_livecopilot_interface_api.py`
  - contrato da API atualizado para consulta ao host permitido

## Hosts permitidos
- `agt01`

## Como cada host foi checado
- `agt01`
  - check local read-only controlado
  - fontes:
    - `socket.gethostname()`
    - `/proc/uptime`
    - `/proc/loadavg`
    - `/proc/meminfo`
  - motivo:
    - a tentativa de self-check por `GET /health` e `GET /status` dentro do mesmo runtime gerou timeout
    - a menor correcao segura foi usar leitura local deterministica para o host permitido local

## Hosts reconhecidos mas nao permitidos
- `debian2-1`
- `llm`

## Perguntas suportadas
- `como esta o servidor agt01?`
- `como esta o servidor debian2-1?`
- `o llm esta saudavel?`
- `o servidor esta saudavel?`

## Contrato
- `target=server`
- `status=ok|warn|fail`
- `answer`
- `bullets`
- `knowledge_context.search_backend=infra_status_connector`
- `knowledge_context.requested_target`
- `knowledge_context.checked_host`
- `knowledge_context.check_mode`

## Evidencia
- conector direto:
  - `como esta o servidor agt01?` -> `status=ok`, `check_mode=whitelist_local_read_only_metrics`
  - `como esta o servidor debian2-1?` -> `status=warn`, alvo nao mapeado
  - `o llm esta saudavel?` -> `status=warn`, alvo nao mapeado
- smoke local:
  - `POST http://127.0.0.1:8000/api/chat`
  - `como esta o servidor agt01?` -> `O servidor agt01 esta saudavel no check local read-only.`
- smoke publicado:
  - `POST https://livecopilot.escossio.dev.br/api/chat`
  - `como esta o servidor agt01?` -> `O servidor agt01 esta saudavel no check local read-only.`
  - `o llm esta saudavel?` -> `O alvo de servidor llm nao esta mapeado neste conector; o host local disponivel e agt01.`

## Testes
- `./.venv/bin/python -m py_compile app/services/infra_status_connector.py tests/test_infra_status_connector.py tests/test_livecopilot_interface_api.py`
- `./.venv/bin/python -m unittest -v tests/test_infra_status_connector.py tests/test_livecopilot_interface_api.py`

## Limitacoes
- so `agt01` esta permitido nesta rodada
- `debian2-1` e `llm` continuam sem fonte controlada disponivel
- sem inventario dinamico
- sem SSH, shell livre ou execucao arbitraria

## Proximo passo
Adicionar outro host permitido apenas quando existir uma fonte read-only controlada para ele, preferencialmente um endpoint de health/status dedicado.
