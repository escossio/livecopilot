# Handoff - Prefix Dry-Run and List-Targets

## status final
concluido

## comandos executados
- ./scripts/ingest_knowledge.sh --source-prefix continuity_docs_selected/ --dry-run
- ./scripts/ingest_knowledge.sh --source-prefix continuity_docs_selected/ --source-prefix terraform_docs_selected_incremental/ --dry-run
- python3 -m app.services.knowledge_ingest --semantic-persist --source-prefix continuity_docs_selected/ --list-targets
- python3 -m app.services.knowledge_ingest --semantic-persist --source-prefix continuity_docs_selected/ --source-prefix terraform_docs_selected_incremental/ --list-targets
- ./scripts/ingest_knowledge.sh --source-prefix continuity_docs_selected/
- python3 -m app.services.knowledge_ingest --semantic-persist --source-prefix nao_existe/ --strict-source-prefix --list-targets
- python3 -m unittest -v tests/test_source_prefix_resolution.py
- ./scripts/unit_test_gate.sh
- scripts/utf8_hygiene_scan.sh --output docs/coverage/utf8_hygiene_scan_validation_prefix_dryrun_listtargets_closeout.json --pretty

## arquivos tocados
- app/services/knowledge_ingest.py
- scripts/ingest_knowledge.sh
- docs/INGESTION_SELECTIVE_PREFIX_MODE.md
- STATUS.md
- docs/HANDOFF_PREFIX_DRYRUN_LISTTARGETS_20260312T211437Z.md
- docs/coverage/prefix_dryrun_*.log
- docs/coverage/prefix_list_targets_*.log
- docs/coverage/prefix_legacy_flow_no_new_flags_20260312T210951Z.log
- docs/coverage/prefix_dryrun_listtargets_missing_strict_20260312T210951Z.log
- docs/coverage/prefix_dryrun_listtargets_validation_20260312T210951Z.json
- docs/coverage/utf8_hygiene_scan_validation_prefix_dryrun_listtargets_closeout.json

## o que foi alterado
- nova flag `--dry-run` para ingestao:
  - resolve e exibe alvos por prefixo, com `selection_mode`, contagem por prefixo e total
  - nao parseia, nao gera chunk, nao escreve state/manifest
- nova flag `--list-targets` para persistencia semantica:
  - requer `--semantic-persist`
  - resolve e exibe `source_files` por prefixo ou por `--semantic-source-file`
  - nao grava embeddings, nao altera banco/estado
- saida operacional estruturada (JSON) com amostra de alvos e truncamento

## o que falta
- opcional: adicionar testes unitarios especificos de CLI para os novos modos de listagem.

## se precisa aprovacao
nao

## se houve erro
- uma primeira execucao de validacao com varredura ampla ficou longa; validacao foi reexecutada em modo controlado e consolidada com `all_pass=true`.
