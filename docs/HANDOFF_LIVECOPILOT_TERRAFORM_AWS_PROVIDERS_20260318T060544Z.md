# Handoff LiveCopilot Terraform AWS Providers (20260318T060544Z)

## Context
- consolidando o subset mínimo do Lote 3 (provider overview + aws_instance) a partir das fontes oficiais HashiCorp.
- as páginas da Registry exigem JS, então usamos o conteúdo gerado em `website/docs` como fonte canônica e rastreamos hashes atualizados.

## Actions
1. baixamos `website/docs/index.html.markdown` e `website/docs/list-resources/instance.html.markdown` do repositório oficial `hashicorp/terraform-provider-aws` e convertimos para HTML.
2. substituímos `data/knowledge_raw/terraform/providers/aws/aws-overview.html` e `.../aws-instance.html`, mantendo cópias idênticas em `data/knowledge_parsed/...`, e atualizamos os hashes no lockfile e no snapshot.
3. criamos chunks para o parágrafo inicial do provedor, o exemplo de uso do provider e as seções `List Resource: aws_instance`, `Example Usage` e `Argument Reference`, registrando-os em `data/knowledge_chunks/terraform/providers/aws/` e em `docs/TERRAFORM_CHUNKING_METADATA.json`.
4. atualizamos o relatório de amostra `docs/TERRAFORM_AWS_PROVIDERS_CHUNKING_SAMPLE_REPORT_20260317T224500Z.md` e geramos o relatório lexical `docs/TERRAFORM_AWS_LEXICAL_VALIDATION_REPORT_20260318T060531Z.md`.

## Estado final
- providers AWS congelados, parseados, chunkados e registrados nos inventários de hash e chunk.
- chunk sample atualizado e chunk metadata agora inclui cinco chunks novos com os IDs terraform-aws-001/002 e terraform-aws-instance-001/002/003.
- o relatório lexical cobre as perguntas previstas sobre o provedor e `aws_instance`.

## Próximos passos
- expandir o mesmo fluxo para outras seções críticas do provider AWS (ex: `data` e recursos confirmados).
- registrar validações adicionais e comparar com a documentação real da Registry para outros domínios do Lote 3.
