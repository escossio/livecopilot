# Kubernetes Core Lexical Refinement Report

## Lacunas da lexical baseline
- `namespace` estava `NAO_RESPONDIVEL`.
- `secret` estava sem chunk dedicado e só aparecia de forma indireta.
- `node` estava subdefinido no chunk de `pods`.
- `service` estava respondivel apenas de forma parcial.

## Chunks criados
- `data/knowledge_chunks/kubernetes/core/kubernetes-namespace-0007.json`
- `data/knowledge_chunks/kubernetes/core/kubernetes-secret-0008.json`

## Chunks expandidos
- `data/knowledge_chunks/kubernetes/core/kubernetes-core-0002.json`
- `data/knowledge_chunks/kubernetes/networking/kubernetes-networking-0001.json`

## Resultado técnico
O refinement reduz as lacunas mais óbvias do núcleo Kubernetes core sem ampliar o corpus para fora do escopo. A frente continua apta a seguir para uma nova validação lexical ou, se aceitável, para `semantic_embeddings`.
