# AWS providers chunking sample report — 2026-03-18T06:04:17Z

## AWS Provider chunk terraform-aws-001
- texto parseado origem: `data/knowledge_parsed/terraform/providers/aws/aws-overview.html`
- chunk: snippet `AWS Provider The Amazon Web Services (AWS) provider is Terraform’s most widely-used provider and the industry-standard way to manage AWS infrastructure as code. It is an indispensa`
- critério: boundary na seção 'AWS Provider' (heading) 
- avaliação: respondível e preserva contexto suficiente para o usuário final.

## Example Usage chunk terraform-aws-002
- texto parseado origem: `data/knowledge_parsed/terraform/providers/aws/aws-overview.html`
- chunk: snippet `Example Usage Terraform 0.13 and later: terraform { required_providers { aws = { source = "hashicorp/aws" version = "~> 6.0" } } } # Configure the AWS Provider provider "aws" { reg`
- critério: boundary na seção 'Example Usage' (heading) 
- avaliação: respondível e preserva contexto suficiente para o usuário final.

## List Resource: aws_instance chunk terraform-aws-instance-001
- texto parseado origem: `data/knowledge_parsed/terraform/providers/aws/aws-instance.html`
- chunk: snippet `List Resource: aws_instance ~> Note: The aws_instance List Resource is in beta. Its interface and behavior may change as the feature evolves, and breaking changes are possible. It`
- critério: boundary na seção 'List Resource: aws_instance' (heading) 
- avaliação: respondível e preserva contexto suficiente para o usuário final.

## Example Usage chunk terraform-aws-instance-002
- texto parseado origem: `data/knowledge_parsed/terraform/providers/aws/aws-instance.html`
- chunk: snippet `Example Usage Basic Usage list "aws_instance" "example" { provider = aws } Filter Usage This example will return instances in the stopped state. list "aws_instance" "example" { pro`
- critério: boundary na seção 'Example Usage' (heading) 
- avaliação: respondível e preserva contexto suficiente para o usuário final.

## Argument Reference chunk terraform-aws-instance-003
- texto parseado origem: `data/knowledge_parsed/terraform/providers/aws/aws-instance.html`
- chunk: snippet `Argument Reference This list resource supports the following arguments: filter - (Optional) One or more filters to apply to the search. If multiple filter blocks are provided, they`
- critério: boundary na seção 'Argument Reference' (heading) 
- avaliação: respondível e preserva contexto suficiente para o usuário final.
