# Handoff 2026-03-12 - persistencia semantica Docker (recorte 79) + reauditoria focada

## Objetivo da rodada
Persistir semanticamente o recorte Docker ja ingerido (`docker_docs_selected/*`, 79 source_files) e medir ganho real de cobertura no tema Docker.

## Escopo executado
- Identificacao automatica dos source_files em `data/knowledge_index/knowledge_state.json` (prefixo `docker_docs_selected/`).
- Persistencia semantica focada apenas nesses source_files.
- Auditoria before/after com 8 perguntas Docker e `top_k=5` por pergunta.
- Comparativo por pergunta: classe, score e origem do top-1.

## Persistencia semantica (validacao)
Arquivo: `docs/coverage/semantic_persist_docker79_validation_20260312.json`

- `documents_selected=79`
- `documents_processed=79`
- `documents_validated=79`
- `documents_failed=0`
- `chunks_persisted=84`
- `sources_with_error=[]`
- `duplicate_source_checksum_rows=[]`

Observacao operacional:
- Mantido o trilho canonico de persistencia minima (`app.services.semantic_min_api.ingest_knowledge_base_min`) sem alteracao de pipeline.
- Para estabilidade operacional com OpenAI, foi usado persist por source_file (lote unitario) com retries controlados.

## Auditoria Docker before/after
Perguntas auditadas:
1. `docker multi stage build best practices`
2. `docker build cache`
3. `docker buildkit`
4. `docker networking bridge host overlay`
5. `docker volumes vs bind mounts`
6. `docker storage drivers`
7. `docker security best practices`
8. `docker image hardening`

### Agregado before
Arquivo: `docs/coverage/semantic_coverage_audit_docker_before_20260312.json`
- `well_covered_count=0`
- `partial_count=2`
- `gap_count=6`
- `global_avg_of_max_score=0.436232`
- `global_avg_of_avg_score=0.400084`

### Agregado after
Arquivo: `docs/coverage/semantic_coverage_audit_docker_after_20260312.json`
- `well_covered_count=6`
- `partial_count=2`
- `gap_count=0`
- `global_avg_of_max_score=0.606646`
- `global_avg_of_avg_score=0.539499`

### Delta (after - before)
Arquivo: `docs/coverage/semantic_coverage_audit_docker_compare_before_after_20260312.json`
- `well_covered: +6`
- `partial: +0`
- `gap: -6`
- `global_avg_of_max_score: +0.170414`
- `global_avg_of_avg_score: +0.139415`
- perguntas com mudanca de classe: `6/8`
- perguntas com top-1 migrando para `docker_docs_selected/*`: `7/8`
- perguntas com top-1 em `docker_docs_selected/*` no after: `7/8`

## Leitura objetiva de impacto
- Ganho estrutural claro no tema Docker (lacunas zeradas na amostra focada; 6 perguntas migraram de lacuna para bem coberta).
- Cobertura de Docker passou a ser ancorada majoritariamente em fonte oficial (`docker_docs_selected/*`), reduzindo dependencia de fontes genericas/smoke.
- Ponto ainda parcial: `docker image hardening` (classe parcial manteve; top-1 continuou fora de `docker_docs_selected/*`).

## Recomendacao objetiva de proximo dominio
- Proximo alvo: **Terraform (backend remoto S3 + locking + state governance)**.
- Motivo: gap recorrente historico e alto impacto transversal em operacao DevOps.

## Artefatos gerados na rodada
- `docs/coverage/docker_source_files_selected_20260312.json`
- `docs/coverage/docker_source_files_selected_20260312.txt`
- `docs/coverage/semantic_persist_docker79_validation_20260312.json`
- `docs/coverage/semantic_coverage_audit_docker_before_20260312.json`
- `docs/coverage/semantic_coverage_audit_docker_after_20260312.json`
- `docs/coverage/semantic_coverage_audit_docker_compare_before_after_20260312.json`
