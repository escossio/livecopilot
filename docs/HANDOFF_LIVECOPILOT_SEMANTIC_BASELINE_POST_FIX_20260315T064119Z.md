# Handoff — Rerun da baseline semantica ampliada pos-fix

## Motivacao
- consolidar o estado atual do nucleo semantico apos as correcoes recentes em Terraform e Observabilidade
- medir a baseline ampliada com comparacao justa contra a baseline anterior

## Execucao real
- backend validado antes da rodada (`service active`, `/health` ok)
- mesma bateria de 9 perguntas da baseline anterior, executada via `POST /api/chat`

## Resultado consolidado
- Terraform: 3/3 coerentes
- Kubernetes: 2/3 coerentes, 1 parcial
- Docker: 0/1 coerentes, 1 parcial
- Observabilidade: 2/2 coerentes

## Melhorias confirmadas
- `backend no Terraform`: falha resolvida
- `Alertmanager`: falha resolvida
- `recording rule no Prometheus`: parcial resolvida
- nenhuma piora observada

## Pontos ainda fracos
- `ConfigMap` em Kubernetes ainda responde como trecho cru de documentacao
- `Dockerfile` em Docker ainda fica no dominio certo, mas sem sintese direta suficiente

## Baseline nova
- `docs/validation/semantic_regression_run_post_fix_20260315T064030Z.json`
- `docs/validation/semantic_regression_baseline_post_fix_20260315T064030Z.json`
- `docs/validation/semantic_regression_report_post_fix_20260315T064030Z.md`
- `docs/validation/semantic_regression_before_after_20260315T064030Z.md`

## Proximo passo sugerido
- atacar as duas parciais restantes com o mesmo padrao cirurgico: `ConfigMap` e `Dockerfile`
