# Linux Front Final Report

## Objetivo
- Encerrar a frente Linux com cobertura documentada de kernel, systemd, networking e comandos essenciais.

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
- Corpus raw+parsed: `data/knowledge_raw/linux/`, `data/knowledge_parsed/linux/`
- Chunks: `data/knowledge_chunks/linux/*.json`
- Embeddings: `data/semantic_index_experiments/linux/`
- Relatórios (raw, parse/chunk, lexical, embeddings, semantic baseline) documentam cada etapa.

## Números finais
- Documentos: 4
- Chunks: 4
- Embeddings: 4 (modelo `text-embedding-3-large`, dim 3072)
- Semantic baseline queries: 4 (kernel subsystem, systemd overview, networking, ps)

## Resultado semântico
- Todas as consultas tiveram top1 alinhado ao chunk esperado; o top3 manteve aderência e não introduziu ruído.

## Decisão final
- `closure_decision`: `closed`
- A frente está pronta para uso semântico no domínio Linux core, sem pendências bloqueantes.
