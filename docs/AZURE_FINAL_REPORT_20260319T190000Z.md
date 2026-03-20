# Azure Front Final Report

## Objetivo da frente
- Formalizar a cobertura do domínio Azure core (compute, networking, storage, identidade e CLI) com foco em fontes oficiais e demonstrar completude de ciclo até o baseline semântico.

## Corpus final e índice
- Documentos: 6 (fonte: manifest e materialização documentada).
- Chunks: 12 (`data/knowledge_chunks/azure__primary__*.chunks.json`).
- Índice/embeddings: `data/semantic_index_experiments/azure/` (modelo `text-embedding-3-large`, dimensão 3072, 12 embeddings, metadata em `metadata.json`).
- Indexação: kernels e comandos oficiais do Azure CLI, networking, storage e identity.

## Chunking e baselines
- Chunking e parsing guiados pelos relatórios `docs/AZURE_PARSE_CHUNK_REPORT.md` e `docs/AZURE_LEXICAL_BASELINE_REPORT.md`.
- Lexical baseline: todos os tópicos (networking, storage, identity, CLI) aprovaram o filtro, sem ruídos.
- Semantic baseline: `docs/AZURE_SEMANTIC_BASELINE_REPORT.md` (4 consultas, 4 COERENTE, `text-embedding-3-large`) confirma o foco dos 12 embeddings.

## Decisão final
- `closure_decision: closed`
- Justificativa: corpus mudou apenas dentro do lock autorizado, o roteamento lookup foi satisfeito, e os baselines lexical e semântico foram aprovados sem ruídos.

## Observações
- Manter vigilância sobre atualizações da documentação Azure CLI e networking; novas versões devem passar por reabertura formal ou revisão do corpus lock.
- Não houve ingestões ou mudanças pós-baseline nesta rodada.
