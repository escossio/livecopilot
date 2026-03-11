# Round Summary: Stage 13.3 Scope (Integracao controlada no fluxo realtime)

Data: 2026-03-11

## Objetivo da subetapa 13.3
Fechar a integracao controlada da saida falada no fluxo `/realtime/respond`, garantindo que a tentativa de voz aconteca apenas em condicoes apropriadas do realtime, sem alterar o modo padrao silencioso.

## O que ja esta pronto
- `13.1` contrato opt-in e guardrails definidos (`docs/STAGE_13_1_VOICE_OUTPUT_CONTRACT.md`).
- `13.2` adaptador externo plugavel implementado (`app/services/voice_output.py`).
- Fallback silencioso obrigatorio ativo quando voz indisponivel.

## Lacuna minima identificada
- O endpoint `/realtime/respond` ainda nao aplica um gate de controle baseado no estado da resposta realtime (ex.: `response_stage=partial`).
- Falta motivo explicito no payload quando voz e suprimida por controle de etapa do realtime.

## Criterio de conclusao da 13.3
- Gate controlado ativo no fluxo realtime para evitar tentativa de voz em resposta parcial/aguardando mais contexto.
- Payload de `voice_output` continua auditavel, com motivo explicito de supressao quando aplicavel.
- Modo silencioso permanece padrao e fluxo textual segue sem quebra.
- Evidencia objetiva de validacao: caso final habilitado e caso parcial com supressao controlada.

## Escopo desta rodada
- Mudanca minima e reversivel em servico/rota ja existentes.
- Sem nova frente, sem ASR local, sem hardware novo, sem redesign, sem mudanca de banco/schema.
