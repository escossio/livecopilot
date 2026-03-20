# HANDOFF LIVECOPILOT SEMANTIC BASELINE POST FIX 20260315T070330Z

## Motivacao da rodada
- rerodar a baseline semantica ampliada apos as correcoes recentes em Terraform e Observabilidade
- medir o estado atual do nucleo semantico com a mesma bateria da baseline oficial anterior
- consolidar uma nova baseline oficial pos-fix sem abrir novas frentes

## Execucao real
- backend validado antes da rodada: `livecopilot-semantic-api.service` em `active`
- `/health` validado em `2026-03-15T07:01:37Z` com `HTTP 200` e corpo `{"status":"ok"}`
- API real usada: `http://127.0.0.1:8099/api/chat`
- bateria executada: 9 perguntas nos dominios Terraform, Kubernetes, Docker e Observabilidade

## Comparacao antes/depois
- melhoraram 3 perguntas:
  - `O que e um backend no Terraform?`: `FALHA -> COERENTE`
  - `O que faz o Alertmanager?`: `FALHA -> COERENTE`
  - `O que e uma recording rule no Prometheus?`: `PARCIALMENTE COERENTE -> COERENTE`
- permaneceram iguais 6 perguntas
- pioras observadas: nenhuma

## Baseline nova
- `docs/validation/semantic_regression_run_post_fix_20260315T070330Z.json`
- `docs/validation/semantic_regression_baseline_post_fix_20260315T070330Z.json`
- `docs/validation/semantic_regression_report_post_fix_20260315T070330Z.md`
- `docs/validation/semantic_regression_before_after_20260315T070330Z.md`

## Pontos ainda fracos
- Kubernetes: `O que e um ConfigMap no Kubernetes?` continua `PARCIALMENTE COERENTE` por devolver trecho cru da documentacao
- Docker: `Para que serve um Dockerfile?` continua `PARCIALMENTE COERENTE` por nao sintetizar diretamente a funcao do Dockerfile

## Proximo passo sugerido
- dominio mais fraco agora: `Docker`, com `0/1` coerentes e `1/1` parcial
- alvo pratico seguinte: sintese controlada de `Dockerfile`, seguida por limpeza de sintese para `ConfigMap`
