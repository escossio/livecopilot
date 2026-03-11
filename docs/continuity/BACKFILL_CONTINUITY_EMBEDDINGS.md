# Backfill Continuity Embeddings

## O que faz
`backfill_continuity_embeddings.py` preenche embeddings em `project_memory_chunks.embedding` de forma incremental e segura.

Escopo do backfill:
- somente tabela `project_memory_chunks`
- sem alterar `project_runs` e `project_facts`

## Script
- `scripts/backfill_continuity_embeddings.py`
- `scripts/maintain_continuity_embeddings.sh` (wrapper operacional opcional)

## Pre-requisitos
- PostgreSQL acessivel para o projeto (`SEMANTIC_PG_DSN` ou `LIVECOPILOT_DB_DSN`)
- `OPENAI_API_KEY` para execucao real
- modelo de embedding (default: `SEMANTIC_EMBED_MODEL` ou `text-embedding-3-small`)

No ambiente local atual (auth `peer`), executar como `postgres`.

## Comportamento
- default: processa apenas `embedding IS NULL` (`only-missing`)
- opera com limite por execucao (`--limit`)
- opera em lotes (`--batch-size`)
- suporta `--dry-run`
- suporte de recorte:
  - `--run-id`
  - `--chunk-id`

## Uso
Dry-run:
```bash
runuser -u postgres -- ./.venv/bin/python scripts/backfill_continuity_embeddings.py \
  --project livecopilot \
  --limit 50 \
  --dry-run \
  --format json
```

Execucao real (incremental):
```bash
set -a && source /etc/livecopilot-semantic.env && set +a
runuser -u postgres -- env \
  OPENAI_API_KEY="$OPENAI_API_KEY" \
  SEMANTIC_EMBED_MODEL="${SEMANTIC_EMBED_MODEL:-text-embedding-3-small}" \
  SEMANTIC_PG_DSN="${SEMANTIC_PG_DSN:-dbname=livecopilot user=postgres}" \
  ./.venv/bin/python scripts/backfill_continuity_embeddings.py \
  --project livecopilot \
  --limit 20 \
  --batch-size 5 \
  --format text
```

Filtrar por run:
```bash
runuser -u postgres -- ./.venv/bin/python scripts/backfill_continuity_embeddings.py \
  --project livecopilot \
  --run-id 11 \
  --limit 10
```

Reprocessar incluindo ja preenchidos (uso excepcional):
```bash
runuser -u postgres -- ./.venv/bin/python scripts/backfill_continuity_embeddings.py \
  --project livecopilot \
  --include-filled \
  --limit 10
```

Wrapper de manutencao (recomendado para rotina):
```bash
./scripts/maintain_continuity_embeddings.sh --limit 200 --batch-size 10
```

Apenas preflight (sem escrita):
```bash
./scripts/maintain_continuity_embeddings.sh --dry-run-only
```

## Observabilidade
Retorna contadores claros:
- `total_candidates`
- `selected_by_limit`
- `processed`
- `updated`
- `failed`
- `failures[]` (amostra de erros)

## Cuidados operacionais
- sempre comecar por `--dry-run`
- usar limites pequenos no inicio
- manter `only-missing` no dia a dia para evitar custo desnecessario
- se `OPENAI_API_KEY` estiver ausente, a execucao real falha com erro claro e sem corromper dados

## Rotina operacional recomendada
1. Preflight diario/semanal:
```bash
./scripts/maintain_continuity_embeddings.sh --dry-run-only
```
2. Se houver faltantes (`total_candidates > 0`), executar preenchimento:
```bash
./scripts/maintain_continuity_embeddings.sh --limit 200 --batch-size 10
```
3. Confirmar SQL final:
```bash
runuser -u postgres -- psql -d livecopilot -c \
\"SELECT COUNT(*) FILTER (WHERE embedding IS NULL) AS missing_embedding FROM project_memory_chunks;\"
```

## Integracao opcional no closeout
Para reduzir drift, a manutencao pode rodar no fim do `run_round_closeout.sh`:

```bash
./scripts/run_round_closeout.sh \
  --enable-continuity-hook \
  --enable-embedding-maintenance \
  --embedding-maintenance-limit 200 \
  --embedding-maintenance-batch-size 10 \
  ...demais argumentos...
```

No fluxo padrao (`scripts/round`), as mesmas flags estao disponiveis e sao repassadas ao closeout.

## Estado validado nesta rodada
- antes da conclusao: `with_embedding=12`, `missing_embedding=18`
- apos conclusao: `with_embedding=30`, `missing_embedding=0`
