# Project Brain Ranking Offline Eval

## Objetivo
Rodar uma bateria pequena e repetivel de queries reais do Livecopilot para medir qualidade pratica do ranking (semantic/hybrid) antes de qualquer ajuste de pesos.

Escopo:
- medicao e diagnostico
- sem mudanca estrutural no banco
- sem ajuste de pesos nesta rodada

## Script
- `scripts/eval_project_brain_ranking_offline.py`
- caminho operacional de consulta usado internamente: `scripts/project_brain_query.sh`

## Como rodar
Execucao padrao:
```bash
./scripts/eval_project_brain_ranking_offline.py --project livecopilot
```

Com bateria customizada:
```bash
./scripts/eval_project_brain_ranking_offline.py \
  --project livecopilot \
  --queries-file docs/continuity/examples/project_brain_ranking_eval_queries.json
```

Saidas geradas:
- `docs/continuity/evals/project_brain_ranking_eval_<timestamp>.json`
- `docs/continuity/evals/project_brain_ranking_eval_<timestamp>.md`
- `docs/continuity/evals/latest_project_brain_ranking_eval.json`
- `docs/continuity/evals/latest_project_brain_ranking_eval.md`

## Bateria inicial
Arquivo canonico:
- `docs/continuity/examples/project_brain_ranking_eval_queries.json`

Categorias cobertas:
- continuidade operacional
- estado recente
- decisoes do projeto
- riscos/bloqueios
- memoria historica
- consultas tecnico-semanticas

## O que o relatorio coleta por query
- `query`
- `mode` (`semantic`/`hybrid`)
- top 5 de `semantic_hits`
- `memory_type` e `source_type` por hit
- `score_original`, `type_weight`, `recency_weight`, `score_final` (via `--debug-ranking`)
- `memory_types_detected`
- observacoes automaticas de diversidade/dominancia

## Heuristicas automaticas atuais
- `top3_dominated_by_<type>`
- `absence_of_fact_in_operational_query`
- `excess_memory_chunk_for_decision_query`
- `run_summary_dominates_where_fact_expected`
- `diversity_good` / `diversity_low`

## Leitura rapida dos resultados
- priorizar `observation_distribution` no consolidado
- validar se queries de operacao/decisao retornam `fact` com boa presenca
- investigar casos com dominancia excessiva no top 3
- usar `score_final` + componentes para explicar comportamento de ranking

## Proximos ajustes sugeridos
- calibrar `max_share` de diversidade por categoria de query
- revisar baseline de `run_summary` quando houver dominancia em consultas de decisao/risco
- ajustar bias por `fact_type` apenas apos 2+ rodadas de medicao comparavel

Comparacao before/after (calibracao controlada):
- resumo: `docs/continuity/ROUND_SUMMARY_PROJECT_BRAIN_RANKING_CALIBRATION_CONTROLLED.md`
