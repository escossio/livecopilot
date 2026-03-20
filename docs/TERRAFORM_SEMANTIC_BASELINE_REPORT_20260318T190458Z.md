# Terraform semantic baseline report -- 2026-03-18T19:04:58Z

## Context
- This report reruns the Terraform semantic baseline after the focused chunk refinement for CLI, state/backend/workspaces, and modules.
- The sandbox remains isolated in `data/semantic_index_experiments/terraform_pilot/` and does not touch the global index.

## Embeddings and isolated index
- Directory: `data/semantic_index_experiments/terraform_pilot/`
- Files: `embeddings.jsonl` and `metadata.json`
- Model: `text-embedding-3-large`
- Chunks embedded: 15
- Embedding dimension: 3072
- Segment word limit: 1200
- Average chunk length: 375.33 words
- Generated at: `2026-03-18T19:05:06.616158+00:00`

## Lexical vs semantic comparison
| Question | Lexical top | Semantic top | Result |
| --- | --- | --- | --- |
| What does terraform plan do? | `terraform-cli-apply-003` / FALHA | `terraform-cli-plan-002` / COERENTE | MELHORA |
| What does terraform apply do? | `terraform-aws-001` / FALHA | `terraform-cli-apply-003` / COERENTE | MELHORA |
| What is Terraform state? | `terraform-state-003` / COERENTE | `terraform-state-003` / COERENTE | EMPATE |
| What is a backend in Terraform? | `terraform-backend-004` / COERENTE | `terraform-backend-004` / COERENTE | EMPATE |
| What are Terraform workspaces? | `terraform-workspaces-005` / COERENTE | `terraform-workspaces-005` / COERENTE | EMPATE |
| What is a Terraform module? | `terraform-module-inputs-003` / PARCIALMENTE_COERENTE | `terraform-modules-001` / COERENTE | MELHORA |
| How do Terraform modules use source? | `terraform-aws-001` / FALHA | `terraform-module-source-002` / COERENTE | MELHORA |
| What are module inputs in Terraform? | `terraform-module-inputs-003` / COERENTE | `terraform-module-inputs-003` / COERENTE | EMPATE |
| What are module outputs in Terraform? | `terraform-aws-001` / FALHA | `terraform-module-outputs-004` / COERENTE | MELHORA |
| What is the AWS provider in Terraform? | `terraform-aws-001` / COERENTE | `terraform-aws-002` / PARCIALMENTE_COERENTE | PIORA |
| What is aws_instance in Terraform? | `terraform-aws-instance-001` / COERENTE | `terraform-aws-instance-001` / COERENTE | EMPATE |

Detailed structured results are stored in `docs/TERRAFORM_SEMANTIC_BASELINE_RESULTS_20260318T190458Z.json`.

## Summary
- Lexical summary: 6 COERENTE, 1 PARCIALMENTE_COERENTE, 4 FALHA.
- Semantic summary: 10 COERENTE, 1 PARCIALMENTE_COERENTE, 0 FALHA.
- Relative to lexical: 5 MELHORA, 5 EMPATE, 1 PIORA.
- The required core topics are now semantically stable:
  - `plan` -> coherent
  - `apply` -> coherent
  - `state` -> coherent
  - `backend` -> coherent
  - `workspaces` -> coherent
  - `module` -> coherent
  - `module source` -> coherent
  - `module inputs` -> coherent
  - `module outputs` -> coherent

## Closure decision
- The refinement is sufficient for formal closure of the Terraform front.
- Reason: every mandatory core/state/modules topic is now semantically coherent in the rerun baseline.
- Residual note: the AWS provider definition question still prefers `terraform-aws-002` semantically, which is only partially coherent because it lands on example usage instead of the overview chunk. This is a provider-specific quality gap, not a blocker for the front closure criteria defined for this round.
