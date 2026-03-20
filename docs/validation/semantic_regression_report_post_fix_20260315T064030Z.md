# Semantic Regression Report Post Fix — 20260315T064030Z

## Resultado por pergunta
### Terraform — Para que serve o arquivo de state no Terraform?
- HTTP status: 200
- answer: No Terraform, o state guarda o mapeamento da infraestrutura real e ajuda a determinar quais mudanças precisam ser aplicadas.
- classificacao: COERENTE
- justificativa: responde diretamente ao papel do state e segue aderente ao corpus.

### Terraform — Qual a diferenca entre terraform plan e terraform apply?
- HTTP status: 200
- answer: No Terraform, `plan` mostra as mudanças previstas antes da execução; `apply` executa essas mudanças na infraestrutura.
- classificacao: COERENTE
- justificativa: diferencia previsao e execucao de forma direta.

### Terraform — O que e um backend no Terraform?
- HTTP status: 200
- answer: No Terraform, backend é o componente que define onde o state fica armazenado e como ele é acessado, podendo ser local ou remoto.
- classificacao: COERENTE
- justificativa: agora responde o conceito de backend no Terraform e nao mais o backend do Livecopilot.

### Kubernetes — Qual a diferenca entre Pod e Service no Kubernetes?
- HTTP status: 200
- answer: No Kubernetes, Pod é a unidade que executa os containers e recebe IP próprio; Service oferece um ponto estável para alcançar e distribuir tráfego para um conjunto de Pods.
- classificacao: COERENTE
- justificativa: distingue corretamente unidade de execucao e ponto estavel de acesso.

### Kubernetes — O que e um Namespace no Kubernetes?
- HTTP status: 200
- answer: Namespaces provide a scope for names. Names of resources need to be unique within a namespace, but not across namespaces.
- classificacao: COERENTE
- justificativa: segue correto, embora em ingles.

### Kubernetes — O que e um ConfigMap no Kubernetes?
- HTTP status: 200
- answer: ## ConfigMap object A ConfigMap is an {{< glossary_tooltip text="API object" term_id="object" >}} that lets you store configuration for other objects to use. Unlike most Kubernete Além disso, title: ConfigMaps api_metadata: - apiVersion: "v1" kind:...
- classificacao: PARCIALMENTE COERENTE
- justificativa: permanece no topico certo, mas ainda sai como trecho cru da documentacao.

### Docker — Para que serve um Dockerfile?
- HTTP status: 200
- answer: Docker solves the "it works on my machine" problem by packaging applications and their dependencies into containers. This makes it easy to run the same application on different env Além disso, ## Create a base image If you need to completely control the...
- classificacao: PARCIALMENTE COERENTE
- justificativa: continua no dominio certo, mas ainda nao sintetiza diretamente a funcao de um Dockerfile.

### Observabilidade — O que faz o Alertmanager?
- HTTP status: 200
- answer: O Alertmanager recebe alertas, agrupa ocorrencias relacionadas, aplica rotas e silenciamentos, e envia as notificacoes para os canais configurados.
- classificacao: COERENTE
- justificativa: passou a usar corpus de observabilidade e sintetizar a funcao principal do Alertmanager.

### Observabilidade — O que e uma recording rule no Prometheus?
- HTTP status: 200
- answer: No Prometheus, uma recording rule precomputa uma consulta e grava o resultado como uma nova série temporal, o que acelera consultas e simplifica alertas.
- classificacao: COERENTE
- justificativa: passou a explicar o conceito em linguagem natural e alinhada ao corpus.

## Resumo por dominio
- Terraform: 3/3 coerentes, 0 parciais, 0 falhas
- Kubernetes: 2/3 coerentes, 1 parciais, 0 falhas
- Docker: 0/1 coerentes, 1 parciais, 0 falhas
- Observabilidade: 2/2 coerentes, 0 parciais, 0 falhas