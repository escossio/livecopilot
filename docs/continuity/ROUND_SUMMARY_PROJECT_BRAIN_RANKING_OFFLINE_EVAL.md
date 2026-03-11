# Round Summary: Project Brain Ranking Offline Eval

## Objetivo
Criar medicao offline util para qualidade de ranking do Project Brain, sem alterar pesos nesta rodada.

## Entregue
- Script novo:
  - `scripts/eval_project_brain_ranking_offline.py`
- Documento operacional:
  - `docs/continuity/PROJECT_BRAIN_RANKING_OFFLINE_EVAL.md`
- Bateria canonica de queries:
  - `docs/continuity/examples/project_brain_ranking_eval_queries.json`
- Evidencias geradas:
  - `docs/continuity/evals/latest_project_brain_ranking_eval.json`
  - `docs/continuity/evals/latest_project_brain_ranking_eval.md`

## Metodo
- Executa 16 queries (semantic/hybrid) via `scripts/project_brain_query.sh`.
- Forca `--debug-ranking` para capturar componentes de score.
- Coleta top 5 semantic hits por query.
- Agrega distribuicao de `memory_type` e sinais automaticos de qualidade.

## Achados desta rodada
- `semantic_warning`: 0 casos.
- Distribuicao global no top 5 agregado:
  - `fact`: 68
  - `run_summary`: 12
- Sinais:
  - `top3_dominated_by_fact`: 13
  - `top3_dominated_by_run_summary`: 1
  - `diversity_low`: 12
  - `diversity_good`: 4

Leitura inicial:
- ranking esta estavel e funcional, com forte prevalencia de `fact` no top.
- diversidade ficou baixa em boa parte das queries; calibracao de diversidade por categoria e candidato claro para proxima rodada.

## Validacao
- `./.venv/bin/python -m py_compile scripts/eval_project_brain_ranking_offline.py` => OK
- `./scripts/eval_project_brain_ranking_offline.py --project livecopilot` => OK
- `./scripts/smoke_project_brain_query_wrapper.sh` => OK

## Nao alterado nesta rodada
- pesos do ranking
- schema/tabelas PostgreSQL
- fluxo operacional de closeout/continuidade
