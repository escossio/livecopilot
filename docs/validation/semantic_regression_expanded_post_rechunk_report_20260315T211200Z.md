# Semantic regression expanded · pós-rechunk (2026-03-15T21:12Z)

1. O reprocessamento dos prefixos Docker, Observability, Terraform e Kubernetes gerou 2.329 novos chunks mas a persistência semântica abortou com `ModuleNotFoundError: No module named 'psycopg'`.
2. Por enquanto o ranking continua refletindo a baseline anterior (`Terraform: 3 coerentes / 2 parciais`, `Kubernetes: 3 / 2`, `Docker: 1 / 4`, `Observabilidade: 2 / 2 / 1`) porque o índice não foi atualizado.
3. Reinstalar `psycopg` e rerodar `scripts/with-semantic-env.sh scripts/ingest_knowledge.sh --semantic-persist --semantic-limit-docs 999 --semantic-max-chunks-per-doc 24 --source-prefix ...` é obrigatório para que as novas versões dos chunks subam no ranking.
