# HANDOFF – Livecopilot AWS Front Closure

## Estado final
- Frente: AWS
- Status: `closed`
- Lifecycle_stage: `closure_decision`
- Corpus lock mantido; as fontes são os manuais oficiais da AWS (EC2, S3, IAM, VPC e AWS CLI).

## Artefatos principais
- Índice/embeddings: `data/semantic_index_experiments/aws/` (6 docs, 8 chunks, `text-embedding-3-large`, dim 3072).
- Lexical baseline: `docs/AWS_LEXICAL_BASELINE_REPORT.md`
- Semantic baseline: `docs/AWS_SEMANTIC_BASELINE_REPORT.md`
- Final report: `docs/AWS_FINAL_REPORT_20260319T192000Z.md`

## Números consolidados
- Documentos: 6
- Chunks: 8
- Semantic baseline final: 4 COERENTE / 0 PARCIALMENTE_COERENTE / 0 FALHA

## Decisões
- `closure_decision`: `closed`
- Índice apto para responder consultas técnicas core (EC2, S3, IAM, VPC, CLI).

## Riscos / limitações não bloqueantes
- Expansões para serviços adicionais (Lambda, Sagemaker) precisarão de nova abertura ou reavaliação do corpus lock.

## Recomendações de uso futuro
- Priorizar o uso do índice `aws` para respostas confiáveis de infraestrutura core.
- Seguir o fluxo do `docs/FRONT_LIFECYCLE_CONTRACT.md` para qualquer mudança de escopo.

## Próximos mantenedores
- Documentar futuras alterações no `docs/FRONT_AWS.md` e revalidar baselines antes de qualquer reabertura.
