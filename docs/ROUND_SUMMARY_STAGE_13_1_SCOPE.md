# Round Summary: Stage 13.1 Scope (Contrato opt-in de saida falada)

Data: 2026-03-11

## Objetivo da subetapa 13.1
Definir e registrar o contrato operacional minimo da saida falada realtime como recurso **opt-in**, sem mudar o comportamento padrao silencioso do Livecopilot.

## O que precisa existir no contrato operacional
- Definicao de escopo: voz como recurso opcional de suporte, nao missao principal.
- Contrato de ativacao por flag/configuracao explicita.
- Contrato de payload minimo para requisicao/resposta de voz.
- Comportamento obrigatorio de fallback silencioso em indisponibilidade de provider/credenciais.
- Guardrails explicitos de nao-regressao da UI silenciosa.

## Flags/payload minimos necessarios
- Flags/config:
  - `VOICE_OUTPUT_ENABLED` (default `false`)
  - `VOICE_OUTPUT_PROVIDER` (default `external`)
  - `VOICE_OUTPUT_MODEL` (default de provider)
- Payload minimo de requisicao (quando opt-in ativo):
  - `text` (conteudo a vocalizar)
  - `mode` (`interview|study|generic`, opcional)
  - `voice_output_enabled` (override opt-in por request, opcional)
- Payload minimo de resposta:
  - `voice_status` (`disabled|ready|fallback_silent|error`)
  - `voice_provider` (quando aplicavel)
  - `voice_enabled_effective` (bool)

## Guardrails obrigatorios
1. Voz e opt-in; default deve permanecer desligado.
2. Modo silencioso (UI textual/sugestoes) continua sendo o comportamento padrao.
3. Saida falada nao substitui a UI silenciosa como missao principal.
4. Falta de credencial/recurso nao pode quebrar fluxo normal (`/ingest`, `/realtime/respond`).
5. Sem dependencia de ASR local/hardware pesado para esta subetapa.
6. Preferencia por provider externo plugavel no caminho inicial.

## O que explicitamente NAO deve acontecer
- Nao ligar voz por padrao no produto.
- Nao introduzir requisito de ASR local robusto.
- Nao bloquear resposta silenciosa quando voz falhar.
- Nao abrir redesign de arquitetura ou frente paralela.

## Criterio de conclusao da 13.1
- Documento contratual da 13.1 criado e aprovado com flags/payload/guardrails.
- Estado oficial atualizado marcando `13.1` como concluida e etapa 13 como `em andamento`.
- Proxima subetapa oficial indicada de forma objetiva (`13.2`).

## Limites desta rodada
- Sem implementacao funcional de voz.
- Sem alteracao de codigo.
- Sem mudanca de schema/banco.
