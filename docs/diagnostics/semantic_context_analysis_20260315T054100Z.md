# Semantic Context Analysis — 2026-03-15T05:41:00Z

## Canary 1 — Terraform state
- Query: `Para que serve o arquivo de state no Terraform?`
- Busca vetorial: 3 resultados relevantes.
- Top fontes vetoriais:
  - `terraform_docs_selected/language/state/index.md`
  - `terraform_docs_selected/language/state/purpose.md`
- Estado apos `generate_suggestions()`:
  - `result_count=0`
  - `context=''`
  - `sources=[]`
- Leitura: retrieval encontrou material correto, mas o contexto foi zerado antes da resposta final.

## Canary 2 — Terraform plan/apply
- Query: `Qual a diferenca entre terraform plan e terraform apply?`
- Busca vetorial: 3 resultados relevantes.
- Top fontes vetoriais:
  - `terraform_docs_selected_incremental_round2/content/terraform/v1.14.x/docs/cli/run/index.md`
  - `terraform_docs_selected/cli/commands/apply.md`
  - `terraform_docs_selected_incremental_round2/content/terraform/v1.14.x/docs/cli/commands/apply.md`
- Estado apos `generate_suggestions()`:
  - `result_count=0`
  - `context=''`
  - `sources=[]`
- Leitura: mesmo padrao do canario de state. O contexto cai para vazio apesar de haver hits semanticos bons.

## Canary 3 — Kubernetes Pod vs Service
- Query: `Qual a diferenca entre Pod e Service no Kubernetes?`
- Busca vetorial: 3 resultados relevantes.
- Top fontes vetoriais:
  - `kubernetes_docs_selected/content/en/docs/concepts/services-networking/service.md`
  - `kubernetes_docs_selected/content/en/docs/concepts/services-networking/service.md`
  - `kubernetes_docs_selected/content/en/docs/concepts/services-networking/service.md`
- Estado apos `generate_suggestions()`:
  - `result_count=3`
  - `context_len=985`
  - fontes preservadas no contexto final
- Problema observado:
  - `final_answer_slot` ficou generico: `Pelo contexto técnico, o caminho mais seguro...`
  - o resumo baseado no conhecimento ficou em `knowledge_summary_slot`, nao no slot principal consumido pela resposta final.
- Leitura: o contexto existe e e plausivel, mas a camada de resposta nao o utiliza como answer principal.

## Classificacao por camada
- Terraform state: `RETRIEVAL OK / CONTEXTO ZERADO`
- Terraform plan/apply: `RETRIEVAL OK / CONTEXTO ZERADO`
- Kubernetes Pod vs Service: `RETRIEVAL OK / CONTEXTO OK / ANSWER SLOT GENERICO`
