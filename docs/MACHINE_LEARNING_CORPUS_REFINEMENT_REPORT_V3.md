# MACHINE_LEARNING Corpus Refinement Report V3

## Contexto
- Refinement cirúrgico após o semantic baseline V4.
- Objetivo: melhorar exclusivamente as três lacunas ainda `PARCIAL` (`what is overfitting`, `bias variance tradeoff`, `machine learning frameworks`) sem avançar o pipeline.

## Novas URLs adicionadas
- `https://scikit-learn.org/stable/getting_started.html`
- `https://scikit-learn.org/stable/modules/cross_validation.html`
- `https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html`
- `https://pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html`

## Número de páginas materializadas
- Total: 4 páginas HTML novas em `data/knowledge_raw/machine_learning/`
- Arquivos:
  - `data/knowledge_raw/machine_learning/framework_guides/getting_started_html.html`
  - `data/knowledge_raw/machine_learning/evaluation/cross_validation_html.html`
  - `data/knowledge_raw/machine_learning/framework_guides/quickstart_tutorial_html.html`
  - `data/knowledge_raw/machine_learning/framework_guides/buildmodel_tutorial_html.html`

## Lacunas cobertas
- `getting_started_html.html`: melhora a visão geral do scikit-learn com menos dependência de índice/TOC.
- `cross_validation_html.html`: ataca `overfitting` e `bias variance tradeoff` com explicação oficial de validação cruzada.
- `quickstart_tutorial_html.html`: reforça o onboarding prático do PyTorch com fluxo de treino/avaliação.
- `buildmodel_tutorial_html.html`: adiciona um tutorial oficial do PyTorch com construção de modelo, útil para a lacuna de frameworks.

## Justificativa da seleção
- As páginas escolhidas são oficiais, estáveis e mais focadas do que páginas puramente navegacionais.
- O par `cross_validation` + `getting_started` deve aumentar a cobertura conceitual em `overfitting` e `bias variance tradeoff`.
- Os dois tutoriais do PyTorch acrescentam conteúdo prático de uso do framework, reduzindo a dependência de índices e páginas-resumo.
- O refinement permaneceu alinhado ao baseline V4 e restringido aos domínios oficiais aceitos.

## Observações operacionais
- O crawler materializou as páginas sem executar parsing, chunking, embeddings, semantic baseline ou closure_decision.
- Uma verificação prévia confirmou que as URLs novas retornam conteúdo oficial estável.
