# Handoff - Diagnostico Profundo da Pipeline Semantica

## Objetivo
Instrumentar a pipeline semantica e identificar onde o desalinhamento ocorre com evidencias reais.

## Instrumentacao aplicada
- `app/api/routes.py` escreve traces JSON para perguntas canario em `docs/diagnostics/semantic_trace_run_<timestamp>.json`.
- Ownership de `docs/diagnostics` ajustado para `postgres:postgres` para permitir gravacao pelo runtime.

## Perguntas canario
- Para que serve o arquivo de state no Terraform?
- Qual a diferenca entre terraform plan e terraform apply?
- Qual a diferenca entre Pod e Service no Kubernetes?

## Evidencias
- `docs/diagnostics/semantic_canary_run_20260315T052910Z.json`
- `docs/diagnostics/semantic_trace_run_20260315T052923Z.json`
- `docs/diagnostics/semantic_trace_run_20260315T052926Z.json`
- `docs/diagnostics/semantic_trace_run_20260315T052930Z.json`
- `docs/diagnostics/semantic_pipeline_map.md`
- `docs/diagnostics/semantic_failure_analysis_20260315T052910Z.md`

## Leitura tecnica (resumo)
- A camada de transcricao (`transcribe_with_trace`) gerou `transcript_text` diferente do `raw_input`, com texto de resposta pronta.
- A busca semantica recuperou documentos coerentes, mas a query usada foi o texto gerado pela transcricao, nao a pergunta original.
- Conclusao: falha primaria na etapa de interpretacao/transcricao do input (texto sendo “respondido” antes do retrieval).

## Proximo passo sugerido
- Diagnosticar por que o provedor de transcricao externo esta devolvendo resposta em vez de normalizar texto.
- Confirmar se `TRANSCRIPTION_PROVIDER`/`TRANSCRIPTION_PREFERENCE` deve ser `mock` para input textual.
