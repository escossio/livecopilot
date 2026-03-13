# Handoff 2026-03-11 - persistencia semantica dos 8 novos livros + reauditoria de cobertura

## Objetivo da rodada
Persistir semanticamente apenas os 8 novos `source_file` ja ingeridos canonicamente e medir impacto real na cobertura com o mesmo conjunto de 20 perguntas representativas usado no baseline pre-stage16.

## Execucao objetiva
- Persistencia semantica (8 fontes alvo):
  - comando efetivo: `.venv/bin/python -m app.services.knowledge_ingest --semantic-persist --semantic-only --semantic-source-file <8 source_file>`
  - resultado: `documents_selected=8`, `documents_processed=8`, `documents_validated=8`, `documents_failed=0`, `chunks_persisted=64`.
- Reauditoria de cobertura:
  - baseline reutilizado: `docs/coverage/semantic_coverage_audit_pre_stage16_20260311.json` (mesmas 20 perguntas);
  - artefatos gerados:
    - `docs/coverage/semantic_coverage_audit_after_8books_20260311.json`
    - `docs/coverage/semantic_coverage_audit_compare_pre_after_8books_20260311.json`.

## Comparativo before/after (20 perguntas)
- `bem_coberta`: `5 -> 5` (delta `0`)
- `parcial`: `5 -> 5` (delta `0`)
- `lacuna`: `10 -> 10` (delta `0`)
- `global_avg_of_max_score`: `0.503941 -> 0.507058` (delta `+0.003117`)
- `global_avg_of_avg_score`: `0.439589 -> 0.443904` (delta `+0.004315`)
- Perguntas que melhoraram: `1` (`python async await e event loop`, ainda classificada como `lacuna`).

## Impacto por tema solicitado
- Docker:
  - before: `bem=0`, `parcial=1`, `lacuna=1`, `avg_max=0.568646`, `avg_avg=0.414955`
  - after:  `bem=0`, `parcial=1`, `lacuna=1`, `avg_max=0.575346`, `avg_avg=0.424179`
- FastAPI:
  - before: `lacuna=1`, `avg_max=0.433701`, `avg_avg=0.350986`
  - after:  `lacuna=1`, `avg_max=0.433792`, `avg_avg=0.391322`
- Kubernetes conceitual:
  - before: `bem=4`, `parcial=1`, `lacuna=1`, `avg_max=0.643958`, `avg_avg=0.575899`
  - after:  `bem=4`, `parcial=1`, `lacuna=1`, `avg_max=0.643966`, `avg_avg=0.575909`

## Confirmacao de gaps priorizados
- AWS IAM: permanece `lacuna`.
- Observabilidade: permanece `lacuna`.
- Terraform: permanece `lacuna`.

## Validacao de persistencia dos 8 livros
- `sources_total=8`, `sources_ok=8`, `sources_with_error=0`.
- `duplicate_source_checksum_rows=[]` (sem duplicacao indevida relevante no recorte validado).
- Para os 8 `source_file`: estado semantico final `validated` com consistencia entre evidencias da validacao e metadados reportados no comparativo.

## Fora de escopo mantido
- Sem abrir Etapa 16.
- Sem alterar pipeline.
- Sem adicionar novos livros.

## Recomendacao objetiva (proxima literatura)
Priorizar um lote enxuto focado em lacunas ainda abertas:
1. AWS IAM (least privilege, policy design, boundaries).
2. Observabilidade (Prometheus, Grafana, Alertmanager com foco operacional).
3. Terraform (remote state S3 + locking, modulos, workflow seguro).
