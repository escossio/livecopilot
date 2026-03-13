# Handoff - Round plan unificado por prefixo

## status final
concluido

## comandos executados
- `./scripts/round_plan.sh --source-prefix continuity_docs_selected/`
- `./scripts/round_plan.sh --source-prefix continuity_docs_selected/ --source-prefix terraform_docs_selected_incremental/`
- `./scripts/round_plan.sh --source-prefix __prefixo_que_nao_existe__/`
- `./scripts/round_plan.sh --source-prefix __prefixo_que_nao_existe__/ --strict-source-prefix`
- `./scripts/round_plan.sh --source-prefix continuity_docs_selected/ --json`
- `./scripts/round_plan.sh --source-prefix continuity_docs_selected/ --source-prefix terraform_docs_selected_incremental/ --json`
- `./.venv/bin/python -m unittest tests/test_knowledge_ingest_cli_modes.py`
- `./scripts/unit_test_gate.sh`
- `scripts/utf8_hygiene_scan.sh --output docs/coverage/utf8_hygiene_scan_validation_round_plan_closeout.json --pretty`

## arquivos tocados
- `docs/ROUND_PLAN_PREFIX_MODE.md`
- `docs/INGESTION_SELECTIVE_PREFIX_MODE.md`
- `STATUS.md`
- `docs/HANDOFF_ROUND_PLAN_PREFIX_MODE_20260312T213700Z.md`
- `docs/coverage/round_plan_single_20260312T213700Z.log`
- `docs/coverage/round_plan_multi_20260312T213700Z.log`
- `docs/coverage/round_plan_missing_non_strict_20260312T213700Z.log`
- `docs/coverage/round_plan_missing_strict_20260312T213700Z.log`
- `docs/coverage/round_plan_single_json_20260312T213700Z.json`
- `docs/coverage/round_plan_multi_json_20260312T213700Z.json`
- `docs/coverage/round_plan_validation_20260312T213700Z.json`
- `docs/coverage/utf8_hygiene_scan_validation_round_plan_closeout.json`

## o que foi alterado
- runbook dedicado do comando unificado `round_plan.sh`.
- secao curta no guia de ingestao seletiva apontando para o modo de plano.
- artefatos de validacao cobrindo 4 cenarios + contrato JSON + verificacao de side-effects.
- scanner UTF-8 final da rodada com resultado limpo.

## o que falta
- nada bloqueante para este objetivo.

## se precisa aprovacao
nao

## se houve erro
- cenario esperado de falha: prefixo inexistente com `--strict-source-prefix` retornou `exit=2` com mensagem clara.
