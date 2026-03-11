# Project Stage Index: Livecopilot

Data de consolidacao: 2026-03-11

Indice oficial de etapas/frentes do projeto, consolidado a partir de `STATUS.md`, `docs/PROJECT_CONTRACT.md`, `docs/PROJECT_EXECUTION_MAP.md`, `docs/history/*`, `docs/continuity/*`, `README.md`, `REALTIME_MVP.md`, `ARCHITECTURE.md` e handoffs/round summaries recentes.

## Sequencia oficial numerada

| # | Etapa | Descricao curta | Status | Dependencias | Evidencias principais |
|---|---|---|---|---|---|
| 1 | Fundacao MVP local | Base executavel FastAPI + UI local + fluxo textual/mock inicial. | concluida | - | `docs/history/MILESTONES.md` (M1), `README.md` |
| 2 | Nucleo realtime silencioso | Contexto de conversa + sugestoes curtas em tela como fluxo principal do produto. | concluida | 1 | `docs/PROJECT_CONTRACT.md`, `REALTIME_MVP.md`, `ARCHITECTURE.md` |
| 3 | Knowledge core local | Ingestao documental, chunking, busca local e explainability de recuperacao. | concluida | 1 | `docs/history/MILESTONES.md` (M4/M5), `ARCHITECTURE.md`, `README.md` |
| 4 | Question bank separado | Trilha separada de perguntas/avaliacao com coverage/action plan sem contaminar knowledge. | concluida | 3 | `docs/history/ARCHITECTURE_DECISIONS.md` (AD-002), `README.md`, `ARCHITECTURE.md` |
| 5 | Gap learning operacional | Deteccao de lacunas, priorizacao e rotina de ingestao acionada por gaps. | concluida | 4 | `docs/history/ARCHITECTURE_DECISIONS.md` (AD-003), `docs/ROUND_SUMMARY_KNOWLEDGE_GAPS_INGESTION.md` |
| 6 | Curadoria de fontes | Camada de staging/revisao/promocao manual para fontes externas controladas. | parcial | 3, 4 | `README.md` (camada curada), `INGESTION_POLICY.md` |
| 7 | Continuidade operacional | Persistencia de rodadas/fatos/memoria (`project_runs`, `project_facts`, `project_memory_chunks`) e fluxo de closeout. | concluida | 2, 3, 4 | `docs/continuity/CONTINUITY_MVP.md`, `docs/PROJECT_EXECUTION_MAP.md` |
| 8 | Project Brain + avaliacao de ranking | Query operacional (structured/semantic/hybrid), bateria offline e calibracao conservadora com evidencia. | em andamento | 7 | `docs/continuity/PROJECT_BRAIN_QUERY.md`, `docs/continuity/PROJECT_BRAIN_RANKING_OFFLINE_EVAL.md`, `docs/ROUND_SUMMARY_PROJECT_BRAIN_RANKING_RECALIBRATION_CONSERVATIVE.md` |
| 9 | Auth PostgreSQL de aplicacao | Acesso explicito via role dedicada + `DATABASE_URL` + TCP/SCRAM, sem peer no fluxo principal. | concluida | 7 | `docs/ROUND_SUMMARY_POSTGRES_APP_AUTH.md`, `docs/HANDOFF_POSTGRES_APP_AUTH.md` |
| 10 | Bootstrap/contexto inicial | Abertura de rodada com action brief compacto e orientado a acao. | concluida | 7, 8, 9 | `docs/ROUND_SUMMARY_BOOTSTRAP_CONTEXT_REFINEMENT.md`, `docs/continuity/NEW_CHAT_CONTEXT.md` |
| 11 | Busca externa controlada | Uso complementar de fonte externa sob politica de insuficiencia/curadoria. | parcial | 3, 4, 6 | `docs/PROJECT_CONTRACT.md`, `docs/PROJECT_EXECUTION_MAP.md` |
| 12 | Audio/compreensao plugavel | Captura de audio local + integracao plugavel, com preferencia operacional atual por API/modelo externo para compreensao de fala e geracao de contexto reconhecido. | concluida | 2 | `docs/PROJECT_EXECUTION_MAP.md`, `docs/PROJECT_CONTRACT.md`, `ARCHITECTURE.md`, `REALTIME_MVP.md`, `docs/PROJECT_STAGE_12_BREAKDOWN.md` |
| 13 | Resposta falada realtime | Saida de voz em tempo real como capacidade futura (opt-in). | concluida | 2, 12 | `docs/PROJECT_EXECUTION_MAP.md`, `docs/PROJECT_CONTRACT.md`, `docs/STAGE_13_1_VOICE_OUTPUT_CONTRACT.md`, `docs/HANDOFF_STAGE_13_2_COMPLETION.md`, `docs/HANDOFF_STAGE_13_3_COMPLETION.md`, `docs/HANDOFF_STAGE_13_4_COMPLETION.md` |
| 14 | ASR local robusto | Pilha local robusta de transcricao em hardware dedicado. | concluida | 12 | `docs/PROJECT_EXECUTION_MAP.md`, `docs/PROJECT_CONTRACT.md`, `docs/STAGE_14_1_ASR_LOCAL_CONTRACT.md`, `docs/HANDOFF_STAGE_14_2_COMPLETION.md`, `docs/HANDOFF_STAGE_14_3_COMPLETION.md`, `docs/HANDOFF_STAGE_14_4_COMPLETION.md` |
| 15 | Ingestao das literaturas no banco semantico | Consolidar base interna local-first com chunking, embeddings, persistencia e validacao de recuperacao. | nao iniciada | 3, 5, 6 | `README.md`, `INGESTION_POLICY.md`, `docs/ROUND_SUMMARY_NEXT_STAGE_PROPOSAL_AFTER_14.md` |
| 16 | Busca externa com governanca ampliada | Expansao externa posterior e controlada, complementar ao core local consolidado. | fora do escopo atual | 11, 15 | `docs/PROJECT_EXECUTION_MAP.md`, `docs/PROJECT_CONTRACT.md`, `docs/ROUND_SUMMARY_NEXT_STAGE_PROPOSAL_AFTER_14.md` |

## Etapa atual oficial
- **Etapa 15 - Ingestao das literaturas no banco semantico** (`nao iniciada`).
- Motivo: após o fechamento da etapa 14, a lacuna arquitetural critica e consolidar a base interna no banco semantico antes de expandir busca externa.

## Proxima Etapa Proposta
- **Etapa 16 - Busca externa com governanca ampliada** (`fora do escopo atual`, proposta para etapa posterior).
- Objetivo central proposto: ampliar busca externa de forma controlada e auditavel somente apos consolidacao da base interna local-first na etapa 15.
- Referencia da proposta: `docs/ROUND_SUMMARY_NEXT_STAGE_PROPOSAL_AFTER_14.md`.
