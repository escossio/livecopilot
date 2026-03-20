# Handoff Livecopilot Server Infra Status 20260313T234023Z

## Objetivo
Adicionar um alvo `server` ao `infra_status_connector` com checks minimos, read-only e deterministas.

## Fonte escolhida
- hostname via `socket.gethostname()`
- `/proc/uptime`
- `/proc/loadavg`
- `/proc/meminfo`

## O que mudou
- `app/services/infra_status_connector.py`
  - novo alvo:
    - `target=server`
  - novas perguntas roteadas:
    - `o servidor esta saudavel?`
    - `como esta a carga do servidor?`
    - `como esta o servidor <nome>?`
  - contrato:
    - `intent=infra_status`
    - `status=ok|warn|fail`
    - `answer`
    - `bullets`
    - `knowledge_context.search_backend=infra_status_connector`

## Seguranca
- sem shell arbitrario
- sem execucao livre
- sem mutacao
- so leitura local de metricas basicas do host

## Comportamento atual
- perguntas genericas de servidor:
  - retornam estado do host local atual (`agt01`)
- perguntas com alvo nomeado:
  - se o alvo nao for o host local mapeado, retornam `warn`
  - exemplo:
    - `como esta o servidor debian2-1?` -> alvo nao mapeado localmente

## Evidencia
- smoke local:
  - `POST /api/chat` com `o servidor esta saudavel?`
  - resposta com `target=server`, `status=ok`
- smoke publicado:
  - `POST https://livecopilot.escossio.dev.br/api/chat` com `o servidor esta saudavel?`
  - resposta com `target=server`, `status=ok`

## Testes
- `./.venv/bin/python -m py_compile app/services/infra_status_connector.py`
- `./.venv/bin/python -m unittest -v tests/test_infra_status_connector.py tests/test_livecopilot_interface_api.py`

## Limitacoes
- cobre apenas o host local do app
- nao faz check remoto real de hosts nomeados
- nao inclui disco, rede ou servicos dedicados

## Proximo passo
Adicionar um mapeamento explicito de hosts permitidos e, se fizer sentido, um endpoint/control-plane read-only por host para checks remotos controlados.
