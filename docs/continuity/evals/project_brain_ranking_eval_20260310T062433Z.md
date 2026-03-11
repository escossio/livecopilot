# Project Brain Ranking Offline Eval

generated_at: 20260310T062433Z
project: livecopilot
wrapper: `/lab/projects/livecopilot/scripts/project_brain_query.sh`
queries: 16

## Ranking Baseline Inspected

- type weights: decision=1.5, milestone=1.3, risk=1.2, fact_default=1.1, run_summary=1.0, chunk/other=0.8
- recency: exp(-days_since/30)
- diversity: max_share per type in top-N (semantic hits=0.6, facts merge=0.7)
- debug ranking available via `--debug-ranking`
- useful JSON fields: semantic_hits.memory_type/source_type/similarity, ranking_debug(score_*)

## Consolidated Distribution

- fact: 68
- run_summary: 12

## Observation Signals

- diversity_good: 4
- diversity_low: 12
- top3_dominated_by_fact: 13
- top3_dominated_by_run_summary: 1

## Query Results

### [continuidade_operacional] continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.53829 | 0.799661 | 1.5 | 0.990372 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.57414 | 0.625715 | 1.1 | 0.990754 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 3 | fact | fact | 0.555058 | 0.60484 | 1.1 | 0.990625 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.54449 | 0.59333 | 1.1 | 0.990634 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.510065 | 0.560992 | 1.1 | 0.999858 | STATUS.md |

### [continuidade_operacional] checkpoint da rodada (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.561412 | 0.617465 | 1.1 | 0.999857 | STATUS.md |
| 2 | fact | fact | 0.562223 | 0.616895 | 1.1 | 0.997493 | STATUS.md |
| 3 | fact | fact | 0.561439 | 0.616028 | 1.1 | 0.997482 | STATUS.md |
| 4 | fact | fact | 0.561103 | 0.615857 | 1.1 | 0.997802 | STATUS.md |
| 5 | fact | fact | 0.541616 | 0.593177 | 1.1 | 0.995635 | STATUS.md |

### [continuidade_operacional] new chat context (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.315086 | 0.344016 | 1.1 | 0.99256 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | run_summary | run_summary | 0.290756 | 0.288593 | 1.0 | 0.99256 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.245519 | 0.268014 | 1.1 | 0.992382 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | fact | fact | 0.223953 | 0.245683 | 1.1 | 0.997298 | STATUS.md |
| 5 | fact | fact | 0.224467 | 0.244986 | 1.1 | 0.992192 | STATUS.md |

### [estado_recente] ultimo closeout (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.421479 | 0.461602 | 1.1 | 0.995633 | STATUS.md |
| 2 | fact | fact | 0.418062 | 0.45786 | 1.1 | 0.995633 | STATUS.md |
| 3 | run_summary | run_summary | 0.431286 | 0.429403 | 1.0 | 0.995633 | STATUS.md |
| 4 | run_summary | run_summary | 0.428917 | 0.427044 | 1.0 | 0.995633 | STATUS.md |
| 5 | run_summary | run_summary | 0.371798 | 0.371744 | 1.0 | 0.999856 | STATUS.md |

### [estado_recente] smoke round continuity (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.559231 | 0.613611 | 1.1 | 0.997491 | STATUS.md |
| 2 | fact | fact | 0.557242 | 0.612878 | 1.1 | 0.999855 | STATUS.md |
| 3 | fact | fact | 0.557396 | 0.611787 | 1.1 | 0.9978 | STATUS.md |
| 4 | fact | fact | 0.556885 | 0.61103 | 1.1 | 0.99748 | STATUS.md |
| 5 | run_summary | run_summary | 0.59914 | 0.597822 | 1.0 | 0.9978 | STATUS.md |

### [estado_recente] embedding maintenance (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.343937 | 0.445165 | 1.3 | 0.995632 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.343937 | 0.443711 | 1.3 | 0.99238 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | fact | fact | 0.343937 | 0.443626 | 1.3 | 0.99219 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.343937 | 0.442983 | 1.3 | 0.990751 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.388192 | 0.425146 | 1.1 | 0.995632 | STATUS.md |

### [decisoes_projeto] separacao question_bank knowledge (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.62587 | 0.936438 | 1.5 | 0.997478 | STATUS.md |
| 2 | fact | fact | 0.62587 | 0.936265 | 1.5 | 0.997295 | STATUS.md |
| 3 | fact | fact | 0.625929 | 0.934792 | 1.5 | 0.995631 | STATUS.md |
| 4 | fact | fact | 0.62587 | 0.934704 | 1.5 | 0.995631 | STATUS.md |
| 5 | fact | fact | 0.62587 | 0.931818 | 1.5 | 0.992558 | STATUS.md |

### [decisoes_projeto] adotar 3 niveis de continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.622851 | 0.925277 | 1.5 | 0.990367 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.497197 | 0.541792 | 1.1 | 0.99063 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | fact | fact | 0.494533 | 0.538954 | 1.1 | 0.990749 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 4 | fact | fact | 0.482761 | 0.526056 | 1.1 | 0.99062 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.446298 | 0.486328 | 1.1 | 0.99063 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [decisoes_projeto] comando padrao operador scripts round (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.429445 | 0.467963 | 1.1 | 0.990629 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.426166 | 0.46512 | 1.1 | 0.992188 | STATUS.md |
| 3 | fact | fact | 0.409979 | 0.44762 | 1.1 | 0.992556 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | run_summary | run_summary | 0.447589 | 0.447523 | 1.0 | 0.999853 | STATUS.md |
| 5 | run_summary | run_summary | 0.447566 | 0.44658 | 1.0 | 0.997797 | STATUS.md |

### [riscos_bloqueios] risco runuser postgres peer auth (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.618719 | 0.742353 | 1.2 | 0.999852 | STATUS.md |
| 2 | fact | fact | 0.618719 | 0.740827 | 1.2 | 0.997797 | STATUS.md |
| 3 | fact | fact | 0.618719 | 0.740598 | 1.2 | 0.997488 | STATUS.md |
| 4 | fact | fact | 0.618719 | 0.740589 | 1.2 | 0.997476 | STATUS.md |
| 5 | fact | fact | 0.618719 | 0.740453 | 1.2 | 0.997293 | STATUS.md |

### [riscos_bloqueios] drift de embeddings (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.199733 | 0.29829 | 1.5 | 0.995629 | STATUS.md |
| 2 | fact | fact | 0.199733 | 0.297369 | 1.5 | 0.992555 | STATUS.md |
| 3 | fact | fact | 0.199733 | 0.297316 | 1.5 | 0.992377 | STATUS.md |
| 4 | fact | fact | 0.199733 | 0.297259 | 1.5 | 0.992187 | STATUS.md |
| 5 | fact | fact | 0.199733 | 0.296827 | 1.5 | 0.990747 | STATUS.md |

### [memoria_historica] mvp continuidade (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.558973 | 0.830381 | 1.5 | 0.990365 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.443967 | 0.574634 | 1.3 | 0.995628 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | fact | fact | 0.443967 | 0.572757 | 1.3 | 0.992377 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.443967 | 0.572647 | 1.3 | 0.992186 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.443967 | 0.571817 | 1.3 | 0.990747 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [memoria_historica] fatos canonicos project_facts (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.458067 | 0.680479 | 1.5 | 0.990364 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.360432 | 0.538284 | 1.5 | 0.995627 | STATUS.md |
| 3 | fact | fact | 0.360409 | 0.53825 | 1.5 | 0.995627 | STATUS.md |
| 4 | fact | fact | 0.360409 | 0.536492 | 1.5 | 0.992376 | STATUS.md |
| 5 | fact | fact | 0.360409 | 0.535611 | 1.5 | 0.990746 | STATUS.md |

### [tecnico_semantico] ranking debug score_final (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_run_summary', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.276303 | 0.275693 | 1.0 | 0.997794 | STATUS.md |
| 2 | run_summary | run_summary | 0.274326 | 0.274285 | 1.0 | 0.999849 | STATUS.md |
| 3 | run_summary | run_summary | 0.273282 | 0.272595 | 1.0 | 0.997485 | STATUS.md |
| 4 | run_summary | run_summary | 0.273081 | 0.272391 | 1.0 | 0.997474 | STATUS.md |
| 5 | run_summary | run_summary | 0.273094 | 0.2719 | 1.0 | 0.995627 | STATUS.md |

### [tecnico_semantico] realtime (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.3223 | 0.35189 | 1.1 | 0.992552 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | fact | fact | 0.314177 | 0.342959 | 1.1 | 0.992375 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.288877 | 0.316903 | 1.1 | 0.99729 | STATUS.md |
| 4 | fact | fact | 0.28846 | 0.316508 | 1.1 | 0.997485 | STATUS.md |
| 5 | fact | fact | 0.287504 | 0.315455 | 1.1 | 0.997473 | STATUS.md |

### [tecnico_semantico] knowledge_search ranking (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.331295 | 0.495686 | 1.5 | 0.997473 | STATUS.md |
| 2 | fact | fact | 0.331295 | 0.495595 | 1.5 | 0.997289 | STATUS.md |
| 3 | fact | fact | 0.331333 | 0.494825 | 1.5 | 0.995625 | STATUS.md |
| 4 | fact | fact | 0.331295 | 0.494769 | 1.5 | 0.995625 | STATUS.md |
| 5 | fact | fact | 0.331295 | 0.493241 | 1.5 | 0.992552 | STATUS.md |

## Calibration Hints (No Weight Change Applied)

- If `top3_dominated_by_*` is frequent: tighten diversity cap or add per-category rules.
- If `absence_of_fact_in_operational_query` appears: increase fact prior in hybrid for operational categories.
- If `run_summary_dominates_where_fact_expected` appears: reduce run_summary baseline in merge stage.
- If decision queries over-return chunks: add stronger fact_type bias for decision/risk intents.
