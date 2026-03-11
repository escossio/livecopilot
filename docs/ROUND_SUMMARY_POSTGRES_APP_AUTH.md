# Round Summary - PostgreSQL App Auth (2026-03-10)

## Escopo
Migracao do acesso PostgreSQL do Livecopilot para autenticacao explicita de aplicacao, removendo dependencia operacional de peer auth/runuser no fluxo normal.

## Before
- Conexao padrao caia em socket local + peer (`dbname=livecopilot user=postgres`).
- Scripts/app tinham fallback implicito para `user=postgres`.
- Fluxo operacional recorria a `runuser -u postgres` para funcionar.

## After
- Role dedicada de app criada: `livecopilot_app` (sem superuser).
- Conexao canônica por TCP localhost + SCRAM.
- DSN unica canônica no ambiente: `DATABASE_URL` em `/etc/livecopilot-semantic.env`.
- Aliases de compatibilidade (`SEMANTIC_PG_DSN` e `LIVECOPILOT_DB_DSN`) apontando para mesma credencial explicita.
- App/scripts priorizam `DATABASE_URL`; fallback implicito para `user=postgres` removido.
- Wrappers operacionais removem uso normal de `runuser`.

## Banco e seguranca
- Cluster ativo: PostgreSQL 17 (`main`, porta `5432`).
- `pg_hba.conf` preserva peer local administrativo e inclui linha explicita para app:
  - `host livecopilot livecopilot_app 127.0.0.1/32 scram-sha-256`
- Role `livecopilot_app`:
  - `rolsuper=false`, `rolcreatedb=false`, `rolcreaterole=false`, `rolcanlogin=true`.
- Privilegios aplicados no DB `livecopilot`:
  - `CONNECT` no database.
  - `USAGE` no schema `public`.
  - `SELECT/INSERT/UPDATE/DELETE` nas tabelas existentes de `public`.
  - `USAGE/SELECT` nas sequences de `public`.
  - default privileges para novos objetos criados por `postgres` no schema `public`.

## Validacao objetiva
- `psql` via TCP com `livecopilot_app`: OK.
- `psycopg.connect(DATABASE_URL)` via venv: OK.
- `scripts/project_brain_query.sh` sem `runuser`: OK.
- `scripts/new_chat_context.sh` sem fallback peer: OK.
- App subiu com DSN explicita e respondeu:
  - `GET /health` => `{"status":"ok"}`
  - `POST /semantic/search` => `status=ok` com resultados.
  - `GET /api/question-bank/search` => resposta HTTP valida.

## Arquivos alterados
- Banco/SO:
  - `/etc/postgresql/17/main/pg_hba.conf`
  - `/etc/livecopilot-semantic.env`
- App/scripts:
  - `app/services/semantic_min_api.py`
  - `scripts/continuity_ingest.py`
  - `scripts/continuity_recall.py`
  - `scripts/continuity_bootstrap_context.py`
  - `scripts/backfill_continuity_embeddings.py`
  - `scripts/project_brain_query.py`
  - `scripts/with-semantic-env.sh`
  - `scripts/project_brain_query.sh`
  - `scripts/new_chat_context.sh`
  - `scripts/maintain_continuity_embeddings.sh`
  - `scripts/smoke_round_continuity_default.sh`
  - `scripts/smoke_openai_embedding.sh`
  - `scripts/semantic_min_ingest_search.sh`
  - `scripts/run_continuity_capture.sh`
  - `scripts/run_round_closeout.sh`

## Risco residual
- Historico em docs de continuidade ainda cita peer/runuser como contexto antigo; operacional atual foi migrado para DSN explicita.
