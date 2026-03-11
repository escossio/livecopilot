# Round Summary: Post-Calibration Operational Observation

## Hipotese da rodada
Confirmar com 1 ciclo comparavel se o estado pos-calibracao (`max_share semantic=0.25`) ainda permanece estavel ou se a regressao material de diversidade persiste.

## Baseline usado nesta rodada
- Fonte baseline validada: `docs/continuity/evals/project_brain_ranking_eval_20260310T115836Z.json`
- `top5_global`: `fact=58`, `run_summary=22`
- `top3_dominated_by_fact=5`
- `top3_dominated_by_run_summary=0`
- `diversity_low=5`
- `diversity_good=11`
- `semantic_warning_total=0`

## Ciclo executado (1)
Evidencias:
- Offline eval: `docs/continuity/evals/project_brain_ranking_eval_20260310T222844Z.json`
- Smoke wrapper: `./scripts/smoke_project_brain_query_wrapper.sh` => OK
- Smoke continuidade: `./scripts/smoke_round_continuity_default.sh` => OK (`run_id=28`, `missing_embedding=0`)

Metricas do ciclo:
- `top5_global`: `fact=52`, `run_summary=28`
- `top3_dominated_by_fact=6`
- `top3_dominated_by_run_summary=3`
- `diversity_low=9`
- `diversity_good=7`
- `semantic_warning_total=0`

Comparacao vs baseline:
- `top3_dominated_by_fact`: `+1`
- `top3_dominated_by_run_summary`: `+3`
- `diversity_low`: `+4`
- `diversity_good`: `-4`
- `semantic_warning_total`: sem alteracao (`0`)

## Conclusao
`instavel` para o gate desta frente, por regressao material de diversidade/dominancia, com operacao ainda funcional (smokes verdes).

## Decisao recomendada
Reabrir calibracao conservadora, minima e reversivel (sem schema), com before/after curto e comparavel, antes de seguir para bootstrap/contexto inicial.
