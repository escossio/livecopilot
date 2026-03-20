# MACHINE_LEARNING Corpus Refinement Report V2

## Contexto
- Refinement cirúrgico após o semantic baseline V3.
- Objetivo: cobrir lacunas pontuais em `overfitting`, `machine learning evaluation metrics`, `bias variance tradeoff` e `machine learning frameworks` sem avançar para parsing/chunking.

## Novas URLs adicionadas
- `https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall`
- `https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc`
- `https://scikit-learn.org/stable/modules/model_evaluation.html`
- `https://scikit-learn.org/stable/modules/learning_curve.html`
- `https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html`
- `https://pytorch.org/tutorials/beginner/basics/intro.html`
- `https://www.tensorflow.org/tutorials/quickstart/beginner`

## Categorias adicionadas
- `evaluation`
- `framework_guides`

## Páginas materializadas nesta rodada
- Total: 7 páginas HTML novas em `data/knowledge_raw/machine_learning/`
- Arquivos:
  - `data/knowledge_raw/machine_learning/evaluation/precision_and_recall.html`
  - `data/knowledge_raw/machine_learning/evaluation/roc_and_auc.html`
  - `data/knowledge_raw/machine_learning/evaluation/model_evaluation_html.html`
  - `data/knowledge_raw/machine_learning/evaluation/learning_curve_html.html`
  - `data/knowledge_raw/machine_learning/evaluation/sklearn_metrics_confusion_matrix_html.html`
  - `data/knowledge_raw/machine_learning/framework_guides/intro_html.html`
  - `data/knowledge_raw/machine_learning/framework_guides/beginner.html`

## Lacunas cobertas por cada página
- `precision_and_recall.html`: reforça `precision`, `recall` e leitura de métricas de classificação.
- `roc_and_auc.html`: cobre ROC/AUC para avaliação binária.
- `model_evaluation_html.html`: amplia o bloco de `evaluation` do scikit-learn com métricas, scoring e seleção de modelos.
- `learning_curve_html.html`: ataca diretamente `overfitting` e `bias variance tradeoff` com curvas de aprendizado.
- `sklearn_metrics_confusion_matrix_html.html`: detalha a `confusion_matrix` usada em classificação.
- `intro_html.html`: melhora a visão geral oficial do PyTorch para a lacuna de frameworks.
- `beginner.html`: reforça o onboarding oficial do TensorFlow para comparação e uso básico do framework.

## Observações operacionais
- O refinement foi cirúrgico e alinhado ao baseline V3: só adicionou fontes oficiais focadas nas lacunas já observadas.
- O crawler materializou as páginas sem alterar parsing, chunking, embeddings ou baseline.
- Uma URL inicial de `scikit-learn` foi corrigida para `learning_curve.html` após 404, mantendo o escopo dentro de domínios oficiais aceitos.
