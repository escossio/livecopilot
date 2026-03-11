# Handoff: Stage 13 Scope

Data: 2026-03-11
Status: concluido (escopo definido, sem implementacao)

## O que foi feito
- Levantamento da Etapa 13 nos artefatos oficiais (indice, contrato, execution map, estado e handoff da etapa 12).
- Consolidacao do escopo minimo da Etapa 13 em `docs/ROUND_SUMMARY_STAGE_13_SCOPE.md`.

## Etapa 13 consolidada
- Nome: `Resposta falada realtime`.
- Estado: `nao iniciada`.
- Dependencias: `2` e `12` (satisfeitas).
- Natureza: capacidade futura, mantendo o produto com comportamento padrao silencioso.

## Menor proximo passo valido
- Executar **13.1**: definir contrato opt-in de saida falada (payload/flags/guardrails) sem alterar comportamento padrao atual.

## Decomposicao proposta (sem implementar)
- `13.1` Contrato de saida falada opt-in.
- `13.2` Adaptador TTS externo plugavel.
- `13.3` Integracao controlada no fluxo realtime.
- `13.4` Validacao minima e fechamento da etapa.

## Guardrails preservados
- Nenhuma mudanca funcional nesta rodada.
- Nenhuma frente paralela aberta.
- Sem ASR local como requisito.
- Alinhamento com `docs/PROJECT_CONTRACT.md` mantido.
