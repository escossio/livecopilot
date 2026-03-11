# Handoff: Post-Calibration Observation (Contract-Anchored)

## Evidencias coletadas
- Baseline validado: `docs/continuity/evals/project_brain_ranking_eval_20260310T115836Z.json`
- Ciclo 1: `docs/continuity/evals/project_brain_ranking_eval_20260310T214530Z.json`
- Ciclo 2: `docs/continuity/evals/project_brain_ranking_eval_20260310T214606Z.json`
- Smokes verdes nos 2 ciclos:
  - `./scripts/smoke_project_brain_query_wrapper.sh`
  - `./scripts/smoke_round_continuity_default.sh`

## Conclusao
- `semantic_warning_total` permaneceu `0`.
- Operacao permaneceu funcional (smokes OK).
- Houve regressao material de diversidade na janela observada:
  - `diversity_low`: `5 -> 7 -> 9`
  - `top3_dominated_by_fact`: `5 -> 6 -> 6`

Veredito da frente: `instavel` para os criterios de estabilidade definidos.

## Decisao recomendada
`c) reabrir calibracao, se necessario`.

Escopo recomendado da proxima frente (sem aplicar automaticamente):
- recalibracao conservadora, com experimento before/after curto,
- foco em recuperar diversidade sem degradar `semantic_warning_total=0`,
- sem mudanca de schema e sem tuning amplo.
