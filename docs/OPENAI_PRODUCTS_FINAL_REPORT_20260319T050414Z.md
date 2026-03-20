# OpenAI Products Final Report

## Objetivo
- Documentar e fechar a frente OPENAI_PRODUCTS, garantindo rastreio técnico desde a política de fontes até o baseline semântico aprovado.

## Source policy resumida
- Apenas domínios oficiais OpenAI (docs/platform/developers/help/blog/index) e fontes CODEX listadas no manifest.
- Conteúdo técnico, rastreável, sem marketing/promocional.

## Source manifest resumido
- API Reference, Models, Embeddings, Realtime, Audio, Images, Rate limits (platform docs).
- CODEX: landing, introduções, IDE, changelog, prompting guide, help articles, modelo gpt-5.3-codex.

## Corpus final
- Documentos raw: 9
- Parsed: 9 (em `data/knowledge_parsed/openai/`)
- Chunks: 122 (em `data/knowledge_chunks/openai/openai_products_chunks.json`)
- Embeddings: 122 vetores (`data/semantic_index_experiments/openai_products/embeddings.jsonl`, modelo `text-embedding-3-large`, dim 3072)

## Chunking
- Chunking simples com janela de ~200 palavras para cada documento parseado.
- Nenhum refinement extra foi necessário após a materialização inicial.

## Embeddings
- Sandbox isolado `data/semantic_index_experiments/openai_products/`.
- Modelo `text-embedding-3-large`, dimensão 3072, 122 embeddings (um por chunk).
- Reporte em `docs/OPENAI_PRODUCTS_EMBEDDINGS_REPORT.md`.

## Semantic baseline
- Bateria de 12 consultas (APIs, policies, Codex) avaliada com `text-embedding-3-large`.
- Todas as 12 consultas classificadas como `COERENTE`.
- Relatório e resultados em `docs/OPENAI_PRODUCTS_SEMANTIC_BASELINE_REPORT.md` e `docs/OPENAI_PRODUCTS_SEMANTIC_BASELINE_RESULTS.json`.

## Decisão final
- `closure_decision: closed`
- Justificativa: cobertura completa do corpus técnico oficial, embeddings completos e baseline semântico sem falhas.

## Observações não bloqueantes
- Revisar streams/Codex se novos lançamentos exigirem atualização; fechamento atual cobre o portfolio documentado até março de 2026.
