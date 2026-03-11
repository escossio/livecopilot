# Round Summary: Stage 14.2 Scope (Adaptador ASR local plugavel)

Data: 2026-03-11

## Objetivo da subetapa 14.2
Implementar o adaptador minimo de ASR local plugavel no fluxo de transcricao, mantendo comportamento atual quando indisponivel e preservando fallback `external -> mock`.

## Ponto de encaixe tecnico
- Entrada principal: `app/services/transcription.py` (`transcribe_with_trace` / `transcribe_with_provider`).
- Contrato de contexto ja reaproveitavel: `app/services/context.py` (metadata por turno).
- Captura permanece inalterada: `app/services/audio_capture.py`.

## Lacuna minima identificada
- Hoje nao existe branch explicito para `provider=local`.
- `provider` diferente de `external|mock` cai direto em fallback `mock`.
- Falta modulo/funcoes dedicadas para ASR local plugavel.

## Escopo minimo de implementacao
1. Criar adaptador local minimo (`app/services/transcription_local.py`) sem dependencia de GPU.
2. Integrar `provider=local` em `transcription.py`.
3. Aplicar politica contratual:
   - local disponivel -> usa local;
   - local indisponivel -> tenta external;
   - external indisponivel/falha -> mock.
4. Nao remover nem alterar contrato do provider external.
5. Nao alterar fluxo principal do produto.

## Fora de escopo desta rodada
- Implementacao de stack ASR pesada.
- Mudanca de rotas/UX/arquitetura.
- Requisito de hardware novo.
- Telemetria extensa alem da trilha minima ja existente.

## Criterio de conclusao da 14.2
- Adaptador local plugavel existente e integrado.
- Fallback encadeado funcionando conforme contrato 14.1.
- `/ingest` e `/realtime/respond` seguem funcionando sem quebra.
- Evidencia objetiva de validacao para local/fallback registrada.
