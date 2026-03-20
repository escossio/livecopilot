# Handoff LiveCopilot Terraform AWS Providers (2026-03-17T22:45:00Z)

## Contexto
- o manifesto autorizou iniciar o Lote 3 com providers; escolhemos o subset mínimo (provider overview + aws_instance) para evitar scope creep.
- as etapas anteriores (freeze/parsing/chunking) permaneceram isoladas do índice global.

## Ações realizadas
1. baixamos as páginas oficiais da Registry para o overview do provider AWS e para `aws_instance`, registrando os hashes em `docs/TERRAFORM_CORPUS_LOCK.*` e em `data/knowledge_raw/terraform/metadata/snapshot.md`.  
2. aplicamos a política de parsing existente e salvamos HTML limpo em `data/knowledge_parsed/terraform/providers/aws/`.  
3. geramos chunks por heading e guardamos as saídas JSON em `data/knowledge_chunks/terraform/providers/aws/`, atualizando `docs/TERRAFORM_CHUNKING_METADATA.json`.  
4. documentamos amostras em `docs/TERRAFORM_AWS_PROVIDERS_CHUNKING_SAMPLE_REPORT_20260317T224500Z.md` para auditoria.

## Estado final do subset AWS
- provider overview e `aws_instance` estão congelados, parseados e chunkados; os chunks cobrem module of provider, argumentos, examples e behavior.  
- o pipeline permanece isolado e pronto para a validação lexical do subset AWS (Etapa 8).  
- o lockfile e o manifesto mantêm rastreio das fontes usadas; nenhuma página não-oficial foi adicionada.

## Próximos passos sugeridos
1. rodar validação lexical do subset AWS (Etapa 8).  
2. planejar a bateria que combine modules + provider/aws antes de abrir outros providers.  
3. manter políticas e inventário atualizados conforme novos lotes forem congelados.
