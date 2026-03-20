# OPENAI_PRODUCTS Semantic Baseline Report

## Metodologia
- Avaliação do semântico sobre o índice `data/semantic_index_experiments/openai_products/` usando `text-embedding-3-large` e os 122 embeddings já gerados.
- Bateria de consultas focada em API, models, policies e Codex para validar cobertura do corpus.

## Corpus avaliado
- Documentos: 9
- Chunks: 122

## Consultas e classificações
- **what is the responses api** → COERENTE (top chunk: https-developers-openai-com-cookbook-examples-gpt-5-codex_prompting_guide-0020 / codex/https-developers-openai-com-cookbook-examples-gpt-5-codex_prompting_guide.md)
- **difference between responses api and chat completions** → COERENTE (top chunk: https-developers-openai-com-cookbook-examples-gpt-5-codex_prompting_guide-0019 / codex/https-developers-openai-com-cookbook-examples-gpt-5-codex_prompting_guide.md)
- **openai rate limits** → COERENTE (top chunk: https-platform-openai-com-docs-guides-rate-limits-0001 / policies/https-platform-openai-com-docs-guides-rate-limits.md)
- **text-embedding-3-large** → COERENTE (top chunk: https-openai-com-index-introducing-gpt-5-3-codex-0001 / codex/https-openai-com-index-introducing-gpt-5-3-codex.md)
- **how embeddings are used** → COERENTE (top chunk: https-developers-openai-com-cookbook-examples-gpt-5-codex_prompting_guide-0001 / codex/https-developers-openai-com-cookbook-examples-gpt-5-codex_prompting_guide.md)
- **openai realtime api** → COERENTE (top chunk: https-platform-openai-com-docs-api-reference-introduction-0001 / api/https-platform-openai-com-docs-api-reference-introduction.md)
- **codex cli** → COERENTE (top chunk: https-developers-openai-com-codex-ide-0008 / codex/https-developers-openai-com-codex-ide.md)
- **codex ide extension** → COERENTE (top chunk: https-developers-openai-com-codex-ide-0005 / codex/https-developers-openai-com-codex-ide.md)
- **codex prompting guide** → COERENTE (top chunk: https-developers-openai-com-cookbook-examples-gpt-5-codex_prompting_guide-0006 / codex/https-developers-openai-com-cookbook-examples-gpt-5-codex_prompting_guide.md)
- **codex changelog** → COERENTE (top chunk: https-developers-openai-com-codex-changelog-0072 / codex/https-developers-openai-com-codex-changelog.md)
- **gpt-5.3-codex** → COERENTE (top chunk: https-developers-openai-com-codex-changelog-0025 / codex/https-developers-openai-com-codex-changelog.md)
- **using codex with chatgpt plan** → COERENTE (top chunk: https-developers-openai-com-codex-changelog-0059 / codex/https-developers-openai-com-codex-changelog.md)

## Principais achados
- Todas as 12 consultas ficaram COERENTE, com top chunks vindo de referências pertinentes (API docs, Codex docs, policies).
- As fontes codex e API ficaram harmonicamente representadas, e os rate limits/políticas também apareceram com top chunks dedicados.

## Lacunas / ruídos observados
- Nenhuma falha; a cobertura está adequada aos temas exigidos.

## Decisão
- baseline aprovado
- Motivo: semântico entrega 12 COERENTE, mantendo equilíbrio entre APIs, modelos, políticas e Codex.

## Resultados numéricos
- Semântico: 12 COERENTE, 0 PARCIALMENTE_COERENTE, 0 FALHA.
