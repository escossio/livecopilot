# FRONT POSTGRESQL

## Objetivo
- Registrar a abertura oficial da frente PostgreSQL e governar seu ciclo documental, garantindo pertencimento ao escopo core antes de qualquer parsing ou validação.

## Escopo
- Domínio: PostgreSQL core (`postgresql.org/docs`), SQL fundamentals, indexing, performance tuning, JSONB, extensões certificadas (`postgis`, `pg_stat_statements`), administração e replicação básica.
- Exclusões: conteúdos de provedores terceiros, material comercial, cursos pagos e artigos opinativos sem origem direta da comunidade PostgreSQL.

## Source policy
- Fontes permitidas: `https://www.postgresql.org/docs/` e páginas auxiliares oficiais da PostgreSQL Global Development Group (ex.: páginas de extensão mantidas pela mesma comunidade).
- Priorizar seções oficiais sobre planejamento de schema, índices, tuning e extensões; evitar seções duplicadas ou versões obsoletas sem contexto.
- Idioma preferido: inglês; traduções oficiais podem ser incluídas se sincronizadas com o release principal.

## Source manifest (inicial)
- PostgreSQL Documentation Home (`https://www.postgresql.org/docs/current/`) – visão geral, architecture, SQL, admin.
- SQL Commands (`https://www.postgresql.org/docs/current/sql.html`) – comandos DDL/DML centrais.
- Indexing & Performance (`https://www.postgresql.org/docs/current/indexes.html`, `https://www.postgresql.org/docs/current/performance-tips.html`).
- JSON & JSONB (`https://www.postgresql.org/docs/current/functions-json.html`) – manipulação e indexing.
- Extensions List (`https://www.postgresql.org/docs/current/extend.html`) – foco em extensões prós integráveis.

## Corpus lock (inicial)
- Locked: URLs acima; serão materializadas e hashadas no corpus preparation.
- Não autorizado: guias de terceiros, cursos de treinamento, posts promocionais.

## Status
- state: `closed`
- stage: `closure_decision`
- próximo passo: acompanhar updates oficiais de `postgresql.org` e reabrir se necessário.

## Lifecycle oficial
- Pipeline completo registrado em `docs/FRONT_LIFECYCLE_CONTRACT.md`; a frente cumpriu todas as etapas e está encerrada formalmente.

## Observação
- Nenhuma ingestão ou chunking foi executada; este documento registra apenas o recorte e as metas iniciais.
