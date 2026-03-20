# Handoff — Terraform backend disambiguation + Observability targeted fix

## Motivacao
- a baseline semantica ampliada mostrou duas prioridades objetivas:
  - colisao de `backend` no Terraform com o backend operacional do Livecopilot
  - baixo desempenho do dominio de Observabilidade (`Alertmanager` falhando e `recording rule` parcial)

## Diagnostico
### Terraform
- a palavra `backend` disparava `infra_status_connector` cedo demais
- a heuristica ignorava o contexto `Terraform` da frase

### Observabilidade
- `Alertmanager`:
  - retrieval vetorial estava correto
  - o domain gating zerava o contexto porque `config/semantic_policy.json` ainda nao trazia sinais de Observabilidade
- `recording rule`:
  - retrieval e contexto estavam corretos
  - faltava sintese especifica; a answer saia crua/parcial

## Correcao aplicada
- `app/services/infra_status_connector.py`
  - desambiguacao explicita para `terraform + backend`
- `config/semantic_policy.json`
  - ampliado com sinais de Terraform e Observabilidade
- `app/services/suggestions.py`
  - sintese especifica para `backend no Terraform`, `Alertmanager` e `recording rule no Prometheus`

## Resultado
- `O que e um backend no Terraform?` -> `COERENTE`
- `O que faz o Alertmanager?` -> `COERENTE`
- `O que e uma recording rule no Prometheus?` -> `COERENTE`
- Smoke A e Smoke B continuaram passando

## Artefatos
- `docs/diagnostics/terraform_backend_disambiguation_20260315T063320Z.md`
- `docs/diagnostics/observability_domain_diagnostic_20260315T063320Z.md`
- `docs/diagnostics/observability_trace_20260315T063320Z.json`
- `docs/diagnostics/semantic_targeted_fix_run_20260315T063320Z.json`
- `docs/diagnostics/semantic_targeted_fix_before_after_20260315T063320Z.md`

## Proximo passo sugerido
- seguir para as perguntas ainda parciais da baseline ampliada, principalmente `ConfigMap` em Kubernetes e `Dockerfile` em Docker, reutilizando o mesmo padrao de diagnostico + sintese controlada
