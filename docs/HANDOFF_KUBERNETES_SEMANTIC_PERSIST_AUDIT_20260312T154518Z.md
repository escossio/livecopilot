# Handoff - Kubernetes Semantic Persist + Audit (2026-03-12T15:45:18Z)

## status final
- concluido com sucesso.

## comandos executados
- precheck de estado (`knowledge_state`, parsed, chunks) para `kubernetes_docs_selected/*`.
- baseline before:
  - `scripts/with-semantic-env.sh .venv/bin/python` com `semantic_search` em bateria de 12 queries Kubernetes.
- persistencia semantica seletiva:
  - `scripts/with-semantic-env.sh .venv/bin/python -m app.services.knowledge_ingest --semantic-persist --semantic-limit-docs 12 --semantic-source-file <12x>`
- auditoria after:
  - mesmo procedimento/mesma bateria do before.
- comparativo before/after (delta agregado e por query).
- closeout UTF-8:
  - `scripts/utf8_hygiene_scan.sh --output docs/coverage/utf8_hygiene_scan_validation_kubernetes_semantic_closeout.json --pretty`

## arquivos tocados
- `STATUS.md`
- `STATUS.md.bak-20260312T154518Z-kubernetes-semantic-persist-round`
- `docs/HANDOFF_KUBERNETES_SEMANTIC_PERSIST_AUDIT_20260312T154518Z.md`
- `docs/coverage/kubernetes_semantic_persist_precheck_20260312T153820Z.json`
- `docs/coverage/kubernetes_audit_queryset_20260312T153820Z.json`
- `docs/coverage/semantic_coverage_audit_kubernetes_before_20260312T153820Z.json`
- `docs/coverage/kubernetes_semantic_persist_validation_20260312T154518Z.json`
- `docs/coverage/semantic_coverage_audit_kubernetes_after_20260312T154518Z.json`
- `docs/coverage/semantic_coverage_audit_kubernetes_compare_before_after_20260312T154518Z.json`
- `docs/coverage/utf8_hygiene_scan_validation_kubernetes_semantic_closeout_20260312T154518Z.json`
- `docs/coverage/utf8_hygiene_scan_validation_kubernetes_semantic_closeout.json`

## o que foi alterado
- persistencia semantica do recorte Kubernetes foi executada de forma seletiva e validada:
  - `documents_selected=12`
  - `documents_processed=12`
  - `documents_validated=12`
  - `documents_failed=0`
  - `chunks_persisted=95`
  - `sources_with_error_count=0`
  - `duplicate_source_checksum_rows_count=0`
- auditoria before/after mostrou ganho no ranking:
  - before: `well=6 partial=5 gap=1 avg_max=0.617786 avg_avg=0.552623`
  - after: `well=9 partial=3 gap=0 avg_max=0.648533 avg_avg=0.605661`
  - delta: `well=+3 partial=-2 gap=-1 avg_max=+0.030747 avg_avg=+0.053038 top1_kubernetes=+5`
- scanner UTF-8 de fechamento aprovado:
  - `total_chunks_scanned=940`
  - `bad_chunks_count=0`
  - `affected_source_files_count=0`

## o que falta
- opcional: aumentar cobertura semantica Kubernetes executando persistencia com `--semantic-max-chunks-per-doc` maior e reauditar.

## se precisa aprovacao
- nao.

## se houve erro
- nao (houve tentativa intermediaria sem efeito com `documents_processed=0`, corrigida na mesma rodada antes do fechamento final).

## artefatos principais
- `docs/coverage/kubernetes_semantic_persist_validation_20260312T154518Z.json`
- `docs/coverage/semantic_coverage_audit_kubernetes_before_20260312T153820Z.json`
- `docs/coverage/semantic_coverage_audit_kubernetes_after_20260312T154518Z.json`
- `docs/coverage/semantic_coverage_audit_kubernetes_compare_before_after_20260312T154518Z.json`
- `docs/coverage/utf8_hygiene_scan_validation_kubernetes_semantic_closeout.json`
