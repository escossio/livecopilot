# Project Brain Ranking Offline Eval

generated_at: 20260311T013958Z
project: livecopilot
wrapper: `/lab/projects/livecopilot/scripts/project_brain_query.sh`
queries: 16

## Ranking Baseline Inspected

- type weights: decision=1.5, milestone=1.3, risk=1.2, fact_default=1.1, run_summary=1.0, chunk/other=0.8
- recency: exp(-days_since/30)
- diversity: max_share per type in top-N (semantic hits=0.25, facts merge=0.7)
- debug ranking available via `--debug-ranking`
- useful JSON fields: semantic_hits.memory_type/source_type/similarity, ranking_debug(score_*)

## Consolidated Distribution

- fact: 52
- run_summary: 28

## Observation Signals

- absence_of_fact_in_operational_query: 1
- diversity_good: 7
- diversity_low: 9
- hybrid_without_fact_memory_type: 2
- run_summary_dominates_where_fact_expected: 1
- top3_dominated_by_fact: 6
- top3_dominated_by_run_summary: 3

## Query Results

### [continuidade_operacional] continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.538341 | 0.77863 | 1.5 | 0.964234 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.574187 | 0.609251 | 1.1 | 0.964606 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 3 | fact | fact | 0.555077 | 0.588897 | 1.1 | 0.964481 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.544534 | 0.577717 | 1.1 | 0.96449 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.512517 | 0.562836 | 1.1 | 0.998346 | STATUS.md |

### [continuidade_operacional] checkpoint da rodada (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.563882 | 0.620265 | 1.1 | 0.999991 | STATUS.md |
| 2 | fact | fact | 0.564222 | 0.619587 | 1.1 | 0.998296 | STATUS.md |
| 3 | fact | fact | 0.563815 | 0.619183 | 1.1 | 0.998365 | STATUS.md |
| 4 | fact | fact | 0.563536 | 0.619002 | 1.1 | 0.998569 | STATUS.md |
| 5 | fact | fact | 0.563433 | 0.617038 | 1.1 | 0.995581 | STATUS.md |

### [continuidade_operacional] new chat context (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.315123 | 0.334976 | 1.1 | 0.966365 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | run_summary | run_summary | 0.290799 | 0.281018 | 1.0 | 0.966365 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.245581 | 0.261006 | 1.1 | 0.966192 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | run_summary | run_summary | 0.20789 | 0.201857 | 1.0 | 0.970978 | STATUS.md |
| 5 | fact | fact | 0.224012 | 0.239262 | 1.1 | 0.970978 | STATUS.md |

### [estado_recente] ultimo closeout (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.421383 | 0.449318 | 1.1 | 0.969357 | STATUS.md |
| 2 | fact | fact | 0.417967 | 0.445675 | 1.1 | 0.969357 | STATUS.md |
| 3 | run_summary | run_summary | 0.43115 | 0.417938 | 1.0 | 0.969357 | STATUS.md |
| 4 | run_summary | run_summary | 0.428798 | 0.415658 | 1.0 | 0.969357 | STATUS.md |
| 5 | run_summary | run_summary | 0.371164 | 0.370549 | 1.0 | 0.998344 | STATUS.md |

### [estado_recente] smoke round continuity (hybrid)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'absence_of_fact_in_operational_query', 'diversity_low', 'hybrid_without_fact_memory_type']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.5943 | 0.594294 | 1.0 | 0.999989 | STATUS.md |
| 2 | run_summary | run_summary | 0.596389 | 0.593833 | 1.0 | 0.995715 | STATUS.md |
| 3 | run_summary | run_summary | 0.593927 | 0.592914 | 1.0 | 0.998294 | STATUS.md |
| 4 | run_summary | run_summary | 0.59522 | 0.592003 | 1.0 | 0.994596 | STATUS.md |
| 5 | run_summary | run_summary | 0.594263 | 0.591636 | 1.0 | 0.995579 | STATUS.md |

### [estado_recente] embedding maintenance (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.343893 | 0.433361 | 1.3 | 0.969356 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.343893 | 0.431946 | 1.3 | 0.96619 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.414119 | 0.401429 | 1.0 | 0.969356 | STATUS.md |
| 4 | run_summary | run_summary | 0.376891 | 0.365341 | 1.0 | 0.969356 | STATUS.md |
| 5 | fact | fact | 0.343893 | 0.431863 | 1.3 | 0.966004 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [decisoes_projeto] separacao question_bank knowledge (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.625948 | 0.938911 | 1.5 | 0.999988 | STATUS.md |
| 2 | fact | fact | 0.625948 | 0.937319 | 1.5 | 0.998293 | STATUS.md |
| 3 | fact | fact | 0.625948 | 0.936364 | 1.5 | 0.997276 | STATUS.md |
| 4 | fact | fact | 0.625948 | 0.934897 | 1.5 | 0.995713 | STATUS.md |
| 5 | fact | fact | 0.625948 | 0.934879 | 1.5 | 0.995694 | STATUS.md |

### [decisoes_projeto] adotar 3 niveis de continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.622805 | 0.900791 | 1.5 | 0.96423 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.497272 | 0.527573 | 1.1 | 0.964486 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.457932 | 0.441552 | 1.0 | 0.96423 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | run_summary | run_summary | 0.457659 | 0.441401 | 1.0 | 0.964476 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.49461 | 0.524812 | 1.1 | 0.964602 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |

### [decisoes_projeto] comando padrao operador scripts round (hybrid)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'run_summary_dominates_where_fact_expected', 'diversity_low', 'hybrid_without_fact_memory_type']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.454104 | 0.452148 | 1.0 | 0.995692 | STATUS.md |
| 2 | run_summary | run_summary | 0.449918 | 0.447989 | 1.0 | 0.995712 | STATUS.md |
| 3 | run_summary | run_summary | 0.447623 | 0.44698 | 1.0 | 0.998564 | STATUS.md |
| 4 | run_summary | run_summary | 0.447227 | 0.446485 | 1.0 | 0.998341 | STATUS.md |
| 5 | run_summary | run_summary | 0.447048 | 0.444637 | 1.0 | 0.994608 | STATUS.md |

### [riscos_bloqueios] risco runuser postgres peer auth (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.618696 | 0.722734 | 1.2 | 0.973464 | STATUS.md |
| 2 | fact | fact | 0.618696 | 0.721249 | 1.2 | 0.971463 | STATUS.md |
| 3 | fact | fact | 0.618696 | 0.721025 | 1.2 | 0.971163 | STATUS.md |
| 4 | fact | fact | 0.618696 | 0.721017 | 1.2 | 0.971152 | STATUS.md |
| 5 | fact | fact | 0.618696 | 0.720885 | 1.2 | 0.970973 | STATUS.md |

### [riscos_bloqueios] drift de embeddings (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.203166 | 0.295409 | 1.5 | 0.969353 | STATUS.md |
| 2 | fact | fact | 0.203166 | 0.294497 | 1.5 | 0.96636 | STATUS.md |
| 3 | run_summary | run_summary | 0.243698 | 0.236229 | 1.0 | 0.969353 | STATUS.md |
| 4 | run_summary | run_summary | 0.226672 | 0.220092 | 1.0 | 0.970972 | STATUS.md |
| 5 | fact | fact | 0.203166 | 0.294445 | 1.5 | 0.966187 | STATUS.md |

### [memoria_historica] mvp continuidade (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.558973 | 0.808466 | 1.5 | 0.964227 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.443967 | 0.559468 | 1.3 | 0.969352 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.497826 | 0.480017 | 1.0 | 0.964227 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | fact | fact | 0.443967 | 0.557641 | 1.3 | 0.966186 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.443967 | 0.557534 | 1.3 | 0.966001 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [memoria_historica] fatos canonicos project_facts (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.457929 | 0.662321 | 1.5 | 0.964227 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.360323 | 0.538155 | 1.5 | 0.99569 | STATUS.md |
| 3 | run_summary | run_summary | 0.489799 | 0.47246 | 1.0 | 0.964599 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 4 | fact | fact | 0.360323 | 0.537569 | 1.5 | 0.994605 | STATUS.md |
| 5 | fact | fact | 0.360323 | 0.533507 | 1.5 | 0.987091 | STATUS.md |

### [tecnico_semantico] ranking debug score_final (semantic)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.278491 | 0.278034 | 1.0 | 0.998357 | STATUS.md |
| 2 | run_summary | run_summary | 0.277155 | 0.275966 | 1.0 | 0.995709 | STATUS.md |
| 3 | run_summary | run_summary | 0.275708 | 0.275236 | 1.0 | 0.998288 | STATUS.md |
| 4 | run_summary | run_summary | 0.275625 | 0.275228 | 1.0 | 0.998561 | STATUS.md |
| 5 | run_summary | run_summary | 0.27344 | 0.272986 | 1.0 | 0.998338 | STATUS.md |

### [tecnico_semantico] realtime (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.3223 | 0.342603 | 1.1 | 0.966358 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | fact | fact | 0.314177 | 0.333908 | 1.1 | 0.966184 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.289987 | 0.317617 | 1.1 | 0.995708 | STATUS.md |
| 4 | fact | fact | 0.288647 | 0.315798 | 1.1 | 0.994604 | STATUS.md |
| 5 | fact | fact | 0.287723 | 0.314783 | 1.1 | 0.994589 | STATUS.md |

### [tecnico_semantico] knowledge_search ranking (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.33138 | 0.496354 | 1.5 | 0.99856 | STATUS.md |
| 2 | fact | fact | 0.33138 | 0.496253 | 1.5 | 0.998356 | STATUS.md |
| 3 | fact | fact | 0.33138 | 0.496243 | 1.5 | 0.998336 | STATUS.md |
| 4 | fact | fact | 0.33129 | 0.496084 | 1.5 | 0.998287 | STATUS.md |
| 5 | fact | fact | 0.33129 | 0.495578 | 1.5 | 0.99727 | STATUS.md |

## Calibration Hints (No Weight Change Applied)

- If `top3_dominated_by_*` is frequent: tighten diversity cap or add per-category rules.
- If `absence_of_fact_in_operational_query` appears: increase fact prior in hybrid for operational categories.
- If `run_summary_dominates_where_fact_expected` appears: reduce run_summary baseline in merge stage.
- If decision queries over-return chunks: add stronger fact_type bias for decision/risk intents.
