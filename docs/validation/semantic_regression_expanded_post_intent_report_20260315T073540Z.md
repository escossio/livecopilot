# Semantic Regression Expanded Post-Intent — 20260315T073540Z

## Resultado por pergunta
### Terraform — Para que serve o arquivo de state no Terraform?
- HTTP status: 200
- answer: No Terraform, o state guarda o mapeamento da infraestrutura real e ajuda a determinar quais mudanças precisam ser aplicadas.
- classification: COERENTE
- justification: Mantem definicao clara do state.
- before: COERENTE

### Terraform — Qual a diferenca entre terraform plan e terraform apply?
- HTTP status: 200
- answer: No Terraform, `plan` mostra as mudanças previstas antes da execução; `apply` executa essas mudanças na infraestrutura.
- classification: COERENTE
- justification: Contraste limpo entre plan e apply.
- before: COERENTE

### Terraform — O que e um backend no Terraform?
- HTTP status: 200
- answer: No Terraform, backend é o componente que define onde o state fica armazenado e como ele é acessado, podendo ser local ou remoto.
- classification: COERENTE
- justification: Define backend de state.
- before: COERENTE

### Terraform — Quando usar modulos no Terraform?
- HTTP status: 200
- answer: Use modulos no Terraform quando when to write a module in principle any combination of resources and other constructs can be factored out into a module, but over-using modules can make your overall terraform
- classification: PARCIALMENTE COERENTE
- justification: Foco no uso, mas ainda repete parte da doc.
- before: PARCIALMENTE COERENTE

### Terraform — O que e um workspace no Terraform?
- HTTP status: 200
- answer: um workspace no Terraform é workspaces allow the use of multiple states with a single configuration directory. start auto generated metadata, do not edit
- classification: PARCIALMENTE COERENTE
- justification: Define workspaces, porem inclui metadata.
- before: PARCIALMENTE COERENTE

### Kubernetes — Qual a diferenca entre Pod e Service no Kubernetes?
- HTTP status: 200
- answer: No Kubernetes, Pod é a unidade que executa os containers e recebe IP próprio; Service oferece um ponto estável para alcançar e distribuir tráfego para um conjunto de Pods.
- classification: COERENTE
- justification: Resposta coerente.
- before: COERENTE

### Kubernetes — O que e um Namespace no Kubernetes?
- HTTP status: 200
- answer: um Namespace no Kubernetes é namespaces provide a scope for names. names of resources need to be unique within a namespace, but not across namespaces.
- classification: COERENTE
- justification: Resposta coerente.
- before: COERENTE

### Kubernetes — O que e um ConfigMap no Kubernetes?
- HTTP status: 200
- answer: No Kubernetes, um ConfigMap é um recurso usado para armazenar configurações não sensíveis separadas da imagem do container. Ele permite injetar variáveis de ambiente, arquivos de configuração ou parâmetros dentro dos Pods.
- classification: COERENTE
- justification: Resposta coerente.
- before: COERENTE

### Kubernetes — Para que serve um Deployment no Kubernetes?
- HTTP status: 200
- answer: um Deployment no Kubernetes serve para a _deployment_ provides declarative updates for and . you descr
- classification: PARCIALMENTE COERENTE
- justification: Apresenta updates declarativos, mas mantem markup.
- before: PARCIALMENTE COERENTE

### Kubernetes — Quando usar um Ingress no Kubernetes?
- HTTP status: 200
- answer: Use um Ingress no Kubernetes quando what is ingress? [ingress](/docs/reference/generated/kubernetes-api//ingress-v1-networking-k8s-io) exposes http and https routes from outside the cluste
- classification: PARCIALMENTE COERENTE
- justification: Aponta rotas externas, mas segue com texto cru.
- before: PARCIALMENTE COERENTE

### Docker — Para que serve um Dockerfile?
- HTTP status: 200
- answer: Dockerfile é um arquivo de instruções usado para construir uma imagem Docker. Ele define passos como qual imagem base usar, quais arquivos copiar, quais comandos executar e qual processo será iniciado quando o container rodar.
- classification: COERENTE
- justification: Explica a construcao da imagem Docker.
- before: COERENTE

### Docker — O que e port publishing no Docker?
- HTTP status: 200
- answer: port publishing no Docker é keywords: network, iptables, firewall --- by default, for both ipv4 and ipv6, the docker d
- classification: PARCIALMENTE COERENTE
- justification: Mostra puertos e keywords, mas resposta continua sintética.
- before: PARCIALMENTE COERENTE

### Docker — O que e o host network driver no Docker?
- HTTP status: 200
- answer: o host network driver no Docker é keywords: network, host, standalone, host mode networking - /network
- classification: PARCIALMENTE COERENTE
- justification: Cita o driver host com keywords.
- before: PARCIALMENTE COERENTE

### Docker — Para que serve o modo rootless no Docker?
- HTTP status: 200
- answer: o modo rootless no Docker serve para keywords: security, namespaces, rootless --- rootless mode lets you run t
- classification: PARCIALMENTE COERENTE
- justification: Cita execucao sem root e segurança.
- before: PARCIALMENTE COERENTE

### Docker — O que e content trust no Docker?
- HTTP status: 200
- answer: content trust no Docker é keywords: content, trust, security, docker, documentation - /engine/security/trust/content
- classification: PARCIALMENTE COERENTE
- justification: Menciona integridade e trust sandbox.
- before: PARCIALMENTE COERENTE

### Observabilidade — O que faz o Alertmanager?
- HTTP status: 200
- answer: O Alertmanager recebe alertas, agrupa ocorrencias relacionadas, aplica rotas e silenciamentos, e envia as notificacoes para os canais configurados.
- classification: COERENTE
- justification: Enumerates grouping, routing, silencing and notifications.
- before: COERENTE

### Observabilidade — O que e uma recording rule no Prometheus?
- HTTP status: 200
- answer: No Prometheus, uma recording rule precomputa uma consulta e grava o resultado como uma nova série temporal, o que acelera consultas e simplifica alertas.
- classification: COERENTE
- justification: Explica precomputacao de consultas.
- before: COERENTE

### Observabilidade — O que e uma alerting rule no Prometheus?
- HTTP status: 200
- answer: uma alerting rule no Prometheus é alerting rules allow you to define alert conditions based on prometheus expression language expressions and to send notifications about
- classification: PARCIALMENTE COERENTE
- justification: Descreve condicoes e notificacoes, mas ainda doc.
- before: PARCIALMENTE COERENTE

### Observabilidade — Para que serve o promtool?
- HTTP status: 200
- answer: Promtool e a CLI do Prometheus que valida arquivos de configuracao, testa regras de alertas e executa consultas para garantir que a instancia esteja ajustada antes de rodar em producao.
- classification: COERENTE
- justification: Define promtool como CLI de validacao.
- before: FALHA

### Observabilidade — O que e uma notification policy no Grafana Alerting?
- HTTP status: 200
- answer: uma notification policy no Grafana Alerting é /notification-policies/notifications/ /docs/grafana//alerting/fundamentals/notification-policies/notifications/
- classification: PARCIALMENTE COERENTE
- justification: Continua com aliases/caminhos.
- before: PARCIALMENTE COERENTE

## Resumo por dominio
- Terraform: total=5, coerentes=3, parciais=2, falhas=0
- Kubernetes: total=5, coerentes=3, parciais=2, falhas=0
- Docker: total=5, coerentes=1, parciais=4, falhas=0
- Observabilidade: total=5, coerentes=3, parciais=2, falhas=0

## Comparacao com a baseline anterior
- Mesmo após a sintese orientada por intenção, os parciais continuam nos mesmos pontos; promtool segue em COERENTE.
