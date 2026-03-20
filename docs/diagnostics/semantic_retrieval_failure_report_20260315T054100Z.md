# Semantic Retrieval / Ranking / Context Failure Report — 2026-03-15T05:41:00Z

## Resumo objetivo
- O corpus vetorial ativo contem documentos e chunks de Terraform e Kubernetes.
- `semantic_search()` recupera resultados corretos para os tres canarios.
- O gargalo principal atual nao e o retrieval vetorial bruto.
- Terraform falha porque `generate_suggestions()` zera os hits semanticos apos `_passes_domain_gating()`.
- Kubernetes falha porque o contexto recuperado nao vira resposta principal; o sistema responde com o slot curto generico.

## Evidencia de retrieval real
### Terraform state
- `semantic_search.count=3`
- fontes: `terraform_docs_selected/language/state/index.md`, `terraform_docs_selected/language/state/purpose.md`
- apos `generate_suggestions()`: `result_count=0`, `context=''`

### Terraform plan/apply
- `semantic_search.count=3`
- fontes: docs de `plan/apply` em `terraform_docs_selected*`
- apos `generate_suggestions()`: `result_count=0`, `context=''`

### Kubernetes Pod vs Service
- `semantic_search.count=3`
- fontes: `kubernetes_docs_selected/.../service.md`
- apos `generate_suggestions()`: `result_count=3`, `context_len=985`
- resposta principal ainda generica

## Ranking e filtros
- Busca vetorial: top resultados plausiveis para os tres canarios.
- Busca lexical: muito ampla e dominada por livros/PDFs, com ruido alto.
- Filtro critico identificado: `_passes_domain_gating()` usa `DOMAIN_SIGNALS` que contem `kubernetes`, `docker`, `backend`, `api` etc., mas nao contem `terraform`, `state`, `plan` ou `apply`.
- Consequencia: consultas Terraform passam pelo retrieval, mas falham no gating e sao descartadas antes de montar a resposta.

## Diferenca Terraform vs Kubernetes
- Terraform: falha principal em `domain_gating` apos retrieval.
- Kubernetes: retrieval e contexto funcionam; falha principal na promocao do conteudo para a resposta final.

## Proxima correcao cirurgica recomendada
1. Revisar `DOMAIN_SIGNALS` / `_passes_domain_gating()` para nao descartar hits semanticos validos de Terraform.
2. Ajustar a selecao de resposta final para priorizar o resumo contextual quando `knowledge_context.result_count > 0`.
3. So depois disso, revalidar se ainda resta problema de ranking lexical ou necessidade de endurecer fallback.
