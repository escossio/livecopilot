# HANDOFF: C Semantic Baseline (Staging)

## Contexto
- Continuação da validação local do subset chunkado (`docs/HANDOFF_LIVECOPILOT_C_CHUNK_LOCAL_VALIDATION_20260315T111100Z.md`).
- Objetivo: habilitar um índice semântico isolado em `data/semantic_index_experiments/c_pilot/` usando `text-embedding-3-large`, sem tocar no índice semântico principal.

## O que foi feito
- Criada a estrutura `data/semantic_index_experiments/c_pilot/` para receber `embeddings.jsonl` e `metadata.json`.
- Documentado o setup em `docs/C_SEMANTIC_ENV_SETUP.md` (número de chunks, modelo, estrutura, instruções de query).
- Preparado o utilitário `scripts/c_semantic_search_test.py` para buscar localmente usando embeddings de consulta.

## Pendências
- `OPENAI_API_KEY` não está definido no ambiente, portanto os embeddings não foram realmente gerados.
- Sem a geração, `embeddings.jsonl`/`metadata.json` permanecem vazios e o script de busca não pode ser validado.

## Próximos passos sugeridos
1. Definir `OPENAI_API_KEY` (por exemplo via `export OPENAI_API_KEY=...`).
2. Executar o script de geração de embeddings para todos os chunks (`text-embedding-3-large`).
3. Revalidar `scripts/c_semantic_search_test.py` com a bateria de perguntas C para comparar lexical vs semântico.
4. Após isso, registrar o checkpoint real da baseline semântica e atualizar o handoff final (`docs/HANDOFF_LIVECOPILOT_C_SEMANTIC_BASELINE_*.md`).
