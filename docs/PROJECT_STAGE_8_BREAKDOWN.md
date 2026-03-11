# Project Stage 8 Breakdown: Project Brain + Ranking

Data de consolidacao: 2026-03-11

Escopo: detalhamento operacional da **Etapa 8** da sequencia oficial (`docs/PROJECT_STAGE_INDEX.md`), sem abrir novas frentes.

## Subetapas oficiais

| # | Subetapa | Descricao curta | Status | Dependencia | Criterio de conclusao |
|---|---|---|---|---|---|
| 8.1 | Query operacional do Project Brain | Consolidar uso do wrapper oficial (`project_brain_query.sh`) com modos `structured/semantic/hybrid` e saida auditavel. | concluida | Etapa 7 | Wrapper oficial operacional e smokes de query sem erro critico. |
| 8.2 | Bateria offline de ranking | Executar bateria canonica para gerar baseline comparavel de qualidade/diversidade de ranking. | concluida | 8.1 | Relatorios offline gerados (`latest_project_brain_ranking_eval.{json,md}`) com metricas de dominancia/diversidade. |
| 8.3 | Calibracao controlada de diversidade | Aplicar ajuste unico e reversivel por evidencia (cap de diversidade) e validar before/after sem regressao operacional. | concluida | 8.2 | Delta objetivo positivo em diversidade com smokes obrigatorios verdes. |
| 8.4 | Observacao pos-calibracao | Rodar ciclos de observacao para confirmar estabilidade e detectar regressao material apos calibracao. | concluida | 8.3 | 1+ ciclos comparaveis documentados com decisao explicita (seguir/reabrir calibracao). |
| 8.5 | Recalibracao conservadora lexical | Aplicar ajuste unico de peso lexical (`lexical_weight=0.85`) com bateria before/after e decisao manter/reverter. | concluida | 8.4 | Top1 estavel na bateria principal + smokes obrigatorios verdes + decisao registrada. |
| 8.6 | Observacao curta de continuidade da Etapa 8 | Monitorar a calibracao ativa em janela curta, mantendo disciplina de evidencia antes de qualquer novo tuning. | concluida | 8.5 | Fechar ciclo curto com evidencias comparaveis (sem regressao material) ou abrir ajuste unico adicional com justificativa objetiva. |

## Evidencias base desta decomposicao
- `docs/continuity/PROJECT_BRAIN_QUERY.md`
- `docs/continuity/PROJECT_BRAIN_RANKING_OFFLINE_EVAL.md`
- `docs/continuity/HANDOFF_PROJECT_BRAIN_RANKING_CALIBRATION_CONTROLLED.md`
- `docs/continuity/HANDOFF_PROJECT_BRAIN_POST_CALIBRATION_OBSERVATION.md`
- `docs/HANDOFF_PROJECT_BRAIN_RANKING_RECALIBRATION_CONSERVATIVE.md`
- `docs/continuity/ROUND_SUMMARY_PROJECT_BRAIN_QUERY.md`
- `docs/continuity/ROUND_SUMMARY_PROJECT_BRAIN_RANKING_OFFLINE_EVAL.md`
- `docs/continuity/ROUND_SUMMARY_PROJECT_BRAIN_RANKING_CALIBRATION_CONTROLLED.md`
- `docs/ROUND_SUMMARY_PROJECT_BRAIN_POST_CALIBRATION_OBSERVATION.md`
- `docs/ROUND_SUMMARY_PROJECT_BRAIN_RANKING_RECALIBRATION_CONSERVATIVE.md`
- `STATUS.md`

## Regra de execucao da Etapa 8
- Seguir estritamente a ordem `8.1 -> 8.2 -> 8.3 -> 8.4 -> 8.5 -> 8.6`.
- Qualquer novo ajuste de ranking so entra apos evidencias de `8.6`.
- Sem abrir frente paralela durante o fechamento da `8.6`.

## Estado de encerramento
- `8.6` foi encerrada com ciclo comparavel estavel e smokes verdes.
- Nao foi necessario ajuste adicional.
- A Etapa 8 pode ser considerada fechada no escopo atual.
