# Handoff: Correcao de Prioridade do Roadmap apos Etapa 14

Data: 2026-03-11
Status: concluido

## Objetivo da correcao
Reposicionar a proxima etapa oficial para fechar a lacuna arquitetural critica: literaturas ainda nao ingeridas no banco semantico.

## Decisao formal
- Proxima etapa oficial: `Etapa 15 - Ingestao das literaturas no banco semantico`.
- Etapa de busca externa ampla removida da posicao imediata e movida para etapa posterior (`Etapa 16`).

## Escopo minimo seguro da Etapa 15
- `15.1` contrato operacional de ingestao.
- `15.2` pipeline minimo (chunking, embeddings, persistencia, metadados).
- `15.3` validacao objetiva da base (integridade/cobertura/recuperacao).
- `15.4` integracao local-first no runtime.

## Fora de escopo agora
- expansao ampla de busca externa;
- crawling/scraping irrestrito;
- redesign grande de arquitetura;
- tuning paralelo de ASR/voz.

## Baseline resultante para a proxima rodada
Roadmap realinhado com principio local-first: primeiro consolidar base interna semantica, depois considerar expansao externa com governanca.
