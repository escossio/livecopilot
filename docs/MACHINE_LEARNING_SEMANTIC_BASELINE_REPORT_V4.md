# MACHINE_LEARNING Semantic Baseline Report V4

## Contexto
- Frente: `MACHINE_LEARNING`
- Fonte semântica: `data/knowledge_embeddings/machine_learning/embeddings.jsonl`
- Filtro aplicado: `source_prefix=machine_learning`
- Objetivo: validar o ranking após o refresh do corpus refinado e comparar com o baseline V3.

## Validação de vazamento
- Nenhum chunk fora de `MACHINE_LEARNING` apareceu no top10 das 10 consultas.
- O ranking permaneceu restrito ao corpus da frente em todas as execuções.

## Resultados por query
1. **machine learning basics**
   - **Top1**: `prereqs_and_prework-0002-601a60add4eb8699` (54.558) — `machine_learning/foundations/prereqs_and_prework.html`
   - **Top3**: `prereqs_and_prework-0002-601a60add4eb8699` (54.558), `crash_course-0002-f779db68bb57add5` (38.727), `intro_html-0002-8eabea9b0a938b89` (27.125)
   - **Classificação**: COERENTE

2. **what is overfitting**
   - **Top1**: `overfitting-0002-3d64e1dcc35a7c1d` (12.741) — `machine_learning/evaluation/overfitting.html`
   - **Top3**: `overfitting-0002-3d64e1dcc35a7c1d` (12.741), `classification-0003-e88009040a2bc0b0` (7.479), `deep_learning_60min_blitz_html-0002-838e77ea7bbc71aa` (7.221)
   - **Classificação**: PARCIAL
   - **Observação**: melhorou a recuperação de overfitting, mas ainda depende de chunk curto de apoio.

3. **linear regression example**
   - **Top1**: `model_evaluation_html-0002-f9a7165b62d75d53` (124.235) — `machine_learning/evaluation/model_evaluation_html.html`
   - **Top3**: `model_evaluation_html-0002-f9a7165b62d75d53` (124.235), `linear_regression-0002-09c953b16480951d` (60.475), `user_guide_html-0002-050d59c7447390fd` (43.874)
   - **Classificação**: COERENTE

4. **classification vs regression**
   - **Top1**: `model_evaluation_html-0002-f9a7165b62d75d53` (120.372) — `machine_learning/evaluation/model_evaluation_html.html`
   - **Top3**: `model_evaluation_html-0002-f9a7165b62d75d53` (120.372), `user_guide_html-0002-050d59c7447390fd` (45.453), `linear_regression-0002-09c953b16480951d` (27.654)
   - **Classificação**: COERENTE

5. **deep learning pytorch tutorial**
   - **Top1**: `deep_learning_60min_blitz_html-0002-838e77ea7bbc71aa` (190.676) — `machine_learning/framework_guides/deep_learning_60min_blitz_html.html`
   - **Top3**: `deep_learning_60min_blitz_html-0002-838e77ea7bbc71aa` (190.676), `intro_html-0002-8eabea9b0a938b89` (177.282), `index_html-0002-f63cf17d9aec3d09` (70.18)
   - **Classificação**: COERENTE

6. **tensorflow classification tutorial**
   - **Top1**: `model_evaluation_html-0002-f9a7165b62d75d53` (78.286) — `machine_learning/evaluation/model_evaluation_html.html`
   - **Top3**: `model_evaluation_html-0002-f9a7165b62d75d53` (78.286), `guide-0002-5f9db6d4df3420bc` (57.97), `classification-0003-e88009040a2bc0b0` (53.337)
   - **Classificação**: COERENTE

7. **machine learning evaluation metrics**
   - **Top1**: `model_evaluation_html-0002-f9a7165b62d75d53` (254.511) — `machine_learning/evaluation/model_evaluation_html.html`
   - **Top3**: `model_evaluation_html-0002-f9a7165b62d75d53` (254.511), `prereqs_and_prework-0002-601a60add4eb8699` (54.013), `crash_course-0002-f779db68bb57add5` (39.427)
   - **Classificação**: COERENTE

8. **bias variance tradeoff**
   - **Top1**: `model_evaluation_html-0002-f9a7165b62d75d53` (66.486) — `machine_learning/evaluation/model_evaluation_html.html`
   - **Top3**: `model_evaluation_html-0002-f9a7165b62d75d53` (66.486), `learning_curve_html-0002-fa28cdef3fd39dbf` (36.187), `linear_regression-0002-09c953b16480951d` (20.559)
   - **Classificação**: PARCIAL
   - **Observação**: learning_curve entrou no ranking, mas o top1 ainda preferiu o bloco de model_evaluation.

9. **supervised vs unsupervised learning**
   - **Top1**: `user_guide_html-0002-050d59c7447390fd` (29.162) — `machine_learning/framework_user_guide/user_guide_html.html`
   - **Top3**: `user_guide_html-0002-050d59c7447390fd` (29.162), `prereqs_and_prework-0002-601a60add4eb8699` (25.48), `crash_course-0002-f779db68bb57add5` (17.29)
   - **Classificação**: COERENTE

10. **machine learning frameworks**
   - **Top1**: `prereqs_and_prework-0002-601a60add4eb8699` (52.769) — `machine_learning/foundations/prereqs_and_prework.html`
   - **Top3**: `prereqs_and_prework-0002-601a60add4eb8699` (52.769), `crash_course-0002-f779db68bb57add5` (36.938), `overfitting-0002-3d64e1dcc35a7c1d` (26.65)
   - **Classificação**: PARCIAL
   - **Observação**: a recuperação continua ancorada em conteúdo introdutório de frameworks.

## Comparação com V3
- O corpus ampliado trouxe ganhos claros em `evaluation`: `model_evaluation`, `precision_and_recall`, `roc_and_auc`, `confusion_matrix` e `learning_curve` passaram a dominar queries de métricas e tradeoff.
- `machine learning basics`, `classification vs regression`, `deep learning pytorch tutorial` e `supervised vs unsupervised learning` continuaram coerentes.
- `what is overfitting`, `bias variance tradeoff` e `machine learning frameworks` ainda aparecem como `PARCIAL`, mas com melhor cobertura do que no V3.

## Conclusão
- **Decisão**: ainda precisa refinement antes de `closure_decision`.
- Motivo: o ranking está limpo e restrito, mas algumas queries seguem mais ancoradas em blocos introdutórios do que em explicações completas.
