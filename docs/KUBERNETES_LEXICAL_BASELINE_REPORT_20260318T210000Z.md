# Kubernetes Core Lexical Baseline Report

## Perguntas testadas
1. What is a Kubernetes cluster?
2. What is a node in Kubernetes?
3. What is a pod?
4. What is a deployment?
5. What is a service in Kubernetes?
6. What is a namespace?
7. What is a ConfigMap?
8. What is a Secret in Kubernetes?
9. What are volumes in Kubernetes?
10. What are liveness and readiness probes?
11. What does kubectl do?
12. What is a Kubernetes manifest YAML?

## Resultados

- What is a Kubernetes cluster?
  - top chunk: `kubernetes-core-0001` (`pods`)
  - class: `RESPONDIVEL`
  - observação: o chunk cobre cluster, node e pod no mesmo trecho e responde a noção central de cluster.

- What is a node in Kubernetes?
  - top chunk: `kubernetes-core-0001` (`pods`)
  - class: `PARCIALMENTE_RESPONDIVEL`
  - observação: o chunk menciona nodes como capacidade de computação, mas não isola a definição de node.

- What is a pod?
  - top chunk: `kubernetes-core-0004` (`probes`)
  - class: `RESPONDIVEL`
  - observação: há menção direta a Pod no contexto de probes, mas a definição ideal ainda está mais forte no corpus de pods.

- What is a deployment?
  - top chunk: `kubernetes-core-0002` (`deployment`)
  - class: `RESPONDIVEL`
  - observação: chunk define Deployment como primitive de rollout e gestão de Pods.

- What is a service in Kubernetes?
  - top chunk: `kubernetes-networking-0001` (`service`)
  - class: `PARCIALMENTE_RESPONDIVEL`
  - observação: responde o conceito, mas está curto e não traz toda a mecânica de endpoints/seletores.

- What is a namespace?
  - top chunk: `kubernetes-core-0001` (`pods`)
  - class: `NAO_RESPONDIVEL`
  - observação: nenhum chunk atual isola namespace com definição suficiente.

- What is a ConfigMap?
  - top chunk: `kubernetes-core-0003` (`configmap`)
  - class: `PARCIALMENTE_RESPONDIVEL`
  - observação: define o propósito, mas a cobertura ainda é compacta.

- What is a Secret in Kubernetes?
  - top chunk: `kubernetes-core-0004` (`probes`)
  - class: `PARCIALMENTE_RESPONDIVEL`
  - observação: o corpus atual não tem chunk específico de Secret.

- What are volumes in Kubernetes?
  - top chunk: `kubernetes-storage-0001` (`volumes`)
  - class: `RESPONDIVEL`
  - observação: explica o papel de volumes e o vínculo com persistência.

- What are liveness and readiness probes?
  - top chunk: `kubernetes-core-0004` (`probes`)
  - class: `RESPONDIVEL`
  - observação: chunk cobre liveness, readiness e startup probes diretamente.

- What does kubectl do?
  - top chunk: `kubernetes-cli-0001` (`kubectl`)
  - class: `RESPONDIVEL`
  - observação: define a CLI e os usos operacionais básicos.

- What is a Kubernetes manifest YAML?
  - top chunk: `kubernetes-core-0006` (`yaml manifests`)
  - class: `RESPONDIVEL`
  - observação: responde bem a noção de manifesto declarativo YAML.

## Cobertura resumida
- RESPONDIVEL: 8
- PARCIALMENTE_RESPONDIVEL: 3
- NAO_RESPONDIVEL: 1

## Leitura técnica
O subset atual está pronto para avançar para `semantic_embeddings` em termos gerais, mas há lacunas claras para `namespace` e `secret`, além de uma definição mais forte de `node` e um reforço no chunk de `service`.
