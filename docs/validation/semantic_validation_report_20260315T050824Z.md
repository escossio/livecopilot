# Validacao Semantica - Livecopilot (2026-03-15)

## Evidencias da base relacionada
- `data/knowledge_raw/terraform_docs_selected_incremental/`
- `data/knowledge_raw/kubernetes_docs_selected/`
- `docs/coverage/semantic_coverage_audit_terraform_after_20260312.json`
- `docs/coverage/kubernetes_semantic_persist_validation_20260312T154518Z.json`

## Perguntas executadas
### Terraform
1. Para que serve o arquivo de state no Terraform?
2. Qual a diferenca entre terraform plan e terraform apply?
3. O que e um backend no Terraform e para que serve?

### Kubernetes
4. O que e um Namespace no Kubernetes?
5. Qual a diferenca entre Pod e Service no Kubernetes?
6. O que e um ConfigMap no Kubernetes?

## Resultados (resumo)
- Arquivo bruto: `docs/validation/semantic_validation_run_20260315T050824Z.json`
- Resumo: `docs/validation/semantic_validation_summary_20260315T050824Z.json`

## Avaliacao por pergunta
1. Terraform state
- classificacao: FRACA/GENERICA
- motivo: resposta sobre "automacao de infraestrutura" sem explicar state.

2. Terraform plan vs apply
- classificacao: FRACA/GENERICA
- motivo: mesma resposta generica, sem diferenciar plan/apply.

3. Terraform backend
- classificacao: FALHA
- motivo: roteado para `infra_status_connector` e respondeu sobre backend do Livecopilot.

4. Kubernetes namespace
- classificacao: FALHA
- motivo: resposta sobre TCP/IP, nao sobre namespaces.

5. Kubernetes pod vs service
- classificacao: FALHA
- motivo: resposta sobre escopo de redes, nao sobre objetos do k8s.

6. Kubernetes configmap
- classificacao: FRACA/GENERICA
- motivo: resposta vaga sem definicao de ConfigMap.

## Leitura geral
- As respostas nao demonstraram aderencia ao corpus local de Terraform/Kubernetes nesta rodada.
- Padrao observado: respostas genericas/desalinhadas e um caso de roteamento incorreto para `infra_status_connector`.
- O nucleo semantico precisa de investigacao posterior (etapa seguinte), pois a validacao atual falhou em perguntas basicas.
