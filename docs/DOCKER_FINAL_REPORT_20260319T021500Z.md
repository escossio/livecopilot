# Docker Core Final Report

## Objetivo da frente
- Executar a frente `docker_core` em escopo estritamente core, usando documentação oficial do Docker e cobrindo os tópicos centrais do domínio.

## Escopo definido
- Container
- Image
- Dockerfile
- `docker build`
- `docker run`
- `docker ps`
- `docker logs`
- `docker exec`
- Volumes
- Networks
- Registry
- Image layers

## Pipeline executado
1. `source_policy`
2. `source_manifest`
3. `corpus_lock`
4. `parsing`
5. `chunking`
6. `lexical_baseline`
7. `semantic_embeddings`
8. `semantic_baseline`
9. `closure_decision`

## Resumo dos artefatos produzidos
- Corpus chunkado em `data/knowledge_chunks/docker/`
- Metadata da frente em `docs/DOCKER_CHUNKING_METADATA.json`
- Relatório de chunking em `docs/DOCKER_CHUNKING_REPORT_20260318T211539Z.md`
- Relatório lexical em `docs/DOCKER_LEXICAL_BASELINE_REPORT_20260319T020109Z.md`
- Sandbox semântico isolado em `data/semantic_index_experiments/docker_pilot/`
- Relatório semântico em `docs/DOCKER_SEMANTIC_BASELINE_REPORT_20260319T020532Z.md`
- Resultado estruturado semântico em `docs/DOCKER_SEMANTIC_BASELINE_RESULTS_20260319T020532Z.json`
- Handoffs de abertura, lexical, semântico e fechamento

## Resultado lexical
- Cobertura da bateria mínima: `12/12 RESPONDIVEL`
- Sem lacunas bloqueantes

## Resultado semântico
- `COERENTE`: `11/12`
- `PARCIALMENTE_COERENTE`: `1/12`
- `FALHA`: `0/12`
- Única divergência:
  - `What is a Docker image?`
  - lexical top: `docker-image-layers-0002`
  - semantic top: `docker-image-0002`

## Decisão final de fechamento
- A frente pode ser marcada como `closed`.
- Justificativa:
  - o corpus ficou congelado no subset previsto;
  - a cobertura lexical atingiu o alvo mínimo;
  - a baseline semântica mostrou consistência alta, sem falhas;
  - a divergência residual em `Docker image` não bloqueia o fechamento do escopo core definido.

## Observações residuais
- Se a frente for reaberta para refinamento fino, o tema `Docker image` é o único ponto que merece ajuste pontual.
