# Handoff - Conclusao da Subetapa 11.4 (Curadoria para persistencia externa)

Data: 2026-03-11
Status final da 11.4: concluida
Foco interno apos fechamento: 11.5 (Fechamento da etapa 11)

## Objetivo da 11.4
Garantir que conhecimento vindo de camada externa so possa ser promovido para persistencia apos curadoria explicita (relevancia/confianca), com trilha auditavel.

## Lacuna que faltava
A 11.3 ja decidia `allow/block` para complemento externo, mas faltava um encadeamento operacional unico, simples e auditavel ate a promocao persistente.

## Implementacao minima aplicada
- Novo script: `scripts/external_persistence_curation.py`
- Reuso direto de logica existente em `app/services/curated_sources.py`:
  - `register_source_candidate`
  - `record_candidate_review_decision`
  - `promote_source_candidate`
  - `build_candidate_review_report`
- Novo log de auditoria da frente: `data/external_persistence_curation.ndjson`

## Evidencia objetiva de validacao
Fluxo executado de ponta a ponta para a query de validacao `stage11.4 validation external persistence flow`:
1. Gate externo: `allow_external_complement` em `scripts/external_search_decision.py`.
2. Registro de candidato externo (origem local controlada).
3. Revisao com decisao `approved`.
4. Promocao confirmada para `data/knowledge_raw/stage11_4_validation_20260311T021427Z.md`.
5. Inspecao final mostrando candidato `promoted` com historico de promocao.
6. Auditoria confirmada em `data/external_persistence_curation.ndjson`.

Candidate id da validacao:
`stage-11-4-validation-candidate-local-data-raw-review-stage11-4-validation-20260`

## O que nao mudou
- Nenhum crawler/scraping.
- Nenhuma automacao externa irrestrita.
- Nenhuma alteracao de schema/banco PostgreSQL.
- Nenhum inicio de escopo da 11.5.

## Arquivos tocados nesta rodada
- `scripts/external_persistence_curation.py`
- `docs/ROUND_SUMMARY_STAGE_11_4_SCOPE.md`
- `docs/PROJECT_STAGE_11_BREAKDOWN.md`
- `docs/project_status_state.json`
- `docs/HANDOFF_STAGE_11_4_COMPLETION.md`
- `STATUS.md`
