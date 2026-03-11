# Handoff: Stage 13.2 Completion

Data: 2026-03-11
Status: concluido

## O que foi fechado
- Subetapa `13.2` concluida com adaptador TTS externo plugavel implementado.
- Recurso de voz manteve-se opt-in; modo silencioso permanece default.

## Implementacao minima aplicada
- Novo servico: `app/services/voice_output.py`
  - runtime/config do voice output (`enabled_default`, `provider`, `model`)
  - adaptador externo com provider `external`
  - fallback silencioso obrigatorio (`disabled|fallback_silent`) em ausencia de recurso/credencial
- Integracao leve em `app/api/routes.py`
  - `/status` expõe runtime de voice output
  - `/realtime/respond` retorna bloco `voice_output` sem quebrar resposta textual
- Configuracoes adicionadas:
  - `VOICE_OUTPUT_ENABLED` (default `false`)
  - `VOICE_OUTPUT_PROVIDER` (default `external`)
  - `VOICE_OUTPUT_MODEL` (default `gpt-4o-mini-tts`)

## Evidencias objetivas
1. default (`VOICE_OUTPUT_ENABLED=false`):
   - `/realtime/respond` retorna `voice_status=disabled`
   - resposta silenciosa textual segue normal
2. opt-in por request (`voice_output_enabled=true`) sem `OPENAI_API_KEY`:
   - `/realtime/respond` retorna `voice_status=fallback_silent`
   - resposta silenciosa textual segue normal
3. `/status`:
   - expõe `voice_output_enabled_default=false`, `voice_output_opt_in=true`, `silent_mode_default=true`

## Estado apos fechamento
- Etapa 13: `parcial` (em andamento)
- Subetapas:
  - `13.1` concluida
  - `13.2` concluida
  - proxima: `13.3` (integracao controlada no fluxo realtime)

## Guardrails preservados
- Sem mudar o modo padrao silencioso
- Sem frente de ASR local
- Sem dependencia de hardware local pesado
- Sem mudanca de schema/banco
