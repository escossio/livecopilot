# MACHINE_LEARNING Semantic Baseline Report V5

## Contexto
- Frente: `MACHINE_LEARNING`
- Fonte semântica: `data/knowledge_embeddings/machine_learning/embeddings.jsonl`
- Filtro aplicado: `source_prefix=machine_learning`
- Comparação-base: `docs/MACHINE_LEARNING_SEMANTIC_BASELINE_REPORT_V4.md`

## Validação de vazamento
- Nenhum chunk fora de `MACHINE_LEARNING` apareceu no top10 das 10 consultas.
- O ranking permaneceu restrito ao corpus da frente em todas as execuções.

## Resultados por query
1. **machine learning basics**
   - **Top1**: `crash_course-0001-a799aaf297d21c80` (0.522844) — `machine_learning/educational_course/crash_course.html`
   - **Top3**: `crash_course-0001-a799aaf297d21c80` (0.522844), `linear_regression-0002-09c953b16480951d` (0.473611), `prereqs_and_prework-0001-427a08f92b7136b5` (0.469595)
   - **Classificação**: COERENTE

2. **what is overfitting**
   - **Top1**: `overfitting-0001-54295e0c2531848e` (0.466751) — `machine_learning/evaluation/overfitting.html`
   - **Top3**: `overfitting-0001-54295e0c2531848e` (0.466751), `learning_curve_html-0002-fa28cdef3fd39dbf` (0.285303), `quickstart_tutorial_html-0006-cac13639e34dd6fb` (0.276356)
   - **Classificação**: COERENTE

3. **linear regression example**
   - **Top1**: `linear_regression-0001-a659c744df4988fd` (0.521728) — `machine_learning/algorithms/linear_regression.html`
   - **Top3**: `linear_regression-0001-a659c744df4988fd` (0.521728), `buildmodel_tutorial_html-0004-fc2ae568a850dce0` (0.345758), `getting_started_html-0001-f7fb18a1f3d7bb4f` (0.325191)
   - **Classificação**: COERENTE

4. **classification vs regression**
   - **Top1**: `roc_and_auc-0001-60a438c59b5cf0ef` (0.393211) — `machine_learning/evaluation/roc_and_auc.html`
   - **Top3**: `roc_and_auc-0001-60a438c59b5cf0ef` (0.393211), `classification-0001-64d1703603357f07` (0.379962), `linear_regression-0002-09c953b16480951d` (0.374076)
   - **Classificação**: COERENTE

5. **deep learning pytorch tutorial**
   - **Top1**: `deep_learning_60min_blitz_html-0001-ecf49b52f0e2a063` (0.663877) — `machine_learning/framework_guides/deep_learning_60min_blitz_html.html`
   - **Top3**: `deep_learning_60min_blitz_html-0001-ecf49b52f0e2a063` (0.663877), `intro_html-0001-590212e3c116a9f5` (0.624444), `quickstart_tutorial_html-0001-ca79398c7ea9ff8a` (0.593359)
   - **Classificação**: COERENTE

6. **tensorflow classification tutorial**
   - **Top1**: `beginner-0001-ada5aa224013e8a4` (0.611733) — `machine_learning/framework_guides/beginner.html`
   - **Top3**: `beginner-0001-ada5aa224013e8a4` (0.611733), `guide-0001-a4648a6bd5198214` (0.556779), `classification-0001-64d1703603357f07` (0.530978)
   - **Classificação**: COERENTE

7. **machine learning evaluation metrics**
   - **Top1**: `precision_and_recall-0001-33f5509d67528ef1` (0.482715) — `machine_learning/evaluation/precision_and_recall.html`
   - **Top3**: `precision_and_recall-0001-33f5509d67528ef1` (0.482715), `model_evaluation_html-0001-16ce974438864e75` (0.469445), `roc_and_auc-0001-60a438c59b5cf0ef` (0.454013)
   - **Classificação**: COERENTE

8. **bias variance tradeoff**
   - **Top1**: `linear_regression-0002-09c953b16480951d` (0.310836) — `machine_learning/algorithms/linear_regression.html`
   - **Top3**: `linear_regression-0002-09c953b16480951d` (0.310836), `learning_curve_html-0002-fa28cdef3fd39dbf` (0.309869), `overfitting-0001-54295e0c2531848e` (0.309145)
   - **Classificação**: PARCIAL

9. **supervised vs unsupervised learning**
   - **Top1**: `user_guide_html-0002-050d59c7447390fd` (0.359339) — `machine_learning/framework_user_guide/user_guide_html.html`
   - **Top3**: `user_guide_html-0002-050d59c7447390fd` (0.359339), `crash_course-0001-a799aaf297d21c80` (0.328861), `roc_and_auc-0001-60a438c59b5cf0ef` (0.307466)
   - **Classificação**: COERENTE

10. **machine learning frameworks**
   - **Top1**: `crash_course-0001-a799aaf297d21c80` (0.506843) — `machine_learning/educational_course/crash_course.html`
   - **Top3**: `crash_course-0001-a799aaf297d21c80` (0.506843), `overfitting-0001-54295e0c2531848e` (0.418133), `roc_and_auc-0001-60a438c59b5cf0ef` (0.402379)
   - **Classificação**: PARCIAL

## Comparação com V4
- Houve ganho claro em cobertura de métricas e tutoriais de framework.
- `what is overfitting` passou a ficar diretamente ancorada em `overfitting.html`.
- `machine learning evaluation metrics` consolidou `precision_and_recall`, `model_evaluation` e `roc_and_auc` no topo.
- `bias variance tradeoff` e `machine learning frameworks` continuam `PARCIAL`, mas sem vazamento externo.

## Conclusão
- **Decisão**: ainda precisa refinement antes de `closure_decision`.
- Motivo: o ranking está limpo e restrito, mas as duas queries restantes ainda dependem de chunks mais gerais.

