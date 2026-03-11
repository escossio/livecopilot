# Handoff: Project Brain Ranking Calibration (Controlled)

## Baseline
- Avaliacao offline (16 queries / 6 categorias):
  - `docs/continuity/evals/project_brain_ranking_eval_20260310T115749Z.json`
- Indicadores baseline:
  - `top5_global`: `fact=68`, `run_summary=12`
  - `top3_dominated_by_fact=13`
  - `diversity_low=12`
  - `diversity_good=4`

## Mudanca aplicada
- Ajuste unico, conservador e reversivel:
  - `semantic_hits` diversity cap `max_share`: `0.6 -> 0.25`
- Sem alteracao de schema, sem mudanca no contrato do payload.

## Before / After
- Before:
  - `docs/continuity/evals/project_brain_ranking_eval_20260310T115749Z.json`
- After:
  - `docs/continuity/evals/project_brain_ranking_eval_20260310T115836Z.json`
- Delta principal:
  - `top5_global fact`: `68 -> 58`
  - `top5_global run_summary`: `12 -> 22`
  - `top3_dominated_by_fact`: `13 -> 5`
  - `diversity_low`: `12 -> 5`
  - `diversity_good`: `4 -> 11`

## Decisao
- Manter ajuste `max_share semantic=0.25` ativo.
- Nao seguir tuning nesta rodada.

## Proximos passos possiveis
1. Observar 1-2 ciclos adicionais com a mesma bateria offline.
2. Testar calibracao por categoria (`semantic` vs `hybrid`) se houver necessidade.
