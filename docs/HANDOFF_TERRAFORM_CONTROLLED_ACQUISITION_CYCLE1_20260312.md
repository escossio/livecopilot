# Handoff 2026-03-12 - ciclo 1 controlado de aquisicao/recorte Terraform

## Objetivo da rodada
Preparar fontes oficiais e recorte seletivo de Terraform focado em gaps recorrentes, sem ingestao cega.

## Contexto lido
- `STATUS.md`
- `README.md`
- `INGESTION_POLICY.md`
- `docs/PROJECT_STAGE_INDEX.md`
- `docs/HANDOFF_TERRAFORM_ACQUISITION_STRATEGY_EXPANSION_20260311.md`
- `docs/HANDOFF_SEMANTIC_PERSISTENCE_AWS5_IAM_AUDIT_20260311.md`
- `docs/HANDOFF_SEMANTIC_PERSIST_DOCKER79_AUDIT_20260312.md`

## Fontes oficiais preparadas
1. Terraform core
- Repo: `https://github.com/hashicorp/terraform`
- Clone local: `data/knowledge_raw/_official_repo_clones/terraform`
- Diagnostico: alto valor para codigo/core; baixa aderencia direta para docs de usuario dos gaps desta rodada.

2. Terraform docs (fonte principal desta rodada)
- Repo: `https://github.com/hashicorp/web-unified-docs`
- Clone local: `data/knowledge_raw/_official_repo_clones/web-unified-docs`
- Caminho aderente: `content/terraform/v1.14.x/docs`
- Diagnostico: fonte mais aderente para backend/state/modules/CLI workflow.

3. Terraform AWS provider (avaliado como opcional)
- Repo: `https://github.com/hashicorp/terraform-provider-aws`
- Clone local: `data/knowledge_raw/_official_repo_clones/terraform-provider-aws`
- Diagnostico: foco majoritario em recursos do provider; nao necessario para o gap central de state/backend/locking/modulos/workflow neste ciclo.

## Recorte recomendado para ingestao seletiva
Recorte materializado em:
- `data/knowledge_raw/terraform_docs_selected`

Artefatos do recorte:
- `docs/coverage/terraform_docs_selected_files_20260312.txt`
- `docs/coverage/terraform_docs_selected_files_20260312.json`

Contagem atual do recorte:
- `43` arquivos `.md` (normalizados de `.mdx` para `.md`, sem mudar pipeline).

Blocos selecionados:
- `language/backend` (foco em `index`, `s3`, `remote`)
- `language/state` (locking, remote state, refactor/remove/import/workspaces)
- `language/modules` (configuration/sources e desenvolvimento de modulos)
- `cli/commands` (init/plan/apply/force-unlock/state/workspace)
- `cli/state` (move/recover)
- `intro/phases` (collaborate/govern para governanca/workflow)

## Limpeza da fonte para ingestao
- `web-unified-docs` usa MDX + frontmatter/componentes; qualidade estrutural boa para docs oficiais.
- Para compatibilidade com trilho canonico atual, o recorte foi normalizado para `.md`.
- Conclusao: **apto para ingestao seletiva** (nao apto para ingestao massiva cega).

## Estimativa objetiva
- Recorte recomendado imediato: `43` arquivos.
- Expansao conservadora de mesmo dominio (sem massivo): ~`60-90` arquivos, incluindo mais comandos CLI relacionados.

## Paginas oficiais aderentes (referencia)
- `https://developer.hashicorp.com/terraform/language/backend/s3`
- `https://developer.hashicorp.com/terraform/language/state/locking`
- `https://developer.hashicorp.com/terraform/language/state/remote`
- `https://developer.hashicorp.com/terraform/language/state/remote-state-data`
- `https://developer.hashicorp.com/terraform/language/modules`
- `https://developer.hashicorp.com/terraform/language/modules/configuration`
- `https://developer.hashicorp.com/terraform/cli/commands/plan`
- `https://developer.hashicorp.com/terraform/cli/commands/apply`
- `https://developer.hashicorp.com/terraform/cli/commands/state`

## Proximo comando correto (nao executado)
Observacao: para manter ingestao controlada e evitar varredura massiva de `_official_repo_clones`, usar isolamento temporario do clone bruto antes do comando canonico.

```bash
cd /lab/projects/livecopilot

HOLD_DIR="/tmp/livecopilot_official_repo_clones_hold_terraform_$(date -u +%Y%m%dT%H%M%SZ)"
mv data/knowledge_raw/_official_repo_clones "$HOLD_DIR"

scripts/ingest_knowledge.sh

mv "$HOLD_DIR" data/knowledge_raw/_official_repo_clones
```

## Restricoes respeitadas
- sem alteracao de pipeline
- sem abertura de Etapa 16
- sem ingestao massiva cega
- foco exclusivo em aquisicao/recorte seletivo Terraform
