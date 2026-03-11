# Project Brain Ranking Offline Eval

generated_at: 20260310T214530Z
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

- fact: 54
- run_summary: 26

## Observation Signals

- diversity_good: 9
- diversity_low: 7
- top3_dominated_by_fact: 6
- top3_dominated_by_run_summary: 1

## Query Results

### [continuidade_operacional] continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.538313 | 0.782827 | 1.5 | 0.969482 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.574161 | 0.612539 | 1.1 | 0.969856 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 3 | fact | fact | 0.555044 | 0.592067 | 1.1 | 0.96973 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.54452 | 0.580847 | 1.1 | 0.969739 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.510075 | 0.54917 | 1.1 | 0.978768 | STATUS.md |

### [continuidade_operacional] checkpoint da rodada (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.560641 | 0.612072 | 1.1 | 0.992488 | STATUS.md |
| 2 | fact | fact | 0.560592 | 0.612008 | 1.1 | 0.99247 | STATUS.md |
| 3 | fact | fact | 0.561612 | 0.609447 | 1.1 | 0.986522 | STATUS.md |
| 4 | fact | fact | 0.5615 | 0.604536 | 1.1 | 0.978768 | STATUS.md |
| 5 | fact | fact | 0.562311 | 0.603978 | 1.1 | 0.976453 | STATUS.md |

### [continuidade_operacional] new chat context (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.315086 | 0.33676 | 1.1 | 0.971624 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | run_summary | run_summary | 0.290756 | 0.282506 | 1.0 | 0.971624 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.245519 | 0.26236 | 1.1 | 0.97145 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | run_summary | run_summary | 0.207854 | 0.20292 | 1.0 | 0.976262 | STATUS.md |
| 5 | fact | fact | 0.223953 | 0.2405 | 1.1 | 0.976262 | STATUS.md |

### [estado_recente] ultimo closeout (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.421437 | 0.451821 | 1.1 | 0.974633 | STATUS.md |
| 2 | fact | fact | 0.418026 | 0.448164 | 1.1 | 0.974633 | STATUS.md |
| 3 | run_summary | run_summary | 0.431167 | 0.420229 | 1.0 | 0.974633 | STATUS.md |
| 4 | run_summary | run_summary | 0.428812 | 0.417934 | 1.0 | 0.974633 | STATUS.md |
| 5 | run_summary | run_summary | 0.367414 | 0.364653 | 1.0 | 0.992486 | STATUS.md |

### [estado_recente] smoke round continuity (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.559202 | 0.600637 | 1.1 | 0.976451 | STATUS.md |
| 2 | run_summary | run_summary | 0.596982 | 0.588935 | 1.0 | 0.98652 | STATUS.md |
| 3 | run_summary | run_summary | 0.59915 | 0.585222 | 1.0 | 0.976753 | STATUS.md |
| 4 | run_summary | run_summary | 0.589089 | 0.584652 | 1.0 | 0.992468 | STATUS.md |
| 5 | run_summary | run_summary | 0.588846 | 0.584421 | 1.0 | 0.992486 | STATUS.md |

### [estado_recente] embedding maintenance (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.343893 | 0.43572 | 1.3 | 0.974631 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.343893 | 0.434297 | 1.3 | 0.971448 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.414119 | 0.403613 | 1.0 | 0.974631 | STATUS.md |
| 4 | run_summary | run_summary | 0.376891 | 0.36733 | 1.0 | 0.974631 | STATUS.md |
| 5 | fact | fact | 0.343893 | 0.434213 | 1.3 | 0.971262 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [decisoes_projeto] separacao question_bank knowledge (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.625987 | 0.931907 | 1.5 | 0.992466 | STATUS.md |
| 2 | fact | fact | 0.625929 | 0.916604 | 1.5 | 0.976259 | STATUS.md |
| 3 | fact | fact | 0.625987 | 0.915159 | 1.5 | 0.974631 | STATUS.md |
| 4 | fact | fact | 0.625929 | 0.915074 | 1.5 | 0.974631 | STATUS.md |
| 5 | fact | fact | 0.625929 | 0.91225 | 1.5 | 0.971622 | STATUS.md |

### [decisoes_projeto] adotar 3 niveis de continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.622805 | 0.905693 | 1.5 | 0.969478 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.497272 | 0.530444 | 1.1 | 0.969735 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.457932 | 0.443955 | 1.0 | 0.969478 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | run_summary | run_summary | 0.457659 | 0.443804 | 1.0 | 0.969725 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.49461 | 0.527668 | 1.1 | 0.969852 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |

### [decisoes_projeto] comando padrao operador scripts round (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.42953 | 0.458183 | 1.1 | 0.969734 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | run_summary | run_summary | 0.445162 | 0.441808 | 1.0 | 0.992465 | STATUS.md |
| 3 | run_summary | run_summary | 0.446518 | 0.440498 | 1.0 | 0.986517 | STATUS.md |
| 4 | run_summary | run_summary | 0.442841 | 0.439512 | 1.0 | 0.992483 | STATUS.md |
| 5 | run_summary | run_summary | 0.447621 | 0.438115 | 1.0 | 0.978763 | STATUS.md |

### [riscos_bloqueios] risco runuser postgres peer auth (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.618797 | 0.726786 | 1.2 | 0.978762 | STATUS.md |
| 2 | fact | fact | 0.618797 | 0.725292 | 1.2 | 0.97675 | STATUS.md |
| 3 | fact | fact | 0.618797 | 0.725068 | 1.2 | 0.976448 | STATUS.md |
| 4 | fact | fact | 0.618797 | 0.725059 | 1.2 | 0.976437 | STATUS.md |
| 5 | fact | fact | 0.618797 | 0.724926 | 1.2 | 0.976257 | STATUS.md |

### [riscos_bloqueios] drift de embeddings (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.199733 | 0.291998 | 1.5 | 0.974628 | STATUS.md |
| 2 | fact | fact | 0.199733 | 0.291097 | 1.5 | 0.971619 | STATUS.md |
| 3 | run_summary | run_summary | 0.240703 | 0.234596 | 1.0 | 0.974628 | STATUS.md |
| 4 | run_summary | run_summary | 0.224333 | 0.219007 | 1.0 | 0.976257 | STATUS.md |
| 5 | fact | fact | 0.199733 | 0.291045 | 1.5 | 0.971445 | STATUS.md |

### [memoria_historica] mvp continuidade (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.558937 | 0.812813 | 1.5 | 0.969475 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.443871 | 0.562392 | 1.3 | 0.974628 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.497753 | 0.482559 | 1.0 | 0.969475 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | fact | fact | 0.443871 | 0.560555 | 1.3 | 0.971445 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.443871 | 0.560447 | 1.3 | 0.971258 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [memoria_historica] fatos canonicos project_facts (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.458035 | 0.66608 | 1.5 | 0.969474 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.360395 | 0.536518 | 1.5 | 0.992463 | STATUS.md |
| 3 | run_summary | run_summary | 0.489869 | 0.475099 | 1.0 | 0.969849 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 4 | fact | fact | 0.360395 | 0.526876 | 1.5 | 0.974627 | STATUS.md |
| 5 | fact | fact | 0.360372 | 0.525122 | 1.5 | 0.971444 | STATUS.md |

### [tecnico_semantico] ranking debug score_final (semantic)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.271898 | 0.269848 | 1.0 | 0.992462 | STATUS.md |
| 2 | run_summary | run_summary | 0.27303 | 0.269348 | 1.0 | 0.986514 | STATUS.md |
| 3 | run_summary | run_summary | 0.275744 | 0.269332 | 1.0 | 0.976748 | STATUS.md |
| 4 | run_summary | run_summary | 0.273768 | 0.267953 | 1.0 | 0.97876 | STATUS.md |
| 5 | run_summary | run_summary | 0.272708 | 0.266285 | 1.0 | 0.976446 | STATUS.md |

### [tecnico_semantico] realtime (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.322325 | 0.344494 | 1.1 | 0.971617 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | fact | fact | 0.314248 | 0.335801 | 1.1 | 0.971443 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.286891 | 0.313207 | 1.1 | 0.992479 | STATUS.md |
| 4 | fact | fact | 0.287877 | 0.312394 | 1.1 | 0.986514 | STATUS.md |
| 5 | fact | fact | 0.288964 | 0.310313 | 1.1 | 0.976254 | STATUS.md |

### [tecnico_semantico] knowledge_search ranking (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.33129 | 0.493188 | 1.5 | 0.992461 | STATUS.md |
| 2 | fact | fact | 0.331253 | 0.48508 | 1.5 | 0.976254 | STATUS.md |
| 3 | fact | fact | 0.33129 | 0.484325 | 1.5 | 0.974625 | STATUS.md |
| 4 | fact | fact | 0.331253 | 0.484271 | 1.5 | 0.974625 | STATUS.md |
| 5 | fact | fact | 0.331253 | 0.482776 | 1.5 | 0.971616 | STATUS.md |

## Calibration Hints (No Weight Change Applied)

- If `top3_dominated_by_*` is frequent: tighten diversity cap or add per-category rules.
- If `absence_of_fact_in_operational_query` appears: increase fact prior in hybrid for operational categories.
- If `run_summary_dominates_where_fact_expected` appears: reduce run_summary baseline in merge stage.
- If decision queries over-return chunks: add stronger fact_type bias for decision/risk intents.
