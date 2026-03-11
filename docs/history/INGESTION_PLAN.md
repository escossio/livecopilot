# Ingestion Plan (Próxima Rodada)

## Escopo desta rodada
Este plano prepara ingestão futura. **Nenhuma ingestão vetorial deve ser executada nesta rodada.**

## Arquivos que devem ser ingeridos (próxima rodada)
Prioridade 1:
- `ARCHITECTURE.md`
- `REALTIME_MVP.md`
- `STATUS.md` (com chunking por checkpoint/etapa)
- `docs/history/PROJECT_ORIGIN.md`
- `docs/history/ARCHITECTURE_DECISIONS.md`
- `docs/history/MILESTONES.md`
- `docs/history/DESIGN_EVOLUTION.md`
- `docs/history/KEY_INSIGHTS.md`

Prioridade 2:
- `CHANGELOG.md`
- `README.md` (seções de contratos/uso, não histórico repetitivo)

## Arquivos que NÃO devem ser ingeridos
- `chat_livecopilot.txt` (fonte bruta de reconstrução, alto ruído)
- backups `.bak*`
- logs temporários e dumps operacionais não curados
- artefatos intermediários redundantes sem contexto canônico

## Proposta de chunking
- Markdown estruturado por headings (`#`, `##`, `###`).
- Para `STATUS.md`: chunk por bloco de checkpoint (cada bloco como unidade semântica).
- Tamanho alvo: 800-1400 caracteres por chunk com sobreposição leve (80-120).
- Preservar blocos de decisão completos (não quebrar campo de decisão/impacto no meio).

## Proposta de metadados
Campos recomendados por chunk:
- `doc_type`: `architecture|history|status|mvp|changelog`
- `source_file`
- `section_title`
- `phase_hint` (ex.: `fase_inicial`, `fase_realtime_3_5`)
- `confidence_level`: `high|medium` (alto para decisão explícita; médio para inferência)
- `decision_kind`: `decision|hypothesis|abandoned|checkpoint`
- `last_updated_hint`

## Ordem recomendada de ingestão
1. Documentos canônicos de história (`docs/history/*`).
2. `ARCHITECTURE.md` e `REALTIME_MVP.md`.
3. `STATUS.md` (em blocos).
4. `CHANGELOG.md` e `README.md` (seleções úteis).

## Riscos de ruído semântico
- Duplicar conteúdo de `STATUS.md` com `docs/history/*` sem deduplicação.
- Canonizar hipóteses antigas como se fossem decisões ativas.
- Over-index de logs técnicos operacionais sem valor de domínio.

## Critérios de qualidade pré-ingestão
- Decisão vs hipótese vs ideia abandonada explicitamente marcadas.
- Sem trechos de chat bruto copiados.
- Sem datas inventadas: usar fases quando não houver data explícita.
- Consistência entre arquitetura, milestones e evolução.
- Revisão de redundância antes da ingestão.

## Regra de canonização
- Priorizar chunks de **decisão consolidada** para recuperação principal.
- Manter **hipóteses históricas** como contexto secundário (não normativo).
- Indexar **ideias abandonadas** apenas com marcador de bloqueio para evitar regressão de decisão.
