# Project Brain Ranking Offline Eval

generated_at: 20260310T161916Z
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

- fact: 56
- run_summary: 24

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
| 1 | fact | fact | 0.538341 | 0.788802 | 1.5 | 0.976831 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.574187 | 0.61721 | 1.1 | 0.977208 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 3 | fact | fact | 0.555077 | 0.596591 | 1.1 | 0.977081 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 4 | fact | fact | 0.544534 | 0.585265 | 1.1 | 0.97709 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.510088 | 0.553347 | 1.1 | 0.986188 | STATUS.md |

### [continuidade_operacional] checkpoint da rodada (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.560465 | 0.616507 | 1.1 | 0.999993 | STATUS.md |
| 2 | fact | fact | 0.561487 | 0.61393 | 1.1 | 0.994 | STATUS.md |
| 3 | fact | fact | 0.561376 | 0.608984 | 1.1 | 0.986187 | STATUS.md |
| 4 | fact | fact | 0.562189 | 0.608424 | 1.1 | 0.983855 | STATUS.md |
| 5 | fact | fact | 0.561403 | 0.607566 | 1.1 | 0.983844 | STATUS.md |

### [continuidade_operacional] new chat context (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.315086 | 0.339313 | 1.1 | 0.97899 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | run_summary | run_summary | 0.290756 | 0.284647 | 1.0 | 0.97899 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.245519 | 0.264349 | 1.1 | 0.978814 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 4 | run_summary | run_summary | 0.207854 | 0.204458 | 1.0 | 0.983662 | STATUS.md |
| 5 | fact | fact | 0.223953 | 0.242324 | 1.1 | 0.983662 | STATUS.md |

### [estado_recente] ultimo closeout (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.421479 | 0.455291 | 1.1 | 0.982021 | STATUS.md |
| 2 | fact | fact | 0.418062 | 0.4516 | 1.1 | 0.982021 | STATUS.md |
| 3 | run_summary | run_summary | 0.431286 | 0.423532 | 1.0 | 0.982021 | STATUS.md |
| 4 | run_summary | run_summary | 0.428917 | 0.421205 | 1.0 | 0.982021 | STATUS.md |
| 5 | run_summary | run_summary | 0.371798 | 0.366662 | 1.0 | 0.986186 | STATUS.md |

### [estado_recente] smoke round continuity (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.558709 | 0.610891 | 1.1 | 0.993998 | STATUS.md |
| 2 | fact | fact | 0.559194 | 0.605181 | 1.1 | 0.983853 | STATUS.md |
| 3 | run_summary | run_summary | 0.596951 | 0.593368 | 1.0 | 0.993998 | STATUS.md |
| 4 | run_summary | run_summary | 0.599118 | 0.589627 | 1.0 | 0.984158 | STATUS.md |
| 5 | run_summary | run_summary | 0.589062 | 0.589057 | 1.0 | 0.999991 | STATUS.md |

### [estado_recente] embedding maintenance (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.343937 | 0.439079 | 1.3 | 0.982019 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.343937 | 0.437645 | 1.3 | 0.978812 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.414223 | 0.406775 | 1.0 | 0.982019 | STATUS.md |
| 4 | run_summary | run_summary | 0.377001 | 0.370222 | 1.0 | 0.982019 | STATUS.md |
| 5 | fact | fact | 0.343937 | 0.437561 | 1.3 | 0.978624 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [decisoes_projeto] separacao question_bank knowledge (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.625929 | 0.938884 | 1.5 | 0.99999 | STATUS.md |
| 2 | fact | fact | 0.62587 | 0.923465 | 1.5 | 0.98366 | STATUS.md |
| 3 | fact | fact | 0.625929 | 0.922011 | 1.5 | 0.982019 | STATUS.md |
| 4 | fact | fact | 0.62587 | 0.921924 | 1.5 | 0.982019 | STATUS.md |
| 5 | fact | fact | 0.62587 | 0.919078 | 1.5 | 0.978987 | STATUS.md |

### [decisoes_projeto] adotar 3 niveis de continuidade (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.622851 | 0.912626 | 1.5 | 0.976827 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.497197 | 0.534384 | 1.1 | 0.977086 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.457992 | 0.447379 | 1.0 | 0.976827 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | run_summary | run_summary | 0.457644 | 0.447153 | 1.0 | 0.977076 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.494533 | 0.531585 | 1.1 | 0.977204 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |

### [decisoes_projeto] comando padrao operador scripts round (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.429411 | 0.461528 | 1.1 | 0.977085 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 2 | fact | fact | 0.426096 | 0.458686 | 1.1 | 0.978622 | STATUS.md |
| 3 | run_summary | run_summary | 0.445073 | 0.445068 | 1.0 | 0.999988 | STATUS.md |
| 4 | run_summary | run_summary | 0.446422 | 0.443741 | 1.0 | 0.993996 | STATUS.md |
| 5 | run_summary | run_summary | 0.447533 | 0.441349 | 1.0 | 0.986182 | STATUS.md |

### [riscos_bloqueios] risco runuser postgres peer auth (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.618719 | 0.732203 | 1.2 | 0.986182 | STATUS.md |
| 2 | fact | fact | 0.618719 | 0.730698 | 1.2 | 0.984154 | STATUS.md |
| 3 | fact | fact | 0.618719 | 0.730472 | 1.2 | 0.98385 | STATUS.md |
| 4 | fact | fact | 0.618719 | 0.730464 | 1.2 | 0.983839 | STATUS.md |
| 5 | fact | fact | 0.618719 | 0.730329 | 1.2 | 0.983658 | STATUS.md |

### [riscos_bloqueios] drift de embeddings (hybrid)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.203166 | 0.299268 | 1.5 | 0.982016 | STATUS.md |
| 2 | fact | fact | 0.203166 | 0.298345 | 1.5 | 0.978985 | STATUS.md |
| 3 | run_summary | run_summary | 0.243698 | 0.239315 | 1.0 | 0.982016 | STATUS.md |
| 4 | run_summary | run_summary | 0.226672 | 0.222968 | 1.0 | 0.983657 | STATUS.md |
| 5 | fact | fact | 0.203166 | 0.298291 | 1.5 | 0.978809 | STATUS.md |

### [memoria_historica] mvp continuidade (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.558955 | 0.819001 | 1.5 | 0.976824 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.443894 | 0.566684 | 1.3 | 0.982015 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 3 | run_summary | run_summary | 0.497776 | 0.486239 | 1.0 | 0.976824 | docs/continuity/ROUND_SUMMARY_CONTINUITY_MVP.md |
| 4 | fact | fact | 0.443894 | 0.564833 | 1.3 | 0.978808 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |
| 5 | fact | fact | 0.443894 | 0.564725 | 1.3 | 0.97862 | docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md |

### [memoria_historica] fatos canonicos project_facts (semantic)

- semantic_warning: None
- memory_types_detected: ['fact', 'run_summary']
- observations: ['diversity_good']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.458067 | 0.671176 | 1.5 | 0.976823 | docs/continuity/CONTINUITY_MVP.md |
| 2 | fact | fact | 0.360432 | 0.54064 | 1.5 | 0.999986 | STATUS.md |
| 3 | run_summary | run_summary | 0.489947 | 0.478776 | 1.0 | 0.9772 | docs/continuity/ROUND_SUMMARY_CONTINUITY_FACTS_ENRICHMENT.md |
| 4 | fact | fact | 0.360432 | 0.530924 | 1.5 | 0.982015 | STATUS.md |
| 5 | fact | fact | 0.360409 | 0.529157 | 1.5 | 0.978808 | STATUS.md |

### [tecnico_semantico] ranking debug score_final (semantic)

- semantic_warning: None
- memory_types_detected: ['run_summary']
- observations: ['top3_dominated_by_run_summary', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | run_summary | run_summary | 0.272449 | 0.272445 | 1.0 | 0.999985 | STATUS.md |
| 2 | run_summary | run_summary | 0.2736 | 0.271956 | 1.0 | 0.993992 | STATUS.md |
| 3 | run_summary | run_summary | 0.276303 | 0.271924 | 1.0 | 0.984152 | STATUS.md |
| 4 | run_summary | run_summary | 0.274326 | 0.270535 | 1.0 | 0.986179 | STATUS.md |
| 5 | run_summary | run_summary | 0.273282 | 0.268868 | 1.0 | 0.983847 | STATUS.md |

### [tecnico_semantico] realtime (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.322325 | 0.347105 | 1.1 | 0.978982 | /lab/projects/livecopilot/.supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 2 | fact | fact | 0.314248 | 0.338347 | 1.1 | 0.978806 | .supervisor/checkpoints/20260307T1525316252060000_run_once.md |
| 3 | fact | fact | 0.286878 | 0.315561 | 1.1 | 0.999984 | STATUS.md |
| 4 | fact | fact | 0.287877 | 0.314762 | 1.1 | 0.993991 | STATUS.md |
| 5 | fact | fact | 0.288964 | 0.312665 | 1.1 | 0.983654 | STATUS.md |

### [tecnico_semantico] knowledge_search ranking (semantic)

- semantic_warning: None
- memory_types_detected: ['fact']
- observations: ['top3_dominated_by_fact', 'diversity_low']

Top 5 semantic hits:

| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fact | fact | 0.331333 | 0.496991 | 1.5 | 0.999984 | STATUS.md |
| 2 | fact | fact | 0.331295 | 0.488819 | 1.5 | 0.983654 | STATUS.md |
| 3 | fact | fact | 0.331333 | 0.48806 | 1.5 | 0.982013 | STATUS.md |
| 4 | fact | fact | 0.331295 | 0.488004 | 1.5 | 0.982013 | STATUS.md |
| 5 | fact | fact | 0.331295 | 0.486497 | 1.5 | 0.978981 | STATUS.md |

## Calibration Hints (No Weight Change Applied)

- If `top3_dominated_by_*` is frequent: tighten diversity cap or add per-category rules.
- If `absence_of_fact_in_operational_query` appears: increase fact prior in hybrid for operational categories.
- If `run_summary_dominates_where_fact_expected` appears: reduce run_summary baseline in merge stage.
- If decision queries over-return chunks: add stronger fact_type bias for decision/risk intents.
