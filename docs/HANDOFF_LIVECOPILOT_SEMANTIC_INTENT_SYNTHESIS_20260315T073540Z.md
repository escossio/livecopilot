# HANDOFF LIVECOPILOT SEMANTIC INTENT SYNTHESIS

## Motivacao
- transformar respostas parciais em explicacoes orientadas pela intencao da pergunta
- evitar multiplas regras manuais limpando o snippet e alinhando o discurso a 'o que é', 'para que serve', etc.
- manter o smoke curto intacto e permitir usar a mesma base de contexto

## Estrategia adotada
- adicionamos `_classify_question_intent()` e `_build_intent_answer()` em `app/services/suggestions.py` para detectar intenções simples (o que é, para que serve, quando usar, qual a diferença, como funciona)
- a camada de intenção usa `_clean_structural_snippet()` para filtrar metadata e transforma a resposta em frases didáticas como “Use X quando …” ou “X é …”, mantendo o contexto recuperado
- mantivemos os casos manuais de alto valor recentes e garantimos que promtool segue coerente

## Resultados antes/depois
- subset representativo (6 perguntas) mostra respostas mais orientadas, mas todas ainda classificadas como `PARCIALMENTE COERENTE` exceto promtool que já havia evoluído
- baseline ampliada pós-intent mantém `Terraform 3/5 coerentes`, `Kubernetes 3/5 coerentes`, `Docker 1/5 coerente`, `Observabilidade 3/5 coerentes` (sem falhas)
- artefatos:
  - `docs/validation/semantic_intent_synthesis_subset_20260315T073539Z.json`
  - `docs/validation/semantic_intent_synthesis_subset_report_20260315T073539Z.md`
  - `docs/validation/semantic_intent_synthesis_before_after_20260315T073539Z.md`
  - `docs/validation/semantic_regression_expanded_post_intent_20260315T073540Z.json`
  - `docs/validation/semantic_regression_expanded_post_intent_report_20260315T073540Z.md`
  - `docs/validation/semantic_regression_expanded_post_intent_summary_20260315T073540Z.md`

## Proximo passo sugerido
- converter parciais remanescentes em respostas didáticas mais específicas (módulos/workspaces, ingress/deployment, Docker networking/security, Grafana notification policy)
- reexecutar a baseline ampliada se o refinamento aprofundar a coerência e atualizar o smoke curto se surgirem novas certezas
