# REACTJS Semantic Baseline Report

## Metodologia
- Avaliação semântica usando `text-embedding-3-large` sobre o índice `data/semantic_index_experiments/reactjs/`.
- Consultas alinhadas aos tópicos críticos descritos no escopo da frente.

## Corpus avaliado
- Documentos: 3
- Chunks: 12
- Modelo: text-embedding-3-large (dimensão 3072)

## Consultas e classificações
- **react useEffect lifecycle** → COERENTE (top1: react_dev_homepage-0001-95a71b55a2689a81 `score 0.876`)
  - Top3: react_dev_homepage-0001-95a71b55a2689a81 (`0.876`), react_dev_api_reference-0002-1dd4b50a2fc0067d (`0.849`), react_dev_api_reference-0001-12b5eb085f6f92bc (`0.826`)
- **react useState example** → COERENTE (top1: react_dev_homepage-0003-ecc17b5807c0f73b `score 0.884`)
  - Top3: react_dev_homepage-0003-ecc17b5807c0f73b (`0.884`), react_dev_learn-0002-478c57b797b65940 (`0.853`), react_dev_homepage-0002-c692e2f9e0bdecf5 (`0.848`)
- **react component rendering** → COERENTE (top1: react_dev_learn-0002-478c57b797b65940 `score 0.889`)
  - Top3: react_dev_learn-0002-478c57b797b65940 (`0.889`), react_dev_api_reference-0002-1dd4b50a2fc0067d (`0.857`), react_dev_homepage-0006-f4ccac51313b00b5 (`0.813`)
- **react hooks rules** → COERENTE (top1: react_dev_api_reference-0002-1dd4b50a2fc0067d `score 0.907`)
  - Top3: react_dev_api_reference-0002-1dd4b50a2fc0067d (`0.907`), react_dev_learn-0002-478c57b797b65940 (`0.868`), react_dev_api_reference-0001-12b5eb085f6f92bc (`0.840`)

## Principais achados
- 4 consultas COERENTE, sem ruídos de outras frentes.

## Lacunas / ruídos observados
- Nenhum ruído ou falha identificado.

## Decisão
- baseline aprovado
- Motivo: os embeddings mantêm o foco nos tópicos solicitados.

## Resultados numéricos
- COERENTE: 4, PARCIALMENTE_COERENTE: 0, FALHA: 0.
