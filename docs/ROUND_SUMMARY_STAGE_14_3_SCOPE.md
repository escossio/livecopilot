# Round Summary: Stage 14.3 Scope (Observabilidade operacional do roteamento de transcricao)

Data: 2026-03-11

## Objetivo da subetapa 14.3
Adicionar hardening minimo de observabilidade operacional ao roteamento local/external/mock, mantendo a fallback chain e sem iniciar otimizacoes avancadas de ASR.

## Escopo minimo
1. Enriquecer metadados retornados por `transcribe_with_trace` com:
   - `provider_selected`
   - `provider_used`
   - `fallback_used`
   - `fallback_reason`
   - `transcription_latency_ms`
2. Introduzir flags operacionais explicitas, sem ruptura:
   - `LOCAL_ASR_ENABLED`
   - `TRANSCRIPTION_PREFERENCE` (`local|external|auto`)
   - `LOCAL_ASR_TIMEOUT_MS`
3. Preservar caminho legado e compatibilidade de fallback chain.
4. Adicionar testes objetivos para validar caminho real e metadados.

## Fora de escopo
- tuning de modelo/local ASR
- VAD/chunking/streaming avancado
- refatoracao grande de pipeline
- requisitos de hardware novo

## Criterio de conclusao
- fallback chain intacta e auditavel por metadados;
- testes cobrindo local ok, local->external e local->external->mock;
- `/ingest` e `/realtime/respond` sem regressao.
