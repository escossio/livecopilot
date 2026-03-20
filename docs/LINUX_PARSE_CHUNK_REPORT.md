# LINUX Parse & Chunk Report

## Resumo
- document_count: 4
- parsed_documents: 4
- chunk_count: 4
- chunk_size_avg: 65.2 palavras
- arquivos processados:
  - `data/knowledge_chunks/linux/kernel_subsystem-chunks.json`
  - `data/knowledge_chunks/linux/man_ps-chunks.json`
  - `data/knowledge_chunks/linux/networking-chunks.json`
  - `data/knowledge_chunks/linux/systemd_overview-chunks.json`
- erros: nenhum

## Fontes
- `data/knowledge_raw/linux/kernel_subsystem.md`
- `data/knowledge_raw/linux/man_ps.md`
- `data/knowledge_raw/linux/networking.md`
- `data/knowledge_raw/linux/systemd_overview.md`

## Observações
- Parsing simples preservou o texto integral, mantendo cabeçalhos e metadados sem alterações.
- Chunking segmentou cada documento em um JSON independente contendo um trecho técnico representativo.
