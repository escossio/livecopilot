# Project Brain Ranking Offline Eval

generated_at: 20260310T223343Z
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
| 1 | fact | fact | 0.538313 | 0.781954 | 1.5 | 0.9684 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.574161 | 0.611856 | 1.1 | 0.968774 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 3 | fact | fact | 0.555044 | 0.591406 | 1.1 | 0.968648 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.54452 | 0.580199 | 1.1 | 0.968657 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.510524 | 0.560956 | 1.1 | 0.998896 | STATUS.md |

### [continuidade_operacional] checkpoint da rodada (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.563433 | 0.619704 | 1.1 | 0.999883 | STATUS.md |
| 2 | fact | fact | 0.56317 | 0.618802 | 1.1 | 0.998895 | STATUS.md |
| 3 | fact | fact | 0.562958 | 0.618578 | 1.1 | 0.998909 | STATUS.md |
| 4 | fact | fact | 0.561612 | 0.608767 | 1.1 | 0.985421 | STATUS.md |
| 5 | fact | fact | 0.5615 | 0.603861 | 1.1 | 0.977675 | STATUS.md |

### [continuidade_operacional] new chat context (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.315086 | 0.336384 | 1.1 | 0.97054 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | run_summary | run_summary | 0.290756 | 0.268081 | 0.95 | 0.97054 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.245519 | 0.262068 | 1.1 | 0.970366 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | run_summary | run_summary | 0.207854 | 0.192559 | 0.95 | 0.975173 | STATUS.md |
| 5 | fact | fact | 0.223953 | 0.240232 | 1.1 | 0.975173 | STATUS.md |

### [estado_recente] ultimo closeout (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.421479 | 0.451362 | 1.1 | 0.973545 | STATUS.md |
| 2 | fact | fact | 0.418062 | 0.447702 | 1.1 | 0.973545 | STATUS.md |
| 3 | run_summary | run_summary | 0.431286 | 0.398883 | 0.95 | 0.973545 | STATUS.md |
| 4 | run_summary | run_summary | 0.428917 | 0.396692 | 0.95 | 0.973545 | STATUS.md |
| 5 | run_summary | run_summary | 0.369436 | 0.350581 | 0.95 | 0.998908 | STATUS.md |

### [estado_recente] smoke round continuity (hybrid)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'absence_of_fact_in_operational_query', 'diversity_low', 'hybrid_without_fact_memory_type']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.59522 | 0.564833 | 0.95 | 0.998893 | STATUS.md |
| 2 | run_summary | run_summary | 0.594263 | 0.564483 | 0.95 | 0.999881 | STATUS.md |
| 3 | run_summary | run_summary | 0.591652 | 0.562068 | 0.95 | 0.999997 | STATUS.md |
| 4 | run_summary | run_summary | 0.596895 | 0.558782 | 0.95 | 0.985419 | STATUS.md |
| 5 | run_summary | run_summary | 0.59906 | 0.555257 | 0.95 | 0.975664 | STATUS.md |

### [estado_recente] embedding maintenance (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.343937 | 0.435289 | 1.3 | 0.973544 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.343937 | 0.433868 | 1.3 | 0.970365 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.414223 | 0.383101 | 0.95 | 0.973544 | STATUS.md |
| 4 | run_summary | run_summary | 0.377001 | 0.348676 | 0.95 | 0.973544 | STATUS.md |
| 5 | fact | fact | 0.343937 | 0.433784 | 1.3 | 0.970178 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [decisoes_projeto] separacao question_bank knowledge (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.625987 | 0.938976 | 1.5 | 0.999995 | STATUS.md |
| 2 | fact | fact | 0.625987 | 0.937953 | 1.5 | 0.998906 | STATUS.md |
| 3 | fact | fact | 0.625987 | 0.930867 | 1.5 | 0.991359 | STATUS.md |
| 4 | fact | fact | 0.625929 | 0.915581 | 1.5 | 0.97517 | STATUS.md |
| 5 | fact | fact | 0.625987 | 0.914138 | 1.5 | 0.973543 | STATUS.md |

### [decisoes_projeto] adotar 3 niveis de continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.622805 | 0.904683 | 1.5 | 0.968396 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.497272 | 0.529852 | 1.1 | 0.968653 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.457932 | 0.421286 | 0.95 | 0.968396 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | run_summary | run_summary | 0.457659 | 0.421143 | 0.95 | 0.968643 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.49461 | 0.527079 | 1.1 | 0.96877 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |

### [decisoes_projeto] comando padrao operador scripts round (hybrid)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'run_summary_dominates_where_fact_expected', 'diversity_low', 'hybrid_without_fact_memory_type']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.454105 | 0.431397 | 0.95 | 0.999994 | STATUS.md |
| 2 | run_summary | run_summary | 0.447049 | 0.424231 | 0.95 | 0.998905 | STATUS.md |
| 3 | run_summary | run_summary | 0.446756 | 0.423947 | 0.95 | 0.99889 | STATUS.md |
| 4 | run_summary | run_summary | 0.446475 | 0.417966 | 0.95 | 0.985417 | STATUS.md |
| 5 | run_summary | run_summary | 0.44758 | 0.415707 | 0.95 | 0.977671 | STATUS.md |

### [riscos_bloqueios] risco runuser postgres peer auth (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.618708 | 0.725871 | 1.2 | 0.97767 | STATUS.md |
| 2 | fact | fact | 0.618708 | 0.724379 | 1.2 | 0.975661 | STATUS.md |
| 3 | fact | fact | 0.618708 | 0.724155 | 1.2 | 0.975359 | STATUS.md |
| 4 | fact | fact | 0.618708 | 0.724146 | 1.2 | 0.975348 | STATUS.md |
| 5 | fact | fact | 0.618708 | 0.724013 | 1.2 | 0.975168 | STATUS.md |

### [riscos_bloqueios] drift de embeddings (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.203156 | 0.296671 | 1.5 | 0.973541 | STATUS.md |
| 2 | fact | fact | 0.203156 | 0.295755 | 1.5 | 0.970535 | STATUS.md |
| 3 | run_summary | run_summary | 0.243663 | 0.225355 | 0.95 | 0.973541 | STATUS.md |
| 4 | run_summary | run_summary | 0.226662 | 0.209982 | 0.95 | 0.975168 | STATUS.md |
| 5 | fact | fact | 0.203156 | 0.295702 | 1.5 | 0.970361 | STATUS.md |

### [memoria_historica] mvp continuidade (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.558973 | 0.811959 | 1.5 | 0.968393 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.443967 | 0.561886 | 1.3 | 0.97354 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.497826 | 0.457987 | 0.95 | 0.968393 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | fact | fact | 0.443967 | 0.560051 | 1.3 | 0.970361 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.443967 | 0.559943 | 1.3 | 0.970174 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [memoria_historica] fatos canonicos project_facts (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.458035 | 0.665337 | 1.5 | 0.968393 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.360395 | 0.540588 | 1.5 | 0.999992 | STATUS.md |
| 3 | run_summary | run_summary | 0.489869 | 0.45084 | 0.95 | 0.968767 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 4 | fact | fact | 0.360395 | 0.539999 | 1.5 | 0.998902 | STATUS.md |
| 5 | fact | fact | 0.360395 | 0.535919 | 1.5 | 0.991355 | STATUS.md |

### [tecnico_semantico] ranking debug score_final (semantic)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.272787 | 0.259145 | 0.95 | 0.999991 | STATUS.md |
| 2 | run_summary | run_summary | 0.272409 | 0.256551 | 0.95 | 0.991355 | STATUS.md |
| 3 | run_summary | run_summary | 0.273559 | 0.25609 | 0.95 | 0.985414 | STATUS.md |
| 4 | run_summary | run_summary | 0.276264 | 0.256062 | 0.95 | 0.975658 | STATUS.md |
| 5 | run_summary | run_summary | 0.274291 | 0.254757 | 0.95 | 0.977668 | STATUS.md |

### [tecnico_semantico] realtime (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.322266 | 0.344047 | 1.1 | 0.970533 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | fact | fact | 0.314163 | 0.335336 | 1.1 | 0.970359 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.288644 | 0.317159 | 1.1 | 0.998901 | STATUS.md |
| 4 | fact | fact | 0.28764 | 0.316364 | 1.1 | 0.999874 | STATUS.md |
| 5 | fact | fact | 0.28772 | 0.31614 | 1.1 | 0.998887 | STATUS.md |

### [tecnico_semantico] knowledge_search ranking (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.331335 | 0.496997 | 1.5 | 0.99999 | STATUS.md |
| 2 | fact | fact | 0.331335 | 0.496456 | 1.5 | 0.9989 | STATUS.md |
| 3 | fact | fact | 0.331335 | 0.492705 | 1.5 | 0.991353 | STATUS.md |
| 4 | fact | fact | 0.331335 | 0.483851 | 1.5 | 0.973538 | STATUS.md |
| 5 | fact | fact | 0.331297 | 0.483795 | 1.5 | 0.973538 | STATUS.md |

## Calibration Hints (No Weight Change Applied)

- If `top3_dominated_by_*` is frequent: tighten diversity cap or add per-category rules.
- If `absence_of_fact_in_operational_query` appears: increase fact prior in hybrid for operational categories.
- If `run_summary_dominates_where_fact_expected` appears: reduce run_summary baseline in merge stage.
- If decision queries over-return chunks: add stronger fact_type bias for decision/risk intents.
