# Handoff: Kubernetes Core Front Opened

## Escopo da frente
A frente `kubernetes_core` cobre o núcleo operacional necessário para uso prático em infraestrutura, sem Helm, operators, controllers avançados, cloud providers ou integração com Terraform.

## Tópicos obrigatórios
- cluster
- node
- pod
- deployment
- service
- namespace
- configmap
- secret
- volumes
- probes (`liveness` / `readiness`)
- `kubectl` CLI
- manifests YAML

## Estrutura de chunks
- `data/knowledge_chunks/kubernetes/core/`
- `data/knowledge_chunks/kubernetes/cli/`
- `data/knowledge_chunks/kubernetes/networking/`
- `data/knowledge_chunks/kubernetes/storage/`

## Contrato de execução
O ciclo da frente segue:
`source_policy` -> `source_manifest` -> `corpus_lock` -> `parsing` -> `chunking` -> `lexical_baseline` -> `semantic_embeddings` -> `semantic_baseline` -> `semantic_refinement` -> `closure_decision`

## Estado inicial
- Corpus ainda não ingerido.
- Chunks ainda não criados.
- Baselines ainda não executadas.
