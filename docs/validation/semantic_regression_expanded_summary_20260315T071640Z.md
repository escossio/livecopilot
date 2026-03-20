# Semantic Regression Expanded Summary — 20260315T071640Z

## Resumo por dominio
- Terraform: total=5, coerentes=3, parciais=2, fracas/genericas=0, falhas=0
- Kubernetes: total=5, coerentes=3, parciais=2, fracas/genericas=0, falhas=0
- Docker: total=5, coerentes=1, parciais=4, fracas/genericas=0, falhas=0
- Observabilidade: total=5, coerentes=2, parciais=2, fracas/genericas=0, falhas=1

## Comparacao com a baseline curta
- os itens do smoke curto continuam fortes nos 4 dominios ja validados
- a bateria ampliada revelou fragilidades novas principalmente em sintese fora dos alvos ja tratados
- topicos mais confiaveis hoje: Terraform state/plan/apply/backend, Kubernetes pod/service/namespace/configmap, Dockerfile, Alertmanager, recording rules
- topicos mais imaturos hoje: Terraform modulos/workspaces, Kubernetes deployment/ingress, Docker networking/security docs, Observabilidade promtool e politicas de notificacao no Grafana

## Proximos alvos sugeridos
- `Para que serve o promtool?`
- `O que e uma notification policy no Grafana Alerting?`
- `O que e port publishing no Docker?`
