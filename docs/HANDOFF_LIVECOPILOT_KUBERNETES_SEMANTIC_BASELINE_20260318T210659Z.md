# Handoff: Kubernetes Core Semantic Baseline

## Embeddings gerados
- Sandbox isolado: `data/semantic_index_experiments/kubernetes_pilot/`
- Arquivos: `embeddings.jsonl` e `metadata.json`
- Modelo: `text-embedding-3-large`
- Dimensão: `3072`
- Chunks: `12`

## Metadata do índice
- `num_chunks`: `12`
- `avg_length_words`: `59.25`
- `embedding_dim`: `3072`
- `generated_at`: `2026-03-18T21:06:54.575736+00:00`

## Resultado da baseline semântica
- `COERENTE`: `12`
- `PARCIALMENTE_COERENTE`: `0`
- `FALHA`: `0`

## Comparação lexical vs semântico
- O semantic top coincide com o chunk lexical esperado em praticamente todo o conjunto.
- As poucas diferenças lexicais iniciais foram corrigidas pelo refinement, especialmente em `namespace` e `secret`.

## Estado da frente
- A frente está pronta para `closure_decision`.
- Não há indicação de refinement adicional obrigatório no subset atual.
