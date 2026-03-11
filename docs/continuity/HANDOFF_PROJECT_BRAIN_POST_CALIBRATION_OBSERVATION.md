# Handoff: Project Brain Post-Calibration Observation

## Evidencias coletadas
- Baseline validado:
  - `docs/continuity/evals/project_brain_ranking_eval_20260310T115836Z.json`
- Ciclo 1:
  - `docs/continuity/evals/project_brain_ranking_eval_20260310T161828Z.json`
  - smoke wrapper OK
  - smoke continuidade OK (`run_id=24`)
- Ciclo 2:
  - `docs/continuity/evals/project_brain_ranking_eval_20260310T161916Z.json`
  - smoke wrapper OK
  - smoke continuidade OK (`run_id=25`)
- Relatorio desta frente:
  - `docs/continuity/ROUND_SUMMARY_PROJECT_BRAIN_POST_CALIBRATION_OBSERVATION.md`

## Conclusao
- Ajuste calibrado (`max_share semantic=0.25`) sustentou operacao sem regressao material.
- `semantic_warning_total` permaneceu `0` em baseline + 2 ciclos.
- Variacao leve em `top3_dominated_by_fact` e `diversity_low` (+1/+2 vs baseline), estavel entre os dois ciclos.

## Decisao recomendada
- **b) seguir para proxima acao inteligente**

## Nota de risco curta
- Se `top3_dominated_by_fact` subir acima de `+2` por 2+ rodadas seguidas, reabrir diagnostico de calibracao (sem aplicar tuning automatico).
