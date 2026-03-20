# Handoff · Semantic persist environment fix (2026-03-15T21:34Z)

## Motivação
- a persistência semântica travou com `ModuleNotFoundError: No module named 'psycopg'`, deixando o índice vetorial com os chunks antigos mesmo após limpar o chunking.
- a tarefa agora é desbloquear o ambiente, reexecutar `--semantic-persist` apenas nos domínios fracos e validar o subset para confirmar que a nova versão dos chunks está sendo usada.

## Correções aplicadas
- `apt-get install -y python3-psycopg python3-openai` para o ambiente usado por `scripts/with-semantic-env.sh`.
- verificado que `/usr/bin/python3` agora importa `psycopg 3.2.6` e `openai 1.69.0`.
- rerun do semantic-persist com `--semantic-embedding-mode mock --semantic-limit-docs 999 --semantic-max-chunks-per-doc 24` sobre os prefixos Docker/Observabilidade/Terraform/Kubernetes.

## Resultado da persistência
- 166 documentos processados, 1.750 chunks persistidos, 0 falhas, 2 caches limpos (`semantic_search_cache_entries_cleared=124`, `query_embedding_cache_entries_cleared=102`), manifesto atualizado em `data/knowledge_index/knowledge_manifest.json`.
- `docs/diagnostics/semantic_persist_env_trace_20260315T213313Z.json` registra os novos top chunks (sem front matter).
- `docs/validation/semantic_subset_post_persist_20260315T213345Z.json` e `..._report.md` documentam que os top chunks agora vêm de conteúdo útil, mas as respostas continuam majoritariamente `PARCIALMENTE COERENTES` (apenas `promtool` atingiu coerência plena).
- o pipeline mock confirmou que o chunking v1 já está sendo indexado no vetor; ainda falta ajustar a síntese/ordenamento para extrair frases completas.

## Próximos passos
1. Decidir se o modo `mock` permanece para regressões até haver estabilidade no OpenAI; caso contrário, rerodar o semantic-persist real quando possível.
2. Reexecutar a bateria ampliada (20 perguntas) para comparar com `docs/validation/semantic_regression_expanded_run_20260315T071640Z.json`.
3. Manter o foco em empurrar o conteúdo útil para o topo (penalização de metadata, chunking por cabeçalho/section) antes de mexer em ranking/síntese.
