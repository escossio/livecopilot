# Project Brain Ranking Offline Eval

generated_at: 20260310T214606Z
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
| 1 | fact | fact | 0.538313 | 0.782816 | 1.5 | 0.969469 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.574161 | 0.61253 | 1.1 | 0.969843 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 3 | fact | fact | 0.555044 | 0.592059 | 1.1 | 0.969716 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.54452 | 0.580839 | 1.1 | 0.969726 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.510524 | 0.561575 | 1.1 | 0.999998 | STATUS.md |

### [continuidade_operacional] checkpoint da rodada (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.563085 | 0.619392 | 1.1 | 0.999997 | STATUS.md |
| 2 | fact | fact | 0.560554 | 0.611969 | 1.1 | 0.992474 | STATUS.md |
| 3 | fact | fact | 0.560502 | 0.611901 | 1.1 | 0.992456 | STATUS.md |
| 4 | fact | fact | 0.561523 | 0.609342 | 1.1 | 0.986508 | STATUS.md |
| 5 | fact | fact | 0.561412 | 0.604433 | 1.1 | 0.978754 | STATUS.md |

### [continuidade_operacional] new chat context (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.315123 | 0.336795 | 1.1 | 0.971611 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | run_summary | run_summary | 0.290799 | 0.282544 | 1.0 | 0.971611 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.245581 | 0.262423 | 1.1 | 0.971437 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | run_summary | run_summary | 0.20789 | 0.202952 | 1.0 | 0.976248 | STATUS.md |
| 5 | fact | fact | 0.224012 | 0.24056 | 1.1 | 0.976248 | STATUS.md |

### [estado_recente] ultimo closeout (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.421479 | 0.45186 | 1.1 | 0.974619 | STATUS.md |
| 2 | fact | fact | 0.418062 | 0.448196 | 1.1 | 0.974619 | STATUS.md |
| 3 | run_summary | run_summary | 0.431286 | 0.42034 | 1.0 | 0.974619 | STATUS.md |
| 4 | run_summary | run_summary | 0.428917 | 0.418031 | 1.0 | 0.974619 | STATUS.md |
| 5 | run_summary | run_summary | 0.367438 | 0.364672 | 1.0 | 0.992473 | STATUS.md |

### [estado_recente] smoke round continuity (hybrid)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'absence_of_fact_in_operational_query', 'diversity_low', 'hybrid_without_fact_memory_type']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.595306 | 0.595303 | 1.0 | 0.999995 | STATUS.md |
| 2 | run_summary | run_summary | 0.596982 | 0.588926 | 1.0 | 0.986506 | STATUS.md |
| 3 | run_summary | run_summary | 0.59915 | 0.585214 | 1.0 | 0.97674 | STATUS.md |
| 4 | run_summary | run_summary | 0.589089 | 0.584644 | 1.0 | 0.992454 | STATUS.md |
| 5 | run_summary | run_summary | 0.588846 | 0.584413 | 1.0 | 0.992472 | STATUS.md |

### [estado_recente] embedding maintenance (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.343955 | 0.435792 | 1.3 | 0.974618 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.343955 | 0.434369 | 1.3 | 0.971435 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.414195 | 0.403682 | 1.0 | 0.974618 | STATUS.md |
| 4 | run_summary | run_summary | 0.376955 | 0.367387 | 1.0 | 0.974618 | STATUS.md |
| 5 | fact | fact | 0.343955 | 0.434285 | 1.3 | 0.971248 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [decisoes_projeto] separacao question_bank knowledge (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.625987 | 0.931894 | 1.5 | 0.992453 | STATUS.md |
| 2 | fact | fact | 0.625929 | 0.916591 | 1.5 | 0.976246 | STATUS.md |
| 3 | fact | fact | 0.625987 | 0.915147 | 1.5 | 0.974617 | STATUS.md |
| 4 | fact | fact | 0.625929 | 0.915062 | 1.5 | 0.974617 | STATUS.md |
| 5 | fact | fact | 0.625929 | 0.912237 | 1.5 | 0.971608 | STATUS.md |

### [decisoes_projeto] adotar 3 niveis de continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.622868 | 0.905772 | 1.5 | 0.969464 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.497267 | 0.530431 | 1.1 | 0.969721 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.458005 | 0.444019 | 1.0 | 0.969464 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | run_summary | run_summary | 0.457712 | 0.443849 | 1.0 | 0.969712 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.494592 | 0.527642 | 1.1 | 0.969838 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |

### [decisoes_projeto] comando padrao operador scripts round (hybrid)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'run_summary_dominates_where_fact_expected', 'diversity_low', 'hybrid_without_fact_memory_type']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.446756 | 0.446753 | 1.0 | 0.999992 | STATUS.md |
| 2 | run_summary | run_summary | 0.445122 | 0.441762 | 1.0 | 0.992451 | STATUS.md |
| 3 | run_summary | run_summary | 0.446475 | 0.440449 | 1.0 | 0.986504 | STATUS.md |
| 4 | run_summary | run_summary | 0.442798 | 0.439463 | 1.0 | 0.992469 | STATUS.md |
| 5 | run_summary | run_summary | 0.44758 | 0.438069 | 1.0 | 0.978749 | STATUS.md |

### [riscos_bloqueios] risco runuser postgres peer auth (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.618719 | 0.726685 | 1.2 | 0.978749 | STATUS.md |
| 2 | fact | fact | 0.618719 | 0.725191 | 1.2 | 0.976737 | STATUS.md |
| 3 | fact | fact | 0.618719 | 0.724966 | 1.2 | 0.976435 | STATUS.md |
| 4 | fact | fact | 0.618719 | 0.724958 | 1.2 | 0.976423 | STATUS.md |
| 5 | fact | fact | 0.618719 | 0.724825 | 1.2 | 0.976244 | STATUS.md |

### [riscos_bloqueios] drift de embeddings (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.199733 | 0.291994 | 1.5 | 0.974615 | STATUS.md |
| 2 | fact | fact | 0.199733 | 0.291093 | 1.5 | 0.971606 | STATUS.md |
| 3 | run_summary | run_summary | 0.240703 | 0.234593 | 1.0 | 0.974615 | STATUS.md |
| 4 | run_summary | run_summary | 0.224333 | 0.219004 | 1.0 | 0.976243 | STATUS.md |
| 5 | fact | fact | 0.199733 | 0.29104 | 1.5 | 0.971432 | STATUS.md |

### [memoria_historica] mvp continuidade (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.559076 | 0.813004 | 1.5 | 0.969462 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.444046 | 0.562605 | 1.3 | 0.974614 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.497868 | 0.482664 | 1.0 | 0.969462 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | fact | fact | 0.444046 | 0.560768 | 1.3 | 0.971431 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.444046 | 0.56066 | 1.3 | 0.971245 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [memoria_historica] fatos canonicos project_facts (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.458067 | 0.666117 | 1.5 | 0.969461 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.360432 | 0.536565 | 1.5 | 0.992449 | STATUS.md |
| 3 | run_summary | run_summary | 0.489947 | 0.475168 | 1.0 | 0.969835 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 4 | fact | fact | 0.360432 | 0.526923 | 1.5 | 0.974613 | STATUS.md |
| 5 | fact | fact | 0.360409 | 0.525168 | 1.5 | 0.971431 | STATUS.md |

### [tecnico_semantico] ranking debug score_final (semantic)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.272409 | 0.270352 | 1.0 | 0.992448 | STATUS.md |
| 2 | run_summary | run_summary | 0.273559 | 0.269866 | 1.0 | 0.9865 | STATUS.md |
| 3 | run_summary | run_summary | 0.276264 | 0.269836 | 1.0 | 0.976734 | STATUS.md |
| 4 | run_summary | run_summary | 0.274291 | 0.268461 | 1.0 | 0.978746 | STATUS.md |
| 5 | run_summary | run_summary | 0.273243 | 0.266803 | 1.0 | 0.976432 | STATUS.md |

### [tecnico_semantico] realtime (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.322325 | 0.344489 | 1.1 | 0.971603 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | fact | fact | 0.314248 | 0.335797 | 1.1 | 0.971429 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.287793 | 0.316569 | 1.1 | 0.999988 | STATUS.md |
| 4 | fact | fact | 0.287877 | 0.31239 | 1.1 | 0.9865 | STATUS.md |
| 5 | fact | fact | 0.288964 | 0.310308 | 1.1 | 0.976241 | STATUS.md |

### [tecnico_semantico] knowledge_search ranking (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.33129 | 0.493182 | 1.5 | 0.992447 | STATUS.md |
| 2 | fact | fact | 0.331253 | 0.485074 | 1.5 | 0.97624 | STATUS.md |
| 3 | fact | fact | 0.33129 | 0.484319 | 1.5 | 0.974611 | STATUS.md |
| 4 | fact | fact | 0.331253 | 0.484264 | 1.5 | 0.974611 | STATUS.md |
| 5 | fact | fact | 0.331253 | 0.482769 | 1.5 | 0.971603 | STATUS.md |

## Calibration Hints (No Weight Change Applied)

- If `top3_dominated_by_*` is frequent: tighten diversity cap or add per-category rules.
- If `absence_of_fact_in_operational_query` appears: increase fact prior in hybrid for operational categories.
- If `run_summary_dominates_where_fact_expected` appears: reduce run_summary baseline in merge stage.
- If decision queries over-return chunks: add stronger fact_type bias for decision/risk intents.
