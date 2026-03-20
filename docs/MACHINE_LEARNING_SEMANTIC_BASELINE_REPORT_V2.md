# MACHINE_LEARNING Semantic Baseline Report V2

## Resumo
- **Modelo de embedding:** text-embedding-3-large (20 embeddings de 3072 dim em `data/knowledge_embeddings/machine_learning/`).
- **Corpus:** 10 documentos e 20 chunks reprocessados após o refinement.
- **Queries testadas:** 10 (lista abaixo no detalhamento).
- **Objetivo:** validar a recuperação semântica com as queries da frente e confirmar o baseline antes da decisão de closure.

## Resultados por query
1. **machine learning basics**
   - Top1: chunk `prereqs_and_prework-0002-601a60add4eb8699` (machine_learning/foundations/prereqs_and_prework.html), score 177.115.
   - Top3: inclui também `crash_course-0002-f779db68bb57add5` e `overfitting-0002-3d64e1dcc35a7c1d`.
   - Top5 docs: foundations/prereqs_and_prework.html; educational_course/crash_course.html; evaluation/overfitting.html; Docker for Developers...; framework_guides/deep_learning_60min_blitz_html.html.
   - Relevância: **Medium** (intro geral, higienizado como low_value_document mas mantém o conceito de fundamentos básicos).

2. **what is overfitting**
   - Top1: chunk `overfitting-0002-3d64e1dcc35a7c1d` (evaluation/overfitting.html), score 58.036.
   - Top3: inclui `azure_networking_documentation-0002-b2214c93fb7b3d0d`, `classification-0003-e88009040a2bc0b0`.
   - Top5 docs: evaluation/overfitting.html; azure/primary/azure_networking_documentation.html; framework_guides/classification.html; Terraform_Up_and_Running_3rd_Ed (x2).
   - Relevância: **High** (top1 vindo da página oficial de overfitting, mesmo com penalidade estética).

3. **linear regression example**
   - Top1: `linear_regression-0002-09c953b16480951d` (algorithms/linear_regression.html), score 198.829.
   - Top3: user_guide_html; crash_course.
   - Top5 docs: algorithms/linear_regression.html; framework_user_guide/user_guide_html.html; educational_course/crash_course.html; Python 3.11 Library Reference (x2).
   - Relevância: **High** (top1 e top2 são páginas oficiais com descrição de regressão linear).

4. **classification vs regression**
   - Top1: `user_guide_html-0002-050d59c7447390fd` (framework_user_guide/user_guide_html.html), score 160.892.
   - Top3: inclui `linear_regression-0002-09c953b16480951d`, `crash_course-0002-f779db68bb57add5`.
   - Top5 docs: framework_user_guide/user_guide_html.html; algorithms/linear_regression.html; educational_course/crash_course.html; AWS Security Cookbook...; docker-docs/text-classification.md.
   - Relevância: **Medium** (expõe regressão/classificação no guia, mas fragmentos são orientados a tópicos técnicos e sofreram penalidades).

5. **deep learning pytorch tutorial**
   - Top1: `deep_learning_60min_blitz_html-0002-838e77ea7bbc71aa` (framework_guides/deep_learning... html), score 580.603.
   - Top3: index_html; prereqs_and_prework.
   - Top5 docs: framework_guides/deep_learning_60min_blitz_html.html; framework_reference/index_html.html; foundations/prereqs_and_prework.html; educational_course/crash_course.html; evaluation/overfitting.html.
   - Relevância: **High** (PyTorch blitz domina o ranking).

6. **tensorflow classification tutorial**
   - Top1: `guide-0002-5f9db6d4df3420bc` (framework_guide/guide.html), score 249.516.
   - Top3: inclui classification, deep_learning_60min_blitz_html.
   - Top5 docs: framework_guide/guide.html; framework_guides/classification.html; framework_guides/deep_learning_60min_blitz_html.html; framework_user_guide/user_guide_html.html; docker-docs/tensorflowjs.md.
   - Relevância: **High** (guia TensorFlow explicitamente classifica classificações).

7. **machine learning evaluation metrics**
   - Top1: `prereqs_and_prework-0002-601a60add4eb8699`, score 178.344.
   - Top3: inclui crash_course e overfitting.
   - Top5 docs: foundations/prereqs_and_prework.html; educational_course/crash_course.html; evaluation/overfitting.html; The KCNA Book...; framework_user_guide/user_guide_html.html.
   - Relevância: **Medium** (intro tem métricas implícitas, mas carece de seção dedicada).

8. **bias variance tradeoff**
   - Top1: chunk de `Building Generative AI Services with FastAPI...`, score 98.848.
   - Top3: linear_regression; Python 3.11 Library Reference.
   - Top5 docs: Building Generative AI Services with FastAPI...; algorithms/linear_regression.html; Python 3.11 Library Reference (x3).
   - Relevância: **Low** (top1 sai de outro front; porém, o ref ML está no top2).

9. **supervised vs unsupervised learning**
   - Top1: `prereqs_and_prework-0002-601a60add4eb8699`, score 98.313.
   - Top3: inclui Building Data Science Applications with FastAPI; user_guide_html.
   - Top5 docs: foundations/prereqs_and_prework.html; Building Data Science Applications with FastAPI.pd.pdf; framework_user_guide/user_guide_html.html; educational_course/crash_course.html; evaluation/overfitting.html.
   - Relevância: **Medium** (front domina top1, mas snippet do prereqs é introdutório).

10. **machine learning frameworks**
   - Top1: `prereqs_and_prework-0002-601a60add4eb8699`, score 174.436.
   - Top3: crash_course; overfitting.
   - Top5 docs: foundations/prereqs_and_prework.html; educational_course/crash_course.html; evaluation/overfitting.html; Docker for Developers by Rafael Gomes... (x2).
   - Relevância: **Medium** (generaliza a visão dos frameworks; top1 suficiente para resposta conceitual).

## Qualidade dos rankings
- 9 dos 10 top1 são chunks do front `machine_learning`, com destaque para `linear_regression` e `deep_learning_60min_blitz_html` que dominam seus respectivos queries com scores acima de 200.
- A única exceção é a query "bias variance tradeoff", cujo top1 foi puxado de um documento fastapi devido à coincidência lexical; entretanto, um chunk da página oficial de regressão linear aparece já em segundo lugar, o que limita o impacto na recall geral.
- Vários resultados carregam o marcador `low_value_document` (prática do pipeline) e penalizam a pontuação ajustada, mas esse nível de ruído permanece limitado ao ranking secundário.

## Cobertura do corpus
- Todas as 10 queries trazem ao menos um chunk do front `machine_learning` dentro do top3 (métrica mantida em 100%).
- O ranking cobre os tópicos essenciais (fundamentos, algoritmos, frameworks) usando os novos documentos refinados; ainda resta atenção à estrutura do conteúdo para evitar penalidades de higiene que forçam entradas secundárias.

## Métricas
- `queries_tested`: 10
- `queries_with_correct_top1`: 9
- `queries_with_correct_top3`: 10
- `average_score` (top1): 197,49
- `semantic_recall_estimate`: 100% (ML chunk dentro do top3 para todas as queries)

## Decisão final
O semantic baseline foi completado com os resultados acima. O índice retornou respostas coerentes para 9 queries no top1 e garantiu cobertura total no top3. A busca está pronta para avançar ao próximo estágio do ciclo (closure_decision) assim que esse checkpoint for autorizado.
