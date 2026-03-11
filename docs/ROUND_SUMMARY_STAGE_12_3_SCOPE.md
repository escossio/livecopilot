# Round Summary: Stage 12.3 Scope (Integracao com API/modelo externo)

Data: 2026-03-11

## Objetivo da 12.3
Fechar a subetapa `12.3` consolidando a integracao com API/modelo externo como caminho operacional preferencial de compreensao, mantendo a camada plugavel e sem exigir ASR local.

## O que ja estava pronto
- Etapa 12 formulada corretamente como `audio/compreensao plugavel`.
- Guardrails ativos: `external_preferred=true` e `local_asr_required=false`.
- Captura local leve (12.2) concluida e integrada ao ciclo do app.

## Lacuna restante identificada
- `app/services/transcription.py` ainda possui apenas `transcribe_mock()`.
- `app/services/pipeline.py` usa somente caminho mock, sem adaptador explicito de integracao externa com fallback conservador.

## Criterio de conclusao da 12.3
- Existir caminho de compreensao/transcricao externa plugavel no `transcription.py`.
- O pipeline principal usar esse caminho como preferencial quando configurado.
- Em indisponibilidade de API externa, manter fallback conservador para mock (sem quebra de fluxo).
- Evidencia objetiva de comportamento (preferencia externa configuravel + fallback) e atualizacao do estado oficial/painel.

## Escopo desta rodada
- Mudanca minima e reversivel.
- Sem frente de ASR local.
- Sem hardware novo.
- Sem mudanca em banco/schema.
- Sem redesign de arquitetura.
