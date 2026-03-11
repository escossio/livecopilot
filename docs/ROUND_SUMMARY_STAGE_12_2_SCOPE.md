# Round Summary: Stage 12.2 Scope (Captura de audio local leve)

Data: 2026-03-11

## Objetivo da 12.2
Fechar a subetapa `12.2` garantindo captura de audio local **leve** como entrada operacional da camada plugavel, sem abrir frente de ASR local pesado.

## O que ja estava pronto
- `app/services/audio_capture.py` com contrato plugavel (`AudioCaptureBase`) e modos `mock`/`live`.
- Inicializacao e encerramento da captura no ciclo do app (`startup`/`shutdown`) via `app/main.py`.
- Exposicao objetiva do estado de captura em `/status` (`capture_mode` e `capture_live`) em `app/api/routes.py`.
- Guardrails ativos da Etapa 12.5 preservando `external_preferred=true` e `local_asr_required=false`.

## Lacuna restante identificada
Lacuna pequena e objetiva: faltava apenas consolidar evidencia comparavel de funcionamento da captura local leve no fluxo real do app e refletir o fechamento da 12.2 no estado oficial.

## Criterio de conclusao da 12.2
- Captura local funcional e integrada ao fluxo de entrada da camada de compreensao.
- Evidencia executavel dos modos `mock/live` e da exposicao no endpoint `/status`.
- Painel/estado oficial atualizado para marcar `12.2` como concluida e mover foco para a proxima subetapa aberta.

## Escopo desta rodada
- Sem redesign.
- Sem ASR local como requisito.
- Sem hardware novo.
- Sem alteracao de banco/schema.
- Mudancas pequenas, reversiveis e auditaveis.
