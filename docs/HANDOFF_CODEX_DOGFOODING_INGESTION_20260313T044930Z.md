# Handoff: Codex Dogfooding Ingestion 2026-03-13

## Objetivo
Executar uma rodada controlada de ingestao real usando documentacao do ecossistema Codex como caso de uso pratico do proprio pipeline de conhecimento.

## Repositorio escolhido
- repo:
  - `https://github.com/openai/codex`
- motivo:
  - repositorio oficial do Codex CLI
  - documentacao operacional concentrada e relevante
  - escopo pequeno o bastante para uma rodada auditavel

## Recorte materializado
- clone local:
  - `_official_repo_clones/codex`
- prefixo canonico:
  - `codex_docs_selected/`
- destino:
  - `data/knowledge_raw/codex_docs_selected/`
- artefato de selecao:
  - `docs/coverage/codex_dogfooding_selection_20260313T034900Z.json`

Arquivos incluidos:
- `README.md`
- `docs/getting-started.md`
- `docs/install.md`
- `docs/authentication.md`
- `docs/config.md`
- `docs/example-config.md`
- `docs/sandbox.md`
- `docs/execpolicy.md`
- `docs/exec.md`
- `docs/skills.md`
- `docs/agents_md.md`
- `docs/slash_commands.md`
- `shell-tool-mcp/README.md`

## Rodadas executadas

### Execucao preliminar
- round id:
  - `20260313T043813Z-codex-dogfooding`
- utilidade:
  - confirmou ingestao e persistencia reais
  - revelou um limite do V1 para prefixo novo
- achado:
  - `semantic_limit_docs=1`
  - causa:
    - o `plan` inicial ainda nao tinha `source_file` resolvido no estado, entao o auto-limit do `run` caiu para `1`

### Execucao final
- round id:
  - `20260313T044239Z-codex-dogfooding-final`
- comandos:
  - `./scripts/knowledge_pipeline.sh --mode plan --round-id 20260313T044239Z-codex-dogfooding-final --source-prefix codex_docs_selected/`
  - `./scripts/knowledge_pipeline.sh --mode run --round-id 20260313T044239Z-codex-dogfooding-final --source-prefix codex_docs_selected/ --semantic-embedding-mode openai`
  - `./scripts/knowledge_pipeline.sh --mode validate --round-id 20260313T044239Z-codex-dogfooding-final --source-prefix codex_docs_selected/`
  - `./scripts/knowledge_pipeline.sh --mode semantic-validate --round-id 20260313T044239Z-codex-dogfooding-final --source-prefix codex_docs_selected/ --semantic-queryset-file docs/coverage/codex_dogfooding_queryset_20260313T043813Z.json`

## Artefatos relevantes
- `docs/coverage/codex_dogfooding_queryset_20260313T043813Z.json`
- `docs/coverage/knowledge_pipeline_plan_20260313T044239Z-codex-dogfooding-final.json`
- `docs/coverage/knowledge_pipeline_run_20260313T044239Z-codex-dogfooding-final.json`
- `docs/coverage/knowledge_pipeline_validate_20260313T044239Z-codex-dogfooding-final.json`
- `docs/coverage/knowledge_pipeline_validate_utf8_20260313T044239Z-codex-dogfooding-final.json`
- `docs/coverage/knowledge_pipeline_semantic_validate_20260313T044239Z-codex-dogfooding-final.json`

## Resultado operacional
- `plan`:
  - `ingest_total_found=13`
  - `semantic_total_source_files=13`
  - `has_divergence=false`
- `run`:
  - `documents_selected=13`
  - `documents_processed=13`
  - `chunks_persisted=26`
  - `embedding_mode_used=openai`
- `validate`:
  - `validation_passed=true`
  - `resolved_sources_total=13`
  - `utf8_scan_clean=true`
  - `bad_chunks_count=0`

## Queries reais usadas
- `how to install codex cli with npm or homebrew`
- `codex cli authentication sign in with chatgpt or api key`
- `codex config toml basic advanced configuration reference`
- `codex sandbox approvals workspace write read only danger full access`
- `codex execution policy approvals rules`
- `codex slash commands and skills documentation`

## Resultado semantico
- `semantic_smoke_passed=true`
- `total_queries=6`
- `top1_expected_source_file_count=5`
- `topk_expected_source_file_count=6`

Acertos observados:
- instalacao:
  - `top1=codex_docs_selected/README.md`
- autenticacao:
  - `top1=codex_docs_selected/docs/authentication.md`
- configuracao:
  - `top1=codex_docs_selected/docs/config.md`
- sandbox:
  - `top1=codex_docs_selected/docs/sandbox.md`
- slash commands:
  - `top1=codex_docs_selected/docs/slash_commands.md`
- execution policy:
  - `top1=codex_docs_selected/docs/sandbox.md`
  - `expected_source_file=codex_docs_selected/docs/execpolicy.md` apareceu em `top2`

## Conclusao
- a rodada foi util como dogfooding real
- o recorte pequeno do repo oficial do Codex CLI respondeu bem a perguntas operacionais de uso
- a busca semantica minima ficou auditavelmente recuperavel dentro do escopo da rodada

## Limitacoes
- o escopo e `round_scope_only`
- parte dos docs selecionados so aponta para documentacao remota oficial
- o V1 ainda merece endurecimento no auto-limit para primeira rodada de prefixo novo

## Proximo passo
- endurecer o `semantic_limit_docs` automatico para prefixos novos e repetir o mesmo padrao de dogfooding com um segundo repo oficial do ecossistema Codex que complemente a camada operacional atual
