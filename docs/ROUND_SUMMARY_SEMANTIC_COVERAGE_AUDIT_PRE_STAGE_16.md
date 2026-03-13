# Round Summary: Auditoria de Cobertura da Base Semântica (Pré-Etapa 16)

Data: 2026-03-11
Status: concluida (auditoria de cobertura; sem busca externa)

## Escopo da auditoria
- Base avaliada: base semântica interna já operacional (local-first).
- Método: `semantic_search` por pergunta representativa do domínio técnico.
- Amostra inicial: 20 perguntas (Kubernetes, Docker, AWS, FastAPI, Python, SQL, observabilidade, CI/CD).
- Top-k por pergunta: `5`.
- Threshold de lacuna: `max_score < 0.45`.
- Threshold de bem coberta: `max_score >= 0.6` e `avg_score >= 0.45`.

## Estatísticas consolidadas
- Perguntas avaliadas: `20`
- Bem cobertas: `5`
- Parcialmente cobertas: `5`
- Lacunas: `10`
- Média global de score máximo: `0.503941`
- Média global de score médio: `0.439589`

## Perguntas bem cobertas
- `logs previous crashloopbackoff kubernetes` | max=0.861 avg=0.747 | top=tmp/semantic_gap_round2/debug_crashloop_logs_previous.md
- `kubectl create token serviceaccount` | max=0.727 avg=0.628 | top=tmp/kubectl_ops_round/kubectl_create_token_serviceaccount.md
- `rbac role rolebinding serviceaccount kubernetes` | max=0.725 avg=0.560 | top=tmp/semantic_gap_round2/rbac_quick_basics.md
- `kubernetes liveness probe e readiness probe diferenca` | max=0.724 avg=0.714 | top=data/question_bank_raw/ckad_exercises/e.observability.md
- `networkpolicy default deny all kubernetes` | max=0.604 avg=0.518 | top=tmp/semantic_gap_round2/networkpolicy_access_control.md

## Perguntas parcialmente cobertas
- `docker compose healthcheck redis` | max=0.702 avg=0.428 | top=__smoke_openai__.md
- `aws vpc security group vs nacl` | max=0.536 avg=0.499 | top=__api_context_smoke__.md
- `statefulset volumeclaimtemplates kubernetes` | max=0.532 avg=0.506 | top=data/raw_review/ckad_exercises_modules/g.state.md
- `persistentvolume persistentvolumeclaim reclaim policy` | max=0.469 avg=0.452 | top=data/question_bank_raw/ckad_exercises/g.state.md
- `ingress nginx tls host path` | max=0.467 avg=0.426 | top=knowledge-gap::gap_20260310t234507_3291540000_4e3b1d6abc47_gap_flow_validation_ingress_nginx_timeout_504.md

## Perguntas com lacuna de conhecimento
- `python async await e event loop` | max=0.242 avg=0.228 | top=tmp/kubectl_ops_round/kubectl_get_events_pod.md
- `ansible playbook idempotencia handlers` | max=0.307 avg=0.284 | top=tmp/semantic_gap_round2/networkpolicy_access_control.md
- `jenkins pipeline declarativa stages` | max=0.338 avg=0.296 | top=knowledge-gap::gap_20260310t232657_6343290000_ce3a020227ec_validation_gap_ingestion_flow_kubernetes_network_policy_baseline.md
- `postgres index btree vs gin` | max=0.338 avg=0.268 | top=knowledge-gap::gap_20260310t234013_4528790000_1706c7323efb_postgres_auth.md
- `terraform aws s3 backend remote state locking` | max=0.391 avg=0.358 | top=relatorio_final.docx
- `observabilidade prometheus grafana alertmanager` | max=0.408 avg=0.370 | top=data/raw_review/ckad_exercises_modules/e.observability.md
- `kubernetes service clusterip vs nodeport vs loadbalancer` | max=0.417 avg=0.410 | top=data/raw_review/ckad_exercises_modules/c.pod_design.md
- `aws iam least privilege policy` | max=0.422 avg=0.345 | top=data/question_bank_raw/sample_assessment.md
- `fastapi dependency injection com exemplos` | max=0.434 avg=0.351 | top=__inline_semantic_min__.txt
- `docker multi stage build best practices` | max=0.435 avg=0.402 | top=__smoke_openai__.md

## Sugestões de literatura para fechar lacunas
- Kubernetes security & auth: ServiceAccount token projection, RBAC avançado, políticas de acesso e exemplos operacionais (`kubectl create token`, projected tokens).
- Kubernetes networking avançado: Ingress TLS/host/path, diferenças práticas de Service types e troubleshooting de rota.
- Storage em Kubernetes: StatefulSet + `volumeClaimTemplates`, reclaim policies de PV/PVC, casos de migração e backup.
- Docker avançado: multi-stage builds, hardening de imagens e otimização de cache em pipelines CI.
- Infra AWS/Terraform: remote state com locking, IAM least privilege por cenário real, VPC SG vs NACL com casos comparativos.
- Backend/observabilidade: FastAPI DI em produção, Prometheus/Grafana/Alertmanager com runbooks e alertas acionáveis.
- Banco de dados: índices PostgreSQL (`btree`, `gin`, `gist`) com guias de escolha por workload.

## Decisão operacional
- A base local já cobre parte relevante do domínio, mas há lacunas materiais (50% da amostra).
- Recomendação: executar ciclo direcionado de ingestão local para as lacunas antes de expandir para busca externa em runtime.
- Esta rodada não abre busca externa nem altera pipeline semântico.
