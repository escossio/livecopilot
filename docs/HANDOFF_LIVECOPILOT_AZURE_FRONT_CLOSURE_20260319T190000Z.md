# HANDOFF – Livecopilot AZURE Front Closure

## Estado final
- Frente: AZURE
- Status: `closed`
- Lifecycle_stage: `closure_decision`
- Corpus lock mantido; nenhuma fonte fora do manifest foi adicionada após a materialização.

## Artefatos principais
- Índice/embeddings: `data/semantic_index_experiments/azure/` (6 docs, 12 chunks, `text-embedding-3-large`, dim 3072).
- Lexical baseline: `docs/AZURE_LEXICAL_BASELINE_REPORT.md`
- Semantic baseline: `docs/AZURE_SEMANTIC_BASELINE_REPORT.md`
- Final report: `docs/AZURE_FINAL_REPORT_20260319T190000Z.md`

## Números consolidados
- Documentos: 6
- Chunks: 12
- Semantic baseline final: 4 COERENTE / 0 PARCIALMENTE_COERENTE / 0 FALHA

## Decisões
- `closure_decision`: `closed`
- Pronto para uso como domínio isolado no routing global do Livecopilot.

## Riscos / limitações não bloqueantes
- Atualizações frequentes da Azure CLI merecem reavaliação do corpus lock.
- A cobertura foca em núcleos oficiais; tópicos experimentais (ex.: extensões preview) podem requerer novo front.

## Recomendações de uso futuro
- Consumir o índice `azure` para respostas técnicas core (compute/network/storage/CLI).
- Reabrir ou criar nova frente se forem liberadas áreas fora do scope atual (ex.: Azure databricks ou AI Studio, que não haviam sido adicionados ao manifest).

## Próximos mantenedores
- Seguir as diretrizes em `docs/FRONT_LIFECYCLE_CONTRACT.md` para qualquer evolução do front.
