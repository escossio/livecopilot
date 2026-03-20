# FRONT AWS

## Objetivo
- Formalizar a frente AWS para mapear os principais serviços oficiais e preparar o corpus antes de parsing.

## Escopo
- Domínio: serviços core da AWS (EC2, S3, IAM, VPC), CLI oficial (`aws`), práticas recomendadas de identidade e redes, e APIs descritas na documentação oficial da AWS.
- Exclusões: conteúdos de provedores terceiros, tutoriais não oficiais e posts promocionais sem base na AWS docs oficial.

## Source policy
- Fontes permitidas: `docs.aws.amazon.com` e domínios oficiais `aws.amazon.com` que hospedam documentação técnica, guias e referências.
- Priorizar documentos de referência (API, CLI, serviços core) com informações de configuração, segurança e operação.
- Evitar blogs de parceiros, cursos pagos e conteúdos que apenas vendem serviços sem aprofundar a documentação oficial.

## Source manifest (inicial)
- AWS Documentation Home (`https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html`) – visão geral dos serviços core.
- Amazon EC2 Documentation (`https://docs.aws.amazon.com/ec2/`) – compute, instâncias, AMIs e operações.
- Amazon S3 Documentation (`https://docs.aws.amazon.com/s3/`) – storage, políticas e camadas.
- AWS IAM Documentation (`https://docs.aws.amazon.com/iam/`) – identidade, permissões e RBAC.
- Amazon VPC Documentation (`https://docs.aws.amazon.com/vpc/`) – redes, subnets, segurança e conectividade.
- AWS CLI Command Reference (`https://docs.aws.amazon.com/cli/latest/reference/`) – comandos da CLI oficial.

## Corpus lock (inicial)
- Scoped: os domínios `docs.aws.amazon.com` e `aws.amazon.com` com documentação técnica oficial dos serviços listados.
- Fora do lock: blogs de integradores, anúncios de marketing e conteúdo específico de parceiros que não represente referência oficial.

## Status
- state: `closed`
- stage: `closure_decision`
- fechamento: final report e handoff registrados (`docs/AWS_FINAL_REPORT_20260319T192000Z.md`, `docs/HANDOFF_LIVECOPILOT_AWS_FRONT_CLOSURE_20260319T192000Z.md`).
- próximo passo: manter o índice `aws` para as consultas core e reabrir apenas se o escopo oficial for ampliado.

## Lifecycle oficial
- Pipeline completo documentado em `docs/FRONT_LIFECYCLE_CONTRACT.md`; esta frente inicia em `corpus_preparation`.

## Observação
- Nenhuma ingestão ou parsing foi rodado; este documento define apenas o escopo e o plano inicial.
