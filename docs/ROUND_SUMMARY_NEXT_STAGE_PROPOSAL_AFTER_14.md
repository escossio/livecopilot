# Round Summary: Proposta de Proxima Etapa apos fechamento da 14

Data: 2026-03-11
Status: proposta corrigida e oficializada (nao iniciada)

## Proxima etapa proposta do roadmap
- Nome: `Etapa 15 - Ingestao das literaturas no banco semantico`.

## Objetivo central
Consolidar a base interna de conhecimento em modo local-first, transformando literaturas em base semantica consultavel com trilha auditavel.

## Escopo minimo seguro (proposta)
1. `15.1` Contrato operacional de ingestao das literaturas.
2. `15.2` Pipeline minimo de ingestao (chunking + embeddings + persistencia + metadados).
3. `15.3` Validacao objetiva da base (integridade, cobertura minima e recuperacao local).
4. `15.4` Integracao local-first no runtime (consulta prioritaria a base consolidada).

## Definicao objetiva da nova Etapa 15
- Transformar literaturas disponiveis em base consultavel local-first.
- Garantir, no minimo: chunking reproducivel, embeddings consistentes, persistencia auditavel, metadados de origem e validacao de recuperacao.
- Preservar a arquitetura atual sem redesign amplo.

## O que nao deve entrar ainda
- expansao ampla de busca externa;
- crawling/scraping irrestrito;
- redesign grande de arquitetura;
- tuning paralelo de ASR/voz.

## Risco de deriva a evitar
Abrir busca externa ampla antes de consolidar base interna, enfraquecendo o principio local-first e a auditabilidade do conhecimento.

## Reordenacao formal
- A antiga proposta de `Etapa 15 - Expansao ampla de busca externa` foi movida para etapa posterior.
- Busca externa com governanca permanece no roadmap, mas nao e a proxima prioridade imediata.
