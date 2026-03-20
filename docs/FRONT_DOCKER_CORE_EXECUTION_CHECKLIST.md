# FRONT DOCKER CORE EXECUTION CHECKLIST

## front_status
- `closed`

## source_policy
- Usar apenas documentação oficial do Docker.
- Manter escopo estritamente core.
- Não incluir Docker Swarm, integração com Kubernetes, orchestration ou Compose avançado.

## source_manifest
- Registrar somente Docker official documentation, Docker CLI reference e Dockerfile reference.

## corpus_lock
- Congelar exatamente os documentos listados no `docs/DOCKER_CORPUS_LOCK.md`.

## parsing
- Preparar o corpus oficial para leitura estruturada.
- Preservar títulos, seções e exemplos essenciais.

## chunking
- Separar o domínio em chunks por tema funcional.
- Cobrir no mínimo container, image, Dockerfile, `docker build`, `docker run`, `docker ps`, `docker logs`, `docker exec`, volumes, networks, registry e image layers.

## lexical_baseline
- Validar cobertura lexical do corpus congelado.

## lexical_refinement
- Ajustar chunks apenas se a baseline lexical mostrar lacunas reais.

## semantic_embeddings
- Criar embeddings apenas após fechamento do corpus e do chunking.

## semantic_baseline
- Rodar baseline semântica do domínio core.

## closure_decision
- Fechar a frente apenas quando a cobertura lexical e semântica estiverem aceitáveis.
- Registrar o estado final no `STATUS.md`.
- Concluído em 2026-03-19 após `lexical_baseline` e `semantic_baseline` com cobertura adequada no subset atual.
