# MACHINE_LEARNING Corpus Refinement Report V6

## Contexto
- Refinement final e estritamente focado na lacuna residual `machine learning frameworks` após o semantic baseline V7.
- Objetivo: adicionar páginas oficiais mais explicativas e práticas de framework para melhorar a recuperação da query.

## Novas URLs adicionadas
- `https://scikit-learn.org/stable/auto_examples/index.html`
- `https://scikit-learn.org/1.3/tutorial/text_analytics/working_with_text_data.html`

## Número de páginas materializadas
- Total: 2 páginas HTML novas em `data/knowledge_raw/machine_learning/`.
- Arquivos:
  - `data/knowledge_raw/machine_learning/framework_reference/index_html.html`
  - `data/knowledge_raw/machine_learning/framework_guides/working_with_text_data_html.html`

## Como ajudam `machine learning frameworks`
- `index_html.html`: reúne exemplos oficiais e práticos do `scikit-learn`, oferecendo recuperação mais orientada a uso real do framework.
- `working_with_text_data_html.html`: tutorial prático oficial com fluxo de uso, útil para responder a query de frameworks com conteúdo mais explicativo do que páginas de índice.

## Justificativa da seleção
- As páginas são oficiais, estáveis e continuam dentro do domínio aceito.
- O foco foi priorizar material mais prático do que navegacional, buscando ancorar a query de frameworks em exemplos e tutorial aplicados.
- O refinement permaneceu restrito à frente `MACHINE_LEARNING`.

## Observações operacionais
- O crawler materializou as páginas sem executar parsing, chunking, embeddings, semantic baseline ou closure_decision.
- Nenhuma outra frente foi alterada.

