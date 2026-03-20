# MACHINE LEARNING Parse & Chunk Report v2

## Resumo
- **Document_count**: 10 (todas as fontes oficiais listadas em `docs/MACHINE_LEARNING_SOURCE_MANIFEST.json`).
- **Parsed_documents**:
  1. `machine_learning/educational_course/crash_course.html`
  2. `machine_learning/framework_guide/guide.html`
  3. `machine_learning/framework_reference/index_html.html`
  4. `machine_learning/framework_user_guide/user_guide_html.html`
  5. `machine_learning/foundations/prereqs_and_prework.html`
  6. `machine_learning/algorithms/linear_regression.html`
  7. `machine_learning/evaluation/overfitting.html`
  8. `machine_learning/framework_guides/classification.html`
  9. `machine_learning/framework_guides/deep_learning_60min_blitz_html.html`
  10. `machine_learning/framework_guides/machine_learning_map.html`
- **Chunk_count_total**: 20 (cada fonte respeitou `chunk_size=1200`, `overlap=180`).
- **Média de chunk_size**: 1200 (parâmetro constante em todas as execuções documentadas).
- **Novos documentos detectados**: as seis páginas adicionadas na etapa de `corpus_refinement` (Foundations, Linear Regression, Overfitting, scikit-learn machine_learning_map, PyTorch blitz, TensorFlow classification).

## Comparação com o parse anterior
- O parse anterior cobria apenas 4 documentos e 8 chunks; a rodada v2 amplia o corpus para 10 documentos e 20 chunks, adicionando 12 chunks novos que mapeiam fundamentos, algoritmos, avaliação e guias de frameworks.
- Os chunks existentes foram revalidados com os mesmos parâmetros, garantindo consistência na granularidade enquanto novos conteúdos entram no índice semântico.

## Observações
- Nenhum embedding, semantic baseline ou closure decision foi executado nesta rodada; todos os artefatos permanecem isolados para a próxima etapa semântica.
- Os arquivos brutos estão em `data/knowledge_raw/machine_learning/` e os parsed/chunked estão em `data/knowledge_parsed/machine_learning/` e `data/knowledge_chunks/machine_learning/`.
