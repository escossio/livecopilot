# Semantic Retrieval Pipeline Map — 2026-03-15T05:41:00Z

## Fluxo real
1. `POST /api/chat` entra em `app/api/routes.py` e chama `_build_livecopilot_reply()`.
2. `_build_livecopilot_reply()` usa `process_ingest()` para preservar `raw_input`, `transcript_text` e `search_query`.
3. `generate_suggestions()` em `app/services/suggestions.py` classifica a pergunta, detecta `topic` e decide se consulta conhecimento.
4. `_compose_search_query_with_context()` monta a query final usada na busca.
5. `_search_semantic_local_with_context()` chama `semantic_search()` em `app/services/semantic_min_api.py`.
6. `semantic_search()` consulta PostgreSQL/pgvector (`documents`, `chunks`, `query_embedding_cache`, `semantic_search_cache`). Nao ha busca lexical aqui.
7. O retorno vetorial passa por `_apply_relevance_floor()` e `_passes_domain_gating()` em `app/services/suggestions.py`.
8. Se ainda houver `matches`, `build_context_from_results()` monta o contexto final.
9. `generate_suggestions()` monta uma lista de sugestoes; `_build_livecopilot_reply()` usa `suggestions[0]` como resposta principal.
10. O fallback lexical (`search_knowledge_chunks_with_debug()` em `app/services/knowledge_search.py`) so e usado se a etapa semantica local e a API semantica falharem por excecao.

## Fontes/indices realmente consultados
- Busca vetorial ativa: PostgreSQL com `pgvector`, tabelas `documents` e `chunks`.
- Cache de embedding: `query_embedding_cache`.
- Cache de resposta semantica: `semantic_search_cache`.
- Busca lexical alternativa: indice local carregado por `app/services/knowledge_search.py`.

## Evidencia de corpus ativo
### Documents
- `kubernetes_docs_selected`: 12
- `terraform_docs_selected`: 43
- `terraform_docs_selected_incremental`: 11
- `terraform_docs_selected_incremental_round2`: 12

### Chunks
- `kubernetes_docs_selected`: 95
- `terraform_docs_selected`: 209
- `terraform_docs_selected_incremental`: 72
- `terraform_docs_selected_incremental_round2`: 171

## Leitura tecnica
- Terraform e Kubernetes estao no universo da busca vetorial ativa.
- O problema atual nao e ausencia de corpus no banco.
- O ponto critico esta no pos-processamento da busca (`domain_gating`) e no consumo final das sugestoes/contexto.
