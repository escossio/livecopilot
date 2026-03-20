# MACHINE_LEARNING Corpus Refinement Report V4

## Contexto
- Refinement final e cirúrgico após o semantic baseline V5.
- Objetivo: atacar apenas as lacunas residuais `bias variance tradeoff` e `machine learning frameworks` sem avançar o pipeline.

## Novas URLs adicionadas
- `https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.validation_curve.html`

## Número de páginas materializadas
- Total: 1 página HTML nova em `data/knowledge_raw/machine_learning/`.
- Arquivo:
  - `data/knowledge_raw/machine_learning/evaluation/sklearn_model_selection_validation_curve_html.html`

## Lacunas cobertas
- `sklearn_model_selection_validation_curve_html.html`: página oficial mais focada para diagnosticar bias-variance tradeoff com curvas de validação e ajuste de hiperparâmetros.

## Justificativa da seleção
- A página é oficial, estável e mais específica do que os módulos gerais já presentes.
- Ela complementa `learning_curve` com um ponto de apoio mais explícito para `bias variance tradeoff`.
- O refinement permaneceu dentro dos domínios oficiais aceitos e não alterou outras frentes.

## Observações operacionais
- O crawler materializou a nova página sem executar parsing, chunking, embeddings, semantic baseline ou closure_decision.
- As páginas já existentes para onboarding de frameworks continuaram válidas; esta rodada focou apenas na lacuna remanescente mais clara do baseline V5.

