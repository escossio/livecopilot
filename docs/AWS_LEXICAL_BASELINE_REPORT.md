# AWS Lexical Baseline Report

## Objetivo
- Garantir que as consultas sobre EC2, S3, IAM e VPC retornem chunks oficiais do domínio AWS.

## Resultados

### 1. Query: `aws ec2 instance types`
- **Top1:** `aws_cli_command_reference-0002-5c306a0c3a87f934` (`aws_cli_command_reference.html`, score 28)
- **Top3:** `aws_service_overview-0003-99fa837793c40338` (24), `aws_service_overview-0005-c9c30dcc8f7693e8` (24)
- **Domínio correto:** AWS

### 2. Query: `aws s3 bucket lifecycle`
- **Top1:** `aws_cli_command_reference-0002-5c306a0c3a87f934` (score 30)
- **Top3:** `aws_service_overview-0005-c9c30dcc8f7693e8` (25), `aws_service_overview-0004-b026f082060a2bfe` (22)
- **Domínio correto:** AWS

### 3. Query: `aws iam role policy`
- **Top1:** `aws_cli_command_reference-0002-5c306a0c3a87f934` (score 26)
- **Top3:** `aws_service_overview-0003-99fa837793c40338` (24), `aws_service_overview-0004-b026f082060a2bfe` (24)
- **Domínio correto:** AWS

### 4. Query: `aws vpc subnet routing`
- **Top1:** `aws_service_overview-0005-c9c30dcc8f7693e8` (score 26)
- **Top3:** `aws_cli_command_reference-0002-5c306a0c3a87f934` (25), `aws_service_overview-0004-b026f082060a2bfe` (22)
- **Domínio correto:** AWS

## Observações
- As quatro consultas priorizam chunks da frente AWS com scores positivos e nenhuma evidência de ruído fora do domínio.
