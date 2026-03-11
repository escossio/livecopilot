# Round Summary: Controlled Calibration of Project Brain Ranking

## Objetivo
Executar uma calibracao conservadora e reversivel para reduzir dominancia de `fact` e melhorar diversidade no top-N, usando a bateria offline existente como baseline.

## Baseline (antes da mudanca)
- arquivo: `docs/continuity/evals/project_brain_ranking_eval_20260310T115749Z.json`
- queries: 16
- distribuicao global top5:
  - `fact=68`
  - `run_summary=12`
- sinais:
  - `top3_dominated_by_fact=13`
  - `top3_dominated_by_run_summary=1`
  - `diversity_low=12`
  - `diversity_good=4`

## Mudanca aplicada (unica rodada)
Arquivo alterado: `scripts/project_brain_query.py`

Mudanca cirurgica:
- no ranking de `semantic_hits`, cap de diversidade por tipo ajustado de `max_share=0.6` para `max_share=0.25`.

Racional:
- reduzir dominancia de um unico `memory_type` no topo quando houver opcoes alternativas ja ranqueadas.
- manter pesos e recencia intactos nesta rodada para isolar efeito da diversidade.

## Resultado (depois da mudanca)
- arquivo: `docs/continuity/evals/project_brain_ranking_eval_20260310T115836Z.json`
- queries: 16
- distribuicao global top5:
  - `fact=58` (antes 68)
  - `run_summary=22` (antes 12)
- sinais:
  - `top3_dominated_by_fact=5` (antes 13)
  - `top3_dominated_by_run_summary=0` (antes 1)
  - `diversity_low=5` (antes 12)
  - `diversity_good=11` (antes 4)

## Exemplos concretos
Melhoras observadas:
- `adotar 3 niveis de continuidade`: top3 `fact,fact,fact` -> `fact,fact,run_summary`
- `drift de embeddings`: top3 `fact,fact,fact` -> `fact,fact,run_summary`
- `realtime`: top3 `fact,fact,fact` -> `fact,fact,run_summary`
- `ranking debug score_final`: top3 `run_summary,run_summary,run_summary` -> `run_summary,run_summary,fact`

Pioras observadas:
- nenhuma piora detectada nas heuristicas alvo desta rodada.

## Smokes de regressao operacional
- `./scripts/smoke_project_brain_query_wrapper.sh` => OK
- `./scripts/smoke_round_continuity_default.sh` => OK (`run_id=23`, `facts=4`, `chunks=5`, `missing_embedding=0`)

## Interpretacao
A calibracao foi efetiva para o alvo principal (dominancia e diversidade) sem regressao operacional evidente.

Trade-off aceito nesta rodada:
- maior presenca de `run_summary` no top5 (12 -> 22), que melhora diversidade mas pode exigir monitoramento para nao diluir demais `fact` em consultas de decisao.

## Decisao final
- manter esta calibracao ativa.
- nao aplicar novo tuning nesta rodada.

## Proximo ajuste sugerido
- se necessario em rodada futura, testar ajuste fino por categoria de query (sem alterar schema), por exemplo:
  - manter cap mais estrito em `semantic` puro
  - cap levemente menos estrito em alguns cenarios `hybrid` operacionais.
