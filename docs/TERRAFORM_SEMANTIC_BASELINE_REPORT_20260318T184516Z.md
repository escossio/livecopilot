# Terraform semantic baseline report -- 2026-03-18T18:45:16Z

## Context
- The Terraform front already had source policy, source manifest, corpus freeze, parsing, chunking, and lexical validation documented.
- This round completed the missing semantic baseline step in an isolated sandbox at `data/semantic_index_experiments/terraform_pilot/`, without touching the global index.
- The baseline reused the existing Terraform chunks exactly as they were found in `data/knowledge_chunks/terraform/`: core/CLI, state, modules, and the minimal AWS subset.

## Embeddings and isolated index
- Directory: `data/semantic_index_experiments/terraform_pilot/`
- Files: `embeddings.jsonl` and `metadata.json`
- Model: `text-embedding-3-large`
- Chunks embedded: 9
- Embedding dimension: 3072
- Segment word limit: 1200
- Average chunk length: 564.67 words
- Generated at: `2026-03-18T18:45:16.623387+00:00`
- Source chunks: `data/knowledge_chunks/terraform/`

## Lexical vs semantic comparison
| Question | Lexical top | Semantic top | Result |
| --- | --- | --- | --- |
| What does terraform plan do? | `terraform-aws-001` / FALHA | `terraform-aws-002` / FALHA | EMPATE |
| What does terraform apply do? | `terraform-aws-001` / FALHA | `terraform-aws-002` / FALHA | EMPATE |
| What is Terraform state? | `terraform-aws-instance-001` / FALHA | `terraform-aws-001` / FALHA | EMPATE |
| What is a backend in Terraform? | none / FALHA | `terraform-aws-001` / FALHA | EMPATE |
| What are Terraform workspaces? | none / FALHA | `terraform-aws-001` / FALHA | EMPATE |
| What is a Terraform module? | `terraform-aws-001` / FALHA | `terraform-aws-002` / FALHA | EMPATE |
| How do Terraform modules use source? | `terraform-aws-001` / FALHA | `terraform-aws-002` / PARCIALMENTE_COERENTE | MELHORA |
| What are module inputs in Terraform? | `terraform-aws-001` / FALHA | `terraform-aws-001` / FALHA | EMPATE |
| What are module outputs in Terraform? | `terraform-aws-001` / FALHA | `terraform-aws-001` / FALHA | EMPATE |
| What is the AWS provider in Terraform? | `terraform-aws-001` / COERENTE | `terraform-aws-002` / PARCIALMENTE_COERENTE | PIORA |
| What is aws_instance in Terraform? | `terraform-aws-instance-001` / COERENTE | `terraform-aws-instance-001` / COERENTE | EMPATE |

Detailed structured results are stored in `docs/TERRAFORM_SEMANTIC_BASELINE_RESULTS_20260318T184516Z.json`.

## Summary
- Semantic baseline status: executed successfully.
- Semantic quality summary: 1 COERENTE, 2 PARCIALMENTE_COERENTE, 8 FALHA.
- Relative to lexical: 1 MELHORA, 9 EMPATE, 1 PIORA.
- Strong point: `aws_instance` is stable in both lexical and semantic retrieval.
- Main weakness: CLI, state, workspaces, and modules remain effectively uncovered because the current chunks for CLI/state/modules are still HashiConf placeholder text.
- Secondary weakness: the long AWS provider chunks dominate retrieval and attract unrelated Terraform questions.

## Conclusion
- The semantic baseline and embeddings now exist, so the front is no longer blocked by the absence of a semantic sandbox.
- The front still should not move to `closed`: the baseline shows insufficient semantic coverage for required topics in CLI, state/backend/workspaces, and modules.
- Terraform remains in `closure_pending` until the front runs semantic refinement or corrective chunk refinement for the weak areas and reruns this baseline.
