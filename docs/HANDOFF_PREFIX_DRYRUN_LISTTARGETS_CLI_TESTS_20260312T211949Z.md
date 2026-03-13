# Handoff - Prefix dry-run/list-targets CLI tests

## status final
concluido

## comandos executados
- python3 -m unittest -v tests/test_knowledge_ingest_cli_modes.py
- ./scripts/unit_test_gate.sh
- scripts/utf8_hygiene_scan.sh --output docs/coverage/utf8_hygiene_scan_validation_prefix_dryrun_listtargets_tests_closeout.json --pretty

## arquivos tocados
- tests/test_knowledge_ingest_cli_modes.py
- scripts/unit_test_gate.sh
- STATUS.md
- docs/HANDOFF_PREFIX_DRYRUN_LISTTARGETS_CLI_TESTS_20260312T211949Z.md
- docs/coverage/prefix_dryrun_listtargets_cli_tests_*.log
- docs/coverage/prefix_dryrun_listtargets_cli_tests_validation_20260312T211925Z.json
- docs/coverage/utf8_hygiene_scan_validation_prefix_dryrun_listtargets_tests_closeout.json

## o que foi alterado
- adicionada suite de testes de CLI para:
  - contrato JSON de `--dry-run`
  - contrato JSON de `--list-targets`
  - strict com prefixo inexistente
  - compatibilidade com `--semantic-source-file`
  - zero side-effects (sem escrita de parsed/chunks/state/manifest e sem embeddings)
- gate local atualizado para incluir a nova suite automaticamente.

## se precisa aprovacao
nao

## se houve erro
nao
