# PostgreSQL Corpus Preparation

## Estratégia de ingestão
- Priorizar o corpo oficial do PostgreSQL documentation hub (`postgresql.org/docs/current/`), cobrindo architecture, SQL commands, performance, extensões e administração de bancos.
- Garantir que cada página seja capturada com data, identificador de release e hash para futura validação.
- Preservar blocos de código e exemplos SQL durante a conversão para markdown técnico.

## Tipos de conteúdo permitidos
- Seções oficiais sobre SQL, performance tips, indexing, JSONB, extensões (ex.: PostGIS, pg_stat_statements), administração básica de banco de dados, backup/restore e replicação.
- Documentos de release focalizados em gerenciamento de versionamento e mudanças críticas que impactam o escopo core.

## Tipos de conteúdo proibidos
- Tutoriais de terceiros, blogs, cursos pagos e qualquer material promocional não publicado pela comunidade PostgreSQL.
- Guias de provedores de nuvem ou consultorias, a menos que sejam meramente espelhos de conteúdos oficiais já listados.

## Estrutura do corpus
- Diretório: `data/knowledge_raw/postgresql/`
- Subpastas sugeridas: `architecture/`, `sql/`, `performance/`, `extensions/`, `admin/`.
- Cada artefato deverá incluir metadados de origem, data capturada e versão do release.

## Workflow de ingestão
1. Baixar as páginas aprovadas, converter para markdown e validar textos e exemplos SQL.
2. Registrar cada arquivo no corpus lock (URL, data, hash) antes de prosseguir para parsing.
3. Documentar fontes adiadas e motivação em `docs/POSTGRESQL_SOURCE_MANIFEST.json` e no STATUS.
4. Confirmar que nenhuma fase de parsing/chunking foi executada nesta etapa; o foco é apenas o nivelamento documental.
