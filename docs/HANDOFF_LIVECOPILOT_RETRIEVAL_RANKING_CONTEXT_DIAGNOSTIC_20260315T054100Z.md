# Handoff — Diagnostico profundo de retrieval / ranking / contexto

## Escopo executado
- inspecao da busca semantica real
- analise por camada de retrieval, ranking, contexto e fallback
- validacao com os 3 canarios semanticos
- geracao de artefatos estruturados em `docs/diagnostics/`

## Leitura objetiva
- o banco vetorial ativo contem corpus de Terraform e Kubernetes
- `semantic_search()` recupera hits plausiveis para os 3 canarios
- o principal problema atual nao esta mais no input nem no retrieval vetorial bruto

## Falha por familia de pergunta
### Terraform
- retrieval vetorial encontra resultados corretos
- `_passes_domain_gating()` descarta esses resultados antes da resposta final
- evidencia: `semantic_search.count=3`, mas `knowledge_context.result_count=0`
- causa provavel: `DOMAIN_SIGNALS` nao cobre termos centrais de Terraform

### Kubernetes
- retrieval vetorial encontra resultados corretos
- contexto final e montado com trechos de `service.md`
- a resposta final continua generica porque o slot principal consumido pelo chat e `suggestions[0]`, enquanto o resumo contextualizado fica em `suggestions[1]`

## Busca lexical
- existe como fallback quando a camada semantica falha por excecao
- para os canarios, mostrou ruido alto e dominancia de livros/PDFs
- nao e o gargalo principal desta rodada, mas tambem nao e um fallback de alta qualidade hoje

## Proxima correcao recomendada
1. revisar `DOMAIN_SIGNALS` / `_passes_domain_gating()` para nao zerar hits validos de Terraform
2. ajustar a selecao da resposta final para promover o conteudo contextual quando `knowledge_context.result_count > 0`
3. depois rerodar os canarios antes de qualquer mexida em ingestao ou ranking lexical

## Artefatos principais
- `docs/diagnostics/semantic_retrieval_trace_20260315T054100Z.json`
- `docs/diagnostics/semantic_ranking_trace_20260315T054100Z.json`
- `docs/diagnostics/semantic_retrieval_pipeline_map_20260315T054100Z.md`
- `docs/diagnostics/semantic_context_analysis_20260315T054100Z.md`
- `docs/diagnostics/semantic_fallback_analysis_20260315T054100Z.md`
- `docs/diagnostics/semantic_retrieval_failure_report_20260315T054100Z.md`
