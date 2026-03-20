# Handoff Livecopilot PostgreSQL Infra Status 20260313T230436Z

## Objetivo
Expandir o `infra_status_connector` para incluir PostgreSQL como alvo real, minimo, seguro e somente leitura.

## Fonte escolhida
- `DATABASE_URL` canonica do projeto
- conexao via `psycopg`
- check fixo:
  - `SELECT 1`
  - `SELECT current_database(), version()`

## O que mudou
- `app/services/infra_status_connector.py`
  - PostgreSQL deixou de responder `postgres_scope_not_configured`
  - agora responde com contrato estruturado:
    - `matched`
    - `intent=infra_status`
    - `status`
    - `answer`
    - `bullets`
    - `knowledge_context.search_backend=infra_status_connector`
    - `knowledge_context.target=postgresql`
- perguntas suportadas:
  - `como esta meu PostgreSQL?`
  - `o PostgreSQL esta de pe?`
  - `o banco esta saudavel?`

## Seguranca
- sem SQL arbitrario
- sem shell/SSH
- sem escrita
- sem detalhes de credencial
- somente queries fixas e read-only

## Evidencia
- check real do ambiente:
  - `status=ok`
  - `database=livecopilot`
  - `SELECT 1` retornando `1`
- smoke local:
  - `POST /api/chat` com `o PostgreSQL esta de pe?` -> `backend=infra_status_connector`, `target=postgresql`
- smoke publicado:
  - `POST https://livecopilot.escossio.dev.br/api/chat` com `o banco esta saudavel?` -> `backend=infra_status_connector`, `target=postgresql`

## Testes
- `./.venv/bin/python -m py_compile app/services/infra_status_connector.py tests/test_infra_status_connector.py tests/test_livecopilot_interface_api.py`
- `./.venv/bin/python -m unittest -v tests/test_infra_status_connector.py tests/test_livecopilot_interface_api.py`

## Limitacoes
- ainda nao cobre locks, filas, conexoes, bloat ou replicacao
- ainda nao resume a versao para formato mais curto

## Proximo passo
Se continuar na frente de infra, o menor passo coerente e enriquecer o alvo PostgreSQL com mais 1 ou 2 sinais read-only de saude, sem abrir consulta livre.
