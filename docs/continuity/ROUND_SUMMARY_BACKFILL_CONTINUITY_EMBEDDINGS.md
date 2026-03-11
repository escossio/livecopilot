# ROUND SUMMARY - BACKFILL CONTINUITY EMBEDDINGS

## status final
success

## objetivo
Ativar camada semantica real do Project Brain preenchendo embeddings em `project_memory_chunks` e validando consultas `semantic`/`hybrid` com hits reais.

## entrega tecnica
- script novo: `scripts/backfill_continuity_embeddings.py`
- documentacao nova: `docs/continuity/BACKFILL_CONTINUITY_EMBEDDINGS.md`
- checkpoint em `STATUS.md`

## comportamento implementado
- busca candidatos em `project_memory_chunks` com filtro por projeto
- default incremental: apenas `embedding IS NULL`
- suporte a `--limit`, `--batch-size`, `--dry-run`
- suporte a recorte por `--run-id` e `--chunk-id`
- suporte a reprocessamento opcional com `--include-filled`
- em execucao real:
  - gera embedding por `content`
  - persiste em `embedding`
  - registra contadores de processados/atualizados/falhas

## testes minimos obrigatorios
1. dry-run:
```bash
runuser -u postgres -- ./.venv/bin/python scripts/backfill_continuity_embeddings.py \
  --project livecopilot --limit 50 --dry-run --format json
```
Resultado: `total_candidates=30`, `selected_by_limit=30`, sem escrita.

2. execucao real (amostra):
```bash
set -a && source /etc/livecopilot-semantic.env && set +a
runuser -u postgres -- env OPENAI_API_KEY="$OPENAI_API_KEY" \
  SEMANTIC_EMBED_MODEL="${SEMANTIC_EMBED_MODEL:-text-embedding-3-small}" \
  SEMANTIC_PG_DSN="${SEMANTIC_PG_DSN:-dbname=livecopilot user=postgres}" \
  ./.venv/bin/python scripts/backfill_continuity_embeddings.py \
  --project livecopilot --limit 12 --batch-size 4 --format json
```
Resultado: `processed=12`, `updated=12`, `failed=0`.

3. validacao SQL pos-backfill:
- antes: `with_embedding=0`, `missing_embedding=30`
- depois: `with_embedding=12`, `missing_embedding=18`

4. `project_brain_query.py` em semantic:
```bash
... scripts/project_brain_query.py --query "continuidade" --mode semantic --memory-limit 5 --format json
```
Resultado: `semantic_hits` com hits reais (nao vazio), `semantic_warning=null`.

5. `project_brain_query.py` em hybrid:
```bash
... scripts/project_brain_query.py --query "continuidade" --mode hybrid --facts-limit 6 --memory-limit 5 --format text
```
Resultado: facts/runs + bloco `semantic hits` preenchido.

6. comprovacao semantic_hits nao vazio:
- confirmado no modo semantic e hybrid apos backfill.

## limitacoes atuais
- backfill foi parcial por limite (12 de 30 faltantes) para manter execucao incremental segura.
- consulta semantic ainda depende de `OPENAI_API_KEY` para embedding da query.
