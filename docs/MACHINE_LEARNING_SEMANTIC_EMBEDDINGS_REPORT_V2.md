# MACHINE LEARNING Semantic Embeddings Report v2

## Estatísticas gerais
- **Documentos processados**: 10 (todos os arquivos do manifesto e do refinement).<br>
- **Chunks totais**: 20 (chunk_size=1200/overlap=180, consistente com o parse atual).<br>
- **Embeddings gerados**: 20 (um por chunk).<br>
- **Modelo utilizado**: text-embedding-3-large.<br>
- **Tempo total da execução**: 10,64 segundos (medido pelo script `app.services.knowledge_embeddings`).<br>
- **Tamanho médio dos vetores**: 3072 dimensões.<br>

## Semantic search validado
Executamos `python3 -m app.services.knowledge_search` com `--limit 3` sobre as queries requisitadas e todos os resultados principais caem dentro das fontes oficiais da frente.

1. **Query**: `machine learning basics`
   - Chunk principal: `prereqs_and_prework-0002-601a60add4eb8699` (Foundations, score 177.115).
   - 2º lugar: `crash_course-0002-f779db68bb57add5` (Crash Course, score 124.2).
   - 3º lugar: `overfitting-0002-3d64e1dcc35a7c1d` (Evaluation, score 88.46).

2. **Query**: `linear regression`
   - Chunk principal: `linear_regression-0002-09c953b16480951d` (Crash Course algorithms, score 198.614).
   - 2º lugar: `user_guide_html-0002-050d59c7447390fd` (scikit-learn User Guide, score 148.506).
   - 3º lugar: `crash_course-0002-f779db68bb57add5` (Crash Course general, score 61.327).

3. **Query**: `overfitting`
   - Chunk principal: `overfitting-0002-3d64e1dcc35a7c1d` (Evaluation, score 65.261).
   - 2º lugar: `classification-0003-e88009040a2bc0b0` (TensorFlow classification guide, score 37.524).
   - 3º lugar: `overfitting-0001-54295e0c2531848e` (Evaluation, score 29.094).

4. **Query**: `deep learning pytorch`
   - Chunk principal: `deep_learning_60min_blitz_html-0002-838e77ea7bbc71aa` (PyTorch 60min blitz, score 480.309).
   - 2º lugar: `index_html-0002-f63cf17d9aec3d09` (PyTorch docs index, score ~235).
   - 3º lugar: `prereqs_and_prework-0002-601a60add4eb8699` (Foundations, score ~101.864).

5. **Query**: `classification tensorflow`
   - Chunk principal: `guide-0002-5f9db6d4df3420bc` (TensorFlow guide, score 249.516).
   - 2º lugar: `classification-0003-e88009040a2bc0b0` (TensorFlow classification tutorial, score 226.383).
   - 3º lugar: `classification-0002-8c073cc8faaf754d` (TensorFlow classification tutorial, score 219.389).

## Observações
- Todos os top resultados são blocos oficiais (Crash Course, scikit-learn, PyTorch e TensorFlow) e confirmam que a recuperação semântica permanece no domínio correto, mesmo com `hygiene_flags` marcando documentos como `low_value_document` por conterem trechos introdutórios/TOCs.
- O script de embeddings truncou chunks longos a 4000 palavras para respeitar o limite de contexto de 8192 tokens, mantendo coerência e evitando erros do OpenAI.
- Os embeddings estão armazenados em `data/knowledge_embeddings/machine_learning/embeddings.jsonl`, e os metadados indicam 10 documentos, 20 chunks e 3072 dimensões.
