# Handoff 2026-03-11 - persistencia semantica AWS (5) + reauditoria IAM

## Objetivo da rodada
Persistir semanticamente apenas os 5 novos `source_file` de AWS e medir impacto objetivo no tema IAM.

## Persistencia semantica (escopo restrito aos 5 source_file)
- Execucao canônica com ambiente semantico carregado (`scripts/with-semantic-env.sh`).
- Resultado validado:
  - `documents_selected=5`
  - `documents_processed=5`
  - `documents_validated=5`
  - `documents_failed=0`
  - `chunks_persisted=40`
  - `sources_with_error=0`
  - `duplicate_source_checksum_rows=[]`
- Evidencia detalhada: `docs/coverage/semantic_persist_aws5_validation_20260311.json`.

## Auditoria IAM focada (8 perguntas)
Perguntas auditadas:
1. `aws iam least privilege policy`
2. `policy evaluation logic aws`
3. `permissions boundaries iam`
4. `iam policy simulator`
5. `explicit deny allow iam`
6. `identity policy resource policy boundary scp aws`
7. `iam best practices aws`
8. `policy boundary vs scp aws`

Resultado agregado pós-persistência:
- `well_covered_count=0`
- `partial_count=6`
- `gap_count=2`
- `global_avg_of_max_score=0.470363`
- `global_avg_of_avg_score=0.468348`

Comparacao before/after focada em IAM:
- baseline historico comparavel disponivel para `1/8` pergunta (`aws iam least privilege policy`);
- melhoria objetiva nessa pergunta:
  - classe: `lacuna -> parcial`
  - `max_score: 0.421688 -> 0.520263` (`+0.098575`)
  - `avg_score: 0.345207 -> 0.514229` (`+0.169022`)
  - `top-1`: `data/question_bank_raw/sample_assessment.md -> aws/Permissions boundaries for IAM entities.pdf`
- `7/8` perguntas passaram a ter `top-1` vindo dos novos documentos `aws/*`.

Artefatos:
- `docs/coverage/semantic_coverage_audit_iam_after_aws5_20260311.json`
- `docs/coverage/semantic_coverage_audit_iam_compare_after_aws5_20260311.json`

## Reauditoria global (opcional, executada)
Comparativo com baseline de 20 perguntas:
- `bem_coberta: 5 -> 5`
- `parcial: 5 -> 6`
- `lacuna: 10 -> 9`
- `global_avg_of_max_score: +0.008203`
- `global_avg_of_avg_score: +0.014236`
- ganho estrutural observado via IAM (`aws iam least privilege policy` saiu de lacuna para parcial).

Artefatos:
- `docs/coverage/semantic_coverage_audit_post_aws5_20260311.json`
- `docs/coverage/semantic_coverage_audit_compare_pre_after_aws5_20260311.json`

## Leitura operacional
- Houve ganho estrutural no recorte IAM (na pergunta comparável histórica) e ganho agregado leve no panorama global.
- Ainda há gaps relevantes fora de IAM (ex.: Terraform backend/state locking, observabilidade, Jenkins, PostgreSQL indexing).

## Proxima recomendacao objetiva
Priorizar literatura de **Terraform (remote state S3 + locking + governance de módulos)** para atacar um gap recorrente que permanece em `lacuna`.
