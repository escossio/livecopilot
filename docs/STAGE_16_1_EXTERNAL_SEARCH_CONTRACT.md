# Stage 16.1: Contrato Operacional da Busca Externa com Governanca

Data: 2026-03-11
Status: definido (sem implementacao funcional nesta rodada)

## 1) Objetivo da 16.1
Definir um contrato operacional claro, auditavel e implementavel para busca externa complementar, preservando o principio local-first ja consolidado na etapa 15.

Resultado esperado da 16.1:
- regra objetiva de quando busca externa pode ser acionada;
- precedencia obrigatoria do `semantic_local`;
- limites, governanca e normalizacao de resultados externos;
- separacao explicita entre contexto temporario e ingestao permanente.

## 2) Principio operacional mandatorio
A busca externa e **complementar** e so pode rodar apos tentativa local.

Ordem obrigatoria de decisao no runtime:
1. `semantic_local` (obrigatorio, primeiro)
2. fallback local lexical (quando aplicavel)
3. avaliacao de insuficiencia local
4. busca externa governada (se criterios forem atendidos)

Regra de bloqueio:
- se `semantic_local` retornar contexto suficiente e coerente, **nao** acionar busca externa.

## 3) Quando a busca externa pode ser acionada
A busca externa so pode ser acionada quando todos os criterios abaixo forem verdadeiros:
1. consulta local executada e registrada (`semantic_local` tentado);
2. contexto local considerado insuficiente por criterio objetivo;
3. pergunta com sinal tecnico/objetivo claro;
4. rota em modo que aceite complemento externo (governado);
5. sem bloqueio de politica de dominio/qualidade.

## 4) Criterios minimos de insuficiencia local
Disparo externo permitido apenas se houver evidencia minima de insuficiencia, por exemplo:
- `result_count_local = 0`; ou
- resultados locais abaixo de piso de relevancia/qualidade; ou
- contexto local sem cobertura verificavel da pergunta.

Contrato de auditoria:
- runtime deve registrar `local_insufficiency_reason` curto e objetivo.

## 5) Provedores permitidos (conceitual)
Sem implementacao nesta etapa. Tipos permitidos para fases seguintes:
- API de busca web com filtros de dominio;
- indice curado de fontes tecnicas confiaveis;
- buscador documental de documentacao oficial.

Vedacao nesta etapa:
- qualquer conector/crawler/scraper em execucao.

## 6) Limites de resultados externos
Limites operacionais minimos (contrato):
- maximo de candidatos brutos por consulta externa: `<= 10`;
- maximo de itens normalizados para consumo de contexto: `<= 3`;
- timeout por consulta externa: definido por configuracao e com fallback seguro;
- sem fan-out agressivo entre multiplos provedores na mesma chamada por padrao.

## 7) Politica de dominios confiaveis
Modelo de governanca por lista permitida (allowlist):
- Tier 1 (preferencial): documentacao oficial de tecnologias/plataformas relevantes;
- Tier 2 (condicional): fontes tecnicas reconhecidas e rastreaveis;
- Tier 3 (bloqueado por padrao): agregadores sem rastreabilidade, conteudo anonimo sem curadoria.

Regras:
- dominio fora da allowlist => bloqueio por padrao;
- excecao so por decisao explicita de governanca (fora da 16.1).

## 8) Normalizacao de resultados externos
Formato alvo minimo por item normalizado:
- `provider`
- `domain`
- `url`
- `title`
- `snippet`
- `published_at` (quando disponivel)
- `retrieved_at`
- `trust_tier`
- `normalization_status`

Regras minimas:
- remover duplicatas por URL canonica;
- truncar snippet para tamanho seguro de contexto;
- manter rastreabilidade de origem para auditoria.

## 9) Contexto temporario vs ingestao permanente
Regra central:
- resultado externo entra primeiro como **contexto temporario** (ephemeral).
- ingestao permanente na memoria semantica **nao e automatica**.

Ingestao permanente so pode ocorrer em etapa posterior, mediante:
- curadoria/revisao;
- politica de qualidade;
- trilha de aprovacao explicita.

## 10) Governanca de qualidade minima
Antes de usar no contexto final, cada item externo deve passar por gates minimos:
- dominio permitido;
- snippet/utilidade minima;
- ausencia de sinais claros de baixa confiabilidade;
- rastreabilidade completa (`provider/domain/url`).

Se falhar em qualquer gate:
- item e descartado sem quebrar fluxo;
- registrar motivo curto de rejeicao.

## 11) Estados operacionais da busca externa
Estados oficiais da trilha externa:
1. `not_applicable` (nao elegivel)
2. `local_sufficient` (local resolveu)
3. `local_insufficient` (insuficiencia detectada)
4. `external_eligible` (apto a consulta externa)
5. `provider_queried` (consulta enviada)
6. `provider_blocked` (bloqueio de politica)
7. `normalized` (resultado normalizado)
8. `quality_rejected` (descartado por gate de qualidade)
9. `context_attached` (contexto temporario aceito)
10. `failed` (erro operacional)

## 12) Evidencia minima de validacao (16.1)
Para considerar a 16.1 cumprida no escopo documental:
1. contrato formal publicado com regras de precedencia local-first;
2. criterios objetivos de disparo externo definidos;
3. limites e governanca de dominio definidos;
4. separacao temporario vs permanente definida;
5. estados operacionais e trilha de auditoria definidos.

## 13) Fora de escopo explicito da 16.1
- crawler amplo;
- scraping massivo;
- ingestao automatica da web;
- redesign do runtime;
- mudanca da arquitetura da memoria semantica.

## 14) Proximo passo oficial apos 16.1
- **16.2**: adaptador minimo de busca externa governada (somente consulta controlada + normalizacao + observabilidade), sem ingestao automatica.
