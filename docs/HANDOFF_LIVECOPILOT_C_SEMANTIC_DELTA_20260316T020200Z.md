# HANDOFF: C Semantic Delta (2026-03-16T02:02:00Z)

## Contexto
- Última rodada visava preencher as lacunas sobre `locale` e `assert` no piloto C sem tocar no índice global.
- O sandbox isolado já tinha embeddings para 23 chunks; o objetivo era adicionar o conteúdo mínimo faltante, regenerar os vetores e rerodar a bateria lexical/semântica.

## O que foi feito
1. Criados os chunks `man7-05` (locale(7) overview) e `man7-06` (assert(3) macro) incluindo `.txt` e `.meta.json` para cada um, além de atualizar `docs/C_CHUNKING_METADATA.json`.
2. Regenerados `data/semantic_index_experiments/c_pilot/embeddings.jsonl` e `metadata.json` com o conjunto completo de 25 chunks usando `text-embedding-3-large`.
3. Executadas as três perguntas-alvo (`locale`, `<assert.h>`, `assert`) tanto lexicamente (gerando `tmp/lexical_locale_assert_after.json`) quanto semanticamente (`tmp/c_semantic_search_results_locale_assert.json`).
4. Produzido `docs/C_SEMANTIC_DELTA_RESULTS_20260316T020200Z.json` e o relatório sintético `docs/C_SEMANTIC_DELTA_REPORT_20260316T020200Z.md` registrando antes/depois e a constatação de que apenas `locale` ficou resolvido de ponta a ponta.

## Resultados principais
- `locale` agora mapeia consistentemente para `man7-05`, tanto na busca lexical quanto na semântica; a cobertura está completa.
- `assert` e `<assert.h>` ganharam ótimos chunks lexicais (`man7-06`), mas a busca semântica continua escolhendo o placeholder `cppreference_c/<assert.h>` com poucas palavras, o que exige próximos passos.

## Próximos passos recomendados
1. Enriquecer o chunk `<assert.h>` (ou promover o `man7/assert.3`) para que o embedding semântico reflita a explicação; isso evita regressões quando `NDEBUG` ou o comportamento curinga é questionado.
2. Após o reforço, rerodar rapidamente a bateria semântica para confirmar que as três perguntas agora apontam para chunks completos e, se aprovado, mover o piloto C para integração controlada.
