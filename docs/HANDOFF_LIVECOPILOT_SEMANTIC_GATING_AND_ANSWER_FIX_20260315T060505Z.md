# Handoff — Correcao cirurgica de gating e promocao da resposta semantica

## Diagnostico de partida
- Terraform tinha retrieval vetorial bom, mas os hits eram descartados por `domain_gating`
- Kubernetes tinha contexto util, mas a answer principal do chat seguia generica

## Correcao aplicada
### 1. Gating
- arquivo: `app/services/suggestions.py`
- acao:
  - adicionados sinais centrais de Terraform em `DOMAIN_SIGNALS`
  - `_passes_domain_gating()` passou a aceitar top semantic hit forte (`score >= 0.6`)
- efeito observado:
  - canarios Terraform sairam de `result_count=0` para `result_count=3`

### 2. Promocao da answer final
- arquivo: `app/api/routes.py`
- acao:
  - criada `_select_primary_answer()`
  - quando ha `knowledge_context` util, a resposta principal promove o resumo contextualizado em vez do slot generico
- efeito observado:
  - canario Kubernetes deixou de responder com a frase generica e passou a refletir o contexto recuperado

## Validacao
- canarios semanticos rerodados com sucesso HTTP 200
- os 3 sairam de genericos para `PARCIALMENTE COERENTE`
- regressao basica passou:
  - smoke principal do chat
  - smoke de skill local estavel

## Limitacao residual
- a answer final ainda e um resumo cru do contexto (`Resumo técnico inicial: QUERY ... SOURCE ... SNIPPET ...`)
- proxima etapa recomendada: sintetizar esse contexto em resposta mais direta sem perder aderencia ao corpus

## Artefatos
- `docs/diagnostics/semantic_fix_gating_trace_20260315T060430Z.json`
- `docs/diagnostics/semantic_fix_answer_selection_trace_20260315T060430Z.json`
- `docs/diagnostics/semantic_fix_before_after_20260315T060430Z.md`
- `docs/diagnostics/semantic_canary_post_fix_20260315T060430Z.json`
- `docs/diagnostics/semantic_trace_run_20260315T060351Z.json`
- `docs/diagnostics/semantic_trace_run_20260315T060353Z.json`
- `docs/diagnostics/semantic_trace_run_20260315T060354Z.json`
