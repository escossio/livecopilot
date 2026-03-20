# Semantic Regression Expanded Post-Synthesis — 20260315T072557Z

## Resultado por pergunta
### Terraform — Para que serve o arquivo de state no Terraform?
- HTTP status: 200
- answer: No Terraform, o state guarda o mapeamento da infraestrutura real e ajuda a determinar quais mudanças precisam ser aplicadas.
- classificacao: COERENTE
- justificativa: responde diretamente o papel do state e segue aderente ao corpus.
- antes: COERENTE

### Terraform — Qual a diferenca entre terraform plan e terraform apply?
- HTTP status: 200
- answer: No Terraform, `plan` mostra as mudanças previstas antes da execução; `apply` executa essas mudanças na infraestrutura.
- classificacao: COERENTE
- justificativa: diferencia preview e execucao de forma limpa.
- antes: COERENTE

### Terraform — O que e um backend no Terraform?
- HTTP status: 200
- answer: No Terraform, backend é o componente que define onde o state fica armazenado e como ele é acessado, podendo ser local ou remoto.
- classificacao: COERENTE
- justificativa: explica backend de state local/remoto de forma precisa.
- antes: COERENTE

### Terraform — Quando usar modulos no Terraform?
- HTTP status: 200
- answer: When to write a module In principle any combination of resources and other constructs can be factored out into a module, but over-using modules can make your overall Terraform Module structure Terraform modules define self-contained, reusable pieces of...
- classificacao: PARCIALMENTE COERENTE
- justificativa: topico certo, mas a resposta permanece como trecho cru.
- antes: PARCIALMENTE COERENTE

### Terraform — O que e um workspace no Terraform?
- HTTP status: 200
- answer: Workspaces allow the use of multiple states with a single configuration directory. START AUTO GENERATED METADATA, DO NOT EDIT Terraform starts with a single, default workspace named default that you cannot delete.
- classificacao: PARCIALMENTE COERENTE
- justificativa: concepto correto, porem com metadata auto e sem sintese natural.
- antes: PARCIALMENTE COERENTE

### Kubernetes — Qual a diferenca entre Pod e Service no Kubernetes?
- HTTP status: 200
- answer: No Kubernetes, Pod é a unidade que executa os containers e recebe IP próprio; Service oferece um ponto estável para alcançar e distribuir tráfego para um conjunto de Pods.
- classificacao: COERENTE
- justificativa: separa execucao e exposicao com clareza.
- antes: COERENTE

### Kubernetes — O que e um Namespace no Kubernetes?
- HTTP status: 200
- answer: Namespaces provide a scope for names. Names of resources need to be unique within a namespace, but not across namespaces.
- classificacao: COERENTE
- justificativa: conceito de escopo/isolamento preservado.
- antes: COERENTE

### Kubernetes — O que e um ConfigMap no Kubernetes?
- HTTP status: 200
- answer: No Kubernetes, um ConfigMap é um recurso usado para armazenar configurações não sensíveis separadas da imagem do container. Ele permite injetar variáveis de ambiente, arquivos de configuração ou parâmetros dentro dos Pods.
- classificacao: COERENTE
- justificativa: sintese limpa sobre configuracoes desacopladas.
- antes: COERENTE

### Kubernetes — Para que serve um Deployment no Kubernetes?
- HTTP status: 200
- answer: A _Deployment_ provides declarative updates for and . You descr Reviewers: - janetkuo - apiVersion: "apps/v1" kind: "Deployment" feature: Kubernetes pro
- classificacao: PARCIALMENTE COERENTE
- justificativa: traz idea de updates declarativos, mas mistura markup do doc.
- antes: PARCIALMENTE COERENTE

### Kubernetes — Quando usar um Ingress no Kubernetes?
- HTTP status: 200
- answer: What is Ingress? [Ingress](/docs/reference/generated/kubernetes-api//ingress-v1-networking-k8s-io) exposes HTTP and HTTPS routes from outside the cluste Terminology For clarity, this guide defines the following terms: * Node: A worker machine in Kubernetes,...
- classificacao: PARCIALMENTE COERENTE
- justificativa: aponta exposicao HTTP/HTTPS, porém com texto ainda cru.
- antes: PARCIALMENTE COERENTE

### Docker — Para que serve um Dockerfile?
- HTTP status: 200
- answer: Dockerfile é um arquivo de instruções usado para construir uma imagem Docker. Ele define passos como qual imagem base usar, quais arquivos copiar, quais comandos executar e qual processo será iniciado quando o container rodar.
- classificacao: COERENTE
- justificativa: descreve passo a passo da imagem Docker.
- antes: COERENTE

### Docker — O que e port publishing no Docker?
- HTTP status: 200
- answer: Keywords: network, iptables, firewall --- By default, for both IPv4 and IPv6, the Docker d Docker solves the "it works on my machine" problem by packaging applications and their dependencies into containers. This makes it easy to run the same application on...
- classificacao: PARCIALMENTE COERENTE
- justificativa: fala de mapeamento de portas mas em formato metadata.
- antes: PARCIALMENTE COERENTE

### Docker — O que e o host network driver no Docker?
- HTTP status: 200
- answer: Keywords: network, host, standalone, host mode networking - /network Keywords: networking, drivers, bridge, routing, routing mesh, overlay, ports --- Dock
- classificacao: PARCIALMENTE COERENTE
- justificativa: cita o driver host mas sem frase completa.
- antes: PARCIALMENTE COERENTE

### Docker — Para que serve o modo rootless no Docker?
- HTTP status: 200
- answer: Keywords: security, namespaces, rootless --- Rootless mode lets you run t Keywords: security, namespaces, rootless --- Advanced usage Daemon {{< tab name="With syst
- classificacao: PARCIALMENTE COERENTE
- justificativa: aponta uso sem root, mas continua com blocos documentais.
- antes: PARCIALMENTE COERENTE

### Docker — O que e content trust no Docker?
- HTTP status: 200
- answer: Keywords: content, trust, security, docker, documentation - /engine/security/trust/content Keywords: trust, security, root, keys, repository, sandbox - /security/trust/trust_sandbox/
- classificacao: PARCIALMENTE COERENTE
- justificativa: indica integridade de imagens e trust sandbox, mas indireta.
- antes: PARCIALMENTE COERENTE

### Observabilidade — O que faz o Alertmanager?
- HTTP status: 200
- answer: O Alertmanager recebe alertas, agrupa ocorrencias relacionadas, aplica rotas e silenciamentos, e envia as notificacoes para os canais configurados.
- classificacao: COERENTE
- justificativa: responde agrupamento, rotas, silenciamentos e notificacoes.
- antes: COERENTE

### Observabilidade — O que e uma recording rule no Prometheus?
- HTTP status: 200
- answer: No Prometheus, uma recording rule precomputa uma consulta e grava o resultado como uma nova série temporal, o que acelera consultas e simplifica alertas.
- classificacao: COERENTE
- justificativa: explica precomputa consulta e grava nova serie temporal.
- antes: COERENTE

### Observabilidade — O que e uma alerting rule no Prometheus?
- HTTP status: 200
- answer: Alerting rules allow you to define alert conditions based on Prometheus expression language expressions and to send notifications about Sending alert notifications Prometheus's alerting rules are good at figuring what is broken *right now*, but they are not a...
- classificacao: PARCIALMENTE COERENTE
- justificativa: fala de condicoes e notificacoes mas derrapa em trecho cru.
- antes: PARCIALMENTE COERENTE

### Observabilidade — Para que serve o promtool?
- HTTP status: 200
- answer: Promtool e a CLI do Prometheus que valida arquivos de configuracao, testa regras de alertas e executa consultas para garantir que a instancia esteja ajustada antes de rodar em producao.
- classificacao: COERENTE
- justificativa: define promtool como CLI que valida configs, regras e consultas.
- antes: FALHA

### Observabilidade — O que e uma notification policy no Grafana Alerting?
- HTTP status: 200
- answer: /notification-policies/notifications/ /docs/grafana//alerting/fundamentals/notification-policies/notifications/ /notifications/ /docs/grafana//alerting/notifications/ - ../unified-alerting/notifications/ /docs/grafana//alerting/unified-a
- classificacao: PARCIALMENTE COERENTE
- justificativa: retorna aliases e caminhos ao inves de explicar a politica.
- antes: PARCIALMENTE COERENTE

## Resumo por dominio
- Terraform: total=5, coerentes=3, parciais=2, fracas/genéricas=0, falhas=0
- Kubernetes: total=5, coerentes=3, parciais=2, fracas/genéricas=0, falhas=0
- Docker: total=5, coerentes=1, parciais=4, fracas/genéricas=0, falhas=0
- Observabilidade: total=5, coerentes=3, parciais=2, fracas/genéricas=0, falhas=0

## Comparacao com baseline anterior
- promtool subiu de FALHA para COERENTE graças ao ajuste manual sincronizado com a nova camada estrutural de sintese.
