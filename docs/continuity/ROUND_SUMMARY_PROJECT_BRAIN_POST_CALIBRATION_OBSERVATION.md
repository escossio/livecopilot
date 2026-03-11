# Round Summary: Post-Calibration Operational Observation (Project Brain)

## Hipotese
Validar se a calibracao controlada encerrada em 2026-03-10 (max_share semantic=0.25) se sustenta por 1-2 ciclos operacionais sem regressao material, sem novo tuning.

## Baseline usado (ultima rodada validada)
- Fonte: `docs/continuity/evals/project_brain_ranking_eval_20260310T115836Z.json`
- Queries: 16
- `top5_global`: `fact=58`, `run_summary=22`
- `top3_dominated_by_fact=5`
- `top3_dominated_by_run_summary=0`
- `diversity_low=5`
- `diversity_good=11`
- `semantic_warning_total=0`

## Ciclo 1 (2026-03-10)
Evidencias:
- Offline eval: `docs/continuity/evals/project_brain_ranking_eval_20260310T161828Z.json`
- Smoke wrapper: `./scripts/smoke_project_brain_query_wrapper.sh` => OK (`semantic_warning_hybrid=null`, `semantic_warning_semantic=null`)
- Smoke continuidade: `./scripts/smoke_round_continuity_default.sh` => OK (`run_id=24`, `run_key=run_9ebcb809c65679074d9636c3`, `facts=4`, `chunks=5`, `missing_embedding=0`)

Metricas:
- `top5_global`: `fact=57`, `run_summary=23`
- `top3_dominated_by_fact=6`
- `top3_dominated_by_run_summary=1`
- `diversity_low=7`
- `diversity_good=9`
- `semantic_warning_total=0`

Delta vs baseline:
- `top3_dominated_by_fact`: `+1`
- `diversity_low`: `+2`
- `semantic_warning_total`: `0` (sem mudanca)

## Ciclo 2 (2026-03-10)
Evidencias:
- Offline eval: `docs/continuity/evals/project_brain_ranking_eval_20260310T161916Z.json`
- Smoke wrapper: `./scripts/smoke_project_brain_query_wrapper.sh` => OK (`semantic_warning_hybrid=null`, `semantic_warning_semantic=null`)
- Smoke continuidade: `./scripts/smoke_round_continuity_default.sh` => OK (`run_id=25`, `run_key=run_462fbc0c24308c928da16229`, `facts=4`, `chunks=5`, `missing_embedding=0`)

Metricas:
- `top5_global`: `fact=56`, `run_summary=24`
- `top3_dominated_by_fact=6`
- `top3_dominated_by_run_summary=1`
- `diversity_low=7`
- `diversity_good=9`
- `semantic_warning_total=0`

Delta vs baseline:
- `top3_dominated_by_fact`: `+1`
- `diversity_low`: `+2`
- `semantic_warning_total`: `0` (sem mudanca)

## Comparacao Baseline vs Ciclos
- Sinal semantico critico permaneceu estavel: `semantic_warning_total=0` em todos os cenarios.
- Houve deriva leve e consistente em diversidade/dominancia (`top3_dominated_by_fact` e `diversity_low` acima do baseline em +1/+2), sem ruptura brusca.
- Smokes operacionais ficaram verdes nos 2 ciclos.

## Conclusao
`estavel` (com deriva leve nao material nesta janela curta de 2 ciclos).

Sem acao corretiva aplicada nesta frente.
