# Handoff - Knowledge Pipeline V2 Semantic Validate

## status final
concluido

## comandos executados
- `./.venv/bin/python -m unittest -v tests/test_knowledge_pipeline_semantic_validate.py`
- `./scripts/knowledge_pipeline.sh --mode semantic-validate --round-id 20260313T030500Z-knowledge-pipeline-v1 --source-prefix continuity_docs_selected/`
- `./scripts/knowledge_pipeline.sh --mode plan --round-id 20260313T033200Z-knowledge-pipeline-v2-terraform --source-prefix terraform_docs_selected_incremental/`
- `./scripts/knowledge_pipeline.sh --mode run --round-id 20260313T033200Z-knowledge-pipeline-v2-terraform --source-prefix terraform_docs_selected_incremental/ --semantic-embedding-mode mock`
- `./scripts/knowledge_pipeline.sh --mode validate --round-id 20260313T033200Z-knowledge-pipeline-v2-terraform --source-prefix terraform_docs_selected_incremental/`
- `./scripts/knowledge_pipeline.sh --mode semantic-validate --round-id 20260313T033200Z-knowledge-pipeline-v2-terraform --source-prefix terraform_docs_selected_incremental/`
- `./scripts/knowledge_pipeline.sh --mode plan --round-id 20260313T034000Z-knowledge-pipeline-v2-terraform-openai --source-prefix terraform_docs_selected_incremental/`
- `./scripts/knowledge_pipeline.sh --mode run --round-id 20260313T034000Z-knowledge-pipeline-v2-terraform-openai --source-prefix terraform_docs_selected_incremental/ --semantic-embedding-mode openai`
- `./scripts/knowledge_pipeline.sh --mode validate --round-id 20260313T034000Z-knowledge-pipeline-v2-terraform-openai --source-prefix terraform_docs_selected_incremental/`
- `./scripts/knowledge_pipeline.sh --mode semantic-validate --round-id 20260313T034000Z-knowledge-pipeline-v2-terraform-openai --source-prefix terraform_docs_selected_incremental/`
- `./scripts/unit_test_gate.sh`

## arquivos tocados
- `app/services/semantic_min_api.py`
- `scripts/knowledge_pipeline.sh`
- `scripts/knowledge_pipeline_semantic_validate.py`
- `docs/KNOWLEDGE_PIPELINE_V1.md`
- `docs/KNOWLEDGE_PIPELINE_V2_SEMANTIC_VALIDATE.md`
- `tests/test_knowledge_pipeline_semantic_validate.py`
- `scripts/unit_test_gate.sh`
- `STATUS.md`
- `docs/HANDOFF_KNOWLEDGE_PIPELINE_V2_SEMANTIC_VALIDATE_20260313T034545Z.md`
- `docs/coverage/knowledge_pipeline_semantic_validate_20260313T030500Z-knowledge-pipeline-v1.json`
- `docs/coverage/knowledge_pipeline_semantic_validate_20260313T033200Z-knowledge-pipeline-v2-terraform.json`
- `docs/coverage/knowledge_pipeline_plan_20260313T034000Z-knowledge-pipeline-v2-terraform-openai.json`
- `docs/coverage/knowledge_pipeline_run_20260313T034000Z-knowledge-pipeline-v2-terraform-openai.json`
- `docs/coverage/knowledge_pipeline_validate_20260313T034000Z-knowledge-pipeline-v2-terraform-openai.json`
- `docs/coverage/knowledge_pipeline_semantic_validate_20260313T034000Z-knowledge-pipeline-v2-terraform-openai.json`

## o que foi alterado
- novo modo `semantic-validate` integrado ao `knowledge_pipeline.sh`
- helper Python dedicado para a V2 com artefato auditavel por rodada
- busca semantica agora suporta `embedding_mode` explicito na trilha da V2, preservando a API antiga
- smoke semantico passou a ranquear apenas dentro do escopo da rodada (`round_scope_only`)
- documentacao V2 criada e V1 atualizada com referencia
- suite de teste minima da V2 adicionada ao gate

## o que falta
- nada bloqueante para a V2 minima
- proximo passo natural: queryset explicito por dominio para reduzir dependencia do nome do arquivo

## se precisa aprovacao
nao

## se houve erro
- nao houve erro bloqueante
- houve evidencia objetiva de limite do `mock`: o caso `20260313T033200Z-knowledge-pipeline-v2-terraform` falhou no smoke (`topk_expected_source_file_count=2/5`), por isso o caso real final foi fechado com `openai`
