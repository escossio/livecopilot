# Round Summary: Stage 13.2 Scope (Adaptador TTS externo plugavel)

Data: 2026-03-11

## Objetivo da subetapa 13.2
Consolidar um adaptador TTS externo plugavel com ativacao opt-in e fallback silencioso obrigatorio, sem alterar o comportamento padrao silencioso do Livecopilot.

## O que ja esta pronto
- Contrato da 13.1 definido (`docs/STAGE_13_1_VOICE_OUTPUT_CONTRACT.md`).
- Etapa 13 ativa com foco em 13.2 no estado oficial.
- Pipeline realtime textual/silencioso consolidado e estavel.

## Lacuna restante identificada
- Ainda nao existe servico/adaptador TTS dedicado no codigo.
- Nao ha selecao/configuracao explicita de provider de saida falada no runtime.
- Nao ha trilha de retorno padronizada para `disabled|ready|fallback_silent|error` no fluxo realtime.

## Criterio de conclusao da 13.2
- Adaptador TTS externo plugavel implementado com configuracao explicita (provider/model/flag).
- Fallback silencioso obrigatorio em ausencia de credencial/recurso, sem quebrar `/realtime/respond`.
- Recurso permanece opt-in (default desligado).
- Validacao objetiva cobrindo: default silencioso, fallback sem credencial, operacao normal do fluxo silencioso.

## Escopo desta rodada
- Mudanca minima e reversivel.
- Sem transformar voz em padrao.
- Sem ASR local/hardware pesado.
- Sem mudanca de banco/schema.
- Sem redesign arquitetural.
