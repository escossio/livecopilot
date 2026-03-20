# PostgreSQL Front Final Report

## Objetivo
- Formalizar o encerramento da frente PostgreSQL com foco em core SQL, performance, indexação e JSONB.

## Pipeline executado
1. `source_policy`
2. `source_manifest`
3. `corpus_preparation`
4. `parsing`
5. `chunking`
6. `lexical_baseline`
7. `semantic_embeddings`
8. `semantic_baseline`
9. `closure_decision`

## Artefatos
- Corpus raw e parsed (`data/knowledge_raw/postgresql/`, `data/knowledge_parsed/postgresql/`)
- Chunks (`data/knowledge_chunks/postgresql/*.json`)
- Embeddings (`data/semantic_index_experiments/postgresql/`)
- Relatórios: raw, parse/chunk, lexical baseline, embeddings, semantic baseline (+ resultados)

## Números consolidados
- Documentos: 4
- Chunks: 4
- Embeddings: 4 (modelo `text-embedding-3-large`, dim 3072)
- Semantic baseline queries: 4 (architecture, SQL commands, indexing, JSONB)

## Resultado semântico
- Todas as consultas tiveram top1 coerente com o chunk antecipado e o top3 manteve-se sem ruído do domínio.

## Decisão final
- `closure_decision`: `closed`
- Baseado na estabilidade semântica total para as consultas-chave, sem lacunas relatadas nos artefatos anteriores.
