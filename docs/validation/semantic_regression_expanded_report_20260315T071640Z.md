# Semantic Regression Expanded Report — 20260315T071640Z

## Dominios evidenciados
- Terraform:
  - data/knowledge_raw/terraform_docs_selected*
  - docs/validation/semantic_regression_report_20260315T061700Z.md (66 docs / 452 chunks somando as colecoes Terraform)
  - docs/coverage/semantic_persist_terraform43_validation_20260312.json (43 docs / 209 chunks no recorte persistido principal)
- Kubernetes:
  - data/knowledge_raw/kubernetes_docs_selected
  - docs/coverage/kubernetes_semantic_persist_validation_20260312T154518Z.json (12 docs / 95 chunks)
  - source files cobrindo ConfigMap, Namespace, Service, Ingress, Deployment, PV, RBAC e probes
- Docker:
  - data/knowledge_raw/docker_docs_selected
  - docs/validation/semantic_regression_report_20260315T061700Z.md (79 docs / 84 chunks)
  - titulos ativos em networking e security: port publishing, host network driver, rootless mode, content trust
- Observabilidade:
  - data/knowledge_raw/observability_docs_selected
  - docs/coverage/semantic_persist_observability35_validation_20260312.json (35 docs / 234 chunks)
  - source files ativos em Alertmanager, Prometheus rules/promtool e Grafana alerting/notification policies

## Bateria ampliada
### Terraform — Para que serve o arquivo de state no Terraform?
- smoke curto: sim
- por que foi escolhida: conceito central do workflow de Terraform e item do smoke curto
- resposta minima aceitavel: explicar que o state mapeia a infraestrutura real e orienta o plano/aplicacao

### Terraform — Qual a diferenca entre terraform plan e terraform apply?
- smoke curto: sim
- por que foi escolhida: valida fluxo basico entre previsao e execucao
- resposta minima aceitavel: diferenciar preview de mudancas e execucao real

### Terraform — O que e um backend no Terraform?
- smoke curto: sim
- por que foi escolhida: mede conceito estrutural de state local/remoto
- resposta minima aceitavel: explicar que backend define onde o state fica armazenado e acessado

### Terraform — Quando usar modulos no Terraform?
- smoke curto: nao
- por que foi escolhida: corpus ativo inclui docs de modules e composicao; avalia recomendacao pratica
- resposta minima aceitavel: indicar reutilizacao/organizacao de conjuntos de recursos sem overuse

### Terraform — O que e um workspace no Terraform?
- smoke curto: nao
- por que foi escolhida: workspace aparece no corpus de state e ajuda a medir organizacao de estados
- resposta minima aceitavel: explicar que permite multiplos states em uma mesma configuracao

### Kubernetes — Qual a diferenca entre Pod e Service no Kubernetes?
- smoke curto: sim
- por que foi escolhida: conceito basico de execucao vs exposicao; item do smoke curto
- resposta minima aceitavel: separar unidade de execucao e ponto estavel de acesso

### Kubernetes — O que e um Namespace no Kubernetes?
- smoke curto: sim
- por que foi escolhida: valida organizacao logica do cluster; item do smoke curto
- resposta minima aceitavel: explicar escopo logico/isolamento de nomes e recursos

### Kubernetes — O que e um ConfigMap no Kubernetes?
- smoke curto: sim
- por que foi escolhida: item do smoke curto refinado recentemente; mede preservacao do fix de sintese
- resposta minima aceitavel: explicar armazenamento de configuracoes nao sensiveis desacopladas da imagem

### Kubernetes — Para que serve um Deployment no Kubernetes?
- smoke curto: nao
- por que foi escolhida: deployment esta no corpus e mede controle declarativo de rollout
- resposta minima aceitavel: explicar que gerencia replicas/rollouts declarativos de Pods

### Kubernetes — Quando usar um Ingress no Kubernetes?
- smoke curto: nao
- por que foi escolhida: ingress esta no corpus e mede exposicao HTTP/HTTPS externa
- resposta minima aceitavel: indicar uso para expor rotas HTTP/HTTPS externas ao cluster

### Docker — Para que serve um Dockerfile?
- smoke curto: sim
- por que foi escolhida: item do smoke curto refinado recentemente; valida preservacao do fix de sintese
- resposta minima aceitavel: explicar que descreve como construir uma imagem Docker

### Docker — O que e port publishing no Docker?
- smoke curto: nao
- por que foi escolhida: port publishing aparece no corpus de networking e mede operacao pratica comum
- resposta minima aceitavel: explicar mapeamento de portas do host para o container

### Docker — O que e o host network driver no Docker?
- smoke curto: nao
- por que foi escolhida: host network driver esta no corpus de networking e mede entendimento de rede
- resposta minima aceitavel: explicar que o container usa a rede do host sem NAT/bridge tradicional

### Docker — Para que serve o modo rootless no Docker?
- smoke curto: nao
- por que foi escolhida: rootless aparece no corpus de security e mede entendimento de execucao sem root
- resposta minima aceitavel: explicar que roda daemon/containers sem privilegios root para reduzir risco

### Docker — O que e content trust no Docker?
- smoke curto: nao
- por que foi escolhida: content trust esta no corpus de security e mede integridade de imagens
- resposta minima aceitavel: explicar verificacao/assinatura de conteudo para confiar em imagens

### Observabilidade — O que faz o Alertmanager?
- smoke curto: sim
- por que foi escolhida: item do smoke curto; mede orquestracao de alertas
- resposta minima aceitavel: explicar agrupamento, roteamento, silenciamento e notificacao

### Observabilidade — O que e uma recording rule no Prometheus?
- smoke curto: sim
- por que foi escolhida: item do smoke curto; mede precomputacao de series
- resposta minima aceitavel: explicar precomputacao de consultas gravadas como nova serie temporal

### Observabilidade — O que e uma alerting rule no Prometheus?
- smoke curto: nao
- por que foi escolhida: alerting rules estao no corpus e medem regra pratica de disparo
- resposta minima aceitavel: explicar condicao de alerta baseada em expressao PromQL que gera alertas

### Observabilidade — Para que serve o promtool?
- smoke curto: nao
- por que foi escolhida: promtool esta no corpus e mede ferramenta operacional importante de validacao
- resposta minima aceitavel: explicar validacao de regras/configuracao e testes de Prometheus

### Observabilidade — O que e uma notification policy no Grafana Alerting?
- smoke curto: nao
- por que foi escolhida: notification policies estao no corpus Grafana e medem roteamento de notificacoes
- resposta minima aceitavel: explicar regra de roteamento/agrupamento de notificacoes no Grafana Alerting

## Execucao real
### Terraform — Para que serve o arquivo de state no Terraform?
- HTTP status: 200
- answer: No Terraform, o state guarda o mapeamento da infraestrutura real e ajuda a determinar quais mudanças precisam ser aplicadas.
- classificacao: COERENTE
- justificativa: responde diretamente ao papel do state.

### Terraform — Qual a diferenca entre terraform plan e terraform apply?
- HTTP status: 200
- answer: No Terraform, `plan` mostra as mudanças previstas antes da execução; `apply` executa essas mudanças na infraestrutura.
- classificacao: COERENTE
- justificativa: contraste tecnico limpo entre os dois comandos.

### Terraform — O que e um backend no Terraform?
- HTTP status: 200
- answer: No Terraform, backend é o componente que define onde o state fica armazenado e como ele é acessado, podendo ser local ou remoto.
- classificacao: COERENTE
- justificativa: responde corretamente o conceito de backend.

### Terraform — Quando usar modulos no Terraform?
- HTTP status: 200
- answer: ## When to write a module In principle any combination of resources and other constructs can be factored out into a module, but over-using modules can make your overall Terraform Além disso, ## Module structure Terraform modules define self-contained,...
- classificacao: PARCIALMENTE COERENTE
- justificativa: topico correto, mas saiu como trecho cru sem sintese objetiva.

### Terraform — O que e um workspace no Terraform?
- HTTP status: 200
- answer: page_title: 'State: Workspaces' description: >- Workspaces allow the use of multiple states with a single configuration directory. # START AUTO GENERATED METADATA, DO NOT EDIT Além disso, Terraform starts with a single, default workspace named `default` that...
- classificacao: PARCIALMENTE COERENTE
- justificativa: atinge o conceito certo, mas despeja metadata e doc crua.

### Kubernetes — Qual a diferenca entre Pod e Service no Kubernetes?
- HTTP status: 200
- answer: No Kubernetes, Pod é a unidade que executa os containers e recebe IP próprio; Service oferece um ponto estável para alcançar e distribuir tráfego para um conjunto de Pods.
- classificacao: COERENTE
- justificativa: distingue corretamente execucao e acesso.

### Kubernetes — O que e um Namespace no Kubernetes?
- HTTP status: 200
- answer: Namespaces provide a scope for names. Names of resources need to be unique within a namespace, but not across namespaces.
- classificacao: COERENTE
- justificativa: conceito correto, embora em ingles.

### Kubernetes — O que e um ConfigMap no Kubernetes?
- HTTP status: 200
- answer: No Kubernetes, um ConfigMap é um recurso usado para armazenar configurações não sensíveis separadas da imagem do container. Ele permite injetar variáveis de ambiente, arquivos de configuração ou parâmetros dentro dos Pods.
- classificacao: COERENTE
- justificativa: sintese limpa e correta do uso de ConfigMap.

### Kubernetes — Para que serve um Deployment no Kubernetes?
- HTTP status: 200
- answer: A _Deployment_ provides declarative updates for {{< glossary_tooltip text="Pods" term_id="pod" >}} and {{< glossary_tooltip term_id="replica-set" text="ReplicaSets" >}}. You descr Além disso, reviewers: - janetkuo title: Deployments api_metadata: -...
- classificacao: PARCIALMENTE COERENTE
- justificativa: tem a ideia central, mas veio com markup e extrato cru.

### Kubernetes — Quando usar um Ingress no Kubernetes?
- HTTP status: 200
- answer: ## What is Ingress? [Ingress](/docs/reference/generated/kubernetes-api/{{< param "version" >}}/#ingress-v1-networking-k8s-io) exposes HTTP and HTTPS routes from outside the cluste Além disso, <!-- body --> ## Terminology For clarity, this guide defines the...
- classificacao: PARCIALMENTE COERENTE
- justificativa: responde o tema, mas sem sintese limpa e com doc crua.

### Docker — Para que serve um Dockerfile?
- HTTP status: 200
- answer: Dockerfile é um arquivo de instruções usado para construir uma imagem Docker. Ele define passos como qual imagem base usar, quais arquivos copiar, quais comandos executar e qual processo será iniciado quando o container rodar.
- classificacao: COERENTE
- justificativa: responde diretamente a funcao do Dockerfile.

### Docker — O que e port publishing no Docker?
- HTTP status: 200
- answer: title: Port publishing and mapping weight: 10 description: Accessing container ports keywords: network, iptables, firewall --- By default, for both IPv4 and IPv6, the Docker d Além disso, Docker solves the "it works on my machine" problem by packaging...
- classificacao: PARCIALMENTE COERENTE
- justificativa: tema correto, mas resposta saiu como metadata e trecho cru.

### Docker — O que e o host network driver no Docker?
- HTTP status: 200
- answer: title: Host network driver description: All about exposing containers on the Docker host's network keywords: network, host, standalone, host mode networking aliases: - /network Além disso, title: Network drivers weight: 20 description: Learn the basics of...
- classificacao: PARCIALMENTE COERENTE
- justificativa: topico correto, mas sem sintese direta do funcionamento.

### Docker — Para que serve o modo rootless no Docker?
- HTTP status: 200
- answer: description: Run the Docker daemon as a non-root user (Rootless mode) keywords: security, namespaces, rootless title: Rootless mode weight: 10 --- Rootless mode lets you run t Além disso, description: Tips for the Rootless mode keywords: security, namespaces,...
- classificacao: PARCIALMENTE COERENTE
- justificativa: ha sinal correto, mas a resposta continua doc crua.

### Docker — O que e content trust no Docker?
- HTTP status: 200
- answer: description: Enabling content trust in Docker keywords: content, trust, security, docker, documentation title: Content trust in Docker aliases: - /engine/security/trust/content Além disso, description: Play in a trust sandbox keywords: trust, security, root,...
- classificacao: PARCIALMENTE COERENTE
- justificativa: dominio correto, mas resposta ainda muito crua e indireta.

### Observabilidade — O que faz o Alertmanager?
- HTTP status: 200
- answer: O Alertmanager recebe alertas, agrupa ocorrencias relacionadas, aplica rotas e silenciamentos, e envia as notificacoes para os canais configurados.
- classificacao: COERENTE
- justificativa: resposta objetiva e tecnicamente correta.

### Observabilidade — O que e uma recording rule no Prometheus?
- HTTP status: 200
- answer: No Prometheus, uma recording rule precomputa uma consulta e grava o resultado como uma nova série temporal, o que acelera consultas e simplifica alertas.
- classificacao: COERENTE
- justificativa: conceito sintetizado corretamente.

### Observabilidade — O que e uma alerting rule no Prometheus?
- HTTP status: 200
- answer: title: Alerting rules sort_rank: 3 --- Alerting rules allow you to define alert conditions based on Prometheus expression language expressions and to send notifications about Além disso, ## Sending alert notifications Prometheus's alerting rules are good at...
- classificacao: PARCIALMENTE COERENTE
- justificativa: tema correto, mas resposta ainda pouco limpa e parcialmente crua.

### Observabilidade — Para que serve o promtool?
- HTTP status: 200
- answer: Ainda nao sei responder isso com confianca porque nao tenho uma fonte confiavel suficiente para este caso.
- classificacao: FALHA
- justificativa: nao usou o corpus disponivel e caiu em resposta de baixa confianca.

### Observabilidade — O que e uma notification policy no Grafana Alerting?
- HTTP status: 200
- answer: aliases: - ../notification-policies/notifications/ # /docs/grafana/<GRAFANA_VERSION>/alerting/fundamentals/notification-policies/notifications/ canonical: https://grafana.com/d Além disso, aliases: - ../notifications/ #...
- classificacao: PARCIALMENTE COERENTE
- justificativa: corpus certo, mas answer quase toda em metadata e alias cru.

## Resumo por dominio
- Terraform: total=5, coerentes=3, parciais=2, fracas/genericas=0, falhas=0
- Kubernetes: total=5, coerentes=3, parciais=2, fracas/genericas=0, falhas=0
- Docker: total=5, coerentes=1, parciais=4, fracas/genericas=0, falhas=0
- Observabilidade: total=5, coerentes=2, parciais=2, fracas/genericas=0, falhas=1
