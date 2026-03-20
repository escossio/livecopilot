# AWS Corpus Preparation

## Objetivo da preparação de corpus
- Organizar os guias oficiais da AWS para EC2, S3, IAM, VPC e CLI, estruturando o corpus raw antes de qualquer engenharia de chunks ou embeddings.

## Estratégia de ingestão
- Priorizar `docs.aws.amazon.com` e subdomínios `aws.amazon.com` que publiquem documentação técnica oficial para os serviços listados.
- Capturar HTML/markdown bruto mantendo headings, tabelas e exemplos de configuração, com metadados `source_url`, `captured_at`, `hash` e `notes`.
- Validar cada URL contra o manifesto oficial e registrar o artefato em `data/knowledge_raw/aws/`.

## Tipos de conteúdo permitidos
- Documentação de referência (API, CLI, conceitual) dedicada a EC2, S3, IAM, VPC, operações e segurança.
- Guias da AWS CLI (`aws docs`), whitepapers técnicos publicados nos domínios oficiais e instruções de automação reconhecidas pela AWS.

## Tipos de conteúdo proibidos
- Tutoriais de terceiros, cursos pagos ou conteúdos promocionais sem prova de revisão da AWS.
- Blogs de integradores, anúncios comerciais e conteúdos específicos de parceiros sem base na documentação técnica oficial.

## Estrutura esperada do corpus raw
- Diretório raiz: `data/knowledge_raw/aws/`
- Subdivisões sugeridas: `ec2/`, `s3/`, `iam/`, `vpc/`, `cli/`.
- Cada arquivo será normalizado para markdown técnico com metadados de origem (`source_url`, `captured_at`, `hash`, `metadata`).

## Confirmação de status
- Nenhuma ingestão, parsing, chunking ou embedding foi executada; esta etapa registra apenas o plano de preparação e a validação das fontes iniciais.
