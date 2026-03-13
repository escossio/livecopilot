# Handoff - Knowledge pipeline V1

## status final
concluido

## comandos executados
- `chmod +x scripts/knowledge_pipeline.sh`
- `bash -n scripts/knowledge_pipeline.sh`
- `./.venv/bin/python -m unittest -v tests/test_knowledge_pipeline_cli_contract.py`
- `./scripts/knowledge_pipeline.sh --mode plan --round-id 20260313T030500Z-knowledge-pipeline-v1 --source-prefix continuity_docs_selected/`
- `./scripts/knowledge_pipeline.sh --mode run --round-id 20260313T030500Z-knowledge-pipeline-v1 --source-prefix continuity_docs_selected/ --semantic-embedding-mode mock`
- `./scripts/knowledge_pipeline.sh --mode validate --round-id 20260313T030500Z-knowledge-pipeline-v1 --source-prefix continuity_docs_selected/`
- `./scripts/unit_test_gate.sh`

## arquivos tocados
- `scripts/knowledge_pipeline.sh`
- `docs/KNOWLEDGE_PIPELINE_V1.md`
- `docs/INGESTION_SELECTIVE_PREFIX_MODE.md`
- `tests/test_knowledge_pipeline_cli_contract.py`
- `scripts/unit_test_gate.sh`
- `STATUS.md`
- `docs/HANDOFF_KNOWLEDGE_PIPELINE_V1_20260313T031559Z.md`
- `docs/coverage/knowledge_pipeline_plan_20260313T030500Z-knowledge-pipeline-v1.json`
- `docs/coverage/knowledge_pipeline_run_20260313T030500Z-knowledge-pipeline-v1.json`
- `docs/coverage/knowledge_pipeline_validate_20260313T030500Z-knowledge-pipeline-v1.json`
- `docs/coverage/knowledge_pipeline_validate_utf8_20260313T030500Z-knowledge-pipeline-v1.json`

## o que foi alterado
- criado o entrypoint `scripts/knowledge_pipeline.sh` com modos `plan`, `run` e `validate`
- o modo `plan` reaproveita `round_plan.sh` e grava artefato consolidado
- o modo `run` executa ingestao seletiva e persistencia semantica seletiva, registrando contagens e escopo resolvido
- o modo `validate` compara o run com o estado atual, verifica parsed/chunks do escopo e roda scanner UTF-8
- documentacao V1 criada e guia existente atualizado com referencia cruzada
- suite de contrato do pipeline adicionada ao gate local

## o que falta
- nada bloqueante para a V1
- proximo passo natural: validacao semantica de cobertura/qualidade por prefixo em cima do artefato de `run`

## se precisa aprovacao
nao

## se houve erro
- nao houve erro bloqueante
- no caso real controlado, a ingestao marcou `processed=0` e `skipped=12`, o que e consistente com artefatos ja existentes para o prefixo
