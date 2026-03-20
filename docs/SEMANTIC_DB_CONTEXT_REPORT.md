# Semantic DB Context Report

Data da inspeção: 2026-03-14
Escopo: leitura, introspecção read-only e mapeamento do código atual. Nenhuma ingestão, schema change ou alteração de código foi executada.

## 1. Banco usado

- Banco ativo: PostgreSQL
- Versão: PostgreSQL 17.8 (Debian 17.8-0+deb13u1)
- Database: `livecopilot`
- Host: `127.0.0.1`
- Porta: `5432`
- Usuário: `livecopilot_app`
- Driver usado no projeto: `psycopg` (sync, psycopg v3 style)
- DSN canônica observada: `DATABASE_URL=postgresql://livecopilot_app:<redacted>@127.0.0.1:5432/livecopilot`
- Fonte canônica da configuração:
  - `/etc/livecopilot-semantic.env`
  - fallback em código: carga opcional de `/etc/livecopilot-semantic.env` e depois `.env` em `app/core/config.py`

### Evidência

- `.env`: informação não encontrada no estado atual do projeto
- `.env.example`: não define `DATABASE_URL`
- `app/core/config.py`: carrega `/etc/livecopilot-semantic.env` antes do `.env`
- `/etc/livecopilot-semantic.env`: define `DATABASE_URL`, `SEMANTIC_PG_DSN` e `LIVECOPILOT_DB_DSN`

## 2. Conexão PostgreSQL e extensões

### Evidência SQL

```sql
SELECT version();
SELECT current_database(), current_user, current_schema();
SELECT extname, extversion FROM pg_extension ORDER BY extname;
```

### Resultado observado

- `version()`: `PostgreSQL 17.8 ...`
- `current_database`: `livecopilot`
- `current_user`: `livecopilot_app`
- `current_schema`: `public`
- Extensões instaladas:
  - `plpgsql 1.0`
  - `vector 0.8.0`

Conclusão: a extensão vetorial está ativa. Não foi encontrada extensão separada chamada `pgvector`; no estado atual ela aparece instalada como `vector`, que é o nome esperado no catálogo.

## 3. Schemas existentes

### Evidência SQL

```sql
SELECT schema_name FROM information_schema.schemata ORDER BY schema_name;
```

### Resultado observado

- `information_schema`
- `pg_catalog`
- `public`

Conclusão: não existe schema semântico dedicado. Toda a estrutura observada está no schema `public`.

## 4. Tabelas, views e funções relevantes

### Tabelas base no schema `public`

- `chunks`
- `documents`
- `ingest_jobs`
- `project_facts`
- `project_memory_chunks`
- `project_runs`
- `query_embedding_cache`
- `semantic_search_cache`

### Views

- Não foram encontradas views próprias do projeto fora de `pg_catalog` e `information_schema`.

### Funções

- Não foram encontradas funções customizadas do projeto no banco.
- As funções listadas em `public` pertencem majoritariamente à extensão `vector` (`vector_dims`, `l2_distance`, `cosine_distance`, `ivfflathandler`, `hnswhandler`, etc.).

## 5. Tabelas relacionadas a semântica e vetor

### Critério usado

Busca por nomes de tabelas/colunas contendo `vector`, `embedding`, `knowledge`, `chunk`, `document`, `semantic`.

### Tabelas relevantes encontradas

#### `public.documents`

- Papel: catálogo de documentos ingeridos para a busca semântica mínima
- Colunas-chave:
  - `id`
  - `source_file`
  - `title`
  - `doc_type`
  - `checksum`
  - `metadata_json`

#### `public.chunks`

- Papel: chunks semânticos consultados pela API `/semantic/search`
- Colunas-chave:
  - `document_id`
  - `chunk_id`
  - `sequence`
  - `title`
  - `content`
  - `trecho_relevante`
  - `tags`
  - `embedding vector(1536)`
  - `metadata_json`

#### `public.query_embedding_cache`

- Papel: cache de embedding da query
- Colunas-chave:
  - `query_raw`
  - `query_normalized`
  - `embed_model`
  - `embedding vector(1536)`
  - `created_at`
  - `last_used_at`
  - `hit_count`

#### `public.semantic_search_cache`

- Papel: cache de resposta semântica pronta
- Colunas-chave:
  - `query_normalized`
  - `embed_model`
  - `limit_n`
  - `relevance_floor`
  - `response_json`
  - `created_at`
  - `last_used_at`
  - `hit_count`

#### `public.project_runs`

- Papel: runs operacionais do projeto

#### `public.project_facts`

- Papel: fatos estruturados por run

#### `public.project_memory_chunks`

- Papel: memória semântica de continuidade operacional
- Colunas-chave:
  - `run_id`
  - `fact_id`
  - `content`
  - `embedding vector(1536)`
  - `source_type`
  - `source_path`
  - `semantic_layer`
  - `tags`
  - `chunk_key`

## 6. Tabelas vetoriais

### Evidência SQL

```sql
SELECT c.relname, a.attname, a.atttypmod, format_type(a.atttypid, a.atttypmod)
FROM pg_attribute a
JOIN pg_class c ON c.oid = a.attrelid
JOIN pg_type t ON t.oid = a.atttypid
WHERE c.relname IN ('chunks', 'project_memory_chunks', 'query_embedding_cache')
  AND a.attname = 'embedding'
  AND t.typname = 'vector';
```

### Resultado observado

| tabela | coluna | tipo | dimensão |
|---|---|---|---|
| `public.chunks` | `embedding` | `vector(1536)` | `1536` |
| `public.project_memory_chunks` | `embedding` | `vector(1536)` | `1536` |
| `public.query_embedding_cache` | `embedding` | `vector(1536)` | `1536` |

### Contagens atuais

| tabela | total | com embedding | sem embedding |
|---|---:|---:|---:|
| `documents` | 279 | n/a | n/a |
| `chunks` | 1248 | 1248 | 0 |
| `query_embedding_cache` | 42 | 42 | 0 |
| `semantic_search_cache` | 36 | n/a | n/a |
| `project_runs` | 28 | n/a | n/a |
| `project_facts` | 107 | n/a | n/a |
| `project_memory_chunks` | 135 | 135 | 0 |

Conclusão: a base vetorial já existe e está povoada.

## 7. Índices vetoriais

### Evidência SQL

```sql
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename, indexname;
```

### Resultado observado

- Foram encontrados apenas índices `btree` e chaves primárias/únicas.
- Não foi encontrado índice vetorial `ivfflat`.
- Não foi encontrado índice vetorial `hnsw`.
- Não foi encontrado uso de `vector_cosine_ops`, `vector_l2_ops` ou opclass vetorial equivalente em índices persistidos.

Conclusão: há colunas `vector`, mas as consultas atuais estão fazendo busca vetorial sem índice ANN persistido.

## 8. Código do projeto que usa esse banco

### Configuração e ambiente

- `app/core/config.py`
- `scripts/with-semantic-env.sh`
- `/etc/livecopilot-semantic.env`

### Serviços/API semântica principal

- `app/services/semantic_min_api.py`
  - faz ingestão em `documents` e `chunks`
  - gera embeddings com OpenAI
  - consulta `chunks` com operador vetorial `<=>`
  - usa cache em `query_embedding_cache` e `semantic_search_cache`
- `app/api/routes.py`
  - expõe `/semantic/search`
  - expõe `/semantic/ingest-min`

### Fluxo de uso em resposta do app

- `app/services/suggestions.py`
  - quando decide buscar conhecimento, tenta primeiro busca semântica local via `semantic_search(...)`
  - se falhar localmente, tenta a API `/semantic/search`
  - se a busca semântica falhar, cai para `search_knowledge_chunks_with_debug()` (léxica/local)
- `app/services/pipeline.py`
  - aciona `generate_suggestions(state)`

### Ingestão semântica do corpus de conhecimento

- `app/services/knowledge_ingest.py`
  - orquestra parsing/chunking do corpus local
  - chama `ingest_knowledge_base_min(...)`

### Trilhas semânticas de continuidade operacional

- `scripts/continuity_ingest.py`
  - grava `project_runs`, `project_facts` e `project_memory_chunks`
- `scripts/backfill_continuity_embeddings.py`
  - preenche embeddings faltantes em `project_memory_chunks`
- `scripts/continuity_recall.py`
  - consulta `project_memory_chunks` por similaridade vetorial
- `scripts/project_brain_query.py`
  - executa busca híbrida/semântica sobre `project_memory_chunks`

### Serviços não semânticos, mas que também usam o mesmo banco

- `app/services/infra_status_connector.py`
  - usa `DATABASE_URL` para health check read-only de PostgreSQL

## 9. Geração de embeddings

### Base semântica principal (`documents` / `chunks`)

- Arquivo: `app/services/semantic_min_api.py`
- Modelo observado:
  - `SEMANTIC_EMBED_MODEL`
  - fallback para `text-embedding-3-small`
- Validação explícita de dimensão:
  - `if len(vec) != 1536: raise ValueError(...)`
- Modos suportados:
  - `openai`
  - `mock`
  - `auto`

### Continuidade operacional (`project_memory_chunks`)

- Arquivos:
  - `scripts/continuity_ingest.py`
  - `scripts/backfill_continuity_embeddings.py`
- Modelo observado:
  - `SEMANTIC_EMBED_MODEL`
  - fallback para `text-embedding-3-small`
- Dimensão esperada:
  - `1536`

## 10. Pipeline atual de busca semântica

### Fluxo real observado no app

1. Uma query entra no fluxo principal do app.
2. `app/services/pipeline.py` chama `generate_suggestions(state)`.
3. `app/services/suggestions.py` decide se precisa consultar conhecimento.
4. O caminho primário atual é `_search_semantic_local_with_context(...)`.
5. `_search_semantic_local_with_context(...)` chama `app.services.semantic_min_api.semantic_search(...)`.
6. `semantic_search(...)` delega para `semantic_search_with_mode(..., embedding_mode="openai")`.
7. `semantic_search_with_mode(...)`:
   - normaliza a query
   - tenta cache de resposta em `semantic_search_cache`
   - tenta cache do embedding da query em `query_embedding_cache`
   - se não houver cache, gera embedding da query via OpenAI
   - consulta `public.chunks`
   - faz `JOIN` com `public.documents`
   - ordena por distância vetorial usando `<=>`
8. O score retornado é calculado como `1 - (c.embedding <=> %s::vector)`.
9. Se a busca semântica local falhar, `suggestions.py` tenta `_search_semantic_api_with_context(...)`, que chama HTTP `POST /semantic/search`.
10. O endpoint `/semantic/search` em `app/api/routes.py` chama o mesmo `semantic_search(...)`.
11. Se a busca semântica falhar também via API, o fallback atual é `app/services/knowledge_search.py::search_knowledge_chunks_with_debug()` usando busca lexical/tag-based local.

### SQL real da busca vetorial principal

Trecho funcional observado em `app/services/semantic_min_api.py`:

```sql
SELECT
    d.source_file,
    c.chunk_id,
    c.title,
    ROUND((1 - (c.embedding <=> %s::vector))::numeric, 6) AS similarity,
    LEFT(c.content, 180) AS snippet
FROM chunks c
JOIN documents d ON d.id = c.document_id
WHERE c.embedding IS NOT NULL
ORDER BY c.embedding <=> %s::vector ASC
LIMIT %s
```

### Operador vetorial usado

- Operador: `<=>`
- Interpretação no código: distância convertida em similaridade com `1 - distance`

### Tabela consultada no caminho principal

- `public.chunks`
- enriquecida por `JOIN public.documents`

### Pipeline paralelo de memória de continuidade

- Não é o mesmo pipeline da API `/semantic/search`.
- Usa `public.project_memory_chunks`.
- Também consulta por `<=>`.
- É usado por scripts de recall/brain (`scripts/continuity_recall.py`, `scripts/project_brain_query.py`).

## 11. Lacunas identificadas

- Não existe schema semântico dedicado; tudo está em `public`.
- Não existem índices vetoriais ANN (`ivfflat`/`hnsw`) nas tabelas com `vector`.
- Não foi encontrada view operacional consolidando o estado semântico do banco.
- Não foram encontradas funções customizadas do projeto no banco para busca semântica; a lógica está na aplicação.
- `.env` local não existe e `.env.example` não documenta o DSN; a configuração real depende de `/etc/livecopilot-semantic.env`.
- Não foi encontrada no estado atual do projeto uma documentação única já consolidada do contrato entre:
  - busca semântica principal em `chunks`
  - memória de continuidade em `project_memory_chunks`

## 12. Respostas objetivas ao objetivo da rodada

### Qual banco está sendo usado

PostgreSQL 17.8, database `livecopilot`, acessado por `psycopg`, com `DATABASE_URL` canônica em `/etc/livecopilot-semantic.env`.

### Qual schema existe

Schemas presentes: `information_schema`, `pg_catalog` e `public`. Não existe schema semântico dedicado.

### Quais tabelas vetoriais existem

- `public.chunks`
- `public.query_embedding_cache`
- `public.project_memory_chunks`

Todas com coluna `embedding vector(1536)`.

### Quais serviços do projeto usam esse banco

- `app/services/semantic_min_api.py`
- `app/services/knowledge_ingest.py`
- `app/services/suggestions.py` (via `semantic_min_api`)
- `app/api/routes.py` (via `/semantic/search` e `/semantic/ingest-min`)
- `scripts/continuity_ingest.py`
- `scripts/backfill_continuity_embeddings.py`
- `scripts/continuity_recall.py`
- `scripts/project_brain_query.py`
- `app/services/infra_status_connector.py`

### Qual pipeline atual de busca semântica

Pipeline principal do app: query -> `generate_suggestions()` -> `semantic_min_api.semantic_search()` -> caches (`semantic_search_cache` / `query_embedding_cache`) -> embedding da query -> busca vetorial em `public.chunks` com `<=>` -> retorno de snippets/contexto.

Fallback atual: se a busca semântica falhar, cai para `search_knowledge_chunks_with_debug()` (léxico/tag-based). Em paralelo, existe outro pipeline semântico para continuidade operacional em `public.project_memory_chunks`.
