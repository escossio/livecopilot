# Handoff: Stage 13.3 Completion

Data: 2026-03-11
Status: concluido

## O que foi fechado
- Subetapa `13.3` concluida com integracao controlada de voz no fluxo realtime.
- A tentativa de voz agora respeita o estado da resposta (`final_stage_only`).

## Implementacao minima aplicada
- `app/services/voice_output.py`
  - novo `synthesize_voice_output_realtime_controlled(...)`.
  - gate de controle: se `response_stage != final` ou `should_wait_more=true`, suprime tentativa de voz com `voice_status=disabled` e `fallback_reason=voice_output_waiting_for_final_context`.
- `app/api/routes.py`
  - `/realtime/respond` passou a usar o gate controlado da voz.
  - `/status` passou a expor `voice_output_control_policy=final_stage_only`.

## Evidencias objetivas
1. `/status`:
   - `voice_output_control_policy=final_stage_only`.
2. `/realtime/respond` com resposta final + `voice_output_enabled=true`:
   - stage `final` e voice path continua opt-in (com fallback silencioso sem credencial).
3. `/realtime/respond` em contexto parcial (`response_stage=partial`, `should_wait_more=true`):
   - `voice_output.voice_status=disabled`;
   - `fallback_reason=voice_output_waiting_for_final_context`.

## Estado apos fechamento
- Etapa 13: `parcial` (em andamento)
- Subetapas:
  - `13.1` concluida
  - `13.2` concluida
  - `13.3` concluida
  - proxima: `13.4`

## Guardrails preservados
- Voz continua opt-in.
- Modo silencioso continua padrao.
- Fallback silencioso continua obrigatorio.
- Sem nova frente, sem ASR local, sem hardware novo, sem mudanca de schema/banco.
