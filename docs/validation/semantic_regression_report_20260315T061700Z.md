# Semantic Regression Report — 20260315T061700Z

## Dominios e evidencias
- Terraform: `data/knowledge_raw/terraform_docs_selected*`, `docs/coverage/semantic_coverage_audit_terraform_after_20260312.json`, banco ativo com 66 docs / 452 chunks somando as colecoes Terraform.
- Kubernetes: `data/knowledge_raw/kubernetes_docs_selected`, `docs/coverage/kubernetes_semantic_persist_validation_20260312T154518Z.json`, banco ativo com 12 docs / 95 chunks.
- Docker: `data/knowledge_raw/docker_docs_selected`, `docs/coverage/semantic_coverage_audit_docker_after_20260312.json`, banco ativo com 79 docs / 84 chunks.
- Observabilidade: `data/knowledge_raw/observability_docs_selected`, `docs/coverage/semantic_coverage_audit_observability_after_20260312.json`, banco ativo com 35 docs / 234 chunks.

## Resultado por pergunta
### Terraform — Para que serve o arquivo de state no Terraform?
- HTTP status: 200
- result_count: 3
- answer: No Terraform, o state guarda o mapeamento da infraestrutura real e ajuda a determinar quais mudanças precisam ser aplicadas.
- classificacao: COERENTE
- justificativa: responde diretamente para que serve o state e permanece alinhada ao corpus de Terraform state.

### Terraform — Qual a diferenca entre terraform plan e terraform apply?
- HTTP status: 200
- result_count: 3
- answer: No Terraform, `plan` mostra as mudanças previstas antes da execução; `apply` executa essas mudanças na infraestrutura.
- classificacao: COERENTE
- justificativa: diferencia preview e execucao de forma limpa e tecnicamente correta.

### Terraform — O que e um backend no Terraform?
- HTTP status: 200
- result_count: 2
- answer: O backend principal do Livecopilot esta saudavel e respondendo com runtime coerente.
- classificacao: FALHA
- justificativa: roteou para o backend do Livecopilot e respondeu outra coisa, nao o conceito de backend do Terraform.

### Kubernetes — Qual a diferenca entre Pod e Service no Kubernetes?
- HTTP status: 200
- result_count: 3
- answer: No Kubernetes, Pod é a unidade que executa os containers e recebe IP próprio; Service oferece um ponto estável para alcançar e distribuir tráfego para um conjunto de Pods.
- classificacao: COERENTE
- justificativa: explica de forma direta a diferenca entre unidade de execucao e ponto estavel de acesso.

### Kubernetes — O que e um Namespace no Kubernetes?
- HTTP status: 200
- result_count: 3
- answer: Namespaces provide a scope for names. Names of resources need to be unique within a namespace, but not across namespaces.
- classificacao: COERENTE
- justificativa: responde corretamente o conceito, embora em ingles.

### Kubernetes — O que e um ConfigMap no Kubernetes?
- HTTP status: 200
- result_count: 3
- answer: ## ConfigMap object A ConfigMap is an {{< glossary_tooltip text="API object" term_id="object" >}} that lets you store configuration for other objects to use. Unlike most Kubernete Além disso, title: ConfigMaps api_metadata: - apiVersion: "v1" kind:...
- classificacao: PARCIALMENTE COERENTE
- justificativa: esta no topico certo, mas a answer saiu como trecho cru da documentacao.

### Docker — Para que serve um Dockerfile?
- HTTP status: 200
- result_count: 3
- answer: Docker solves the "it works on my machine" problem by packaging applications and their dependencies into containers. This makes it easy to run the same application on different env Além disso, ## Create a base image If you need to completely control the...
- classificacao: PARCIALMENTE COERENTE
- justificativa: permanece no dominio Docker/build, mas nao responde de forma direta que o Dockerfile descreve como construir a imagem.

### Observabilidade — O que faz o Alertmanager?
- HTTP status: 200
- result_count: 1
- answer: Ainda nao sei responder isso com confianca porque nao tenho uma fonte confiavel suficiente para este caso.
- classificacao: FALHA
- justificativa: nao usou o corpus presente e caiu em resposta de baixa confianca.

### Observabilidade — O que e uma recording rule no Prometheus?
- HTTP status: 200
- result_count: 3
- answer: title: Defining recording rules nav_title: Recording rules sort_rank: 2 --- ## Configuring rules Prometheus supports two types of rules which may be configured and then evalu Além disso, When the file is syntactically valid, the checker prints a textual...
- classificacao: PARCIALMENTE COERENTE
- justificativa: atinge o topico correto, mas ainda despeja trecho cru da documentacao em vez de sintetizar o conceito.

## Resumo por dominio
- Terraform: 2/3 coerentes, 0 parciais, 1 falhas
- Kubernetes: 2/3 coerentes, 1 parciais, 0 falhas
- Docker: 0/1 coerentes, 1 parciais, 0 falhas
- Observabilidade: 0/2 coerentes, 1 parciais, 1 falhas

## Smoke semantico curto sugerido
- Para que serve o arquivo de state no Terraform?
- Qual a diferenca entre terraform plan e terraform apply?
- Qual a diferenca entre Pod e Service no Kubernetes?
- O que e um Namespace no Kubernetes?
- Para que serve um Dockerfile?
- O que faz o Alertmanager?