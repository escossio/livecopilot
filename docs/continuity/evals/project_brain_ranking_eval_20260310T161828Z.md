# Project Brain Ranking Offline Eval

generated_at: 20260310T161828Z
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

- fact: 57
- run_summary: 23

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
| 1 | fact | fact | 0.538313 | 0.788776 | 1.5 | 0.976849 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.574161 | 0.617194 | 1.1 | 0.977226 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 3 | fact | fact | 0.555044 | 0.596566 | 1.1 | 0.977099 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.54452 | 0.58526 | 1.1 | 0.977108 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.510075 | 0.553343 | 1.1 | 0.986206 | STATUS.md |

### [continuidade_operacional] checkpoint da rodada (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.561487 | 0.613941 | 1.1 | 0.994019 | STATUS.md |
| 2 | fact | fact | 0.561376 | 0.608995 | 1.1 | 0.986205 | STATUS.md |
| 3 | fact | fact | 0.562189 | 0.608435 | 1.1 | 0.983873 | STATUS.md |
| 4 | fact | fact | 0.561403 | 0.607577 | 1.1 | 0.983862 | STATUS.md |
| 5 | fact | fact | 0.561069 | 0.607411 | 1.1 | 0.984178 | STATUS.md |

### [continuidade_operacional] new chat context (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.315086 | 0.339319 | 1.1 | 0.979008 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | run_summary | run_summary | 0.290756 | 0.284652 | 1.0 | 0.979008 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.245519 | 0.264354 | 1.1 | 0.978832 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | run_summary | run_summary | 0.207854 | 0.204462 | 1.0 | 0.98368 | STATUS.md |
| 5 | fact | fact | 0.223953 | 0.242328 | 1.1 | 0.98368 | STATUS.md |

### [estado_recente] ultimo closeout (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.421479 | 0.4553 | 1.1 | 0.982039 | STATUS.md |
| 2 | fact | fact | 0.418062 | 0.451608 | 1.1 | 0.982039 | STATUS.md |
| 3 | run_summary | run_summary | 0.431286 | 0.42354 | 1.0 | 0.982039 | STATUS.md |
| 4 | run_summary | run_summary | 0.428917 | 0.421213 | 1.0 | 0.982039 | STATUS.md |
| 5 | run_summary | run_summary | 0.371798 | 0.366669 | 1.0 | 0.986204 | STATUS.md |

### [estado_recente] smoke round continuity (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.558719 | 0.610913 | 1.1 | 0.994016 | STATUS.md |
| 2 | fact | fact | 0.559202 | 0.605201 | 1.1 | 0.983871 | STATUS.md |
| 3 | run_summary | run_summary | 0.596982 | 0.59341 | 1.0 | 0.994016 | STATUS.md |
| 4 | run_summary | run_summary | 0.59915 | 0.589669 | 1.0 | 0.984176 | STATUS.md |
| 5 | fact | fact | 0.557364 | 0.603399 | 1.1 | 0.984176 | STATUS.md |

### [estado_recente] embedding maintenance (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.343937 | 0.439087 | 1.3 | 0.982038 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.343937 | 0.437653 | 1.3 | 0.97883 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.414223 | 0.406783 | 1.0 | 0.982038 | STATUS.md |
| 4 | run_summary | run_summary | 0.377001 | 0.370229 | 1.0 | 0.982038 | STATUS.md |
| 5 | fact | fact | 0.343937 | 0.437569 | 1.3 | 0.978642 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [decisoes_projeto] separacao question_bank knowledge (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.62587 | 0.923652 | 1.5 | 0.983859 | STATUS.md |
| 2 | fact | fact | 0.62587 | 0.923482 | 1.5 | 0.983678 | STATUS.md |
| 3 | fact | fact | 0.625929 | 0.922028 | 1.5 | 0.982037 | STATUS.md |
| 4 | fact | fact | 0.62587 | 0.921941 | 1.5 | 0.982037 | STATUS.md |
| 5 | fact | fact | 0.62587 | 0.919095 | 1.5 | 0.979005 | STATUS.md |

### [decisoes_projeto] adotar 3 niveis de continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.622851 | 0.912643 | 1.5 | 0.976845 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.497197 | 0.534394 | 1.1 | 0.977104 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.457992 | 0.447387 | 1.0 | 0.976845 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | run_summary | run_summary | 0.457644 | 0.447161 | 1.0 | 0.977094 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.494533 | 0.531595 | 1.1 | 0.977222 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |

### [decisoes_projeto] comando padrao operador scripts round (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.429411 | 0.461537 | 1.1 | 0.977103 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.426096 | 0.458694 | 1.1 | 0.978641 | STATUS.md |
| 3 | run_summary | run_summary | 0.446422 | 0.44375 | 1.0 | 0.994014 | STATUS.md |
| 4 | run_summary | run_summary | 0.447533 | 0.441357 | 1.0 | 0.986201 | STATUS.md |
| 5 | run_summary | run_summary | 0.447509 | 0.440426 | 1.0 | 0.984173 | STATUS.md |

### [riscos_bloqueios] risco runuser postgres peer auth (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.618741 | 0.732243 | 1.2 | 0.9862 | STATUS.md |
| 2 | fact | fact | 0.618741 | 0.730738 | 1.2 | 0.984173 | STATUS.md |
| 3 | fact | fact | 0.618741 | 0.730511 | 1.2 | 0.983868 | STATUS.md |
| 4 | fact | fact | 0.618741 | 0.730503 | 1.2 | 0.983857 | STATUS.md |
| 5 | fact | fact | 0.618741 | 0.730369 | 1.2 | 0.983676 | STATUS.md |

### [riscos_bloqueios] drift de embeddings (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.199733 | 0.294217 | 1.5 | 0.982034 | STATUS.md |
| 2 | fact | fact | 0.199733 | 0.293309 | 1.5 | 0.979003 | STATUS.md |
| 3 | run_summary | run_summary | 0.240703 | 0.236379 | 1.0 | 0.982034 | STATUS.md |
| 4 | run_summary | run_summary | 0.224333 | 0.220671 | 1.0 | 0.983675 | STATUS.md |
| 5 | fact | fact | 0.199733 | 0.293256 | 1.5 | 0.978827 | STATUS.md |

### [memoria_historica] mvp continuidade (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.558973 | 0.819043 | 1.5 | 0.976842 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.443967 | 0.566788 | 1.3 | 0.982034 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.497826 | 0.486297 | 1.0 | 0.976842 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | fact | fact | 0.443967 | 0.564937 | 1.3 | 0.978827 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.443967 | 0.564828 | 1.3 | 0.978639 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [memoria_historica] fatos canonicos project_facts (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.458035 | 0.671141 | 1.5 | 0.976841 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.360395 | 0.53088 | 1.5 | 0.982033 | STATUS.md |
| 3 | run_summary | run_summary | 0.489869 | 0.478709 | 1.0 | 0.977218 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 4 | fact | fact | 0.360372 | 0.530846 | 1.5 | 0.982033 | STATUS.md |
| 5 | fact | fact | 0.360372 | 0.529112 | 1.5 | 0.978826 | STATUS.md |

### [tecnico_semantico] ranking debug score_final (semantic)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.2736 | 0.271961 | 1.0 | 0.994011 | STATUS.md |
| 2 | run_summary | run_summary | 0.276303 | 0.271929 | 1.0 | 0.98417 | STATUS.md |
| 3 | run_summary | run_summary | 0.274326 | 0.27054 | 1.0 | 0.986197 | STATUS.md |
| 4 | run_summary | run_summary | 0.273282 | 0.268873 | 1.0 | 0.983866 | STATUS.md |
| 5 | run_summary | run_summary | 0.273081 | 0.268672 | 1.0 | 0.983854 | STATUS.md |

### [tecnico_semantico] realtime (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.322325 | 0.347112 | 1.1 | 0.979 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | fact | fact | 0.314248 | 0.338353 | 1.1 | 0.978825 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.287877 | 0.314768 | 1.1 | 0.99401 | STATUS.md |
| 4 | fact | fact | 0.288964 | 0.312671 | 1.1 | 0.983673 | STATUS.md |
| 5 | fact | fact | 0.288529 | 0.312261 | 1.1 | 0.983865 | STATUS.md |

### [tecnico_semantico] knowledge_search ranking (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.331295 | 0.488918 | 1.5 | 0.983853 | STATUS.md |
| 2 | fact | fact | 0.331295 | 0.488828 | 1.5 | 0.983672 | STATUS.md |
| 3 | fact | fact | 0.331333 | 0.488069 | 1.5 | 0.982031 | STATUS.md |
| 4 | fact | fact | 0.331295 | 0.488013 | 1.5 | 0.982031 | STATUS.md |
| 5 | fact | fact | 0.331295 | 0.486506 | 1.5 | 0.978999 | STATUS.md |

## Calibration Hints (No Weight Change Applied)

- If `top3_dominated_by_*` is frequent: tighten diversity cap or add per-category rules.
- If `absence_of_fact_in_operational_query` appears: increase fact prior in hybrid for operational categories.
- If `run_summary_dominates_where_fact_expected` appears: reduce run_summary baseline in merge stage.
- If decision queries over-return chunks: add stronger fact_type bias for decision/risk intents.
