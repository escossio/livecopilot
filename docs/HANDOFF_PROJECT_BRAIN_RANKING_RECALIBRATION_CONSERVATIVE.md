# Handoff: Project Brain Ranking Recalibration (Conservative)

Data: 2026-03-11
Status: concluido (mudanca mantida)

## Mudanca aplicada
- Arquivo: `app/services/knowledge_search.py`
- Ajuste unico:
  - `LEXICAL_WEIGHT = 0.85`
  - `adjusted_score = (base_score * LEXICAL_WEIGHT * hygiene_score) + (practicality_bonus * practicality_bonus_weight)`

## Escopo respeitado
- sem alteracao de schema
- sem alteracao de banco vetorial
- sem alteracao de ingestao
- sem alteracao de routing
- apenas recalibracao do peso lexical

## Evidencia before/after
- Bateria com 8 queries principais (top3 auditado com `source_file`, `score`, `base_score`, `practicality_bonus`, `signals`).
- Resultado consolidado:
  - top1 estavel em `8/8`
  - diversidade global de fontes no top3 preservada (`6` fontes unicas em 24 slots before/after)
  - sinais praticos do top1 preservados

## Smokes
- `./scripts/smoke_project_brain_query_wrapper.sh` => OK
- `./scripts/smoke_round_continuity_default.sh` => OK

## Decisao operacional
- manter a mudanca (nao reverter).
- proxima acao recomendada: observacao curta com queries reais adicionais antes de nova calibragem.
