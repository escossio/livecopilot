# Round Summary: Stage 13 Scope (Resposta falada realtime)

Data: 2026-03-11

## Identificacao objetiva da Etapa 13
- Nome: `Resposta falada realtime`
- Descricao curta: capacidade futura de saida de voz em tempo real.
- Status atual: `nao iniciada`.
- Dependencias: `2` (Nucleo realtime silencioso) e `12` (Audio/compreensao plugavel) - ambas concluidas.

## O que ja esta pronto
- Pipeline realtime de entrada/contexto/sugestao funcional (`/ingest`, `/realtime/respond`).
- Camada de audio/compreensao plugavel concluida na Etapa 12, com trilha auditavel de contexto reconhecido.
- Guardrails de escopo ativos no contrato: voz nao e missao principal e nao pode desancorar o copiloto silencioso.

## O que ainda falta
- Contrato minimo de saida falada (quando, como e com qual payload), sem alterar comportamento padrao do produto.
- Definicao do modo opt-in/feature-flag para voz de saida.
- Delimitacao de fallback e telemetria minima da saida falada.

## Escopo minimo inicial da Etapa 13 (proximo passo valido)
Definir e aprovar o contrato operacional minimo de saida falada **sem implementacao funcional nesta rodada**:
1. interface de saida falada opcional (nao padrao);
2. provider externo plugavel como caminho preferencial inicial;
3. fallback silencioso para manter o comportamento atual quando indisponivel;
4. criterio de aceite/validacao objetiva para primeira subetapa da Etapa 13.

## Proposta de decomposicao oficial (sem implementacao)
- `13.1` Contrato de saida falada opt-in (API/payload/flags/guardrails).
- `13.2` Adaptador TTS externo plugavel (provider + fallback conservador).
- `13.3` Integracao controlada no fluxo realtime (sem mudar o modo padrao silencioso).
- `13.4` Validacao operacional minima e encerramento da etapa no escopo definido.

## Limites desta rodada
- Nenhuma mudanca funcional.
- Nenhuma alteracao de codigo.
- Nenhuma frente paralela.
- Sem ASR local robusto.
