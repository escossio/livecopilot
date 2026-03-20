# POSTGRESQL Parse & Chunk Report

## Resumo
- document_count: 4
- parsed_documents: 4
- chunk_count: 4
- chunk_size_avg: 58.5 palavras
- arquivos processados:
  - `data/knowledge_chunks/postgresql/architecture-chunks.json`
  - `data/knowledge_chunks/postgresql/indexing-chunks.json`
  - `data/knowledge_chunks/postgresql/jsonb-chunks.json`
  - `data/knowledge_chunks/postgresql/sql_commands-chunks.json`
- erros: nenhum

## Fontes
- `data/knowledge_raw/postgresql/architecture.md`
- `data/knowledge_raw/postgresql/indexing.md`
- `data/knowledge_raw/postgresql/jsonb.md`
- `data/knowledge_raw/postgresql/sql_commands.md`

## Observações
- Parsing simples preservou o texto integral, mantendo cabeçalhos e metadados sem alterações.
- Chunking segmentou cada documento em um JSON independente contendo um trecho técnico representativo.
