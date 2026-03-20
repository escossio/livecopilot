# Chunking + front matter fix · 2026-03-15T21:12Z

## Ajustes de parsing
- `_strip_document_metadata()` agora remove `alias`, `notification_path`, `docs_path`, `redirect*`, `breadcrumb(s)` e outros cabeçalhos conhecidos antes de gerar os chunks.
- Reaplicamos `FRONT_MATTER_PATTERN` em loop para limpar blocos repetidos e detectamos comentários de metadata (`# START AUTO GENERATED ...`) antes de parar o consumo.
- Pipeline tag foi elevada para `2026-03-15-chunking-v1`, garantindo que reprocessos detectem a nova regra.

## Escopo de reingestão
- Comando utilizado:  
  `scripts/with-semantic-env.sh scripts/ingest_knowledge.sh --source-prefix docker_docs_selected/ --source-prefix observability_docs_selected/ --source-prefix terraform_docs_selected/ --source-prefix kubernetes_docs_selected/`
- Resumo da execução sem `--semantic-persist`: `169` arquivos encontrados, `3` processados (chunks atualizados) e `2.329` chunks gerados; manifesto em `/lab/projects/livecopilot/data/knowledge_index/knowledge_manifest.json`.
- Uma tentativa anterior incluindo `--semantic-persist` abortou com `ModuleNotFoundError: No module named 'psycopg'`. Os chunks foram gerados, mas a indexação semântica ainda reflete os dados antigos.

## Resultados observados
- `terraform_docs_selected/language/state/workspaces.md` agora começa com `# Workspaces` e o trecho útil passa a ser o chunk 1, não mais o bloco YAML.  
- `observability_docs_selected/grafana/docs/sources/alerting/fundamentals/notifications/notification-policies.md` também perde o front matter nas primeiras palavras.
- As capturas de busca mais recentes (ver `chunking_frontmatter_fix_trace_20260315T211004Z.json`) ainda mostram fragments de metadata porque o índice semântico não foi reatualizado.

## Próximos passos
- Instalar `psycopg` no ambiente e rerodar `scripts/with-semantic-env.sh scripts/ingest_knowledge.sh --semantic-persist --semantic-limit-docs 999 --semantic-max-chunks-per-doc 24 --source-prefix ...` para persistir os novos chunks.
- Validar novamente o subset (perguntas listadas) e, se houver avanço, rerodar a baseline expandida para documentar o ganho.
