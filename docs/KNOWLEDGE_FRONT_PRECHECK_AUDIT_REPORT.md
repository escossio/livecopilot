# Knowledge Front Precheck Audit Report

## Frentes auditadas
- `JAVA`
- `OPENAI_PRODUCTS`
- `TERRAFORM`
- `DOCKER`
- `KUBERNETES`
- `PYTHON`
- `POSTGRESQL`
- `LINUX`
- `C_PILOT`
- `MACHINE_LEARNING`

## Resultado por frente
| Front | Status | Motivo |
| --- | --- | --- |
| `JAVA` | `PASS` | Todos os artefatos obrigatórios existem e o registry está consistente. |
| `OPENAI_PRODUCTS` | `PASS` | Todos os artefatos obrigatórios existem e o registry está consistente. |
| `TERRAFORM` | `FAIL` | `Missing front document: docs/FRONT_TERRAFORM.md` |
| `DOCKER` | `FAIL` | `Missing front document: docs/FRONT_DOCKER.md` |
| `KUBERNETES` | `FAIL` | `Missing front document: docs/FRONT_KUBERNETES.md` |
| `PYTHON` | `FAIL` | `knowledge fronts index missing required reference: PYTHON` |
| `POSTGRESQL` | `FAIL` | `knowledge fronts index missing required reference: POSTGRESQL` |
| `LINUX` | `FAIL` | `knowledge fronts index missing required reference: LINUX` |
| `C_PILOT` | `FAIL` | `Missing front document: docs/FRONT_C_PILOT.md` |
| `MACHINE_LEARNING` | `PASS` | Todos os artefatos obrigatórios existem e o registry está consistente. |

## Resumo das frentes regulares
- `JAVA`, `OPENAI_PRODUCTS`, `MACHINE_LEARNING`

## Resumo das frentes irregulares
- `TERRAFORM`, `DOCKER`, `KUBERNETES`, `PYTHON`, `POSTGRESQL`, `LINUX`, `C_PILOT`

## Totais
- **PASS**: 3
- **FAIL**: 7

## Observação
- A auditoria foi bloqueante e não alterou corpus, embeddings ou baselines.
- Os FAILs apontam exatamente o requisito ausente ou divergente, sem mascaramento.
