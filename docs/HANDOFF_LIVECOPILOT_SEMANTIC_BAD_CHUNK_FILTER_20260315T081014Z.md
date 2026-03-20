# HANDOFF LIVECOPILOT SEMANTIC BAD CHUNK FILTER

## Motivação
- os casos ainda `PARCIALMENTE COERENTES` continuavam sendo alimentados por front matters ou blocos documentais sem primeira frase útil, mesmo depois da síntese por intenção, LLM e ranking por intenção.

## Hipótese testada
- aplicar uma penalidade/remoção controlada antes da síntese para chunks com:
  - front matter (`---`, `page_title`, `description`, `keywords`, `canonical`)
  - aliases/breadcrumbs (rotas `/docs/...`, `/notification-policies/...`, etc.)
  - reviewer headers e metadata gerada automaticamente.

## Correção aplicada
- `STRUCTURAL_NOISE_PATTERNS` em `app/services/knowledge_search.py` identifica esses sinais e soma até `0.6` de penalidade por chunk.  
- `_structural_noise_penalty()` é chamada dentro de `_search_chunks_scored()` e reduz o score final antes do ranking/diversity; os motivos são expostos em `structural_noise_reasons`.  
- O gatilho não remove candidatos à força, apenas coloca metadata pesada abaixo de qualquer chunk limpo, preservando o resto do pipeline e evitando regressões.

## Resultados
- Diagnóstico e trace:  
  - `docs/diagnostics/semantic_bad_chunk_diagnostic_20260315T080942Z.md`  
  - `docs/diagnostics/semantic_bad_chunk_trace_20260315T080942Z.json`  
  - `docs/validation/semantic_bad_chunk_before_after_20260315T080942Z.md`  
- Subset revalidado: `docs/validation/semantic_bad_chunk_subset_20260315T080959Z.json` (todas as respostas ainda parciais, mas com top chunk reordenado).  
- Baseline expandida pós-filtro:  
  - `docs/validation/semantic_regression_expanded_post_bad_chunk_filter_20260315T081014Z.json`  
  - `docs/validation/semantic_regression_expanded_post_bad_chunk_filter_report_20260315T081014Z.md`  
- O filtro não converteu parciais em coerentes, mas prepara o ranking para aceitar qualquer chunk limpo que surja sem regredir o que já funcionava.

## Próximos passos
- buscar chunks alternativos (nova ingestão, reorganização do corpus) para as perguntas `what is/purpose/when to use` e repetir o filtro; se chunks melhores aparecerem, o ranking já os privilegiará automaticamente.
