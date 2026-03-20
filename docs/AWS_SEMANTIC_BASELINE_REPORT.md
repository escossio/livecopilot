# AWS Semantic Baseline Report

## Metodologia
- Avaliação semântica usando `text-embedding-3-large` sobre o índice `data/semantic_index_experiments/aws/`.
- Consultas alinhadas aos tópicos críticos descritos no escopo da frente.

## Corpus avaliado
- Documentos: 6
- Chunks: 8
- Modelo: text-embedding-3-large (dimensão 3072)

## Consultas e classificações
- **aws ec2 instance types** → COERENTE (top1: aws_service_overview-0006-5a4e945a6a690e00 `score 0.862`)
  - Top3: aws_service_overview-0006-5a4e945a6a690e00 (`0.862`), aws_service_overview-0003-99fa837793c40338 (`0.834`), aws_service_overview-0005-c9c30dcc8f7693e8 (`0.832`)
- **aws s3 bucket lifecycle** → COERENTE (top1: aws_service_overview-0003-99fa837793c40338 `score 0.864`)
  - Top3: aws_service_overview-0003-99fa837793c40338 (`0.864`), aws_service_overview-0002-c6fcad21a31efa27 (`0.863`), aws_cli_command_reference-0002-5c306a0c3a87f934 (`0.835`)
- **aws iam role policy** → COERENTE (top1: aws_service_overview-0003-99fa837793c40338 `score 0.856`)
  - Top3: aws_service_overview-0003-99fa837793c40338 (`0.856`), aws_service_overview-0004-b026f082060a2bfe (`0.855`), aws_cli_command_reference-0002-5c306a0c3a87f934 (`0.840`)
- **aws vpc subnet routing** → COERENTE (top1: aws_cli_command_reference-0002-5c306a0c3a87f934 `score 0.864`)
  - Top3: aws_cli_command_reference-0002-5c306a0c3a87f934 (`0.864`), aws_service_overview-0005-c9c30dcc8f7693e8 (`0.851`), aws_service_overview-0006-5a4e945a6a690e00 (`0.839`)

## Principais achados
- 4 consultas COERENTE, sem ruídos de outras frentes.

## Lacunas / ruídos observados
- Nenhum ruído ou falha identificado.

## Decisão
- baseline aprovado
- Motivo: os embeddings mantêm o foco nos tópicos solicitados.

## Resultados numéricos
- COERENTE: 4, PARCIALMENTE_COERENTE: 0, FALHA: 0.
