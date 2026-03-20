# Mapa da Pipeline Semantica (Livecopilot)

## Fluxo real (entrada -> resposta)
1. `POST /api/chat`
   - arquivo: `app/api/routes.py`
   - funcao: `api_chat()` -> `_build_livecopilot_reply()`

2. Normalizacao e transcricao
   - arquivo: `app/services/pipeline.py`
   - funcao: `process_ingest()`
   - sub-passos:
     - `normalize_input()` em `app/services/ingestion.py`
     - `transcribe_with_trace()` em `app/services/transcription.py`
     - `update_context()` em `app/services/context.py`

3. Geracao de sugestoes (inclui busca semantica)
   - arquivo: `app/services/suggestions.py`
   - funcao: `generate_suggestions()`
   - sub-passos relevantes:
     - `_classify_input()` / `detect_topic()`
     - `_should_lookup_knowledge()`
     - `_compose_search_query_with_context()`
     - `_search_semantic_local_with_context()` -> `semantic_search()`
     - `build_context_from_results()` em `app/services/knowledge_search.py`
     - `_build_knowledge_enriched_suggestions()`

4. Recuperacao/Ranking local
   - arquivo: `app/services/semantic_min_api.py` (entrada `semantic_search()`)
   - arquivo: `app/services/knowledge_search.py` (ranking, filtros e contexto)
   - funcoes-chave:
     - `search_knowledge_chunks_with_debug()`
     - `_search_chunks_scored()`
     - `_select_diverse_results()`
     - `build_context_from_results()`

5. Roteamento operacional (fora do nucleo semantico)
   - arquivo: `app/api/routes.py`
   - funcoes:
     - `_resolve_operational_skill_query()`
     - `resolve_infra_status_query()`
     - `resolve_project_state_query()`
     - `resolve_response_guidance()`

6. Montagem da resposta final
   - arquivo: `app/api/routes.py`
   - funcao: `_build_livecopilot_reply()`
   - saida: `answer`, `bullets`, `knowledge_context`, `backend`

## Instrumentacao adicionada
- `app/api/routes.py`
  - trace JSON para perguntas canario em `docs/diagnostics/semantic_trace_run_<timestamp>.json`
