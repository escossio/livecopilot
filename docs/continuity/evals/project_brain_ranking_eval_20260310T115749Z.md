# Project Brain Ranking Offline Eval

generated_at: 20260310T115749Z
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
| 1 | fact | fact | 0.538313 | 0.793549 | 1.5 | 0.982761 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.574161 | 0.620929 | 1.1 | 0.98314 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 3 | fact | fact | 0.555044 | 0.600176 | 1.1 | 0.983012 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.54452 | 0.588802 | 1.1 | 0.983021 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.510075 | 0.556692 | 1.1 | 0.992174 | STATUS.md |

### [continuidade_operacional] checkpoint da rodada (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.561412 | 0.61272 | 1.1 | 0.992173 | STATUS.md |
| 2 | fact | fact | 0.562223 | 0.612154 | 1.1 | 0.989827 | STATUS.md |
| 3 | fact | fact | 0.561439 | 0.611293 | 1.1 | 0.989816 | STATUS.md |
| 4 | fact | fact | 0.561103 | 0.611124 | 1.1 | 0.990134 | STATUS.md |
| 5 | fact | fact | 0.541616 | 0.588618 | 1.1 | 0.987983 | STATUS.md |

### [continuidade_operacional] new chat context (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.315086 | 0.341372 | 1.1 | 0.984932 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | run_summary | run_summary | 0.290756 | 0.286375 | 1.0 | 0.984932 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.245519 | 0.265954 | 1.1 | 0.984756 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | fact | fact | 0.223953 | 0.243794 | 1.1 | 0.989633 | STATUS.md |
| 5 | fact | fact | 0.224467 | 0.243103 | 1.1 | 0.984567 | STATUS.md |

### [estado_recente] ultimo closeout (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.421479 | 0.458055 | 1.1 | 0.987982 | STATUS.md |
| 2 | fact | fact | 0.418062 | 0.454341 | 1.1 | 0.987982 | STATUS.md |
| 3 | run_summary | run_summary | 0.431286 | 0.426103 | 1.0 | 0.987982 | STATUS.md |
| 4 | run_summary | run_summary | 0.428917 | 0.423762 | 1.0 | 0.987982 | STATUS.md |
| 5 | run_summary | run_summary | 0.371798 | 0.368888 | 1.0 | 0.992172 | STATUS.md |

### [estado_recente] smoke round continuity (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.559111 | 0.608764 | 1.1 | 0.989825 | STATUS.md |
| 2 | fact | fact | 0.557123 | 0.608038 | 1.1 | 0.992171 | STATUS.md |
| 3 | fact | fact | 0.557273 | 0.606951 | 1.1 | 0.990132 | STATUS.md |
| 4 | fact | fact | 0.556765 | 0.606203 | 1.1 | 0.989814 | STATUS.md |
| 5 | run_summary | run_summary | 0.59906 | 0.593148 | 1.0 | 0.990132 | STATUS.md |

### [estado_recente] embedding maintenance (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.343893 | 0.441687 | 1.3 | 0.98798 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.343893 | 0.440245 | 1.3 | 0.984754 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | fact | fact | 0.343893 | 0.44016 | 1.3 | 0.984565 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.343893 | 0.439522 | 1.3 | 0.983137 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.388052 | 0.421727 | 1.1 | 0.98798 | STATUS.md |

### [decisoes_projeto] separacao question_bank knowledge (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.62587 | 0.929241 | 1.5 | 0.989813 | STATUS.md |
| 2 | fact | fact | 0.62587 | 0.92907 | 1.5 | 0.989631 | STATUS.md |
| 3 | fact | fact | 0.625929 | 0.927608 | 1.5 | 0.98798 | STATUS.md |
| 4 | fact | fact | 0.62587 | 0.92752 | 1.5 | 0.98798 | STATUS.md |
| 5 | fact | fact | 0.62587 | 0.924657 | 1.5 | 0.98493 | STATUS.md |

### [decisoes_projeto] adotar 3 niveis de continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.622851 | 0.918166 | 1.5 | 0.982756 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.497197 | 0.537628 | 1.1 | 0.983017 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | fact | fact | 0.494533 | 0.534812 | 1.1 | 0.983135 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 4 | fact | fact | 0.482761 | 0.522013 | 1.1 | 0.983007 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.446298 | 0.48259 | 1.1 | 0.983017 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [decisoes_projeto] comando padrao operador scripts round (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.429411 | 0.46433 | 1.1 | 0.983016 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.426096 | 0.46147 | 1.1 | 0.984563 | STATUS.md |
| 3 | fact | fact | 0.409946 | 0.444144 | 1.1 | 0.984929 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | run_summary | run_summary | 0.447533 | 0.444028 | 1.0 | 0.992169 | STATUS.md |
| 5 | run_summary | run_summary | 0.447509 | 0.443092 | 1.0 | 0.990129 | STATUS.md |

### [riscos_bloqueios] risco runuser postgres peer auth (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.618719 | 0.736648 | 1.2 | 0.992168 | STATUS.md |
| 2 | fact | fact | 0.618719 | 0.735134 | 1.2 | 0.990129 | STATUS.md |
| 3 | fact | fact | 0.618719 | 0.734906 | 1.2 | 0.989822 | STATUS.md |
| 4 | fact | fact | 0.618719 | 0.734898 | 1.2 | 0.989811 | STATUS.md |
| 5 | fact | fact | 0.618719 | 0.734763 | 1.2 | 0.989629 | STATUS.md |

### [riscos_bloqueios] drift de embeddings (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.199733 | 0.295998 | 1.5 | 0.987977 | STATUS.md |
| 2 | fact | fact | 0.199733 | 0.295084 | 1.5 | 0.984927 | STATUS.md |
| 3 | fact | fact | 0.199733 | 0.295031 | 1.5 | 0.984751 | STATUS.md |
| 4 | fact | fact | 0.199733 | 0.294974 | 1.5 | 0.984562 | STATUS.md |
| 5 | fact | fact | 0.199733 | 0.294546 | 1.5 | 0.983134 | STATUS.md |

### [memoria_historica] mvp continuidade (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.558937 | 0.823946 | 1.5 | 0.982754 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.443871 | 0.570094 | 1.3 | 0.987977 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | fact | fact | 0.443871 | 0.568233 | 1.3 | 0.98475 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.443871 | 0.568124 | 1.3 | 0.984561 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.443871 | 0.567299 | 1.3 | 0.983133 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [memoria_historica] fatos canonicos project_facts (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.458047 | 0.67522 | 1.5 | 0.982753 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.360377 | 0.534066 | 1.5 | 0.987976 | STATUS.md |
| 3 | fact | fact | 0.360354 | 0.534032 | 1.5 | 0.987976 | STATUS.md |
| 4 | fact | fact | 0.360354 | 0.532288 | 1.5 | 0.984749 | STATUS.md |
| 5 | fact | fact | 0.360354 | 0.531413 | 1.5 | 0.983132 | STATUS.md |

### [tecnico_semantico] ranking debug score_final (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_run_summary', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.276264 | 0.273536 | 1.0 | 0.990126 | STATUS.md |
| 2 | run_summary | run_summary | 0.274291 | 0.272142 | 1.0 | 0.992165 | STATUS.md |
| 3 | run_summary | run_summary | 0.273243 | 0.270461 | 1.0 | 0.98982 | STATUS.md |
| 4 | run_summary | run_summary | 0.273045 | 0.270262 | 1.0 | 0.989808 | STATUS.md |
| 5 | run_summary | run_summary | 0.273059 | 0.269776 | 1.0 | 0.987975 | STATUS.md |

### [tecnico_semantico] realtime (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.322325 | 0.349212 | 1.1 | 0.984925 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | fact | fact | 0.314248 | 0.340401 | 1.1 | 0.984748 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.288964 | 0.314563 | 1.1 | 0.989626 | STATUS.md |
| 4 | fact | fact | 0.288529 | 0.314151 | 1.1 | 0.989819 | STATUS.md |
| 5 | fact | fact | 0.287574 | 0.313107 | 1.1 | 0.989808 | STATUS.md |

### [tecnico_semantico] knowledge_search ranking (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.331297 | 0.49188 | 1.5 | 0.989807 | STATUS.md |
| 2 | fact | fact | 0.331297 | 0.49179 | 1.5 | 0.989625 | STATUS.md |
| 3 | fact | fact | 0.331335 | 0.491026 | 1.5 | 0.987974 | STATUS.md |
| 4 | fact | fact | 0.331297 | 0.490969 | 1.5 | 0.987974 | STATUS.md |
| 5 | fact | fact | 0.331297 | 0.489454 | 1.5 | 0.984924 | STATUS.md |

## Calibration Hints (No Weight Change Applied)

- If `top3_dominated_by_*` is frequent: tighten diversity cap or add per-category rules.
- If `absence_of_fact_in_operational_query` appears: increase fact prior in hybrid for operational categories.
- If `run_summary_dominates_where_fact_expected` appears: reduce run_summary baseline in merge stage.
- If decision queries over-return chunks: add stronger fact_type bias for decision/risk intents.
