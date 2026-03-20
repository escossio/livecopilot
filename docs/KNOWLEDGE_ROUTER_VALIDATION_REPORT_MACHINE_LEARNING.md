# KNOWLEDGE Router Validation Report — MACHINE_LEARNING

## Evidência de registry
- `app/knowledge/knowledge_front_registry.json` contém a entrada `MACHINE_LEARNING`.
- Campos validados: `status: closed`, `enabled_for_routing: true`, `index_path: data/knowledge_embeddings/machine_learning`.
- Keywords incluídas: `machine learning`, `overfitting`, `supervised learning`, `unsupervised learning`, `linear regression`, `classification`, `gradient descent`, `confusion matrix`, `bias variance`, `scikit-learn`, `pytorch`, `tensorflow`.

## Queries de teste
| Query | Frente escolhida | Confidence | Observação |
| --- | --- | --- | --- |
| `what is overfitting` | `MACHINE_LEARNING` | `0.083` | Match direto por keyword `overfitting`; sem fallback. |
| `machine learning frameworks` | `MACHINE_LEARNING` | `0.083` | Match direto por keyword `machine learning`; sem fallback. |
| `linear regression example` | `MACHINE_LEARNING` | `0.083` | Match direto por keyword `linear regression`; sem ruído de substring. |

## Resultado final da integração
- O router passou a reconhecer `MACHINE_LEARNING` como frente roteável.
- A validação mostrou seleção consistente da frente em queries representativas.
- O precheck de fechamento foi executado e retornou `PRECHECK PASSED`.
- O fechamento permanece válido e regularizado com a frente integrada ao registry e ao índice de frentes.
