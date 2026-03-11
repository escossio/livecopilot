# Round Summary: Stage 14 Scope (ASR local robusto)

Data: 2026-03-11

## Identificacao objetiva da Etapa 14
- Nome: `ASR local robusto`.
- Descricao curta: consolidar uma pilha local de transcricao robusta para uso realtime continuo, com degradacao controlada e sem quebrar o fluxo principal silencioso.
- Status atual: `nao iniciada`.
- Dependencia oficial: `12` (Audio/compreensao plugavel) - concluida.

## O que ja existe hoje e pode ser reaproveitado
- Captura plugavel com baseline local:
  - `app/services/audio_capture.py` (`mock|live`).
- Camada de transcricao plugavel com runtime/fallback:
  - `app/services/transcription.py` (`provider`, `transcribe_with_trace`, fallback para `mock`).
- Integracao de contexto ja pronta para carregar metadados de reconhecimento:
  - `app/services/context.py` + trilha de metadata em turnos.
- Superficie realtime ja consolidada e estavel no contrato do produto:
  - `REALTIME_MVP.md`, `ARCHITECTURE.md`, `/ingest`, `/realtime/*`.
- Guardrails governantes ja ativos no contrato:
  - modo silencioso como comportamento padrao;
  - mudancas pequenas/reversiveis;
  - sem transformar voz falada em missao principal.

## O que ainda falta para a Etapa 14
- Definir contrato operacional explicito de ASR local robusto (SLOs, degradacao, limites de hardware, observabilidade minima).
- Definir provider local robusto alvo e modo de comutacao (`local` x `external` x `mock`) sem ambiguidade.
- Definir criterio de prontidao real para transcricao local continua (estabilidade em carga, latencia e taxa de fallback aceitavel).
- Definir plano de validacao objetiva para comprovar robustez local sem depender de hardware inexistente.

## Riscos e guardrails
Riscos principais:
1. Pressupor hardware local que nao existe e travar a etapa por premissa invalida.
2. Reabrir frente de voz de saida (Etapa 13) ou desancorar o modo silencioso.
3. Expandir escopo para redesign amplo de realtime antes de contrato minimo.
4. Acoplar a etapa a infraestrutura pesada sem criterio de aceite incremental.

Guardrails obrigatorios:
1. Nenhuma mudanca funcional nesta rodada de escopo.
2. Nao alterar o contrato de produto (copiloto silencioso continua principal).
3. Nao assumir hardware novo; quando necessario, registrar explicitamente premissas e fallback.
4. Manter fallback controlado para provider externo/mock ate prova objetiva de robustez local.
5. Avancar por subetapas com evidencia auditavel por checkpoint.

## Escopo minimo inicial da Etapa 14 (menor proximo passo valido)
Definir e aprovar o **contrato minimo da 14.1** sem implementacao funcional:
1. requisitos operacionais minimos do ASR local robusto (latencia alvo, taxa maxima de fallback, comportamento em indisponibilidade);
2. matriz de runtime suportada (`local`, `external`, `mock`) com precedencia clara;
3. estrategia de degradacao explicita para preservar fluxo realtime silencioso;
4. plano de validacao objetiva (smokes minimos e evidencias obrigatorias);
5. declaracao explicita de restricoes de hardware do ambiente atual.

## Proposta de decomposicao oficial da Etapa 14 (sem implementar)
- `14.1` Contrato operacional do ASR local robusto (SLOs, fallback, runtime matrix, limites de hardware).
- `14.2` Adaptador local robusto plugavel em `transcription.py` (sem trocar contrato de API).
- `14.3` Integracao controlada no realtime com telemetria minima de robustez (sem quebrar fluxo silencioso).
- `14.4` Validacao operacional minima e fechamento da etapa no escopo aprovado.

## Fora de escopo desta rodada
- Implementar provider local novo.
- Trocar pipeline de captura/transcricao em producao.
- Alterar rotas ou comportamento funcional do app.
- Abrir frentes paralelas fora da Etapa 14.
