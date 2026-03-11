# Handoff - PostgreSQL App Auth (2026-03-10)

## Status final
Concluido. Livecopilot agora conecta ao PostgreSQL por autenticacao explicita de aplicacao (TCP localhost + role dedicada + senha + SCRAM), sem dependencia de peer auth no fluxo normal.

## Canonico de conexao
- Arquivo: `/etc/livecopilot-semantic.env`
- Variavel principal: `DATABASE_URL`
- Variaveis de compatibilidade: `SEMANTIC_PG_DSN`, `LIVECOPILOT_DB_DSN`
- Consumidores principais:
  - `app/services/semantic_min_api.py`
  - scripts de continuidade (`continuity_*`, `project_brain_query*`, `run_*`, `smoke_*`)

## Role e acesso
- Role: `livecopilot_app`
- DB: `livecopilot`
- Host/porta: `127.0.0.1:5432`
- Auth: `scram-sha-256`
- Sem privilegios administrativos (nao-superuser)

## Operacao
- Fluxo principal nao usa mais `runuser -u postgres` para DB.
- Peer foi preservado apenas para uso administrativo local no `pg_hba.conf`.

## Comandos rapidos de verificacao
- `psql "$DATABASE_URL" -Atqc "select current_user, current_database();"`
- `./scripts/project_brain_query.sh --project livecopilot --query "postgres" --mode structured`
- `./scripts/new_chat_context.sh --project livecopilot --format json --snapshot-output /tmp/latest_snapshot.json --output /tmp/new_chat_context.json`
- `curl http://127.0.0.1:8013/health` (com app em execucao)
