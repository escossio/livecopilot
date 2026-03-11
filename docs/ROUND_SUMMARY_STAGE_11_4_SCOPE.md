# Round Summary - Stage 11.4 Scope

## Subetapa alvo
- 11.4 - Curadoria para persistencia externa

## Objetivo da 11.4
Garantir que conhecimento vindo de fonte externa so persista apos avaliacao de relevancia/confianca/curadoria.

## O que ja estava implementado
- Gate de acionamento externo complementar da 11.3 (`allow_external_complement` / `block_external_complement`) com trilha auditavel em `data/external_search_decisions.ndjson`.
- Politica de curadoria existente em `INGESTION_POLICY.md`.
- Fluxo de curadoria/promocao manual existente em `app/services/curated_sources.py` (`register-candidate`, `record-review-decision`, `promote-candidate`).

## O que faltava para considerar 11.4 concluida
- Ponte operacional explicita entre a decisao de acionamento externo (11.3) e a persistencia via curadoria.
- Trilha auditavel unica de ponta a ponta para o caminho:
  - decisao externa permitida -> cadastro curatorial -> decisao de revisao -> promocao persistente.

## Criterio de conclusao da 11.4
"Politica de curadoria aplicada de ponta a ponta para promocao persistente, sem ingestao externa automatica irrestrita."

## Avaliacao da lacuna
Lacuna pequena e objetiva: falta um wrapper minimo que force o gate da 11.3 antes do fluxo curatorial e deixe rastro auditavel consolidado por evento.

## Decisao desta rodada
Implementar minimo necessario:
- wrapper operacional para curadoria de persistencia externa condicionado ao `allow_external_complement`;
- log auditavel dedicado da cadeia curatorial;
- validacao controlada de ponta a ponta sem alterar schema/banco/rotas.
