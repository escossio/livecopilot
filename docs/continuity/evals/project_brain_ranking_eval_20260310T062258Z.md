# Project Brain Ranking Offline Eval

generated_at: 20260310T062258Z
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
| 1 | fact | fact | 0.538313 | 0.799724 | 1.5 | 0.990408 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.574161 | 0.62576 | 1.1 | 0.99079 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 3 | fact | fact | 0.555044 | 0.604846 | 1.1 | 0.990661 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.54452 | 0.593384 | 1.1 | 0.99067 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.510075 | 0.561023 | 1.1 | 0.999894 | STATUS.md |

### [continuidade_operacional] checkpoint da rodada (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.5615 | 0.617584 | 1.1 | 0.999894 | STATUS.md |
| 2 | fact | fact | 0.562311 | 0.617014 | 1.1 | 0.997529 | STATUS.md |
| 3 | fact | fact | 0.561523 | 0.616142 | 1.1 | 0.997518 | STATUS.md |
| 4 | fact | fact | 0.561191 | 0.615976 | 1.1 | 0.997838 | STATUS.md |
| 5 | fact | fact | 0.541692 | 0.593282 | 1.1 | 0.995671 | STATUS.md |

### [continuidade_operacional] new chat context (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.315086 | 0.344029 | 1.1 | 0.992596 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | run_summary | run_summary | 0.290756 | 0.288603 | 1.0 | 0.992596 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.245519 | 0.268023 | 1.1 | 0.992418 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | fact | fact | 0.223953 | 0.245691 | 1.1 | 0.997334 | STATUS.md |
| 5 | fact | fact | 0.224467 | 0.244995 | 1.1 | 0.992228 | STATUS.md |

### [estado_recente] ultimo closeout (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.421479 | 0.461619 | 1.1 | 0.995669 | STATUS.md |
| 2 | fact | fact | 0.418062 | 0.457877 | 1.1 | 0.995669 | STATUS.md |
| 3 | run_summary | run_summary | 0.431286 | 0.429418 | 1.0 | 0.995669 | STATUS.md |
| 4 | run_summary | run_summary | 0.428917 | 0.42706 | 1.0 | 0.995669 | STATUS.md |
| 5 | run_summary | run_summary | 0.371798 | 0.371758 | 1.0 | 0.999892 | STATUS.md |

### [estado_recente] smoke round continuity (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.559202 | 0.613601 | 1.1 | 0.997527 | STATUS.md |
| 2 | fact | fact | 0.557214 | 0.612869 | 1.1 | 0.999892 | STATUS.md |
| 3 | fact | fact | 0.557364 | 0.611774 | 1.1 | 0.997836 | STATUS.md |
| 4 | fact | fact | 0.556855 | 0.611019 | 1.1 | 0.997516 | STATUS.md |
| 5 | run_summary | run_summary | 0.59915 | 0.597854 | 1.0 | 0.997836 | STATUS.md |

### [estado_recente] embedding maintenance (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.343898 | 0.445131 | 1.3 | 0.995668 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.343898 | 0.443677 | 1.3 | 0.992416 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | fact | fact | 0.343898 | 0.443592 | 1.3 | 0.992226 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.343898 | 0.442948 | 1.3 | 0.990786 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.38816 | 0.425126 | 1.1 | 0.995668 | STATUS.md |

### [decisoes_projeto] separacao question_bank knowledge (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.62587 | 0.936472 | 1.5 | 0.997515 | STATUS.md |
| 2 | fact | fact | 0.62587 | 0.936299 | 1.5 | 0.997331 | STATUS.md |
| 3 | fact | fact | 0.625929 | 0.934826 | 1.5 | 0.995667 | STATUS.md |
| 4 | fact | fact | 0.62587 | 0.934737 | 1.5 | 0.995667 | STATUS.md |
| 5 | fact | fact | 0.62587 | 0.931852 | 1.5 | 0.992594 | STATUS.md |

### [decisoes_projeto] adotar 3 niveis de continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.622868 | 0.925336 | 1.5 | 0.990403 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.497267 | 0.541888 | 1.1 | 0.990666 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | fact | fact | 0.494592 | 0.539038 | 1.1 | 0.990785 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 4 | fact | fact | 0.482818 | 0.526137 | 1.1 | 0.990656 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.446362 | 0.486415 | 1.1 | 0.990666 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [decisoes_projeto] comando padrao operador scripts round (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.429411 | 0.467943 | 1.1 | 0.990665 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.426096 | 0.465061 | 1.1 | 0.992224 | STATUS.md |
| 3 | fact | fact | 0.409946 | 0.4476 | 1.1 | 0.992592 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | run_summary | run_summary | 0.447533 | 0.447483 | 1.0 | 0.999889 | STATUS.md |
| 5 | run_summary | run_summary | 0.447509 | 0.446539 | 1.0 | 0.997833 | STATUS.md |

### [riscos_bloqueios] risco runuser postgres peer auth (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.618719 | 0.74238 | 1.2 | 0.999888 | STATUS.md |
| 2 | fact | fact | 0.618719 | 0.740854 | 1.2 | 0.997833 | STATUS.md |
| 3 | fact | fact | 0.618719 | 0.740625 | 1.2 | 0.997524 | STATUS.md |
| 4 | fact | fact | 0.618719 | 0.740616 | 1.2 | 0.997513 | STATUS.md |
| 5 | fact | fact | 0.618719 | 0.74048 | 1.2 | 0.997329 | STATUS.md |

### [riscos_bloqueios] drift de embeddings (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.199733 | 0.298301 | 1.5 | 0.995665 | STATUS.md |
| 2 | fact | fact | 0.199733 | 0.29738 | 1.5 | 0.992591 | STATUS.md |
| 3 | fact | fact | 0.199733 | 0.297327 | 1.5 | 0.992413 | STATUS.md |
| 4 | fact | fact | 0.199733 | 0.297269 | 1.5 | 0.992223 | STATUS.md |
| 5 | fact | fact | 0.199733 | 0.296838 | 1.5 | 0.990783 | STATUS.md |

### [memoria_historica] mvp continuidade (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.558937 | 0.830357 | 1.5 | 0.9904 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.443871 | 0.57453 | 1.3 | 0.995664 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | fact | fact | 0.443871 | 0.572654 | 1.3 | 0.992413 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.443871 | 0.572544 | 1.3 | 0.992222 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.443871 | 0.571714 | 1.3 | 0.990783 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [memoria_historica] fatos canonicos project_facts (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.458067 | 0.680504 | 1.5 | 0.9904 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.360432 | 0.538304 | 1.5 | 0.995664 | STATUS.md |
| 3 | fact | fact | 0.360409 | 0.538269 | 1.5 | 0.995664 | STATUS.md |
| 4 | fact | fact | 0.360409 | 0.536511 | 1.5 | 0.992412 | STATUS.md |
| 5 | fact | fact | 0.360409 | 0.53563 | 1.5 | 0.990782 | STATUS.md |

### [tecnico_semantico] ranking debug score_final (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_run_summary', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.276303 | 0.275703 | 1.0 | 0.99783 | STATUS.md |
| 2 | run_summary | run_summary | 0.274326 | 0.274295 | 1.0 | 0.999886 | STATUS.md |
| 3 | run_summary | run_summary | 0.273282 | 0.272605 | 1.0 | 0.997522 | STATUS.md |
| 4 | run_summary | run_summary | 0.273081 | 0.272401 | 1.0 | 0.99751 | STATUS.md |
| 5 | run_summary | run_summary | 0.273094 | 0.27191 | 1.0 | 0.995663 | STATUS.md |

### [tecnico_semantico] realtime (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.322325 | 0.35193 | 1.1 | 0.992589 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | fact | fact | 0.314248 | 0.343049 | 1.1 | 0.992411 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.288964 | 0.31701 | 1.1 | 0.997326 | STATUS.md |
| 4 | fact | fact | 0.288529 | 0.316595 | 1.1 | 0.997521 | STATUS.md |
| 5 | fact | fact | 0.287574 | 0.315544 | 1.1 | 0.997509 | STATUS.md |

### [tecnico_semantico] knowledge_search ranking (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.331295 | 0.495705 | 1.5 | 0.997509 | STATUS.md |
| 2 | fact | fact | 0.331295 | 0.495613 | 1.5 | 0.997325 | STATUS.md |
| 3 | fact | fact | 0.331333 | 0.494843 | 1.5 | 0.995662 | STATUS.md |
| 4 | fact | fact | 0.331295 | 0.494787 | 1.5 | 0.995662 | STATUS.md |
| 5 | fact | fact | 0.331295 | 0.493259 | 1.5 | 0.992588 | STATUS.md |

## Calibration Hints (No Weight Change Applied)

- If `top3_dominated_by_*` is frequent: tighten diversity cap or add per-category rules.
- If `absence_of_fact_in_operational_query` appears: increase fact prior in hybrid for operational categories.
- If `run_summary_dominates_where_fact_expected` appears: reduce run_summary baseline in merge stage.
- If decision queries over-return chunks: add stronger fact_type bias for decision/risk intents.
