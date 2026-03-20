# Docker core semantic baseline report

## Embeddings e índice isolado
- Directory: `data/semantic_index_experiments/docker_pilot/`
- Files: `embeddings.jsonl` and `metadata.json`
- Model: `text-embedding-3-large`
- Chunks: `12`
- Embedding dim: `3072`
- Average words per chunk: `42.25`
- Generated at: `2026-03-19T02:05:27.085301+00:00`

## Lexical vs semantic comparison
- What is a container?
  - lexical top: `docker-container-0001` (`container`)
  - semantic top: `docker-container-0001` (`container`) score `0.660425`
  - class: `COERENTE`

- What is a Docker image?
  - lexical top: `docker-image-layers-0002` (`image layers`)
  - semantic top: `docker-image-0002` (`image`) score `0.620343`
  - class: `PARCIALMENTE_COERENTE`

- What is a Dockerfile?
  - lexical top: `docker-dockerfile-0003` (`dockerfile`)
  - semantic top: `docker-dockerfile-0003` (`dockerfile`) score `0.725232`
  - class: `COERENTE`

- What does docker build do?
  - lexical top: `docker-cli-build-0002` (`docker build`)
  - semantic top: `docker-cli-build-0002` (`docker build`) score `0.688378`
  - class: `COERENTE`

- What does docker run do?
  - lexical top: `docker-cli-run-0001` (`docker run`)
  - semantic top: `docker-cli-run-0001` (`docker run`) score `0.612891`
  - class: `COERENTE`

- What does docker ps do?
  - lexical top: `docker-cli-ps-0003` (`docker ps`)
  - semantic top: `docker-cli-ps-0003` (`docker ps`) score `0.671005`
  - class: `COERENTE`

- What does docker logs do?
  - lexical top: `docker-cli-logs-0004` (`docker logs`)
  - semantic top: `docker-cli-logs-0004` (`docker logs`) score `0.72276`
  - class: `COERENTE`

- What does docker exec do?
  - lexical top: `docker-cli-exec-0005` (`docker exec`)
  - semantic top: `docker-cli-exec-0005` (`docker exec`) score `0.712722`
  - class: `COERENTE`

- What are Docker volumes?
  - lexical top: `docker-volumes-0001` (`docker volumes`)
  - semantic top: `docker-volumes-0001` (`docker volumes`) score `0.726924`
  - class: `COERENTE`

- What are Docker networks?
  - lexical top: `docker-networks-0001` (`docker networks`)
  - semantic top: `docker-networks-0001` (`docker networks`) score `0.710064`
  - class: `COERENTE`

- What is a Docker registry?
  - lexical top: `docker-registry-0002` (`docker registry`)
  - semantic top: `docker-registry-0002` (`docker registry`) score `0.739994`
  - class: `COERENTE`

- What are image layers?
  - lexical top: `docker-image-layers-0002` (`image layers`)
  - semantic top: `docker-image-layers-0002` (`image layers`) score `0.534133`
  - class: `COERENTE`

## Summary
- COERENTE: 11
- PARCIALMENTE_COERENTE: 1
- FALHA: 0

## Assessment
- The semantic baseline is operational and the front looks close to closure.
