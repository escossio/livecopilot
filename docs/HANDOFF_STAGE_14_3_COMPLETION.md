# Handoff: Stage 14.3 Completion

Data: 2026-03-11
Status: concluido

## O que foi fechado
- Subetapa `14.3` concluida com hardening minimo de observabilidade operacional do roteamento de transcricao (`local|external|mock`).
- Sem otimização avançada de ASR e sem refatoração ampla.

## Before -> After (escopo real)
- Before:
  - trilha de provider limitada a `configured_provider/effective_provider/fallback_used`;
  - sem `fallback_reason` explicito e sem latencia por transcricao;
  - sem flags operacionais explicitas para preferencia/timeout local.
- After:
  - metadados operacionais claros em `transcribe_with_trace`:
    - `provider_selected`
    - `provider_used`
    - `fallback_used`
    - `fallback_reason`
    - `transcription_latency_ms`
  - flags operacionais adicionadas e compatíveis:
    - `LOCAL_ASR_ENABLED`
    - `TRANSCRIPTION_PREFERENCE` (`local|external|auto`)
    - `LOCAL_ASR_TIMEOUT_MS`
  - fallback chain preservada e auditável.

## Implementacao minima aplicada
- `app/services/transcription.py`:
  - seleção de provider por preferencia operacional;
  - observabilidade de fallback e latencia;
  - manutenção de chaves legadas para compatibilidade.
- `app/services/transcription_local.py`:
  - runtime local com suporte a timeout configurável.
- `app/services/pipeline.py`:
  - metadados de transcricao no contexto com `provider_selected/used`, `fallback_reason`, `transcription_latency_ms`.
- `app/api/routes.py`:
  - `/status` expõe preferencia/seleção e parâmetros operacionais locais.
- `app/core/config.py` e `.env.example`:
  - novas variáveis de operação da trilha local.

## Evidencias objetivas
1. Testes unitários novos (`tests/test_transcription_routing.py`):
   - local ok -> `provider_used=local`;
   - local falha -> `provider_used=external`, `fallback_used=true`;
   - local+external falham -> `provider_used=mock`, `fallback_used=true`.
2. Integração (`TestClient`):
   - `/status` `200` com campos de operação da transcrição;
   - `/ingest` `200` e transcript com metadados operacionais;
   - `/realtime/respond` `200` sem regressão.

## Estado apos fechamento
- Etapa 14: `parcial` com `14.1`, `14.2`, `14.3` concluidas.
- Proximo passo oficial sugerido: `14.4` (validacao operacional minima e fechamento da etapa).

## Guardrails preservados
- Sem exigência de GPU/hardware novo.
- Sem ruptura no fluxo principal `/ingest` e `/realtime/respond`.
- Sem frente paralela.
- Mudança pequena e reversível.
