# Handoff — Bateria semantica ampliada de regressao

## Motivacao
- o nucleo semantico voltou a responder os 3 canarios principais de forma coerente
- esta rodada consolidou isso em uma baseline ampliada para medir regressao futura por dominio

## Dominios validados
- Terraform
- Kubernetes
- Docker
- Observabilidade

Todos escolhidos com evidencias reais de corpus em `data/knowledge_raw/`, cobertura em `docs/coverage/` e material ativo no banco vetorial.

## Bateria executada
- 9 perguntas pela API real `POST /api/chat`
- resultados registrados em JSON e markdown reutilizaveis

## Leitura objetiva
- Terraform continua forte nos canarios centrais, mas ainda existe colisao lexical/roteamento em `backend no Terraform`
- Kubernetes esta melhor no nucleo, mas ainda ha casos de resposta parcialmente crua (`ConfigMap`)
- Docker responde no topico certo, mas ainda superficial no caso de `Dockerfile`
- Observabilidade e o dominio mais fraco desta bateria: `Alertmanager` falhou e `recording rule` ficou parcial

## Baseline criada
- `docs/validation/semantic_regression_run_20260315T061700Z.json`
- `docs/validation/semantic_regression_baseline_20260315T061700Z.json`
- `docs/validation/semantic_regression_report_20260315T061700Z.md`

## Proximo passo sugerido
1. tratar a colisao de roteamento em `backend no Terraform`
2. ampliar a sintese controlada para Docker/Observabilidade e alguns conceitos de Kubernetes ainda crus
3. promover um subconjunto curto desta bateria a smoke semantico recorrente
