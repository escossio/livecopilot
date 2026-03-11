# Stage 12.5 Guardrails (Operational)

Data: 2026-03-11

## Guardrails obrigatorios da Etapa 12
1. Etapa 12 e `audio/compreensao plugavel`, nao frente de ASR local obrigatorio.
2. Caminho operacional preferencial atual: API/modelo externo para compreensao de fala.
3. Captura local de audio e permitida como entrada leve, sem pipeline local pesado como requisito.
4. Nao assumir hardware dedicado inexistente para fechar esta etapa.
5. Qualquer necessidade de ASR local robusto deve ser tratada na Etapa 14, fora do escopo da Etapa 12 atual.

## Evidencias de alinhamento
- `docs/PROJECT_CONTRACT.md`
- `docs/PROJECT_STAGE_12_BREAKDOWN.md`
- `docs/project_status_state.json`

## Checklist de conformidade
- [x] `stage_12_focus.external_preferred = true`
- [x] `stage_12_focus.local_asr_required = false`
- [x] Etapa 12 no indice/estado descrita como plugavel
- [x] Painel simples e fiel ao estado real
