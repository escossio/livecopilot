# Project Brain Ranking Offline Eval

generated_at: 20260310T222844Z
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
| 1 | fact | fact | 0.538303 | 0.78203 | 1.5 | 0.968512 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.574145 | 0.611909 | 1.1 | 0.968886 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 3 | fact | fact | 0.555038 | 0.591468 | 1.1 | 0.96876 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.544491 | 0.580235 | 1.1 | 0.968769 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.510506 | 0.561001 | 1.1 | 0.999011 | STATUS.md |

### [continuidade_operacional] checkpoint da rodada (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.563385 | 0.619722 | 1.1 | 0.999998 | STATUS.md |
| 2 | fact | fact | 0.563119 | 0.618818 | 1.1 | 0.99901 | STATUS.md |
| 3 | fact | fact | 0.562908 | 0.618595 | 1.1 | 0.999025 | STATUS.md |
| 4 | fact | fact | 0.561561 | 0.608782 | 1.1 | 0.985535 | STATUS.md |
| 5 | fact | fact | 0.56145 | 0.603877 | 1.1 | 0.977788 | STATUS.md |

### [continuidade_operacional] new chat context (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.315125 | 0.336465 | 1.1 | 0.970653 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | run_summary | run_summary | 0.290814 | 0.282279 | 1.0 | 0.970653 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.245579 | 0.262162 | 1.1 | 0.970479 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | run_summary | run_summary | 0.207882 | 0.202744 | 1.0 | 0.975285 | STATUS.md |
| 5 | fact | fact | 0.224024 | 0.240336 | 1.1 | 0.975285 | STATUS.md |

### [estado_recente] ultimo closeout (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.421492 | 0.451428 | 1.1 | 0.973658 | STATUS.md |
| 2 | fact | fact | 0.418072 | 0.447765 | 1.1 | 0.973658 | STATUS.md |
| 3 | run_summary | run_summary | 0.43125 | 0.41989 | 1.0 | 0.973658 | STATUS.md |
| 4 | run_summary | run_summary | 0.428896 | 0.417598 | 1.0 | 0.973658 | STATUS.md |
| 5 | run_summary | run_summary | 0.369467 | 0.369106 | 1.0 | 0.999024 | STATUS.md |

### [estado_recente] smoke round continuity (hybrid)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'absence_of_fact_in_operational_query', 'diversity_low', 'hybrid_without_fact_memory_type']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.595245 | 0.594655 | 1.0 | 0.999008 | STATUS.md |
| 2 | run_summary | run_summary | 0.594287 | 0.594285 | 1.0 | 0.999996 | STATUS.md |
| 3 | run_summary | run_summary | 0.589502 | 0.588926 | 1.0 | 0.999023 | STATUS.md |
| 4 | run_summary | run_summary | 0.596922 | 0.588286 | 1.0 | 0.985533 | STATUS.md |
| 5 | run_summary | run_summary | 0.599088 | 0.584576 | 1.0 | 0.975776 | STATUS.md |

### [estado_recente] embedding maintenance (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.343893 | 0.435284 | 1.3 | 0.973656 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.343893 | 0.433862 | 1.3 | 0.970477 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.414119 | 0.40321 | 1.0 | 0.973656 | STATUS.md |
| 4 | run_summary | run_summary | 0.376891 | 0.366962 | 1.0 | 0.973656 | STATUS.md |
| 5 | fact | fact | 0.343893 | 0.433779 | 1.3 | 0.97029 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [decisoes_projeto] separacao question_bank knowledge (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.625987 | 0.938062 | 1.5 | 0.999022 | STATUS.md |
| 2 | fact | fact | 0.625987 | 0.930975 | 1.5 | 0.991474 | STATUS.md |
| 3 | fact | fact | 0.625929 | 0.915687 | 1.5 | 0.975283 | STATUS.md |
| 4 | fact | fact | 0.625987 | 0.914244 | 1.5 | 0.973656 | STATUS.md |
| 5 | fact | fact | 0.625929 | 0.914159 | 1.5 | 0.973656 | STATUS.md |

### [decisoes_projeto] adotar 3 niveis de continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.622805 | 0.904787 | 1.5 | 0.968508 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.497272 | 0.529913 | 1.1 | 0.968765 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.457932 | 0.443511 | 1.0 | 0.968508 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | run_summary | run_summary | 0.457659 | 0.44336 | 1.0 | 0.968755 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.49461 | 0.52714 | 1.1 | 0.968882 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |

### [decisoes_projeto] comando padrao operador scripts round (hybrid)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'run_summary_dominates_where_fact_expected', 'diversity_low', 'hybrid_without_fact_memory_type']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.447049 | 0.446611 | 1.0 | 0.99902 | STATUS.md |
| 2 | run_summary | run_summary | 0.446756 | 0.446312 | 1.0 | 0.999006 | STATUS.md |
| 3 | run_summary | run_summary | 0.445122 | 0.441326 | 1.0 | 0.991472 | STATUS.md |
| 4 | run_summary | run_summary | 0.446475 | 0.440015 | 1.0 | 0.985531 | STATUS.md |
| 5 | run_summary | run_summary | 0.44758 | 0.437637 | 1.0 | 0.977784 | STATUS.md |

### [riscos_bloqueios] risco runuser postgres peer auth (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.618797 | 0.726059 | 1.2 | 0.977783 | STATUS.md |
| 2 | fact | fact | 0.618797 | 0.724567 | 1.2 | 0.975773 | STATUS.md |
| 3 | fact | fact | 0.618797 | 0.724343 | 1.2 | 0.975471 | STATUS.md |
| 4 | fact | fact | 0.618797 | 0.724334 | 1.2 | 0.97546 | STATUS.md |
| 5 | fact | fact | 0.618797 | 0.724201 | 1.2 | 0.975281 | STATUS.md |

### [riscos_bloqueios] drift de embeddings (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.199733 | 0.291706 | 1.5 | 0.973653 | STATUS.md |
| 2 | fact | fact | 0.199733 | 0.290805 | 1.5 | 0.970647 | STATUS.md |
| 3 | run_summary | run_summary | 0.240703 | 0.234361 | 1.0 | 0.973653 | STATUS.md |
| 4 | run_summary | run_summary | 0.224333 | 0.218788 | 1.0 | 0.97528 | STATUS.md |
| 5 | fact | fact | 0.199733 | 0.290753 | 1.5 | 0.970474 | STATUS.md |

### [memoria_historica] mvp continuidade (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.558973 | 0.812052 | 1.5 | 0.968505 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.443967 | 0.561951 | 1.3 | 0.973653 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.497826 | 0.482147 | 1.0 | 0.968505 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | fact | fact | 0.443967 | 0.560115 | 1.3 | 0.970473 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.443967 | 0.560008 | 1.3 | 0.970286 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [memoria_historica] fatos canonicos project_facts (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.457965 | 0.665312 | 1.5 | 0.968505 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.360349 | 0.539993 | 1.5 | 0.999018 | STATUS.md |
| 3 | run_summary | run_summary | 0.489878 | 0.474632 | 1.0 | 0.968878 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 4 | fact | fact | 0.360349 | 0.535913 | 1.5 | 0.99147 | STATUS.md |
| 5 | fact | fact | 0.360349 | 0.526282 | 1.5 | 0.973652 | STATUS.md |

### [tecnico_semantico] ranking debug score_final (semantic)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.272449 | 0.270125 | 1.0 | 0.991469 | STATUS.md |
| 2 | run_summary | run_summary | 0.2736 | 0.26964 | 1.0 | 0.985527 | STATUS.md |
| 3 | run_summary | run_summary | 0.276303 | 0.269608 | 1.0 | 0.975771 | STATUS.md |
| 4 | run_summary | run_summary | 0.274326 | 0.268231 | 1.0 | 0.977781 | STATUS.md |
| 5 | run_summary | run_summary | 0.273282 | 0.266578 | 1.0 | 0.975469 | STATUS.md |

### [tecnico_semantico] realtime (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.322266 | 0.344086 | 1.1 | 0.970645 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | fact | fact | 0.314163 | 0.335375 | 1.1 | 0.970471 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.288644 | 0.317196 | 1.1 | 0.999016 | STATUS.md |
| 4 | fact | fact | 0.28764 | 0.316401 | 1.1 | 0.99999 | STATUS.md |
| 5 | fact | fact | 0.28772 | 0.316176 | 1.1 | 0.999002 | STATUS.md |

### [tecnico_semantico] knowledge_search ranking (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.33129 | 0.496446 | 1.5 | 0.999016 | STATUS.md |
| 2 | fact | fact | 0.33129 | 0.492695 | 1.5 | 0.991468 | STATUS.md |
| 3 | fact | fact | 0.33129 | 0.483841 | 1.5 | 0.97365 | STATUS.md |
| 4 | fact | fact | 0.331253 | 0.483787 | 1.5 | 0.97365 | STATUS.md |
| 5 | fact | fact | 0.331253 | 0.482293 | 1.5 | 0.970644 | STATUS.md |

## Calibration Hints (No Weight Change Applied)

- If `top3_dominated_by_*` is frequent: tighten diversity cap or add per-category rules.
- If `absence_of_fact_in_operational_query` appears: increase fact prior in hybrid for operational categories.
- If `run_summary_dominates_where_fact_expected` appears: reduce run_summary baseline in merge stage.
- If decision queries over-return chunks: add stronger fact_type bias for decision/risk intents.
