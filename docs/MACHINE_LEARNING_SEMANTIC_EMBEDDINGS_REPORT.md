# MACHINE LEARNING Semantic Embeddings Report

- **Modelo usado**: text-embedding-3-large
- **Dimensão dos vetores**: 3072
- **Embeddings gerados**: 8 (um por chunk preparado no estágio anterior)
- **Fontes processadas**:
  1. `data/knowledge_raw/machine_learning/educational_course/crash_course.html`
  2. `data/knowledge_raw/machine_learning/framework_guide/guide.html`
  3. `data/knowledge_raw/machine_learning/framework_reference/index_html.html`
  4. `data/knowledge_raw/machine_learning/framework_user_guide/user_guide_html.html`
- **Confirmação de sucesso**: todos os vetores foram persistidos em `data/semantic_index_experiments/machine_learning/embeddings.jsonl` e o resumo está em `metadata.json`; a etapa semantic_embeddings foi concluída sem executar o semantic baseline nesta rodada.
