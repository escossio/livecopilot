# Handoff - AWS IAM Controlled Round (2026-03-12)

## Objetivo
Executar rodada controlada AWS IAM com baseline comparavel robusto para:
- policy evaluation
- policy simulator
- permissions boundaries
- SCP

## Escopo executado
1. Inspecao da rodada AWS anterior e confirmacao do baseline fraco (1 pergunta comparavel).
2. Aquisicao/recorte oficial AWS em `aws_iam_docs_selected`.
3. Auditoria BEFORE (8 perguntas praticas).
4. Ingestao canonica controlada do recorte.
5. Persistencia semantica seletiva apenas dos 10 source_files do recorte.
6. Auditoria AFTER (mesmas 8 perguntas) e comparativo.

## Recorte oficial selecionado
- Pasta: `data/knowledge_raw/aws_iam_docs_selected`
- Total: `10` arquivos
- Inventario:
  - `docs/coverage/aws_iam_docs_selected_inventory_20260312.json`
  - `docs/coverage/aws_iam_docs_selected_files_20260312.txt`
- Fontes: IAM User Guide + AWS Organizations (SCP)
  - mapeamento: `docs/coverage/aws_iam_official_sources_mapping_20260312.json`

## Ingestao controlada
- Log: `/tmp/aws_iam_ingest_controlled_20260312.log`
- Resultado:
  - `found=222`
  - `processed=10`
  - `skipped=212`
  - `errors=0`
- Validacao:
  - `docs/coverage/aws_iam_ingest_controlled_validation_20260312.json`

## Persistencia semantica seletiva
- Log: `/tmp/aws_iam_semantic_persist_20260312.log`
- Resultado:
  - `documents_selected=10`
  - `documents_processed=10`
  - `documents_validated=10`
  - `documents_failed=0`
  - `chunks_persisted=73`
  - `sources_with_error=[]`
  - `duplicate_source_checksum_rows=[]`
- Validacao:
  - `docs/coverage/semantic_persist_aws_iam_docs_selected_20260312_validation.json`

## Auditoria before/after (mesma bateria)
- Queryset:
  - `docs/coverage/aws_iam_audit_queryset_20260312.json`
- BEFORE:
  - `docs/coverage/semantic_coverage_audit_aws_iam_before_20260312.json`
  - `well=0 partial=3 gap=5 avg_max=0.456336 avg_avg=0.442417`
- AFTER:
  - `docs/coverage/semantic_coverage_audit_aws_iam_after_20260312.json`
  - `well=7 partial=1 gap=0 avg_max=0.629874 avg_avg=0.595118`
- COMPARE:
  - `docs/coverage/semantic_coverage_audit_aws_iam_compare_before_after_20260312.json`
  - `class_changed=8/8`
  - `top1_shifted_to_aws_iam_docs_selected=8/8`
  - `delta avg_max=+0.173538`

## Leitura final
- Resultado da rodada: **ganho estrutural forte**.
- Observacao operacional: erro de encoding UTF-8 em `semantic_search` segue existente; auditoria foi executada por consulta vetorial segura (sem leitura de `content`) para evitar bloqueio sem refatorar pipeline nesta rodada.
- Snapshot de prioridade pos-rodada (`knowledge_gap_engine`):
  - `docs/coverage/knowledge_gap_engine_validation_after_aws_iam_20260312.json`
  - ordem: `terraform > observability > docker > aws_iam`.

## Proximo passo recomendado
Rodada curta dedicada para corrigir o problema de encoding UTF-8 no caminho padrao de `semantic_search`, mantendo o contrato do pipeline e removendo workaround de auditoria.
