# Handoff 2026-03-12 - Kubernetes ingestao canonica controlada (12 docs)

## Objetivo da rodada
Executar ingestao canonica do recorte oficial Kubernetes (`kubernetes_docs_selected`) e preparar o corpus para persistencia semantica posterior, sem executar persistencia nesta rodada.

## Escopo executado
- Clone oficial:
  - `data/knowledge_raw/_official_repo_clones/kubernetes-website`
- Recorte materializado:
  - `data/knowledge_raw/kubernetes_docs_selected`
  - `12` arquivos `.md` (conforme proposta aprovada)
- Ingestao canonica:
  - `scripts/ingest_knowledge.sh`
  - execucao controlada com isolamento temporario de `_official_repo_clones` para manter escopo no recorte.

## Evidencias de ingestao
- Log:
  - `/tmp/kubernetes_ingest_controlled_20260312.log`
- Resumo:
  - `files_found=234`
  - `files_processed=12`
  - `files_ignored=222`
  - `parsing_errors=0`
  - `unsupported_files=0`
- Validacao consolidada:
  - `docs/coverage/kubernetes_ingest_controlled_validation_20260312.json`

## Artefatos do recorte
- Materializacao:
  - `docs/coverage/kubernetes_docs_selected_materialization_validation_20260312.json`
  - `docs/coverage/kubernetes_docs_selected_materialized_files_20260312.txt`
- Source files ingeridos:
  - `docs/coverage/kubernetes_source_files_ingested_20260312.txt`

## Resultado objetivo pos-ingestao
- `knowledge_state`: `12` entradas `kubernetes_docs_selected/*`.
- parsed gerados: `12`.
- chunks gerados: `12` arquivos de chunks, total `431` chunks no recorte.
- Manifest delta:
  - `document_count: +12` (`222 -> 234`)
  - `chunk_document_count: +12` (`222 -> 234`)
  - `chunk_count: +431` (`53710 -> 54141`)

## Persistencia semantica
- Nao executada nesta rodada (intencional).

## Closeout checklist (UTF-8)
- Comando:
```bash
scripts/utf8_hygiene_scan.sh \
  --output docs/coverage/utf8_hygiene_scan_validation_kubernetes_ingest_closeout.json \
  --pretty
```
- Resultado:
  - `bad_chunks_count=0`
  - `affected_source_files_count=0`
  - `total_chunks_scanned=845`
- Status: **aprovado**.

## Proximo passo recomendado
Executar persistencia semantica seletiva dos 12 source_files Kubernetes e depois auditoria before/after focada no dominio:

```bash
scripts/with-semantic-env.sh .venv/bin/python -m app.services.knowledge_ingest \
  --semantic-persist \
  --semantic-limit-docs 12 \
  $(jq -r '.files | to_entries[] | select(.key|startswith("kubernetes_docs_selected/")) | "--semantic-source-file \"" + .key + "\""' data/knowledge_index/knowledge_state.json)
```
