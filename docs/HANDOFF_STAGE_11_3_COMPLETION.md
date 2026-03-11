# Handoff - Stage 11.3 Completion

## Status
- Subetapa 11.3: **concluida**.
- Novo foco interno da etapa 11: **11.4 (Curadoria para persistencia externa)**.

## O que foi entregue
- Gate operacional auditavel para acionamento externo complementar.
- Implementacao minima: `scripts/external_search_decision.py`.
- Trilha de decisao: `data/external_search_decisions.ndjson`.

## Regra de decisao aplicada
- `allow_external_complement` somente quando houver insuficiencia explicita registrada para a query em `data/knowledge_gaps.ndjson` com motivo aceito:
  - `empty_result`
  - `low_average_score`
  - `collapsed_diversity`
- Sem evidência de insuficiencia explicita: `block_external_complement`.

## Evidencia de validacao
- Query sem gap explicito -> `block_external_complement`.
- Query com gap explicito (`collapsed_diversity`) -> `allow_external_complement`.

## Limites preservados
- Sem crawler/scraping.
- Sem automacao cega de busca externa.
- Sem alteracao de schema/banco/rotas.

## Proximo passo
Executar 11.4 com foco em curadoria/relevancia/confianca para persistencia de conhecimento externo.
