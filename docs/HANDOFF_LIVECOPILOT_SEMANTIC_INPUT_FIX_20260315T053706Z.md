# Handoff - Correcao da camada de transcricao/interpretacao do input

## Causa raiz
- `transcribe_with_trace()` foi acionado para texto digitado e chamou o provedor externo.
- O provedor externo devolveu resposta pronta, substituindo a pergunta original (`transcript_text != raw_input`).
- `search_query` passou a usar texto contaminado.

## Correcao aplicada
- Novo helper em `app/services/transcription.py`: `transcribe_text_input_with_trace()` (echo, sem LLM).
- `app/services/pipeline.py`: `process_ingest()` passou a usar `transcribe_text_input_with_trace()` para input textual.

## Evidencias antes/depois
- Comparativo: `docs/diagnostics/semantic_before_after_comparison_20260315T053706Z.md`
- Trace fix consolidado: `docs/diagnostics/semantic_trace_fix_run_20260315T053706Z.json`

## Revalidacao canario
- `docs/diagnostics/semantic_canary_rerun_20260315T053706Z.json`
- Traces:
  - `docs/diagnostics/semantic_trace_run_20260315T053717Z.json`
  - `docs/diagnostics/semantic_trace_run_20260315T053718Z.json`
  - `docs/diagnostics/semantic_trace_run_20260315T053720Z.json`

## Resultado
- Contaminacao do input resolvida: `raw_input == transcript_text == search_query`.
- Terraform retornou `result_count=0` no `semantic_local` nesta rodada (investigar retrieval/ranking em etapa seguinte).

## Regressao basica
- Smoke A passou:
  - `/srv/liveui/artifacts/chat-e2e-initial-2026-03-15T053816954Z.png`
  - `/srv/liveui/artifacts/chat-e2e-final-2026-03-15T053816954Z.png`
  - `/srv/liveui/artifacts/chat-e2e-log-2026-03-15T053816954Z.json`
- Smoke B passou:
  - `/srv/liveui/artifacts/chat-skill-initial-2026-03-15T053825245Z.png`
  - `/srv/liveui/artifacts/chat-skill-final-2026-03-15T053825245Z.png`
  - `/srv/liveui/artifacts/chat-skill-log-2026-03-15T053825245Z.json`
