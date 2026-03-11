# Project Stage 12 Breakdown: Audio/Compreensao Plugavel

Data de consolidacao: 2026-03-11

Escopo: detalhamento operacional da **Etapa 12** da sequencia oficial, sem abrir frente de ASR local pesado.

Definicao oficial da etapa:
- captura de audio local
- camada de integracao plugavel
- preferencia operacional atual por API/modelo externo para compreensao de fala
- transformacao de audio em contexto reconhecido para o restante do pipeline

Nao e objetivo da etapa atual:
- transcricao local obrigatoria
- Whisper local como requisito central
- pipeline local pesado de ASR

## Subetapas oficiais

| # | Subetapa | Descricao curta | Status | Dependencia | Criterio de conclusao |
|---|---|---|---|---|---|
| 12.1 | Contrato plugavel de audio/compreensao | Formalizar que a camada e plugavel e que o caminho preferencial atual e externo. | concluida | Etapa 2 | Contrato/estado/documentacao alinhados sem ambiguidade de ASR local obrigatorio. |
| 12.2 | Captura de audio local (leve) | Manter captura local como entrada do modulo, sem exigir processamento ASR pesado na maquina. | concluida | 12.1 | Captura local funcional e integrada ao fluxo de entrada da camada de compreensao. |
| 12.3 | Integracao com API/modelo externo | Usar integracao externa como caminho operacional preferencial para compreensao de fala. | concluida | 12.1, 12.2 | Pipeline de compreensao externa operando com fallback conservador quando indisponivel. |
| 12.4 | Audio -> contexto reconhecido | Entregar saida reconhecida de fala em formato util para contexto/sugestoes do pipeline principal. | concluida | 12.3 | Contexto reconhecido consumido pelo fluxo realtime sem quebrar a missao de copiloto silencioso. |
| 12.5 | Operacao e guardrails da etapa | Fechar guardrails: sem escopo de ASR local pesado e sem assumir hardware nao disponivel. | concluida | 12.4 | Regras de escopo e execucao da etapa mantidas no painel/contrato/docs operacionais. |

## Regra de execucao da Etapa 12
- Seguir ordem `12.1 -> 12.2 -> 12.3 -> 12.4 -> 12.5`.
- Nao abrir frente paralela de ASR local pesado dentro desta etapa.
- Se houver necessidade de ASR local robusto, tratar na Etapa 14 (se e quando priorizada).

## Estado atual da Etapa 12
- `12.2` encerrada com evidencia objetiva de captura local leve integrada ao app (modos `mock/live`, startup/shutdown e exposicao em `/status`).
- `12.3` encerrada com adaptador de compreensao externa no pipeline (`TRANSCRIPTION_PROVIDER=external`) e fallback conservador para `mock` quando API externa indisponivel.
- `12.4` encerrada com metadados auditaveis de contexto reconhecido no `transcript` (`context_source`, provider configurado/efetivo e fallback), consumidos no fluxo realtime.
- `12.5` encerrada com guardrails consolidados em contrato + breakdown + painel + doc operacional.
- Etapa 12 esta **concluida** no escopo atual da arquitetura plugavel.

## Evidencias base desta decomposicao
- `docs/PROJECT_CONTRACT.md`
- `docs/PROJECT_STAGE_INDEX.md`
- `docs/PROJECT_EXECUTION_MAP.md`
- `REALTIME_MVP.md`
- `ARCHITECTURE.md`
- `STATUS.md`
- `docs/project_status_state.json`
