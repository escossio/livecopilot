# AZURE Parse & Chunk Report

- `document_count`: 6 (todas as páginas oficiais da pasta `azure/primary/`)
- `parsed_documents`: 6 (`data/knowledge_parsed/azure__primary__*.json` sem os arquivos de metadata)
- `chunk_count`: 12 (consolida duas chunks por documento como esperado com chunk_size=1200)
- `chunk_size_avg`: 1.334 caracteres
- `arquivos processados`:
  1. `azure/primary/azure_architecture_center.html`
  2. `azure/primary/azure_cli_documentation.html`
  3. `azure/primary/azure_compute_documentation.html`
  4. `azure/primary/azure_identity_documentation.html`
  5. `azure/primary/azure_networking_documentation.html`
  6. `azure/primary/azure_storage_documentation.html`
- `chunk_files gerados`:
  - `azure__primary__azure_architecture_center.html.chunks.json`
  - `azure__primary__azure_cli_documentation.html.chunks.json`
  - `azure__primary__azure_compute_documentation.html.chunks.json`
  - `azure__primary__azure_identity_documentation.html.chunks.json`
  - `azure__primary__azure_networking_documentation.html.chunks.json`
  - `azure__primary__azure_storage_documentation.html.chunks.json`
- `erros`: nenhum

<sup>Parsing aplicou a política padrão de limpeza HTML; o chunking ficou isolado dentro de cada fonte, sem embeddings nem baseline.</sup>
