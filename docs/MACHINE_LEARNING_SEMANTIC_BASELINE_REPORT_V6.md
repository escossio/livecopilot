# MACHINE_LEARNING Semantic Baseline Report V6

## Contexto
- Frente: `MACHINE_LEARNING`
- Fonte semântica: `data/knowledge_embeddings/machine_learning/embeddings.jsonl`
- Filtro aplicado: `source_prefix=machine_learning`
- Base de comparação: `docs/MACHINE_LEARNING_SEMANTIC_BASELINE_REPORT_V5.md`

## Validação de vazamento
- Nenhum chunk fora de `MACHINE_LEARNING` apareceu no top10 das 10 consultas.
- O ranking permaneceu restrito ao corpus da frente em todas as execuções.

## Resultados por query
1. **machine learning basics**
   - **Top3**: `crash_course-0001-a799aaf297d21c80` (0.522874), `linear_regression-0002-09c953b16480951d` (0.474267), `prereqs_and_prework-0001-427a08f92b7136b5` (0.46967)
   - **Avaliação final**: COERENTE

2. **what is overfitting**
   - **Top3**: `overfitting-0001-54295e0c2531848e` (0.466804), `learning_curve_html-0002-fa28cdef3fd39dbf` (0.285866), `quickstart_tutorial_html-0006-cac13639e34dd6fb` (0.275897)
   - **Avaliação final**: COERENTE

3. **linear regression example**
   - **Top3**: `linear_regression-0001-a659c744df4988fd` (0.52163), `buildmodel_tutorial_html-0004-fc2ae568a850dce0` (0.346613), `getting_started_html-0001-f7fb18a1f3d7bb4f` (0.324729)
   - **Avaliação final**: COERENTE

4. **classification vs regression**
   - **Top3**: `roc_and_auc-0001-60a438c59b5cf0ef` (0.393211), `classification-0001-64d1703603357f07` (0.379989), `linear_regression-0002-09c953b16480951d` (0.374333)
   - **Avaliação final**: COERENTE

5. **deep learning pytorch tutorial**
   - **Top3**: `deep_learning_60min_blitz_html-0001-ecf49b52f0e2a063` (0.66389), `intro_html-0001-590212e3c116a9f5` (0.624444), `quickstart_tutorial_html-0001-ca79398c7ea9ff8a` (0.593378)
   - **Avaliação final**: COERENTE

6. **tensorflow classification tutorial**
   - **Top3**: `beginner-0001-ada5aa224013e8a4` (0.611822), `guide-0001-a4648a6bd5198214` (0.556859), `classification-0001-64d1703603357f07` (0.530965)
   - **Avaliação final**: COERENTE

7. **machine learning evaluation metrics**
   - **Top3**: `precision_and_recall-0001-33f5509d67528ef1` (0.482755), `model_evaluation_html-0001-16ce974438864e75` (0.469486), `roc_and_auc-0001-60a438c59b5cf0ef` (0.454021)
   - **Avaliação final**: COERENTE

8. **bias variance tradeoff**
   - **Top3**: `learning_curve_html-0002-fa28cdef3fd39dbf` (0.315461), `linear_regression-0002-09c953b16480951d` (0.31145), `model_evaluation_html-0002-f9a7165b62d75d53` (0.309684)
   - **Avaliação final**: COERENTE
   - **Mudança vs V5**: passou de `PARCIAL` para `COERENTE`

9. **supervised vs unsupervised learning**
   - **Top3**: `user_guide_html-0002-050d59c7447390fd` (0.358677), `crash_course-0001-a799aaf297d21c80` (0.329017), `roc_and_auc-0001-60a438c59b5cf0ef` (0.307695)
   - **Avaliação final**: COERENTE

10. **machine learning frameworks**
   - **Top3**: `crash_course-0001-a799aaf297d21c80` (0.506863), `overfitting-0001-54295e0c2531848e` (0.418151), `roc_and_auc-0001-60a438c59b5cf0ef` (0.402379)
   - **Avaliação final**: PARCIAL
   - **Mudança vs V5**: continua `PARCIAL`

## Comparação com V5
- `bias variance tradeoff` melhorou e agora está `COERENTE`.
- O ranking segue restrito ao `source_prefix=machine_learning`.
- `machine learning frameworks` ainda depende de chunks introdutórios mais gerais e não fechou a lacuna.

## Conclusão
- **Decisão**: ainda precisa refinement.
- Motivo: uma das duas lacunas alvo ainda permanece `PARCIAL`.

