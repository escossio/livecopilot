# Round Summary: Post-Calibration Operational Observation (Contract-Anchored)

## Referencial governante da rodada
- Contrato do projeto: `docs/PROJECT_CONTRACT.md`
- Missao aplicada nesta frente: preservar estabilidade operacional do motor de apoio (Project Brain) sem reabrir tuning por ansiedade e sem perder aderencia ao fluxo principal do produto.

## Hipotese
Com `max_share semantic=0.25` mantido, o ranking do Project Brain deve permanecer operacionalmente estavel em 1-2 ciclos adicionais, sem regressao material em:
- `top3_dominated_by_fact`
- `diversity_low`
- `semantic_warning_total`

## Artefatos revisados antes da execucao
- `docs/PROJECT_CONTRACT.md`
- `STATUS.md`
- `docs/continuity/HANDOFF_PROJECT_BRAIN_RANKING_CALIBRATION_CONTROLLED.md`
- `docs/continuity/PROJECT_BRAIN_RANKING_OFFLINE_EVAL.md`
- evidencias before/after da calibracao controlada:
  - `docs/continuity/evals/project_brain_ranking_eval_20260310T115749Z.json` (before)
  - `docs/continuity/evals/project_brain_ranking_eval_20260310T115836Z.json` (after)

## Baseline operacional usado (ultima rodada validada)
Fonte: `docs/continuity/evals/project_brain_ranking_eval_20260310T115836Z.json`
- `top5_global`: `fact=58`, `run_summary=22`
- `top3_dominated_by_fact=5`
- `top3_dominated_by_run_summary=0`
- `diversity_low=5`
- `diversity_good=11`
- `semantic_warning_total=0`

## Ciclo 1
Evidencias:
- offline eval: `docs/continuity/evals/project_brain_ranking_eval_20260310T214530Z.json`
- smoke wrapper: `./scripts/smoke_project_brain_query_wrapper.sh` => OK (`semantic_warning_hybrid=null`, `semantic_warning_semantic=null`)
- smoke continuidade: `./scripts/smoke_round_continuity_default.sh` => OK (`run_id=26`, `run_key=run_b6d21e4ba0b8d76ae614661b`, `facts=4`, `chunks=5`, `missing_embedding=0`)

Metricas:
- `top5_global`: `fact=54`, `run_summary=26`
- `top3_dominated_by_fact=6`
- `top3_dominated_by_run_summary=1`
- `diversity_low=7`
- `diversity_good=9`
- `semantic_warning_total=0`

Delta vs baseline:
- `top3_dominated_by_fact`: `+1`
- `diversity_low`: `+2`
- `semantic_warning_total`: `0` (sem mudanca)

## Ciclo 2
Evidencias:
- offline eval: `docs/continuity/evals/project_brain_ranking_eval_20260310T214606Z.json`
- smoke wrapper: `./scripts/smoke_project_brain_query_wrapper.sh` => OK (`semantic_warning_hybrid=null`, `semantic_warning_semantic=null`)
- smoke continuidade: `./scripts/smoke_round_continuity_default.sh` => OK (`run_id=27`, `run_key=run_b12404b369752d6e0d9163f3`, `facts=4`, `chunks=5`, `missing_embedding=0`)

Metricas:
- `top5_global`: `fact=52`, `run_summary=28`
- `top3_dominated_by_fact=6`
- `top3_dominated_by_run_summary=3`
- `diversity_low=9`
- `diversity_good=7`
- `semantic_warning_total=0`

Delta vs baseline:
- `top3_dominated_by_fact`: `+1`
- `diversity_low`: `+4`
- `semantic_warning_total`: `0` (sem mudanca)

## Comparacao Baseline vs Ciclos
- Smokes operacionais permaneceram verdes nos 2 ciclos.
- `semantic_warning_total` permaneceu estavel em `0`.
- Houve deriva progressiva e piora de diversidade:
  - `diversity_low`: `5 -> 7 -> 9`
  - `top3_dominated_by_fact`: `5 -> 6 -> 6`
  - `top3_dominated_by_run_summary`: `0 -> 1 -> 3`
- Sinal objetivo: regressao material em diversidade (`diversity_low`) na janela observada.

## Conclusao
`instavel` para os criterios desta frente (regressao material de diversidade), com operacao ainda funcional (smokes OK e sem warning semantico).

Sem tuning aplicado nesta rodada (diagnostico apenas).

## Proposta (nao aplicada)
Abrir frente dedicada de recalibracao conservadora (sem schema), focada em reduzir `diversity_low` sem perder `semantic_warning=0`, com candidatos minimos:
1. revisar cap de diversidade por modo (`semantic` vs `hybrid`) em vez de ajuste global unico;
2. testar limite mais equilibrado para evitar subida de `run_summary` no top3;
3. validar em before/after com a mesma bateria de 16 queries antes de promover mudanca.
