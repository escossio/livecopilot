# Handoff 2026-03-12 - persistencia semantica Observabilidade (35) + auditoria before/after

## Objetivo da rodada
Persistir semanticamente apenas `observability_docs_selected/*` (35 source_files) e medir ganho real com auditoria before/after comparavel a Docker/Terraform.

## Escopo e validacao inicial
- `knowledge_state`: 35 source_files `observability_docs_selected/*`, todos `parsed`.
- Banco semantico antes da rodada:
  - documentos `observability_docs_selected/*`: `0`
  - chunks `observability_docs_selected/*`: `0`

## Auditoria BEFORE
Arquivo: `docs/coverage/semantic_coverage_audit_observability_before_20260312.json`

Perguntas (8):
1. `prometheus scrape_configs relabel_configs example`
2. `prometheus recording rules and alerting rules`
3. `prometheus service discovery http_sd kubernetes`
4. `promql rate sum by instance`
5. `grafana prometheus datasource configuration`
6. `grafana dashboard variables template variables`
7. `grafana alerting provisioning contact points`
8. `alertmanager route receivers grouping inhibition silences templates`

Agregado before:
- `well_covered=0`
- `partial=0`
- `gap=8`
- `avg_max=0.342409`
- `avg_avg=0.32384`

## Persistencia semantica (somente recorte Observabilidade)
Comando base reutilizado:
- `scripts/with-semantic-env.sh .venv/bin/python -m app.services.knowledge_ingest --semantic-persist --semantic-limit-docs 35 --semantic-source-file ...`

Observacao operacional:
- tentativa inicial sem isolamento de `_official_repo_clones` foi interrompida ao detectar reprocessamento fora de escopo.
- execucao final foi controlada com stash temporario de `_official_repo_clones` e restore ao final.

Resultado da execucao controlada:
- ingestao canonica previa: `processados=0`, `ignorados=212` (sem reingestao efetiva)
- persistencia semantica:
  - `documents_selected=35`
  - `documents_processed=35`
  - `documents_validated=35`
  - `documents_failed=0`
  - `chunks_persisted=234`
  - `sources_with_error=[]`
  - `duplicate_source_checksum_rows=[]`
  - `embedding_mode_used=openai`
  - `cache_invalidation`:
    - `semantic_search_cache_entries_cleared=16`
    - `query_embedding_cache_entries_cleared=16`

Evidencia:
- `docs/coverage/semantic_persist_observability35_validation_20260312.json`
- log: `/tmp/observability_semantic_persist_controlled_20260312.log`

## Auditoria AFTER
Arquivo: `docs/coverage/semantic_coverage_audit_observability_after_20260312.json`

Agregado after:
- `well_covered=5`
- `partial=3`
- `gap=0`
- `avg_max=0.617553`
- `avg_avg=0.570856`

## Comparativo before/after
Arquivo: `docs/coverage/semantic_coverage_audit_observability_compare_before_after_20260312.json`

Delta:
- `well: +5`
- `partial: +3`
- `gap: -8`
- `avg_max: +0.275144`
- `avg_avg: +0.247016`

Indicadores de mudança:
- perguntas com mudanca de classe: `8/8`
- perguntas com top-1 migrando para `observability_docs_selected/*`: `8/8`
- top-1 em `observability_docs_selected/*` no after: `8/8`

## Conclusao objetiva
- Classificacao da rodada: **ganho estrutural forte**.
- Houve zeragem de lacunas no conjunto focado e dominancia de top-1 da fonte oficial recortada em toda a bateria.

## Proximo passo recomendado
- Consolidar relatorio unico comparativo multi-dominio (AWS IAM + Docker + Terraform + Observabilidade) para priorizacao do proximo eixo de aquisicao/persistencia.
