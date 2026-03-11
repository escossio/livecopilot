# ROUND SUMMARY - CONTINUITY MVP

## status final
success

## comandos executados
```bash
./.venv/bin/python -m py_compile scripts/continuity_ingest.py scripts/continuity_recall.py
runuser -u postgres -- psql -d livecopilot -f scripts/continuity_schema.sql
runuser -u postgres -- ./.venv/bin/python scripts/continuity_ingest.py --input docs/continuity/examples/sample_run_payload.json
runuser -u postgres -- ./.venv/bin/python scripts/continuity_recall.py --project livecopilot --runs 5 --facts 10 --search continuidade --search-limit 5 --json
runuser -u postgres -- psql -d livecopilot -c "SELECT COUNT(*) AS runs FROM project_runs; SELECT COUNT(*) AS facts FROM project_facts; SELECT COUNT(*) AS chunks FROM project_memory_chunks;"
runuser -u postgres -- ./.venv/bin/python scripts/continuity_ingest.py --input docs/continuity/examples/sample_run_payload.json
```

## arquivos tocados
- `docs/continuity/CONTINUITY_MVP.md`
- `docs/continuity/examples/sample_run_payload.json`
- `scripts/continuity_schema.sql`
- `scripts/continuity_ingest.py`
- `scripts/continuity_recall.py`
- `docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md`
- `STATUS.md`

## o que foi alterado
- schema inicial de continuidade criado no PostgreSQL com 3 tabelas:
  - `project_runs`
  - `project_facts`
  - `project_memory_chunks`
- taxonomias minimas de `fact_type` e `fact_status` aplicadas por `CHECK` no schema.
- idempotencia basica implementada por chaves:
  - `run_key` unico em `project_runs`
  - `fact_key` unico por `run_id`
  - `chunk_key` unico por `run_id`
- script de ingestao implementado com:
  - validacao de payload canonico
  - upsert de run/facts/chunks
  - embeddings opcionais com fallback sem bloquear ingestao
- script de recall implementado com:
  - listagem de runs recentes
  - listagem de fatos ativos
  - busca textual
  - busca semantica opcional
- documentacao operacional do MVP criada.

## o que falta
- integrar ingestao automaticamente ao loop principal.
- adicionar testes automatizados (nao so smoke manual).
- adicionar estrategia de reconciliacao semantica entre fatos de rodadas diferentes.

## se precisa aprovacao
nao para uso manual do MVP.
sim para integrar no fluxo principal automatizado.

## se houve erro
- houve erro inicial de autenticacao `peer` ao rodar ingest/recall sem `runuser -u postgres`.
- correcao aplicada: executar scripts de DB com usuario `postgres` no ambiente atual.
