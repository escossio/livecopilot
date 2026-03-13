# HANDOFF - Terraform Incremental Round 2 Diagnosis (20260312T164346Z)

## Status final
- Diagnostico por query residual concluido.
- Round 2 **nao foi executada nesta chamada**; ficou pronta para execucao com recorte minimo orientado por evidencia.

## O que foi executado
1. Leitura de AFTER/COMPARE da rodada incremental 1.
2. Extracao das 4 queries que permaneceram `partial` com top-k/top1.
3. Classificacao de causa por query.
4. Validacao de docs oficiais candidatos no clone local e ausencia no corpus chunked.
5. Definicao de recorte minimo de round 2.
6. Fechamento com scanner UTF-8.

## Queries partial remanescentes
- `terraform force unlock`
- `terraform modules best practices`
- `terraform module sources`
- `terraform init plan apply workflow`

## Diagnostico por query
- `terraform force unlock`
  - categoria: `query_ja_melhorou_mas_ainda_nao_cruza_threshold`
  - leitura: top1 ja incremental; ganho de avg sem mudanca de classe.
- `terraform modules best practices`
  - categoria: `falta_documento_oficial_especifico`
  - candidato ausente: `content/terraform/v1.14.x/docs/language/style.mdx`
- `terraform module sources`
  - categoria: `falta_documento_oficial_especifico`
  - candidato ausente: `content/terraform/v1.14.x/docs/language/block/module.mdx`
- `terraform init plan apply workflow`
  - categoria: `falta_documento_oficial_especifico`
  - candidatos ausentes: `content/terraform/v1.14.x/docs/cli/run/index.mdx`, `content/terraform/v1.14.x/docs/intro/core-workflow.mdx`, `content/terraform/v1.14.x/docs/cli/commands/index.mdx`

## Decisao
- Executar Terraform incremental round 2.
- Justificativa: 3/4 partials apontam ausencia objetiva de documentos oficiais especificos diretamente relacionados as queries.

## Proposta minima round 2
- `--semantic-max-chunks-per-doc=32`
- Manter para refresh seletivo (7 docs): `force-unlock`, `locking`, `plan`, `init`, `apply`, `modules/sources`, `modules/develop/structure`.
- Adicionar 5 docs novos (materializar + ingerir):
  - `content/terraform/v1.14.x/docs/language/style.mdx`
  - `content/terraform/v1.14.x/docs/language/block/module.mdx`
  - `content/terraform/v1.14.x/docs/cli/run/index.mdx`
  - `content/terraform/v1.14.x/docs/intro/core-workflow.mdx`
  - `content/terraform/v1.14.x/docs/cli/commands/index.mdx`
- Nota operacional: materializar `.mdx -> .md` no diretorio incremental round 2 por compatibilidade do parser.

## Artefatos
- `docs/coverage/terraform_incremental_partial_queries_after_20260312T164346Z.json`
- `docs/coverage/terraform_incremental_round2_query_diagnosis_20260312T164346Z.json`
- `docs/coverage/terraform_incremental_round2_missing_docs_validation_20260312T164346Z.json`
- `docs/coverage/terraform_incremental_round2_docs_selected_proposed_20260312T164346Z.json`
- `docs/coverage/terraform_incremental_round2_docs_selected_proposed_20260312T164346Z.txt`
- `docs/coverage/utf8_hygiene_scan_validation_terraform_incremental_round2_diagnosis_closeout_20260312T164346Z.json`
- `docs/coverage/utf8_hygiene_scan_validation_terraform_incremental_round2_diagnosis_closeout.json`

## UTF-8 closeout
- `total_chunks_scanned=1072`
- `bad_chunks_count=0`
- `affected_source_files_count=0`

## Proximo passo recomendado
- Rodar a round 2 operacional usando o recorte proposto e reexecutar a bateria before/after Terraform para medir delta em `partial` e `priority_score`.
