# HANDOFF LIVECOPILOT SEMANTIC REGRESSION EXPANDED 20260315T071640Z

## Motivacao da rodada
- consolidar uma regressao semantica mais robusta apos a limpeza da baseline curta principal
- transformar a conquista do smoke curto em patrimonio reutilizavel do projeto
- medir honestamente a cobertura atual sem abrir novas frentes de correcao

## Bateria ampliada escolhida
- 20 perguntas no total
- 5 perguntas por dominio: Terraform, Kubernetes, Docker e Observabilidade
- bateria montada apenas com evidencia real do corpus ativo em `data/knowledge_raw/*_docs_selected*` e artefatos de persistencia/cobertura

## Execucao real
- API real usada: `http://127.0.0.1:8099/api/chat`
- total executado: 20/20 perguntas
- resumo:
  - Terraform: 3 coerentes, 2 parciais
  - Kubernetes: 3 coerentes, 2 parciais
  - Docker: 1 coerente, 4 parciais
  - Observabilidade: 2 coerentes, 2 parciais, 1 falha

## Baseline ampliada criada
- `docs/validation/semantic_regression_expanded_run_20260315T071640Z.json`
- `docs/validation/semantic_regression_expanded_baseline_20260315T071640Z.json`
- `docs/validation/semantic_regression_expanded_report_20260315T071640Z.md`
- `docs/validation/semantic_regression_expanded_summary_20260315T071640Z.md`

## Pontos fracos remanescentes
- predominio de respostas parcialmente coerentes quando o retrieval acha o topico certo mas a sintese final despeja trecho cru de documentacao
- pior caso desta rodada: `Para que serve o promtool?`, que caiu em `response_guidance` e falhou apesar de corpus ativo
- Docker foi o dominio mais fraco na bateria ampliada

## Proximo passo sugerido
- atacar primeiro `promtool`, `notification policy no Grafana Alerting` e `port publishing no Docker`
- depois reexecutar a bateria ampliada para medir ganho sem tocar na baseline curta existente
