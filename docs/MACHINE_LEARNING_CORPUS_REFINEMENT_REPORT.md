# MACHINE LEARNING Corpus Refinement Report

## Contexto
- Frente `MACHINE_LEARNING` em `corpus_refinement` após o baseline semântico que validou os 8 chunks iniciais.
- Objetivo: enriquecer o manifesto com páginas conceituais adicionais oficiais e materializar o raw correspondente, mantendo o pipeline parado antes do parsing.

## Atualizações no manifesto
| URL | Categoria | Observação |
| --- | --- | --- |
| `https://developers.google.com/machine-learning/crash-course/prereqs-and-prework` | foundations | Introduz álgebra, probabilidade e fluxos de dados usados pela etapa Foundations.
| `https://developers.google.com/machine-learning/crash-course/linear-regression` | algorithms | Descreve arquitetura, loss e gradient descent aplicada a regressão linear.
| `https://developers.google.com/machine-learning/crash-course/overfitting` | evaluation | Aborda generalização, métricas de validação e matriz de confusão.
| `https://scikit-learn.org/stable/tutorial/machine_learning_map/` | framework_guides | Mapa conceitual do scikit-learn relacionando algoritmos aos desafios supervisionados e não supervisionados.
| `https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html` | framework_guides | Tutorial prático do PyTorch com tensores, autograd e treinamento de redes.
| `https://www.tensorflow.org/tutorials/keras/classification` | framework_guides | Guia passo a passo de classificação com tf.keras para treino, avaliação e exportação.

## Corpus materializado
- `scripts/corpus/manifest_crawler.py machine_learning` materializou 6 páginas novas (Foundations, Linear Regression, Overfitting, scikit-learn map, PyTorch blitz e TensorFlow classification) em `data/knowledge_raw/machine_learning/` sob as categorias `foundations`, `algorithms`, `evaluation` e `framework_guides`.
- Cada download gerou o HTML e o `.metadata.json` com `url`, `domain`, `content_hash` e `download_timestamp`, mantendo o histórico do crawler.
- Não foi executado parsing, chunking, embeddings ou baseline nesta rodada; os arquivos permanecem brutos para as próximas etapas.

## Próximos passos planejados
- Validar que as novas páginas cobrem lacunas conceituais detectadas no baseline.
- Preparar parsing/chunking após a etapa `corpus_refinement` ser confirmada.
