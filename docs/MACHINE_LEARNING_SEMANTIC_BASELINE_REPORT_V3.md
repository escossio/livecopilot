# MACHINE_LEARNING Semantic Baseline Report V3

## Contexto
- Frente: `MACHINE_LEARNING`
- Fonte semântica: `data/knowledge_embeddings/machine_learning/embeddings.jsonl`
- Filtro aplicado: `source_prefix=machine_learning`
- Objetivo: validar o ranking após a correção do `knowledge_search` e decidir se a frente pode ser fechada.

## Validação de vazamento
- Nenhum chunk fora de `MACHINE_LEARNING` apareceu no top10 das 10 consultas.
- O ranking ficou restrito ao corpus da frente em todas as execuções.

## Resultados por query
1. **machine learning basics**
   - **Top1**: `prereqs_and_prework-0002-601a60add4eb8699` (51.519) — `machine_learning/foundations/prereqs_and_prework.html`
   - **Top3**: `prereqs_and_prework-0002-601a60add4eb8699` (51.519), `crash_course-0002-f779db68bb57add5` (36.534), `overfitting-0002-3d64e1dcc35a7c1d` (25.173)
   - **Classificação**: COERENTE

2. **what is overfitting**
   - **Top1**: `overfitting-0002-3d64e1dcc35a7c1d` (11.85) — `machine_learning/evaluation/overfitting.html`
   - **Top3**: `overfitting-0002-3d64e1dcc35a7c1d` (11.85), `deep_learning_60min_blitz_html-0002-838e77ea7bbc71aa` (7.362), `classification-0003-e88009040a2bc0b0` (6.955)
   - **Classificação**: PARCIAL
   - **Observação**: resposta ainda apoiada em chunk de navegação/TOC ou em fragmento pouco descritivo.

3. **linear regression example**
   - **Top1**: `linear_regression-0002-09c953b16480951d` (58.214) — `machine_learning/algorithms/linear_regression.html`
   - **Top3**: `linear_regression-0002-09c953b16480951d` (58.214), `user_guide_html-0002-050d59c7447390fd` (42.221), `crash_course-0002-f779db68bb57add5` (15.952)
   - **Classificação**: COERENTE

4. **classification vs regression**
   - **Top1**: `user_guide_html-0002-050d59c7447390fd` (44.645) — `machine_learning/framework_user_guide/user_guide_html.html`
   - **Top3**: `user_guide_html-0002-050d59c7447390fd` (44.645), `linear_regression-0002-09c953b16480951d` (26.931), `crash_course-0002-f779db68bb57add5` (15.952)
   - **Classificação**: COERENTE

5. **deep learning pytorch tutorial**
   - **Top1**: `deep_learning_60min_blitz_html-0002-838e77ea7bbc71aa` (175.123) — `machine_learning/framework_guides/deep_learning_60min_blitz_html.html`
   - **Top3**: `deep_learning_60min_blitz_html-0002-838e77ea7bbc71aa` (175.123), `index_html-0002-f63cf17d9aec3d09` (65.338), `prereqs_and_prework-0002-601a60add4eb8699` (30.025)
   - **Classificação**: COERENTE

6. **tensorflow classification tutorial**
   - **Top1**: `guide-0002-5f9db6d4df3420bc` (52.679) — `machine_learning/framework_guide/guide.html`
   - **Top3**: `guide-0002-5f9db6d4df3420bc` (52.679), `classification-0003-e88009040a2bc0b0` (49.04), `deep_learning_60min_blitz_html-0002-838e77ea7bbc71aa` (38.386)
   - **Classificação**: COERENTE

7. **machine learning evaluation metrics**
   - **Top1**: `prereqs_and_prework-0002-601a60add4eb8699` (51.311) — `machine_learning/foundations/prereqs_and_prework.html`
   - **Top3**: `prereqs_and_prework-0002-601a60add4eb8699` (51.311), `crash_course-0002-f779db68bb57add5` (37.746), `overfitting-0002-3d64e1dcc35a7c1d` (28.721)
   - **Classificação**: PARCIAL
   - **Observação**: resposta ainda apoiada em chunk de navegação/TOC ou em fragmento pouco descritivo.

8. **bias variance tradeoff**
   - **Top1**: `linear_regression-0002-09c953b16480951d` (20.946) — `machine_learning/algorithms/linear_regression.html`
   - **Top3**: `linear_regression-0002-09c953b16480951d` (20.946), `user_guide_html-0002-050d59c7447390fd` (4.077), `overfitting-0002-3d64e1dcc35a7c1d` (3.769)
   - **Classificação**: PARCIAL
   - **Observação**: resposta ainda apoiada em chunk de navegação/TOC ou em fragmento pouco descritivo.

9. **supervised vs unsupervised learning**
   - **Top1**: `user_guide_html-0002-050d59c7447390fd` (27.067) — `machine_learning/framework_user_guide/user_guide_html.html`
   - **Top3**: `user_guide_html-0002-050d59c7447390fd` (27.067), `prereqs_and_prework-0002-601a60add4eb8699` (24.505), `crash_course-0002-f779db68bb57add5` (16.628)
   - **Classificação**: COERENTE

10. **machine learning frameworks**
   - **Top1**: `prereqs_and_prework-0002-601a60add4eb8699` (49.891) — `machine_learning/foundations/prereqs_and_prework.html`
   - **Top3**: `prereqs_and_prework-0002-601a60add4eb8699` (49.891), `crash_course-0002-f779db68bb57add5` (34.906), `overfitting-0002-3d64e1dcc35a7c1d` (25.173)
   - **Classificação**: PARCIAL
   - **Observação**: resposta ainda apoiada em chunk de navegação/TOC ou em fragmento pouco descritivo.

## Before / After
- **Before**: o baseline anterior ainda apresentava ruído fora da frente e um top1 externo em pelo menos uma consulta.
- **After**: o vazamento foi eliminado; o ranking agora permanece dentro de `machine_learning` e os top resultados são consistentes com o corpus refinado.

## Conclusão
- **Decisão**: ainda aberto, sem `closure_decision`.
- Motivo: apesar do ranking restrito e limpo, algumas queries seguem com suporte apenas parcial de chunks introdutórios, TOCs ou snippets curtos.
- Próximo passo correto: refinar o corpus/chunking se a meta for aumentar a cobertura textual antes do fechamento.
