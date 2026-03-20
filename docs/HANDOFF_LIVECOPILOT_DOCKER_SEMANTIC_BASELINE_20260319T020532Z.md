# HANDOFF_LIVECOPILOT_DOCKER_SEMANTIC_BASELINE_20260319T020532Z

## Embeddings gerados
- Sandbox isolado: `data/semantic_index_experiments/docker_pilot/`
- Arquivos: `embeddings.jsonl` e `metadata.json`
- Modelo: `text-embedding-3-large`
- Chunks: `12`
- Dimensão: `3072`
- Média de palavras por chunk: `42.25`
- Timestamp: `2026-03-19T02:05:27.085301+00:00`
- O índice isolado não toca no índice global.

## Resultado da baseline semântica
- COERENTE: `11/12`
- PARCIALMENTE_COERENTE: `1/12`
- FALHA: `0/12`
- Relatório: `docs/DOCKER_SEMANTIC_BASELINE_REPORT_20260319T020532Z.md`
- Resultados estruturados: `docs/DOCKER_SEMANTIC_BASELINE_RESULTS_20260319T020532Z.json`

## Comparação lexical vs semântico
- `What is a container?` -> mesmo topo lexical e semântico: `docker-container-0001`
- `What is a Docker image?` -> lexical top `docker-image-layers-0002`; semantic top `docker-image-0002`; classificação `PARCIALMENTE_COERENTE`
- `What is a Dockerfile?` -> mesmo topo: `docker-dockerfile-0003`
- `What does docker build do?` -> mesmo topo: `docker-cli-build-0002`
- `What does docker run do?` -> mesmo topo: `docker-cli-run-0001`
- `What does docker ps do?` -> mesmo topo: `docker-cli-ps-0003`
- `What does docker logs do?` -> mesmo topo: `docker-cli-logs-0004`
- `What does docker exec do?` -> mesmo topo: `docker-cli-exec-0005`
- `What are Docker volumes?` -> mesmo topo: `docker-volumes-0001`
- `What are Docker networks?` -> mesmo topo: `docker-networks-0001`
- `What is a Docker registry?` -> mesmo topo: `docker-registry-0002`
- `What are image layers?` -> mesmo topo: `docker-image-layers-0002`

## Estado atual da frente
- A frente está semanticamente forte para o corpus atual.
- O único desvio é a pergunta definicional de `Docker image`, que no embedding prefere o chunk de `image` em vez do chunk de `image layers`.
- Isso não bloqueia fechamento técnico por cobertura, mas recomenda uma revisão fina se a meta for maximizar alinhamento lexical/semântico no tema `image`.
- Não houve expansão de corpus, Swarm, Kubernetes, Compose avançado ou integração externa.

## Pronto para closure_decision
- Sim, com observação residual no tópico `Docker image`.
- Se o critério da frente exigir alinhamento perfeito em todas as perguntas, então ainda cabe refinement pontual do chunk de imagem.
