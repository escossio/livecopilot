# Handoff: Stage 15.1 Completion

Data: 2026-03-11
Status: concluida (contrato operacional definido)

## Objetivo da subetapa
Formalizar o contrato operacional da ingestao das literaturas no banco semantico antes de implementacao funcional da 15.2.

## Entrega realizada
- Documento criado: `docs/STAGE_15_1_INGESTION_OPERATIONAL_CONTRACT.md`.
- Contrato cobre:
  - objetivo e escopo de ingestao;
  - fontes, formatos e unidades (document/chunk);
  - metadados obrigatorios por documento e chunk;
  - regra de `document_id`/`chunk_id`;
  - versionamento/reingestao/deduplicacao;
  - estados oficiais (`discovered` -> `validated`/`failed`);
  - criterios de sucesso/falha e evidencias minimas;
  - relacao com runtime local-first;
  - fora de escopo da 15.1.

## Diagnostico consolidado do baseline
- Ja existe trilha local `raw -> parsed -> chunks -> manifest/state` operacional.
- Ja existe camada semantica minima (`documents/chunks/ingest_jobs`, `/semantic/ingest-min`, `/semantic/search`).
- Faltava contrato unificado para orientar 15.2-15.4 sem retrabalho.

## Decisao de estado
- 15.1 concluida no escopo documental.
- Proximo passo oficial: **15.2 pipeline minimo de ingestao**.
