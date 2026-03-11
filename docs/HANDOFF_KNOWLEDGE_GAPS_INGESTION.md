# HANDOFF — KNOWLEDGE GAPS INGESTION

Data: 2026-03-10
Status: concluido

## Fluxo fechado
`project brain query` -> detecta insuficiencia local -> `log_knowledge_gap` -> `data/knowledge_gaps.ndjson` -> `scripts/ingest_knowledge_gaps.py` -> pipeline de ingestao existente -> banco vetorial -> `status=resolved`.

## Arquivos-chave
- Logger: `app/services/knowledge_gap_logger.py`
- Integracao de gatilhos: `scripts/project_brain_query.py`
- Registro NDJSON: `data/knowledge_gaps.ndjson`
- Ingestao de gaps: `scripts/ingest_knowledge_gaps.py`
- Raw derivado de gaps: `data/knowledge_raw/gaps/`

## Comandos operacionais
- Registrar gap (automatico via query):
  - `scripts/project_brain_query.py --project livecopilot --query "..." --mode hybrid`
- Ingerir gaps abertos:
  - `./scripts/with-semantic-env.sh ./.venv/bin/python scripts/ingest_knowledge_gaps.py --limit 20 --max-chunks 5`
- Verificar contagem vetorial de gaps:
  - `./scripts/with-semantic-env.sh ./.venv/bin/python - <<'PY'`
  - `import os, psycopg`
  - `dsn=os.environ['DATABASE_URL']`
  - `with psycopg.connect(dsn) as c:`
  - `  with c.cursor() as cur:`
  - `    cur.execute("select count(*) from documents where source_file like %s", ("knowledge-gap::%",))`
  - `    print(cur.fetchone()[0])`
  - `PY`

## Observacoes
- Rotina atual e local-first: registra e ingere, mas nao busca conteudo externo automaticamente.
- Mantem trilha auditavel de abertura/resolucao em NDJSON.
- Estado validado nesta rodada: `3` documentos de gap e `6` chunks vetoriais (`source_file like 'knowledge-gap::%'`).
