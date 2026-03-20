# MACHINE_LEARNING Corpus Refinement Report V7

## Contexto
- Refinement final e estritamente focado na lacuna residual `machine learning frameworks` após o semantic baseline V8.
- Objetivo: adicionar páginas oficiais do `scikit-learn` com uso prático e mais explicativo.

## Novas URLs adicionadas
- `https://scikit-learn.org/1.3/tutorial/statistical_inference/supervised_learning.html`
- `https://scikit-learn.org/1.3/tutorial/statistical_inference/model_selection.html`

## Número de páginas materializadas
- Total: 2 páginas HTML novas em `data/knowledge_raw/machine_learning/`.
- Arquivos:
  - `data/knowledge_raw/machine_learning/framework_guides/supervised_learning_html.html`
  - `data/knowledge_raw/machine_learning/framework_guides/model_selection_html.html`

## Como ajudam `machine learning frameworks`
- `supervised_learning_html.html`: tutorial prático oficial que mostra como usar `scikit-learn` para aprendizado supervisionado de forma mais direta.
- `model_selection_html.html`: tutorial oficial que explica `cross-validation`, `tuning` e seleção de modelo, reforçando o uso real do framework em vez de páginas de índice.

## Justificativa da seleção
- As páginas são oficiais, estáveis e mais orientadas a uso do que páginas de navegação.
- O foco foi maximizar conteúdo de onboarding e aplicação prática do framework.
- O refinement permaneceu restrito à frente `MACHINE_LEARNING`.

## Observações operacionais
- O crawler materializou as páginas sem executar parsing, chunking, embeddings, semantic baseline ou closure_decision.
- Nenhuma outra frente foi alterada.

