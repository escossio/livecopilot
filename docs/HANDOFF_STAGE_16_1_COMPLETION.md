# Handoff: Stage 16.1 Completion

Data: 2026-03-11
Status: concluida (contrato operacional definido)

## Objetivo da subetapa
Definir o contrato operacional da busca externa governada sem implementar adaptador/crawler e sem quebrar o principio local-first.

## Entrega realizada
- Documento criado: `docs/STAGE_16_1_EXTERNAL_SEARCH_CONTRACT.md`.
- Contrato cobre:
  - precedencia obrigatoria de `semantic_local`;
  - criterios minimos de disparo externo por insuficiencia local;
  - provedores permitidos (conceitual);
  - limites de resultados e politica de dominios confiaveis;
  - normalizacao minima de resultados;
  - separacao de contexto temporario vs ingestao permanente;
  - governanca de qualidade minima;
  - estados operacionais e evidencia minima de validacao.

## Fora de escopo mantido
- crawler amplo;
- scraping massivo;
- ingestao automatica da web;
- redesign de runtime;
- mudanca na arquitetura da memoria semantica.

## Riscos/dividas explicitas
- dependencia de credencial OpenAI em parte da camada semantica atual;
- fallback lexical segue como degradacao segura;
- Etapa 16 ainda sem adaptador implementado (somente contrato).

## Decisao de estado
- **16.1 concluida** no escopo documental.
- Etapa 16 passa a **parcial/em andamento** sem alteracao funcional do runtime nesta rodada.
