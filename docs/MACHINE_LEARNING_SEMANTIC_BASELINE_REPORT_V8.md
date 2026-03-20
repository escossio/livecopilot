# MACHINE_LEARNING Semantic Baseline Report V8

## Contexto
- Frente: `MACHINE_LEARNING`
- Fonte semântica: `data/knowledge_embeddings/machine_learning/embeddings.jsonl`
- Filtro aplicado: `source_prefix=machine_learning`
- Base de comparação: `docs/MACHINE_LEARNING_SEMANTIC_BASELINE_REPORT_V7.md`

## Validação de vazamento
- Nenhum chunk fora de `MACHINE_LEARNING` apareceu no top10 das 10 consultas.
- O ranking permaneceu restrito ao corpus da frente em todas as execuções.

## Resultados por query
1. **machine learning basics**
   - **Top3**: `tutorial_html-0001-ba96b1a635b30e84` (0.525735), `crash_course-0001-a799aaf297d21c80` (0.522882), `linear_regression-0002-09c953b16480951d` (0.473647)
   - **Avaliação final**: COERENTE

2. **what is overfitting**
   - **Top3**: `overfitting-0001-54295e0c2531848e` (0.465861), `learning_curve_html-0002-fa28cdef3fd39dbf` (0.285745), `quickstart_tutorial_html-0006-cac13639e34dd6fb` (0.275806)
   - **Avaliação final**: COERENTE

3. **linear regression example**
   - **Top3**: `linear_regression-0001-a659c744df4988fd` (0.52163), `index_html-0001-162fe8fcddd437de` (0.414908), `tutorial_html-0001-ba96b1a635b30e84` (0.374271)
   - **Avaliação final**: COERENTE

4. **classification vs regression**
   - **Top3**: `roc_and_auc-0001-60a438c59b5cf0ef` (0.393211), `tutorial_html-0002-c73f977cbe27bf87` (0.381838), `classification-0001-64d1703603357f07` (0.379989)
   - **Avaliação final**: COERENTE

5. **deep learning pytorch tutorial**
   - **Top3**: `deep_learning_60min_blitz_html-0001-ecf49b52f0e2a063` (0.66376), `intro_html-0001-590212e3c116a9f5` (0.624444), `quickstart_tutorial_html-0001-ca79398c7ea9ff8a` (0.593359)
   - **Avaliação final**: COERENTE

6. **tensorflow classification tutorial**
   - **Top3**: `beginner-0001-ada5aa224013e8a4` (0.611756), `guide-0001-a4648a6bd5198214` (0.556779), `classification-0001-64d1703603357f07` (0.53101)
   - **Avaliação final**: COERENTE

7. **machine learning evaluation metrics**
   - **Top3**: `precision_and_recall-0001-33f5509d67528ef1` (0.482755), `model_evaluation_html-0001-16ce974438864e75` (0.469505), `roc_and_auc-0001-60a438c59b5cf0ef` (0.454021)
   - **Avaliação final**: COERENTE

8. **bias variance tradeoff**
   - **Top3**: `learning_curve_html-0002-fa28cdef3fd39dbf` (0.314623), `linear_regression-0002-09c953b16480951d` (0.311375), `model_evaluation_html-0002-f9a7165b62d75d53` (0.309719)
   - **Avaliação final**: COERENTE

9. **supervised vs unsupervised learning**
   - **Top3**: `user_guide_html-0002-050d59c7447390fd` (0.35835), `tutorial_html-0002-c73f977cbe27bf87` (0.329409), `crash_course-0001-a799aaf297d21c80` (0.329028)
   - **Avaliação final**: COERENTE

10. **machine learning frameworks**
   - **Top3**: `crash_course-0001-a799aaf297d21c80` (0.506883), `tutorial_html-0001-ba96b1a635b30e84` (0.431311), `overfitting-0001-54295e0c2531848e` (0.417701)
   - **Avaliação final**: PARCIAL

## Comparação com V7
- A nova dupla de páginas `index_html.html` e `working_with_text_data_html.html` entrou no corpus e ajudou em queries vizinhas, mas não foi suficiente para fechar `machine learning frameworks`.
- O ranking permaneceu restrito ao `source_prefix=machine_learning`.

## Conclusão
- **Decisão**: ainda precisa refinement.
- Motivo: `machine learning frameworks` continua `PARCIAL`.

