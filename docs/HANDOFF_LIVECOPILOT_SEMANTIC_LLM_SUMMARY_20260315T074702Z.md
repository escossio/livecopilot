# HANDOFF LIVECOPILOT SEMANTIC LLM SUMMARY

## Motivacao
- os casos PARCIALMENTE COERENTE restantes exigem reformulacao semantica, nao apenas limpeza textual
- queremos usar um LLM como compressor fiel do contexto, nao como improvisador

## Estrategia adotada
- `_llm_summary_allowed()` identifica perguntas parciais (modulos, workspace, Deployment, Ingress, Docker networking, Grafana policies)
- `_snippet_context_for_llm()` junta os snippets destilados para alimentar o LLM
- `_call_llm_summary()` chama OpenAI (`gpt-3.5-turbo`) com prompt instruindo “responda em Português, com 1-2 frases, apenas com base no contexto e sem metadata”
- a ordem de decisão permanece manual > intenção > LLM > fallback estrutural

## Resultados antes/depois
- subset (10 perguntas) continua parcial, mas a resposta final agora vem como frases LLM dirigidas à intenção
- baseline ampliada pós-LLM manteve 3 coerentes em Terraform/Kubernetes, 1 em Docker e 3 em Observabilidade (sem falhas)
- artefatos:
  - `docs/validation/semantic_llm_summary_subset_20260315T074701Z.json`
  - `docs/validation/semantic_llm_summary_subset_report_20260315T074701Z.md`
  - `docs/validation/semantic_llm_summary_before_after_20260315T074701Z.md`
  - `docs/validation/semantic_regression_expanded_post_llm_summary_20260315T074702Z.json`
  - `docs/validation/semantic_regression_expanded_post_llm_summary_report_20260315T074702Z.md`
  - `docs/validation/semantic_regression_expanded_post_llm_summary_summary_20260315T074702Z.md`

## Proximo passo sugerido
- aprofundar síntese dos tópicos remanescentes e reexecutar a baseline caso a coerência avance
