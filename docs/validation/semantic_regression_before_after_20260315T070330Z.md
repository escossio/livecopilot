# Semantic Regression Before/After — 20260315T070330Z

## Para que serve o arquivo de state no Terraform?
- Antes: COERENTE
- Depois: COERENTE
- Answer antes: No Terraform, o state guarda o mapeamento da infraestrutura real e ajuda a determinar quais mudanças precisam ser aplicadas.
- Answer depois: No Terraform, o state guarda o mapeamento da infraestrutura real e ajuda a determinar quais mudanças precisam ser aplicadas.

## Qual a diferenca entre terraform plan e terraform apply?
- Antes: COERENTE
- Depois: COERENTE
- Answer antes: No Terraform, `plan` mostra as mudanças previstas antes da execução; `apply` executa essas mudanças na infraestrutura.
- Answer depois: No Terraform, `plan` mostra as mudanças previstas antes da execução; `apply` executa essas mudanças na infraestrutura.

## O que e um backend no Terraform?
- Antes: FALHA
- Depois: COERENTE
- Answer antes: O backend principal do Livecopilot esta saudavel e respondendo com runtime coerente.
- Answer depois: No Terraform, backend é o componente que define onde o state fica armazenado e como ele é acessado, podendo ser local ou remoto.

## Qual a diferenca entre Pod e Service no Kubernetes?
- Antes: COERENTE
- Depois: COERENTE
- Answer antes: No Kubernetes, Pod é a unidade que executa os containers e recebe IP próprio; Service oferece um ponto estável para alcançar e distribuir tráfego para um conjunto de Pods.
- Answer depois: No Kubernetes, Pod é a unidade que executa os containers e recebe IP próprio; Service oferece um ponto estável para alcançar e distribuir tráfego para um conjunto de Pods.

## O que e um Namespace no Kubernetes?
- Antes: COERENTE
- Depois: COERENTE
- Answer antes: Namespaces provide a scope for names. Names of resources need to be unique within a namespace, but not across namespaces.
- Answer depois: Namespaces provide a scope for names. Names of resources need to be unique within a namespace, but not across namespaces.

## O que e um ConfigMap no Kubernetes?
- Antes: PARCIALMENTE COERENTE
- Depois: PARCIALMENTE COERENTE
- Answer antes: ## ConfigMap object A ConfigMap is an {{< glossary_tooltip text="API object" term_id="object" >}} that lets you store configuration for other objects to use. Unlike most Kubernete Além disso, title: ConfigMaps api_metadata: - apiVersion: "v1" kind:...
- Answer depois: ## ConfigMap object A ConfigMap is an {{< glossary_tooltip text="API object" term_id="object" >}} that lets you store configuration for other objects to use. Unlike most Kubernete Além disso, title: ConfigMaps api_metadata: - apiVersion: "v1" kind:...

## Para que serve um Dockerfile?
- Antes: PARCIALMENTE COERENTE
- Depois: PARCIALMENTE COERENTE
- Answer antes: Docker solves the "it works on my machine" problem by packaging applications and their dependencies into containers. This makes it easy to run the same application on different env Além disso, ## Create a base image If you need to completely control the...
- Answer depois: Docker solves the "it works on my machine" problem by packaging applications and their dependencies into containers. This makes it easy to run the same application on different env Além disso, ## Create a base image If you need to completely control the...

## O que faz o Alertmanager?
- Antes: FALHA
- Depois: COERENTE
- Answer antes: Ainda nao sei responder isso com confianca porque nao tenho uma fonte confiavel suficiente para este caso.
- Answer depois: O Alertmanager recebe alertas, agrupa ocorrencias relacionadas, aplica rotas e silenciamentos, e envia as notificacoes para os canais configurados.

## O que e uma recording rule no Prometheus?
- Antes: PARCIALMENTE COERENTE
- Depois: COERENTE
- Answer antes: title: Defining recording rules nav_title: Recording rules sort_rank: 2 --- ## Configuring rules Prometheus supports two types of rules which may be configured and then evalu Além disso, When the file is syntactically valid, the checker prints a textual...
- Answer depois: No Prometheus, uma recording rule precomputa uma consulta e grava o resultado como uma nova série temporal, o que acelera consultas e simplifica alertas.

## Consolidado
- Melhoraram: 3
- O que e um backend no Terraform?
- O que faz o Alertmanager?
- O que e uma recording rule no Prometheus?
- Iguais: 6
- Para que serve o arquivo de state no Terraform?
- Qual a diferenca entre terraform plan e terraform apply?
- Qual a diferenca entre Pod e Service no Kubernetes?
- O que e um Namespace no Kubernetes?
- O que e um ConfigMap no Kubernetes?
- Para que serve um Dockerfile?
- Pioraram: 0
