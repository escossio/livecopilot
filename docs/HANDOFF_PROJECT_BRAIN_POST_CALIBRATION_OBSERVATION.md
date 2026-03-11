# Handoff: Project Brain Post-Calibration Observation

## Evidencias coletadas
- Baseline: `docs/continuity/evals/project_brain_ranking_eval_20260310T115836Z.json`
- Ciclo atual: `docs/continuity/evals/project_brain_ranking_eval_20260310T222844Z.json`
- Smokes:
  - `./scripts/smoke_project_brain_query_wrapper.sh` => OK
  - `./scripts/smoke_round_continuity_default.sh` => OK (`run_id=28`, `facts=4`, `chunks=5`, `missing_embedding=0`)

## Resultado da observacao
- `top5_global`: `fact=58 -> 52`, `run_summary=22 -> 28`
- `top3_dominated_by_fact`: `5 -> 6`
- `top3_dominated_by_run_summary`: `0 -> 3`
- `diversity_low`: `5 -> 9`
- `diversity_good`: `11 -> 7`
- `semantic_warning_total`: `0 -> 0`

## Conclusao
`instavel` (regressao material de diversidade confirmada em ciclo comparavel).

## Decisao recomendada
**c) reabrir calibracao conservadora** (curta, sem schema, reversivel), mantendo smokes obrigatorios e comparacao before/after.
