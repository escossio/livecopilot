# Handoff - UTF8 Hygiene em chunks.content (2026-03-12)

## Objetivo
Corrigir registros legados corrompidos em `chunks.content` sem alterar pipeline e sem expandir corpus.

## Diagnóstico
- Scanner server-side (`LEFT(content,180)` com captura de exceção) identificou:
  - `2` chunks corrompidos
  - ambos em `observability_docs_selected/alertmanager/docs/high_availability.md`
- Evidência:
  - `docs/coverage/utf8_corrupted_chunks_diagnostic_20260312.json`

## Origem provável
- Payload canônico local do mesmo source_file codifica em UTF-8 sem erro.
- Hipótese mais provável: legado de armazenamento semântico em rows específicas (não origem no corpus atual/parsing atual).
- Evidência:
  - `docs/coverage/utf8_corrupted_chunks_origin_analysis_20260312.json`

## Estratégia e execução
- Tentativa inicial: reingestão semântica seletiva de 1 source_file (não eliminou os 2 rows corrompidos).
- Correção final mínima:
  - update cirúrgico dos 2 `chunk_pk` afetados com conteúdo canônico saneado.
  - marcação em `metadata_json` (`utf8_hygiene_fix_20260312=true`).
- Artefatos:
  - `docs/coverage/utf8_corrupted_chunks_fix_plan_20260312.json`
  - `docs/coverage/utf8_corrupted_chunks_fix_execution_20260312.json`

## Validação
- Scanner pós-fix:
  - `bad_chunks_count=0`
  - `docs/coverage/utf8_corrupted_chunks_post_fix_scan_20260312.json`
- Semantic search no caso afetado:
  - `snippet_fallback_due_encoding=false` nas probes novas
  - `docs/coverage/utf8_corrupted_chunks_semantic_search_validation_20260312.json`

## Resultado
- Casos afetados corrigidos.
- Fallback por title eliminado para as consultas afetadas nesta rodada.

## Próximo passo recomendado
- Adicionar checagem periódica read-only de UTF-8 em `chunks.content` no fechamento de rodadas semânticas para detectar regressão cedo.
