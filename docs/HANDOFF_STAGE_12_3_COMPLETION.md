# Handoff: Stage 12.3 Completion

Data: 2026-03-11
Status: concluido

## O que foi fechado
- Subetapa `12.3` (Integracao com API/modelo externo) encerrada com mudanca minima.
- O pipeline de ingestao passou a usar caminho de compreensao externa como preferencial quando `TRANSCRIPTION_PROVIDER=external`.
- Fallback conservador para `mock` mantido quando a API/modelo externo estiver indisponivel.

## Implementacao minima aplicada
- `app/services/transcription.py`
  - novo runtime de transcricao (`get_transcription_runtime`)
  - novo caminho externo (`_transcribe_external`) usando `OPENAI_API_KEY`
  - seletor plugavel (`transcribe_with_provider`) com fallback conservador para `transcribe_mock`
- `app/services/pipeline.py`
  - `process_ingest` passou de `transcribe_mock` para `transcribe_with_provider`
- `app/api/routes.py`
  - `/status` expõe estado da transcricao (`provider`, preferencia/ disponibilidade externa, modelo)
- `.env.example`
  - flags explicitas: `TRANSCRIPTION_PROVIDER`, `TRANSCRIPTION_EXTERNAL_MODEL`

## Evidencias objetivas
1. `TRANSCRIPTION_PROVIDER=mock`:
   - runtime indica provider `mock`
   - transcricao retorna fluxo mock
2. `TRANSCRIPTION_PROVIDER=external` sem `OPENAI_API_KEY`:
   - runtime indica preferencia externa
   - evento `transcription_external_fallback`
   - fluxo segue com `transcribe_mock` sem quebrar ingestao
3. `TRANSCRIPTION_PROVIDER=external` com stub externo:
   - `process_ingest` consome saida externa e grava no contexto (`snapshot.transcript`)
4. `/status`:
   - retorna campos de estado de transcricao para auditoria operacional.

## Estado apos fechamento
- `12.1`: concluida
- `12.2`: concluida
- `12.3`: concluida
- `12.4`: parcial (novo foco)
- `12.5`: concluida
- Etapa 12 permanece `parcial` no escopo atual.

## Guardrails preservados
- `external_preferred=true`
- `local_asr_required=false`
- sem requisito de ASR local/hardware novo
- sem mudanca de banco/schema
