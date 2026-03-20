# C Semantic Environment Setup (isolated)

Este documento descreve o ambiente criado para a baseline semântica local do piloto da linguagem C — tudo fica isolado em `data/semantic_index_experiments/c_pilot/` para garantir que o índice global nunca seja tocado.

## Estatísticas iniciais do subset chunkado
- número de chunks: 23 (conforme `docs/C_CHUNKING_METADATA.json`).
- tamanho médio: ~582 palavras por chunk (lexicalmente limpo).
- modelo alvo de embeddings: `text-embedding-3-large` (OpenAI).

## Estrutura do índice experimental
```
data/semantic_index_experiments/c_pilot/
├── embeddings.jsonl   # cada linha contém {chunk_id, source_family, source_file, title, text, embedding}
├── metadata.json      # resumo com num_chunks, dimensão do embedding, modelo utilizado
```

## Geração dos embeddings
1. Defina `OPENAI_API_KEY` no ambiente (não está presente neste workspace). Sem essa variável os embeddings não podem ser construídos.
2. Execute o script de geração (p.ex. copiar o comando abaixo):
   ```bash
   python3 - <<'PY'
import json
from pathlib import Path
import openai, os
openai.api_key = os.getenv('OPENAI_API_KEY')
# ... (reusar o script criado neste commit para varrer docs/C_CHUNKING_METADATA.json e chamar openai.Embedding)
PY
   ```
3. O script deve preencher `embeddings.jsonl` e `metadata.json` conforme o modelo acima.

## Utilitário de busca semântica local
- Arquivo: `scripts/c_semantic_search_test.py`
- Uso exemplo:
  ```bash
  python scripts/c_semantic_search_test.py "O que pthread_create faz?"
  ```
- O script lê `embeddings.jsonl`, gera o embedding da pergunta com `text-embedding-3-large`, calcula similaridade cosseno e exibe os top 5 chunks.

## Dados pendentes
- Ainda não há embeddings porque `OPENAI_API_KEY` faltante bloqueou a criação automatizada.
- Assim que a chave estiver disponível, execute novamente o script para completar o índice isolado.
