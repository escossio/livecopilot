# AZURE Semantic Baseline Report

## Metodologia
- Avaliação semântica usando `text-embedding-3-large` sobre o índice `data/semantic_index_experiments/azure/`.
- Consultas alinhadas aos tópicos críticos descritos no escopo da frente.

## Corpus avaliado
- Documentos: 6
- Chunks: 12
- Modelo: text-embedding-3-large (dimensão 3072)

## Consultas e classificações
- **azure virtual machine networking** → COERENTE (top1: azure_compute_documentation-0002-5a401a43f4a9f565 `score 0.923`)
  - Top3: azure_compute_documentation-0002-5a401a43f4a9f565 (`0.923`), azure_cli_documentation-0002-e903dbbf3f1d194e (`0.836`), azure_compute_documentation-0001-9d7b37b0f8cca958 (`0.830`)
- **azure storage account types** → COERENTE (top1: azure_cli_documentation-0002-e903dbbf3f1d194e `score 0.882`)
  - Top3: azure_cli_documentation-0002-e903dbbf3f1d194e (`0.882`), azure_storage_documentation-0002-3596c49a4c2f6cb4 (`0.869`), azure_compute_documentation-0002-5a401a43f4a9f565 (`0.856`)
- **azure identity managed identities** → COERENTE (top1: azure_identity_documentation-0002-9a8f8ab9b9d113eb `score 0.912`)
  - Top3: azure_identity_documentation-0002-9a8f8ab9b9d113eb (`0.912`), azure_identity_documentation-0001-9b8e5640c4a25ebc (`0.840`), azure_cli_documentation-0002-e903dbbf3f1d194e (`0.817`)
- **azure cli login command** → COERENTE (top1: azure_cli_documentation-0002-e903dbbf3f1d194e `score 0.908`)
  - Top3: azure_cli_documentation-0002-e903dbbf3f1d194e (`0.908`), azure_cli_documentation-0001-c7e6a755ae46d3a0 (`0.879`), azure_compute_documentation-0002-5a401a43f4a9f565 (`0.837`)

## Principais achados
- 4 consultas COERENTE, sem ruídos de outras frentes.

## Lacunas / ruídos observados
- Nenhum ruído ou falha identificado.

## Decisão
- baseline aprovado
- Motivo: os embeddings mantêm o foco nos tópicos solicitados.

## Resultados numéricos
- COERENTE: 4, PARCIALMENTE_COERENTE: 0, FALHA: 0.
