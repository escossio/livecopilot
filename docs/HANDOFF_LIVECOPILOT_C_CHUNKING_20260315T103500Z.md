# HANDOFF: C Chunking Pilot

## Contexto
- Desdobramento da etapa de parsing (`docs/C_PARSING_POLICY.md`) e do lockfile (`docs/C_CORPUS_LOCK.*`).
- Esta rodada aplica chunking controlado e produz arquivos em `data/knowledge_chunks/c/{wg14,posix_issue7,cppreference_c,man7}`.

## O que foi gerado
- Chunk policy: `docs/C_CHUNKING_POLICY.md` descreve heurísticas por tipo de fonte e aponta para `docs/C_CHUNKING_METADATA.json` com metadados.
- Chunks piloto:
  - `wg14`: cinco seções numeradas de `n2756`, cada uma guarda o corpo entre títulos (intro, limites, small storage, type punning, etc.).
  - `posix_issue7`: cinco funções/headers (stdio.h, stdlib.h, pthread.h, pthread_create, read) preservando nome, synopsis e notas.
  - `cppreference_c`: cinco itens (Basic concepts e outras seções da linguagem + primeiros headers) com descrições enxutas.
  - `man7`: NAME/SYNOPSIS/DESCRIPTION/RETURN VALUE/ERRORS de `printf(3)` sem escape ANSI.
- Sample report: `docs/C_CHUNKING_SAMPLE_REPORT_20260315T103000Z.md` mostra comparativos antes/depois e confirma chunks respondíveis.

## Próximos passos sugeridos
1. Validar a cobertura dos chunks com um subset semântico interno (lote 1 do manifesto) antes de gerar embeddings.
2. Confirmar hashes/metadados de `docs/C_CHUNKING_METADATA.json` e integrar com o pipeline que fará o ranking para C.
