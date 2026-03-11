# Round Summary: Subetapa 8.6 - Observacao Curta de Continuidade

Data: 2026-03-11

## Objetivo da rodada
Fechar a subetapa 8.6 com 1 ciclo curto e comparavel para decidir objetivamente: manter estado atual do ranking ou propor 1 ajuste minimo adicional.

## Baseline explicito da 8.6
- Baseline usado: `docs/continuity/evals/project_brain_ranking_eval_20260310T223343Z.json`
- Justificativa: ultimo ciclo offline comparavel consolidado no fechamento da trilha de recalibracao conservadora antes desta observacao curta.

Metricas baseline:
- `top5_global`: `fact=52`, `run_summary=28`
- `top3_dominated_by_fact`: `6`
- `top3_dominated_by_run_summary`: `3`
- `diversity_low`: `9`
- `diversity_good`: `7`
- `semantic_warning_total`: `0`

## Ciclo curto executado (8.6)
- Offline eval atual:
  - `docs/continuity/evals/project_brain_ranking_eval_20260311T013958Z.json`
- Smokes obrigatorios:
  - `./scripts/smoke_project_brain_query_wrapper.sh` => OK
  - `./scripts/smoke_round_continuity_default.sh` => OK (`run_id=36`, `missing_embedding=0`)

Metricas ciclo atual:
- `top5_global`: `fact=52`, `run_summary=28`
- `top3_dominated_by_fact`: `6`
- `top3_dominated_by_run_summary`: `3`
- `diversity_low`: `9`
- `diversity_good`: `7`
- `semantic_warning_total`: `0`

## Comparacao baseline vs ciclo atual
- `top5_global`: sem alteracao
- `top3_dominated_by_fact`: `delta=0`
- `top3_dominated_by_run_summary`: `delta=0`
- `diversity_low`: `delta=0`
- `diversity_good`: `delta=0`
- `semantic_warning_total`: `delta=0`

## Decisao objetiva
- **Manter estado atual do ranking**.
- Nao ha evidencia de regressao material nem sinal tecnico para ajuste adicional nesta rodada.
- Nao aplicar tuning adicional agora.

## Encerramento da subetapa
- `8.6`: **concluida**.
- Etapa 8 pode ser considerada fechada no escopo atual.

## Observacao operacional
- Na execucao do eval, houve ruído inicial por log JSON de `knowledge_gap_logger` no stdout; ciclo foi rerodado com `LOG_LEVEL=ERROR` para manter parse comparavel, sem alterar codigo funcional.
