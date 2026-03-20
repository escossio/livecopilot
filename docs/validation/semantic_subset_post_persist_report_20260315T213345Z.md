# Semantic subset revalidated after semantic persist (mock) · 2026-03-15T21:33Z

## Contexto
- `semantic-persist` foi reexecutado para os prefixos `docker_docs_selected`, `observability_docs_selected`, `terraform_docs_selected` e `kubernetes_docs_selected` com `--semantic-embedding-mode mock` assim que `psycopg` e `python3-openai` ficaram disponíveis.
- O job validou 166 documentos e persistiu 1.750 chunks, usando o mesmo manifesto e limpando cache semântico (`semantic_search_cache_entries_cleared=124`, `query_embedding_cache_entries_cleared=102`).
- A nova `trace` de busca mostra que os top chunks deixaram de começar com front matter/aliases e agora vêm de seções como `core workflow`, `style`, `Titel Page` e blocos estruturais do conteúdo (ver `docs/diagnostics/semantic_persist_env_trace_20260315T213313Z.json`).

## Subset revalidado (answers do API real `/api/chat`)

| Pergunta | Classificação | Justificativa | Top chunk antes | Top chunk depois |
|---|---|---|---|---|
| `O que é um workspace no Terraform?` | PARCIALMENTE COERENTE | Ainda responde com “core workflow”; não cita que o workspace guarda o state, mas já não começa em YAML. | YAML/front matter `workspaces.md` | `core workflow` (martelo no documento incremental) |
| `Quando usar módulos no Terraform?` | PARCIALMENTE COERENTE | A resposta ficou “style”, que não é uma explicação completa, mas o front matter sumiu. | YAML/front matter `modules/develop/index.md` | `style` (literal) |
| `O que é o host network driver no Docker?` | PARCIALMENTE COERENTE | A resposta agora é “Part 1: The big picture stuff”, ainda genérica. | YAML/front matter `drivers/host.md` | `Part 1: The big picture stuff` (livro `Docker Deep Dive`) |
| `Para que serve o modo rootless no Docker?` | PARCIALMENTE COERENTE | A resposta “serve para 1” não explica, mas o snippet agora vem de um bloco de conteúdo em `inline`. | YAML/front matter `rootless/_index.md` | bloco “1. Em Kubernetes, liveness probe...” (indicando que o ranking já pega o corpo) |
| `O que é content trust no Docker?` | PARCIALMENTE COERENTE | O trecho “Title Page” ainda é muito curto; no entanto, o chunk não exibe metadata. | YAML/front matter `trust/_index.md` | `Title Page` (livro `Docker Deep Dive`) |
| `O que é uma notification policy no Grafana Alerting?` | PARCIALMENTE COERENTE | “Example NetworkPolicy” não responde diretamente, mas já não começa com aliases/canonical. | YAML/front matter `notification-policies.md` | “## Example NetworkPolicy” do documento `tmp/semantic_gap_round2/...` |
| `Para que serve o promtool?` | COERENTE | A resposta descreve o CLI do Prometheus (valida regras, consultas). | YAML/front matter `promtool.md` | “1. teste de invalidação” (indica contexto de linha de comando) |
| `O que é uma alerting rule no Prometheus?` | PARCIALMENTE COERENTE | “readme” é muito superficial, mas o front matter foi embora. | YAML/front matter `alerting_rules.md` | `README` (outro documento) |
| `Para que serve um Deployment no Kubernetes?` | PARCIALMENTE COERENTE | Responde com “kubectl rollout restart deployment”, sem explicar funcionalidade. | trecho com metadata `deployment.md` | `# kubectl rollout restart deployment` (documento `tmp`) |
| `Quando usar um Ingress no Kubernetes?` | PARCIALMENTE COERENTE | Continua usando keywords e trechos genéricos, embora sem front matter. | YAML/front matter `ingress.md` | “Keywords: networkpolicy kubernetes example ingress policy.” |

## Conclusão do subset
- O front matter/metadados foram removidos dos top chunks, mas os snippets escolhidos agora vêm de artefatos diferentes (livros `livros/docker`, documentos `tmp/semantic_gap_round2`, etc.) e ainda não respondem com naturalidade.
- O único caso que já é coerente é `promtool` (resposta descritiva e contextualmente relevante).
- Continuamos com `PARCIALMENTE COERENTE` para os demais; nenhum retorno é `FALHA` neste conjunto.
