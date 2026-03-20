# FRONT KUBERNETES CORE EXECUTION CHECKLIST

## source_policy
- Usar apenas fontes oficiais do Kubernetes.
- Não incluir Helm, operators, controllers avançados, cloud providers ou integrações com Terraform.
- Manter o escopo estritamente core.
 - status: completed

## source_manifest
- Registrar somente docs oficiais, referência `kubectl` e definições de recursos da API.
- Não aceitar fontes derivadas, blogs ou material de terceiros.
 - status: completed

## corpus_lock
- Congelar exatamente os documentos listados no `docs/KUBERNETES_CORPUS_LOCK.md`.
- Qualquer inclusão futura exige atualização explícita do lock.
 - status: completed

## parsing
- Preparar o corpus oficial para leitura estruturada.
- Preservar títulos, seções e exemplos essenciais.
 - status: completed

## chunking
- Separar o domínio em chunks por tema funcional.
- Cobrir no mínimo cluster, node, pod, deployment, service, namespace, configmap, secret, volumes, probes, `kubectl` CLI e manifests YAML.
 - status: completed

## lexical_baseline
- Validar cobertura lexical do corpus congelado.
- Confirmar que cada tópico obrigatório tem acesso direto por termos naturais.
 - status: completed

## semantic_embeddings
- Criar embeddings apenas após fechamento do corpus e do chunking.
 - status: completed

## semantic_baseline
- Rodar baseline semântica do domínio core.
- Verificar recuperação para perguntas práticas de infraestrutura.
 - status: completed

## semantic_refinement
- Ajustar chunks apenas se a baseline semântica mostrar lacunas reais.
- Não ampliar o escopo da frente.
 - status: completed

## closure_decision
- Fechar a frente apenas quando a cobertura lexical e semântica estiverem aceitáveis.
- Registrar o estado final no `STATUS.md`.
 - status: completed

## front_status
- domain: kubernetes_core
- state: closed
- closure_decision: approved
