# C Semantic Delta Report (2026-03-16T02:02:00Z)

## 1. Cobertura adicionada
- Inserted `man7-05` (`locale(7) overview`) containing a concise explanation of locales, setlocale/localeconv, category macros, struct `lconv`, and the LC_ALL/LANG selection order.
- Added `man7-06` (`assert(3) macro`) describing `assert`, the effect of `NDEBUG`, `abort`, and the risk of disabling diagnostics.
- Both chunks live under `data/knowledge_chunks/c/man7/` and are listed in `docs/C_CHUNKING_METADATA.json` with fresh `.txt` + `.meta.json` pairs.

## 2. Embeddings regenerados
- Re-ran the isolated embedding pipeline (`text-embedding-3-large`) so `data/semantic_index_experiments/c_pilot/embeddings.jsonl` now reflects 25 chunks and `metadata.json` reports the new average word count (552.2) and timestamp `2026-03-16T02:01:38Z`.

## 3. Perguntas-alvo (lexical vs semântico)
| Pergunta | Lexical antes | Lexical depois | Semântico antes | Semântico depois | Notas |
| --- | --- | --- | --- | --- | --- |
| O que é locale em C? | `man7/printf-3.txt` (COERENTE) | `man7/locale.7` (COERENTE) | `man7/locale.7` (COERENTE) | `man7/locale.7` (COERENTE) | Locale now lands on the explainer chunk both lexically and semantically, so the case is resolved. |
| O que é <assert.h>? | `cppreference_c/<assert.h>` (PARCIALMENTE COERENTE) | `man7/assert.3` (COERENTE) | `cppreference_c/<assert.h>` (COERENTE) | `cppreference_c/<assert.h>` (FALHA) | Lexical search now honors the new chunk; semantic search still returns the bare header text, so the chunk embedding needs more density. |
| Para que serve assert? | `posix_issue7/stdio.h.txt` (COERENTE) | `man7/assert.3` (COERENTE) | `cppreference_c/<assert.h>` (COERENTE) | `cppreference_c/<assert.h>` (FALHA) | Semantic path has regressed because the query still hits the minimal `<assert.h>` chunk; the man7 chunk does not beat the header name. |

## 4. Impacto na baseline
- Locale coverage now has dedicated chunk, and the isolated semantic index decisively favors it for both lexical and semantic routes.
- Assert coverage improved at the lexical layer but the semantic route still prefers the unchanged cppreference placeholder. We need to either enrich the `<assert.h>` chunk or promote the man7 chunk’s signal (for example by including the word `assert` multiple times, adding more context, or manipulating the text-to-embedding ratio) before this question can be marked fully resolved.
- No regression observed in the other questions (stdio.h, pthread_create, read, printf) because the new embeddings preserve their prior chunks.

## 5. Próximos passos sugeridos
1. Expand the `<assert.h>` content in `data/knowledge_chunks/c/cppreference_c` so the semantic embedding contains actual prose instead of just the header name, or adjust the man7 chunk to appear earlier in the embedding list (e.g., via aliasing or duplicate signals). 2. Rerun the semantic battery once more to confirm `<assert.h>` and `assert` goals are met before promoting the pilot C subset.
