# Observability Domain Diagnostic — 20260315T063320Z

## O que faz o Alertmanager?
- Retrieval: 3 candidatos; top fonte `observability_docs_selected/alertmanager/docs/alertmanager.md`
- Contexto: result_count=3 | context_len=959
- Answer final: O Alertmanager recebe alertas, agrupa ocorrencias relacionadas, aplica rotas e silenciamentos, e envia as notificacoes para os canais configurados.
- Fallback: nao
- Classificacao da falha por camada (antes da correcao): RETRIEVAL OK / GATING RUIM

## O que e uma recording rule no Prometheus?
- Retrieval: 3 candidatos; top fonte `observability_docs_selected/prometheus/docs/configuration/recording_rules.md`
- Contexto: result_count=3 | context_len=978
- Answer final: No Prometheus, uma recording rule precomputa uma consulta e grava o resultado como uma nova série temporal, o que acelera consultas e simplifica alertas.
- Fallback: nao
- Classificacao da falha por camada (antes da correcao): RETRIEVAL OK / SINTESE CRUA
