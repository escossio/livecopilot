# Round Summary: Project Brain Ranking Recalibration (Conservative)

Data: 2026-03-11

## Objetivo da rodada
Aplicar uma unica recalibracao conservadora para reduzir dominancia lexical no ranking local, sem alterar schema, ingestao, banco vetorial ou routing.

## Mudanca unica aplicada
- Arquivo: `app/services/knowledge_search.py`
- Formula antes:
  - `adjusted_score = (base_score * hygiene_score) + (practicality_bonus * practicality_bonus_weight)`
- Formula depois:
  - `lexical_weight = 0.85`
  - `adjusted_score = (base_score * lexical_weight * hygiene_score) + (practicality_bonus * practicality_bonus_weight)`
- Escopo: apenas peso lexical no score final; nenhuma outra alteracao de ranking.

## Bateria before/after (8 queries)
Queries:
- `helm install chart`
- `liveness probe nginx`
- `kubectl create pod`
- `readiness probe service`
- `nginx deployment kubernetes`
- `terraform helm provider`
- `docker container healthcheck`
- `kubernetes service manifest`

### Top3 (campos auditados)
Formato por item: `source_file | score | base_score | practicality_bonus | signals`

1) `helm install chart`
- before
  - `Mastering Terraform...epub | 181.759 | 175.099 | 0.37 | [helm, devops-context]`
  - `Mastering Terraform...epub | 161.522 | 158.102 | 0.19 | [helm, devops-context]`
  - `Mastering Terraform...epub | 150.798 | 147.378 | 0.19 | [helm, devops-context]`
- after
  - `Mastering Terraform...epub | 155.494 | 175.099 | 0.37 | [helm, devops-context]`
  - `Mastering Terraform...epub | 137.807 | 158.102 | 0.19 | [helm, devops-context]`
  - `Mastering Terraform...epub | 128.691 | 147.378 | 0.19 | [helm, devops-context]`

2) `liveness probe nginx`
- before
  - `Kubernetes Up and Running...epub | 117.593 | 107.873 | 0.54 | [liveness-probe, liveness, probe, devops-context]`
  - `Kubernetes Up and Running...epub | 101.371 | 91.651 | 0.54 | [liveness-probe, liveness, probe, devops-context]`
  - `Kubernetes Up and Running...epub | 100.861 | 99.421 | 0.08 | [nginx, devops-context]`
- after
  - `Kubernetes Up and Running...epub | 101.412 | 107.873 | 0.54 | [liveness-probe, liveness, probe, devops-context]`
  - `Kubernetes Up and Running...epub | 87.623 | 91.651 | 0.54 | [liveness-probe, liveness, probe, devops-context]`
  - `Kubernetes Up and Running...epub | 85.948 | 99.421 | 0.08 | [nginx, devops-context]`

3) `kubectl create pod`
- before
  - `Kubernetes Up and Running...epub | 162.696 | 155.856 | 0.38 | [kubectl, pod, devops-context]`
  - `Kubernetes Up and Running...epub | 153.242 | 143.882 | 0.52 | [kubectl, pod, create, devops-context]`
  - `Kubernetes Up and Running...epub | 145.324 | 138.124 | 0.4 | [kubectl, pod, create]`
- after
  - `Kubernetes Up and Running...epub | 139.318 | 155.856 | 0.38 | [kubectl, pod, devops-context]`
  - `Kubernetes Up and Running...epub | 131.66 | 143.882 | 0.52 | [kubectl, pod, create, devops-context]`
  - `Kubernetes Up and Running...epub | 124.606 | 138.124 | 0.4 | [kubectl, pod, create]`

4) `readiness probe service`
- before
  - `Kubernetes Up and Running...epub | 110.965 | 100.165 | 0.6 | [readiness, probe, service, devops-context]`
  - `Kubernetes Up and Running...epub | 97.39 | 89.83 | 0.42 | [readiness, probe, service, devops-context]`
  - `Designing Distributed Systems...epub | 87.649 | 80.089 | 0.42 | [readiness, probe, service, devops-context]`
- after
  - `Kubernetes Up and Running...epub | 95.94 | 100.165 | 0.6 | [readiness, probe, service, devops-context]`
  - `Kubernetes Up and Running...epub | 83.915 | 89.83 | 0.42 | [readiness, probe, service, devops-context]`
  - `Designing Distributed Systems...epub | 75.636 | 80.089 | 0.42 | [readiness, probe, service, devops-context]`

5) `nginx deployment kubernetes`
- before
  - `Mastering Terraform...epub | 139.617 | 135.657 | 0.22 | [nginx, deployment, devops-context]`
  - `Kubernetes Up and Running...epub | 131.327 | 127.367 | 0.22 | [nginx, deployment, devops-context]`
  - `Mastering Terraform...epub | 118.541 | 113.861 | 0.26 | [deployment, devops-context]`
- after
  - `Mastering Terraform...epub | 119.268 | 135.657 | 0.22 | [nginx, deployment, devops-context]`
  - `Kubernetes Up and Running...epub | 112.222 | 127.367 | 0.22 | [nginx, deployment, devops-context]`
  - `Mastering Terraform...epub | 101.462 | 113.861 | 0.26 | [deployment, devops-context]`

6) `terraform helm provider`
- before
  - `Mastering Terraform...epub | 258.739 | 252.079 | 0.37 | [helm, devops-context]`
  - `Mastering Terraform...epub | 182.669 | 179.249 | 0.19 | [helm, devops-context]`
  - `Terraform in Depth.pdf | 145.36 | 148.6 | -0.18 | [exam]`
- after
  - `Mastering Terraform...epub | 220.927 | 252.079 | 0.37 | [helm, devops-context]`
  - `Mastering Terraform...epub | 155.782 | 179.249 | 0.19 | [helm, devops-context]`
  - `Terraform in Depth.pdf | 123.07 | 148.6 | -0.18 | [exam]`

7) `docker container healthcheck`
- before
  - `Docker_Deep_Dive_Nigel_Poulton.pdf | 250.536 | 249.096 | 0.08 | [container, devops-context]`
  - `Docker_Deep_Dive_Nigel_Poulton.pdf | 241.498 | 242.218 | -0.04 | [exam]`
  - `Docker for Developers...epub | 185.883 | 183.363 | 0.14 | [container]`
- after
  - `Docker_Deep_Dive_Nigel_Poulton.pdf | 213.172 | 249.096 | 0.08 | [container, devops-context]`
  - `Docker_Deep_Dive_Nigel_Poulton.pdf | 205.165 | 242.218 | -0.04 | [exam]`
  - `Docker for Developers...epub | 158.378 | 183.363 | 0.14 | [container]`

8) `kubernetes service manifest`
- before
  - `Mastering Terraform...epub | 126.628 | 121.948 | 0.26 | [service, devops-context]`
  - `Mastering Terraform...epub | 123.396 | 121.956 | 0.08 | [service, devops-context]`
  - `Kubernetes Up and Running...epub | 122.974 | 118.294 | 0.26 | [service, devops-context]`
- after
  - `Mastering Terraform...epub | 108.336 | 121.948 | 0.26 | [service, devops-context]`
  - `Kubernetes Up and Running...epub | 105.23 | 118.294 | 0.26 | [service, devops-context]`
  - `Mastering Terraform...epub | 105.102 | 121.956 | 0.08 | [service, devops-context]`

## Avaliacao objetiva
- Estabilidade de top1: `8/8` queries (100%).
- Diversidade de fontes no conjunto top3 (24 slots):
  - before: `6` fontes unicas
  - after: `6` fontes unicas
- Sinais praticos no top1: mantidos (mesmos `practicality_bonus` e sinais do top1 em todas as queries).
- Regressao evidente: nao observada no topo (top1 preservado em toda a bateria).

## Smokes obrigatorios
- `./scripts/smoke_project_brain_query_wrapper.sh` => OK
- `./scripts/smoke_round_continuity_default.sh` => OK

## Decisao
- **Manter mudanca** (`lexical_weight=0.85`).
- Justificativa: recalibracao conservadora atingiu objetivo de reduzir dominancia lexical sem quebrar top1 nem smokes.
