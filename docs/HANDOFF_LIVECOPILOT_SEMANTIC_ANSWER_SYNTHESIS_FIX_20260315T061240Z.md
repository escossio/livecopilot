# Handoff — Melhoria da sintese final da resposta semantica

## Problema de partida
- o sistema ja recuperava contexto util, mas a answer final ainda saia como dump cru do contexto (`QUERY`, `SOURCE`, `SNIPPET`)
- isso mantinha os canarios em `PARCIALMENTE COERENTE`

## Correcao aplicada
- arquivo principal: `app/services/suggestions.py`
- suporte em: `app/api/routes.py`
- acao:
  - criada `_synthesize_knowledge_answer(query, matches)` para gerar uma resposta curta e controlada a partir dos chunks recuperados
  - `_build_knowledge_enriched_suggestions()` passou a usar essa sintese como resposta principal quando ha contexto util
  - `_select_primary_answer()` passou a preservar a nova answer sintetizada quando ela ja nao e generica

## Resultado
- Terraform state: `COERENTE`
- Terraform plan/apply: `COERENTE`
- Kubernetes Pod vs Service: `COERENTE`
- os 3 canarios deixaram de responder com dump cru e passaram a responder em linguagem natural, ainda ancorados no contexto recuperado

## Regressao
- Smoke A passou
- Smoke B passou

## Proximo passo sugerido
- ampliar a sintese controlada para novas familias de pergunta sem reintroduzir resposta generica nem perder aderencia ao corpus

## Artefatos
- `docs/diagnostics/semantic_answer_synthesis_trace_20260315T061230Z.json`
- `docs/diagnostics/semantic_answer_synthesis_before_after_20260315T061230Z.md`
- `docs/diagnostics/semantic_canary_synthesis_post_fix_20260315T061230Z.json`
- `docs/diagnostics/semantic_trace_run_20260315T061147Z.json`
- `docs/diagnostics/semantic_trace_run_20260315T061148Z.json`
- `docs/diagnostics/semantic_trace_run_20260315T061149Z.json`
