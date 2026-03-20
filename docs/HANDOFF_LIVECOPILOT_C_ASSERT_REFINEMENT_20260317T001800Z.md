# HANDOFF: C Assert Refinement (2026-03-17T00:18:00Z)

## Contexto
- O domínio C isolado já estava em produção (chunks, embeddings e utilitário); a última lacuna visível era o chunk `<assert.h>`/`assert`, cujo embedding retornava apenas o título em cppreference.
- A rodada atual visa enriquecer esse chunk, regenerar os embeddings do domínio e validar se as perguntas-alvo melhoraram sem afetar as demais.

## O que foi feito
1. Substituído o chunk `cppreference_c-06` por um texto completo sobre `<assert.h>`, `assert(expression)`, `NDEBUG`, `abort` e boas práticas de diagnóstico, e ajustados os metadados (`chunk_index`, `.meta.json`).
2. Atualizado `metadata/domain_metadata.json` para registrar a nova versão e para listar essa cobertura como força, mantendo `read` como lacuna a trabalhar.
3. Criado e executado `scripts/c_domain_rebuild_embeddings.py` para regenerar `data/knowledge_domains/c_programming/embeddings/embeddings.jsonl` e `metadata.json` com todos os 25 chunks e o modelo `text-embedding-3-large`.
4. Rerodada a bateria curta (`<assert.h>`, `assert`, `read`, `printf`, `pthread_create`) via `scripts/c_domain_query.py`; os resultados estão levantados em `docs/C_ASSERT_REFINEMENT_RESULTS_20260317T001800Z.json`.

## Resultados principais
- `<assert.h>` e `assert` passam a apontar consistentemente para o chunk `man7/assert.3` no topo, oferecendo descrição do macro, a mensagem simples e o efeito de `abort`, além do papel do `NDEBUG`.
- As perguntas `printf` e `pthread_create` mantiveram os chunks corretos; `read` segue parcialmente coerente porque `<ctype.h>` lidera a semântica.
- O domínio registrou a nova massa semântica e o relatório de refinamento (`docs/C_ASSERT_REFINEMENT_REPORT_20260317T001800Z.md`) sumariza o impacto.

## Próximos passos recomendados
1. Ajustar o chunk de `read` ou reforçar o sinal semântico dele para que o score supere `<ctype.h>` no topo da busca.
2. Após isto, repassar a bateria de validação e considerar a promoção do domínio C para o índice global de forma controlada.
