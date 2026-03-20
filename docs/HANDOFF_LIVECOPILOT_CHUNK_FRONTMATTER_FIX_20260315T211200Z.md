# Handoff · Chunk front matter fix (2026-03-15T21:12Z)

## Motivação
- casos ainda `PARCIALMENTE COERENTES` estão sendo puxados por chunks que começam no YAML/front matter (workspace, Docker networking, notification policy etc.).

## O que mudou
- `_strip_document_metadata()` ganhou cobertura para `alias/aliases`, `notification_path`, `docs_path`, `header`, `breadcrumb(s)` e sinais como `# START AUTO GENERATED METADATA`; blocos `---` repetidos são limpos recursivamente.
- A `TAG_PIPELINE_VERSION` subiu para `2026-03-15-chunking-v1`, obrigando a reprocessar os arquivos.

## Fonte reprocessada
- Comando: `scripts/with-semantic-env.sh scripts/ingest_knowledge.sh --source-prefix docker_docs_selected/ --source-prefix observability_docs_selected/ --source-prefix terraform_docs_selected/ --source-prefix kubernetes_docs_selected/`
- Dados: `169` arquivos encontrados, `3` atualizados, `2.329` chunks salvos, manifesto em `data/knowledge_index/knowledge_manifest.json`.

## Resultados
- Os chunks agora começam na definição útil (ex.: `terraform_docs_selected/language/state/workspaces.md` inicia em “# Workspaces”; `grafana` notification policy mostra logo o texto da política).
- A captura de busca mais recente (`chunking_frontmatter_fix_trace_20260315T211004Z.json`) ainda traz metadata porque o índice semântico não foi reatualizado.
- Validação parcial do subset (`semantic_subset_post_rechunk_20260315T211200Z.json`) mostra respostas extraídas de metadata.

## Próximos passos
1. Instalar `psycopg` (ou garantir que a dependência `psycopg` esteja acessível no venv).
2. Rerodar `scripts/with-semantic-env.sh scripts/ingest_knowledge.sh --semantic-persist --semantic-limit-docs 999 --semantic-max-chunks-per-doc 24` com os prefixos atuais para recriar embeddings a partir dos novos chunks.
3. Atualizar os artefatos das validações/hand-offs e reavaliar o subset e a baseline ampliada após o reindex.
