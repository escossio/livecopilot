# MACHINE_LEARNING Search Fix Report

## Causa raiz
- O fluxo de `knowledge_search` ainda podia misturar candidatos de outras frentes quando havia fallback de ranking.
- O score principal continuava dependente do ranking lexical/ajustes internos, sem usar `cosine similarity` normalizada sobre o índice semântico da frente.
- Não havia um filtro explícito por `source_prefix` antes do ranking semântico, então o top-k podia carregar chunks fora do domínio desejado.

## Correção aplicada
- `app/services/knowledge_search.py` passou a aceitar `--source-prefix` e a filtrar os chunks antes de qualquer ranking.
- Quando `source_prefix=machine_learning`, o ranking usa o índice em `data/knowledge_embeddings/machine_learning/embeddings.jsonl` e calcula `score` como `cosine similarity` normalizada.
- O fallback global foi restringido ao mesmo conjunto filtrado, evitando vazamento entre frentes.
- O debug dos resultados agora expõe `chunk_id`, `front`, `score` e `path`.

## Before / After
- Before: o baseline semântico anterior mostrava ruído externo no top1 para `bias variance tradeoff` e scores inconsistentes entre consultas.
- After: com `source_prefix=machine_learning`, todos os top resultados das queries validadas ficaram dentro da frente `machine_learning`, com ranking semântico baseado em cosine normalizada.

## Evidência de eliminação do vazamento
Validação executada com `source_prefix=machine_learning`:

- `bias variance tradeoff`
  - top1: `linear_regression-0002-09c953b16480951d`
  - front: `machine_learning`
  - path: `machine_learning/algorithms/linear_regression.html`
- `what is overfitting in machine learning`
  - top1: `prereqs_and_prework-0002-601a60add4eb8699`
  - front: `machine_learning`
  - path: `machine_learning/foundations/prereqs_and_prework.html`
- `linear regression example`
  - top1: `linear_regression-0002-09c953b16480951d`
  - front: `machine_learning`
  - path: `machine_learning/algorithms/linear_regression.html`

Nenhum resultado fora da frente `MACHINE_LEARNING` apareceu no top10 dessas consultas.

## Impacto esperado no ranking
- O ranking fica estável e comparável entre queries porque o score semântico passou a ser normalizado.
- O filtro por frente elimina a contaminação de domínios vizinhos no top-k.
- O debug facilita auditoria rápida de `chunk_id`, origem e score sem precisar abrir os artefatos manualmente.
