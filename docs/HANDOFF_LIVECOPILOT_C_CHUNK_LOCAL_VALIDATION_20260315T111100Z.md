# HANDOFF: C Chunk Local Validation

## Contexto
- Continua o piloto de chunking descrito em `docs/HANDOFF_LIVECOPILOT_C_CHUNKING_20260315T103500Z.md`.
- O objetivo aqui foi validar localmente uma bateria de perguntas simples antes de prosseguir para embeddings.

## Bateria usada
1. O que é comportamento definido pela implementação em C?
2. O que é locale em C?
3. Para que serve stdio.h?
4. O que pthread_create faz?
5. O que read faz?
6. O que é <assert.h>?
7. Para que serve assert?
8. O que printf retorna?
9. Quando printf pode falhar?

## Resultados principais
- Apenas o chunk `<assert.h>` (cppreference) ficou parcialmente respondível; todas as demais perguntas mapearam chunks RESPONDIVEIS (6 POSIX, 2 man7). Nenhum NAO_RESPONDIVEL foi detectado.
- O chunk `read` (POSIX) acabou respondendo duas perguntas diferentes porque contém múltiplos trechos de comportamento documentado; reforça a utilidade das funções de libc.
- O chunk `printf(3)` RETURN VALUE captura bem retornos/falhas de printf; man7 está pronto para perguntas práticas.

## Conclusão/decisão sugerida
- O subset chunkado está bom o suficiente para avançar (subset semântico local + embeddings) porque quase todas as perguntas tiveram chunks responsivos.
- Ainda recomenda-se reforçar WG14/cppreference com textos mais completos caso sejam alvos críticos de perguntas normativas antes de expandir o corpus.
