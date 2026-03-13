# Round Plan Prefix Mode

## Motivacao
`round_plan.sh` unifica a pre-visualizacao operacional de rodada por prefixo em um unico comando.
Ele consolida:
- ingestao em `--dry-run`
- persistencia semantica em `--list-targets`

Objetivo: mostrar o escopo completo da rodada antes da execucao real, sem alterar estado.

## Comando

```bash
scripts/round_plan.sh [--source-prefix PREFIX ...] [--strict-source-prefix] [--json]
```

## Como funciona
Internamente o comando executa:
1. `python -m app.services.knowledge_ingest ... --dry-run`
2. `python -m app.services.knowledge_ingest ... --semantic-persist --list-targets`

Depois consolida em um plano unico com:
- `plan_mode`
- `source_prefixes` normalizados
- bloco `ingest_dry_run`
- bloco `semantic_list_targets`
- `totals`
- `divergence`

## Exemplo (prefixo unico)

```bash
./scripts/round_plan.sh \
  --source-prefix continuity_docs_selected/
```

## Exemplo (multiplos prefixos)

```bash
./scripts/round_plan.sh \
  --source-prefix continuity_docs_selected/ \
  --source-prefix terraform_docs_selected_incremental/
```

## Exemplo (JSON consolidado)

```bash
./scripts/round_plan.sh \
  --source-prefix continuity_docs_selected/ \
  --json
```

## Diferenca entre plano e execucao real
- plano (`round_plan.sh`): somente pre-visualizacao, sem ingestao real e sem persistencia real
- execucao real: usar `scripts/ingest_knowledge.sh` e/ou fluxo `--semantic-persist` sem `--list-targets`

## Troubleshooting
- erro `strict-source-prefix habilitado...`:
  - causa: nenhum alvo resolvido para os prefixos informados com `--strict-source-prefix`
  - acao: ajustar prefixo ou remover strict para modo diagnostico
- saida com `payload_kind=semantic_noop_summary`:
  - causa: persistencia semantica nao encontrou `source_files` para o recorte
  - acao: validar se os arquivos ja existem no estado canonico
- divergencia entre ingestao e persistencia (`divergence.has_divergence=true`):
  - causa comum: diferenca entre arquivos detectados no raw e source_files materializados no estado
  - acao: revisar amostras `ingest_only_sample` e `semantic_only_sample`
