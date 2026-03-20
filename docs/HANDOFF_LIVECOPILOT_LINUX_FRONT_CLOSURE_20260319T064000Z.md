# HandOff – Linux Front Closure

## Estado final
- Status: `closed`
- Lifecycle_stage: `closure_decision`
- Corpus lock restrito a kernel.org, freedesktop.org e man7.org; nenhuma fonte externa adicionada.

## Artefatos principais
- Corpus raw/parsed: `data/knowledge_raw/linux/`, `data/knowledge_parsed/linux/`
- Chunks: `data/knowledge_chunks/linux/*.json`
- Embeddings: `data/semantic_index_experiments/linux/`
- Semantic baseline: `docs/LINUX_SEMANTIC_BASELINE_REPORT.md`, `docs/LINUX_SEMANTIC_BASELINE_RESULTS.json`
- Relatório final: `docs/LINUX_FINAL_REPORT_20260319T064000Z.md`

## Decisões
- closure_decision: `closed`
- Justificativa: cobertura semântica completa das consultas SES principais; ranking semântico não apresentou ruído.

## Observações
- Reavaliar apenas se houver mudanças significativas no kernel ou nas ferramentas systemd/networking; caso contrário, manter o índice fechado.
