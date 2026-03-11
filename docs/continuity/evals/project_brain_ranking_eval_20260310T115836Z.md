# Project Brain Ranking Offline Eval

generated_at: 20260310T115836Z
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

- fact: 58
- run_summary: 22

## Observation Signals

- diversity_good: 11
- diversity_low: 5
- top3_dominated_by_fact: 5

## Query Results

### [continuidade_operacional] continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.538313 | 0.793535 | 1.5 | 0.982743 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.574161 | 0.620918 | 1.1 | 0.983123 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 3 | fact | fact | 0.555044 | 0.600166 | 1.1 | 0.982994 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.54452 | 0.588792 | 1.1 | 0.983004 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.510075 | 0.556682 | 1.1 | 0.992156 | STATUS.md |

### [continuidade_operacional] checkpoint da rodada (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.561412 | 0.612709 | 1.1 | 0.992156 | STATUS.md |
| 2 | fact | fact | 0.562223 | 0.612143 | 1.1 | 0.98981 | STATUS.md |
| 3 | fact | fact | 0.561439 | 0.611283 | 1.1 | 0.989799 | STATUS.md |
| 4 | fact | fact | 0.561103 | 0.611113 | 1.1 | 0.990116 | STATUS.md |
| 5 | fact | fact | 0.541616 | 0.588608 | 1.1 | 0.987966 | STATUS.md |

### [continuidade_operacional] new chat context (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.315086 | 0.341366 | 1.1 | 0.984915 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | run_summary | run_summary | 0.290756 | 0.28637 | 1.0 | 0.984915 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.245519 | 0.265949 | 1.1 | 0.984739 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | run_summary | run_summary | 0.207854 | 0.205696 | 1.0 | 0.989616 | STATUS.md |
| 5 | fact | fact | 0.223953 | 0.24379 | 1.1 | 0.989616 | STATUS.md |

### [estado_recente] ultimo closeout (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.421479 | 0.458047 | 1.1 | 0.987964 | STATUS.md |
| 2 | fact | fact | 0.418062 | 0.454333 | 1.1 | 0.987964 | STATUS.md |
| 3 | run_summary | run_summary | 0.431286 | 0.426095 | 1.0 | 0.987964 | STATUS.md |
| 4 | run_summary | run_summary | 0.428917 | 0.423755 | 1.0 | 0.987964 | STATUS.md |
| 5 | run_summary | run_summary | 0.371798 | 0.368881 | 1.0 | 0.992155 | STATUS.md |

### [estado_recente] smoke round continuity (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.559202 | 0.608853 | 1.1 | 0.989808 | STATUS.md |
| 2 | fact | fact | 0.557214 | 0.608126 | 1.1 | 0.992154 | STATUS.md |
| 3 | run_summary | run_summary | 0.59915 | 0.593227 | 1.0 | 0.990114 | STATUS.md |
| 4 | run_summary | run_summary | 0.597543 | 0.591453 | 1.0 | 0.989808 | STATUS.md |
| 5 | fact | fact | 0.557364 | 0.607039 | 1.1 | 0.990114 | STATUS.md |

### [estado_recente] embedding maintenance (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.343937 | 0.441736 | 1.3 | 0.987963 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.343937 | 0.440294 | 1.3 | 0.984737 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.414223 | 0.409237 | 1.0 | 0.987963 | STATUS.md |
| 4 | run_summary | run_summary | 0.377001 | 0.372463 | 1.0 | 0.987963 | STATUS.md |
| 5 | fact | fact | 0.343937 | 0.440209 | 1.3 | 0.984547 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [decisoes_projeto] separacao question_bank knowledge (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.62587 | 0.929225 | 1.5 | 0.989795 | STATUS.md |
| 2 | fact | fact | 0.62587 | 0.929054 | 1.5 | 0.989613 | STATUS.md |
| 3 | fact | fact | 0.625929 | 0.927591 | 1.5 | 0.987962 | STATUS.md |
| 4 | fact | fact | 0.62587 | 0.927504 | 1.5 | 0.987962 | STATUS.md |
| 5 | fact | fact | 0.62587 | 0.924641 | 1.5 | 0.984912 | STATUS.md |

### [decisoes_projeto] adotar 3 niveis de continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.622868 | 0.918175 | 1.5 | 0.982739 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.497267 | 0.537694 | 1.1 | 0.982999 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.458005 | 0.450099 | 1.0 | 0.982739 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | run_summary | run_summary | 0.457712 | 0.449926 | 1.0 | 0.98299 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.494592 | 0.534866 | 1.1 | 0.983118 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |

### [decisoes_projeto] comando padrao operador scripts round (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.429454 | 0.464368 | 1.1 | 0.982998 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.426148 | 0.461518 | 1.1 | 0.984545 | STATUS.md |
| 3 | run_summary | run_summary | 0.447559 | 0.444046 | 1.0 | 0.992151 | STATUS.md |
| 4 | run_summary | run_summary | 0.447538 | 0.443112 | 1.0 | 0.990111 | STATUS.md |
| 5 | fact | fact | 0.409917 | 0.444105 | 1.1 | 0.984911 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |

### [riscos_bloqueios] risco runuser postgres peer auth (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.618719 | 0.736635 | 1.2 | 0.99215 | STATUS.md |
| 2 | fact | fact | 0.618719 | 0.73512 | 1.2 | 0.990111 | STATUS.md |
| 3 | fact | fact | 0.618719 | 0.734893 | 1.2 | 0.989804 | STATUS.md |
| 4 | fact | fact | 0.618719 | 0.734885 | 1.2 | 0.989793 | STATUS.md |
| 5 | fact | fact | 0.618719 | 0.734749 | 1.2 | 0.989611 | STATUS.md |

### [riscos_bloqueios] drift de embeddings (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.199733 | 0.295992 | 1.5 | 0.987959 | STATUS.md |
| 2 | fact | fact | 0.199733 | 0.295078 | 1.5 | 0.98491 | STATUS.md |
| 3 | run_summary | run_summary | 0.240703 | 0.237805 | 1.0 | 0.987959 | STATUS.md |
| 4 | run_summary | run_summary | 0.224333 | 0.222002 | 1.0 | 0.98961 | STATUS.md |
| 5 | fact | fact | 0.199733 | 0.295026 | 1.5 | 0.984733 | STATUS.md |

### [memoria_historica] mvp continuidade (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.558937 | 0.823931 | 1.5 | 0.982736 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.443871 | 0.570084 | 1.3 | 0.987959 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.497753 | 0.48916 | 1.0 | 0.982736 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | fact | fact | 0.443871 | 0.568222 | 1.3 | 0.984732 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.443871 | 0.568113 | 1.3 | 0.984543 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [memoria_historica] fatos canonicos project_facts (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.458067 | 0.675238 | 1.5 | 0.982735 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.360432 | 0.534138 | 1.5 | 0.987958 | STATUS.md |
| 3 | run_summary | run_summary | 0.489947 | 0.481674 | 1.0 | 0.983114 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 4 | fact | fact | 0.360409 | 0.534104 | 1.5 | 0.987958 | STATUS.md |
| 5 | fact | fact | 0.360409 | 0.532359 | 1.5 | 0.984732 | STATUS.md |

### [tecnico_semantico] ranking debug score_final (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.276303 | 0.27357 | 1.0 | 0.990108 | STATUS.md |
| 2 | run_summary | run_summary | 0.274326 | 0.272172 | 1.0 | 0.992148 | STATUS.md |
| 3 | fact | fact | 0.240274 | 0.261119 | 1.1 | 0.987958 | STATUS.md |
| 4 | run_summary | run_summary | 0.273282 | 0.270495 | 1.0 | 0.989802 | STATUS.md |
| 5 | run_summary | run_summary | 0.273081 | 0.270293 | 1.0 | 0.98979 | STATUS.md |

### [tecnico_semantico] realtime (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.322325 | 0.349206 | 1.1 | 0.984907 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | fact | fact | 0.314248 | 0.340395 | 1.1 | 0.98473 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | run_summary | run_summary | 0.279601 | 0.275332 | 1.0 | 0.98473 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | fact | fact | 0.288964 | 0.314557 | 1.1 | 0.989608 | STATUS.md |
| 5 | fact | fact | 0.288529 | 0.314145 | 1.1 | 0.989801 | STATUS.md |

### [tecnico_semantico] knowledge_search ranking (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.331295 | 0.491868 | 1.5 | 0.989789 | STATUS.md |
| 2 | fact | fact | 0.331295 | 0.491778 | 1.5 | 0.989607 | STATUS.md |
| 3 | fact | fact | 0.331333 | 0.491014 | 1.5 | 0.987956 | STATUS.md |
| 4 | fact | fact | 0.331295 | 0.490957 | 1.5 | 0.987956 | STATUS.md |
| 5 | fact | fact | 0.331295 | 0.489442 | 1.5 | 0.984906 | STATUS.md |

## Calibration Hints (No Weight Change Applied)

- If `top3_dominated_by_*` is frequent: tighten diversity cap or add per-category rules.
- If `absence_of_fact_in_operational_query` appears: increase fact prior in hybrid for operational categories.
- If `run_summary_dominates_where_fact_expected` appears: reduce run_summary baseline in merge stage.
- If decision queries over-return chunks: add stronger fact_type bias for decision/risk intents.
