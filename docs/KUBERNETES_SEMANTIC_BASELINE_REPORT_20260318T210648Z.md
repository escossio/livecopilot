# Kubernetes Core Semantic Baseline Report

## Sandbox
- Directory: `data/semantic_index_experiments/kubernetes_pilot`
- Files: `embeddings.jsonl` and `metadata.json`
- Model: `text-embedding-3-large`
- Chunks: `12`
- Embedding dim: `3072`

## Results
- What is a Kubernetes cluster?
  - lexical top: `kubernetes-namespace-0007` (`namespace`)
  - semantic top: `kubernetes-core-0001` (`pods`) score `0.542315`
  - class: `COERENTE`

- What is a node in Kubernetes?
  - lexical top: `kubernetes-core-0002` (`deployment`)
  - semantic top: `kubernetes-core-0001` (`pods`) score `0.642531`
  - class: `COERENTE`

- What is a pod?
  - lexical top: `kubernetes-core-0004` (`probes`)
  - semantic top: `kubernetes-core-0001` (`pods`) score `0.569385`
  - class: `COERENTE`

- What is a deployment?
  - lexical top: `kubernetes-core-0002` (`deployment`)
  - semantic top: `kubernetes-core-0002` (`deployment`) score `0.558047`
  - class: `COERENTE`

- What is a service in Kubernetes?
  - lexical top: `kubernetes-networking-0001` (`service`)
  - semantic top: `kubernetes-networking-0001` (`service`) score `0.655483`
  - class: `COERENTE`

- What is a namespace?
  - lexical top: `kubernetes-namespace-0007` (`namespace`)
  - semantic top: `kubernetes-namespace-0007` (`namespace`) score `0.613287`
  - class: `COERENTE`

- What is a ConfigMap?
  - lexical top: `kubernetes-secret-0008` (`secret`)
  - semantic top: `kubernetes-core-0003` (`configmap`) score `0.689863`
  - class: `COERENTE`

- What is a Secret in Kubernetes?
  - lexical top: `kubernetes-secret-0008` (`secret`)
  - semantic top: `kubernetes-secret-0008` (`secret`) score `0.738108`
  - class: `COERENTE`

- What are volumes in Kubernetes?
  - lexical top: `kubernetes-storage-0001` (`volumes`)
  - semantic top: `kubernetes-storage-0001` (`volumes`) score `0.700156`
  - class: `COERENTE`

- What are liveness and readiness probes?
  - lexical top: `kubernetes-core-0004` (`probes`)
  - semantic top: `kubernetes-core-0004` (`probes`) score `0.779283`
  - class: `COERENTE`

- What does kubectl do?
  - lexical top: `kubernetes-cli-0001` (`kubectl`)
  - semantic top: `kubernetes-cli-0001` (`kubectl`) score `0.683362`
  - class: `COERENTE`

- What is a Kubernetes manifest YAML?
  - lexical top: `kubernetes-core-0006` (`yaml manifests`)
  - semantic top: `kubernetes-core-0006` (`yaml manifests`) score `0.75214`
  - class: `COERENTE`

## Summary
- COERENTE: 12
- PARCIALMENTE_COERENTE: 0
- FALHA: 0

## Assessment
The semantic baseline is operational and the front looks close to closure.
