# OPENAI_PRODUCTS Parse & Chunk Report

## Resumo
- document_count: 9
- parsed_documents: 9
- chunk_count: 122
- chunk_size_avg: 188.1 palavras
- parsing: executado (normalização simples para markdown)
- embeddings: não executado

## Arquivos processados
- base raw: `data/knowledge_raw/openai/`
- parsed: `data/knowledge_parsed/openai/` (mesmos nomes dos raw)
- chunks: `data/knowledge_chunks/openai/openai_products_chunks.json`

## Erros
- Nenhum erro registrado na materialização ou no parsing/chunking simplificado.

## Notas
- Chunking simples com janela de ~200 palavras; manutenção de metadados `chunk_id` com nome de arquivo e índice.
- Nenhum conteúdo não oficial processado.
