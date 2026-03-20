# Handoff: Docker Core Front Opened

## Escopo da frente
A frente `docker_core` cobre o núcleo operacional do Docker para uso prático, sem Swarm, integração com Kubernetes, Compose avançado ou orchestration.

## Tópicos obrigatórios
- container
- image
- dockerfile
- `docker build`
- `docker run`
- `docker ps`
- `docker logs`
- `docker exec`
- Docker volumes
- Docker networks
- Docker registry
- image layers

## Estrutura de chunks
- `data/knowledge_chunks/docker/core/`
- `data/knowledge_chunks/docker/cli/`
- `data/knowledge_chunks/docker/storage/`
- `data/knowledge_chunks/docker/networking/`

## Contrato de execução
`source_policy` -> `source_manifest` -> `corpus_lock` -> `parsing` -> `chunking` -> `lexical_baseline` -> `lexical_refinement` -> `semantic_embeddings` -> `semantic_baseline` -> `closure_decision`

## Estado inicial
- Corpus ainda não ingerido.
- Chunks ainda não criados.
- Baselines ainda não executadas.
