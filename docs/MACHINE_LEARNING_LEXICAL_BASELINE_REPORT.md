# MACHINE LEARNING Lexical Baseline Report

## Context
- Corpus: 4 HTMLs oficiais chunked em 8 arquivos (2 chunks por HTML) provenientes dos guias de scikit-learn, PyTorch, TensorFlow e Google ML Crash Course.
- Stage: avaliação lexical pós-chunking antes de qualquer embedding.

## Query Summary
| Query | Top chunk (source) | Top1 relevance | Top3 quality | Notes (lacunas / ruído) |
| --- | --- | --- | --- | --- |
| what is overfitting in machine learning | `crash_course-0002-f779db68bb57add5` (crash_course.html) | Alta (lista “Datasets, generalization, and overfitting” e módulos de preparação de dados) | Alta (TF guide e scikit-learn docs complementam com generalização e regularização) | Nenhuma lacuna crítica; zero ruído, domínio claro. |
| difference between supervised and unsupervised learning | `user_guide_html-0002-050d59c7447390fd` (user_guide_html.html) | Média-alta (TOC do scikit-learn evidencia os dois blocos) | Média (top3 inclui PyTorch/TensorFlow neon cada um com listas de tópicos) | Lacuna leve: o chunk atual enumera seções mas o texto de apoio deve ser reforçado no semantic stage; não há ruído. |
| what is gradient descent | `crash_course-0002-f779db68bb57add5` (crash_course.html) | Alta (módulo “Linear Regression” destaca loss, gradient descent e tuning) | Alta (scikit-learn lista SGD, PyTorch reference realça otimização iterativa) | Lacuna tolerável: falta de fórmula numérica, mas a explicação contextual é consistente; sem ruído. |
| what is a confusion matrix | `crash_course-0002-f779db68bb57add5` (crash_course.html) | Alta (confusion matrices e métricas aparecem logo no módulo de classificação) | Alta (scikit-learn enumera classificadores e métricas relevantes; TensorFlow guide cita “Metrics”) | Nenhuma lacuna crítica; domínio mantido sem ruído. |

## Observações
- O corpus responde com chunks que fazem referência direta aos tópicos solicitados e os top3 permanecem em domínio de ML técnico, sem trazer marketing ou domínios externos.
- Os únicos gaps são no nível de detalhe (explicações curtas/TOC) e serão atendidos naturalmente pela próxima fase de embeddings + semantic baseline.

## Decision
- **Status**: aprovado para `semantic_embeddings`
- Justificativa: a bateria lexical mostra alta coerência e ausência de ruído, e os principais tópicos do manifesto estão representados por chunked content técnico; as lacunas detectadas (falta de detalhamento textual além de listas) podem ser resolvidas na aproximação semântica.
