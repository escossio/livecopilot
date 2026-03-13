# Ingestion Selective Prefix Mode

## Motivacao
O pipeline canonico de ingestao varre todo `data/knowledge_raw` por padrao.
Em rodadas incrementais/continuidade isso pode causar reprocessamento amplo e baixa previsibilidade.

Para reduzir esse custo, foi adicionado suporte nativo a filtro por prefixo relativo ao `knowledge_raw`.

## Comportamento padrao (sem prefixo)
Sem `--source-prefix`, nada muda:
- a ingestao continua varrendo todo `data/knowledge_raw`
- estado/manifest seguem o fluxo atual

Exemplo:

```bash
scripts/ingest_knowledge.sh
```

## Modo seletivo por prefixo
Use `--source-prefix` para limitar os candidatos de ingestao a subcaminhos especificos.

Regras:
- prefixo e relativo a `data/knowledge_raw`
- pode repetir o argumento
- aceita com ou sem barra final
- prefixos invalidos sao rejeitados:
  - vazio apos normalizacao
  - contendo segmento `..`

### Exemplo (prefixo unico)

```bash
scripts/ingest_knowledge.sh --source-prefix continuity_docs_selected/
```

Escopo esperado:
- apenas arquivos em `data/knowledge_raw/continuity_docs_selected/`

### Exemplo (multiplos prefixos)

```bash
scripts/ingest_knowledge.sh \
  --source-prefix continuity_docs_selected/ \
  --source-prefix terraform_docs_selected_incremental/
```

Escopo esperado:
- uniao dos dois prefixos

## Detalhes de implementacao
- argumento adicionado em `app.services.knowledge_ingest`:
  - `--source-prefix` (repetivel)
  - `--strict-source-prefix`
- o filtro atua somente na ingestao canonica (varredura/parsing/chunking)
- persistencia semantica nao foi alterada por este recurso

Quando o modo seletivo esta ativo:
- limpeza de estado/artefatos fica restrita ao escopo dos prefixos informados
- dados fora do escopo nao sao removidos
- o resumo mostra:
  - prefixos normalizados
  - contagem de arquivos encontrados por prefixo

## Modo de visualizacao da ingestao (`--dry-run`)
Use `--dry-run` para inspecionar os alvos de ingestao antes da rodada real.

Regras:
- resolve e mostra os candidatos de ingestao no escopo atual
- exibe `selection_mode`, prefixos normalizados, contagem por prefixo e total selecionado
- nao gera parsed/chunks
- nao altera state/manifest

Exemplo:

```bash
scripts/ingest_knowledge.sh \
  --source-prefix continuity_docs_selected/ \
  --dry-run
```

## Persistencia semantica seletiva por prefixo
Tambem e possivel usar `--source-prefix` junto com `--semantic-persist`.

Fluxo:
1. resolve prefixos em `source_files` existentes no estado canonico
2. reutiliza a trilha de persistencia ja existente por `source_file`

### Prioridade entre filtros
- `--semantic-source-file` explicito tem prioridade (compatibilidade preservada)
- sem `--semantic-source-file`, se houver `--source-prefix`, a selecao semantica e resolvida por prefixo
- sem prefixo e sem source_file explicito, comportamento atual permanece (persistencia padrao)

### Exemplo (prefixo unico)

```bash
scripts/with-semantic-env.sh .venv/bin/python -m app.services.knowledge_ingest \
  --semantic-persist \
  --semantic-embedding-mode mock \
  --source-prefix continuity_docs_selected/
```

### Exemplo (multiplos prefixos)

```bash
scripts/with-semantic-env.sh .venv/bin/python -m app.services.knowledge_ingest \
  --semantic-persist \
  --semantic-embedding-mode mock \
  --source-prefix continuity_docs_selected/ \
  --source-prefix terraform_docs_selected_incremental/
```

### Exemplo (source_file explicito, modo legado)

```bash
scripts/with-semantic-env.sh .venv/bin/python -m app.services.knowledge_ingest \
  --semantic-persist \
  --semantic-source-file continuity_docs_selected/docs/SEMANTIC_ROUND_CLOSEOUT_CHECKLIST.md
```

### Troubleshooting na persistencia
Quando a selecao por prefixo e usada na persistencia, a saida inclui:
- prefixos normalizados
- quantidade de `source_files` resolvidos por prefixo
- total de `source_files` selecionados

## Modo de visualizacao da persistencia (`--list-targets`)
Use `--list-targets` junto com `--semantic-persist` para listar os `source_files` sem persistir embeddings.

Regras:
- resolve e mostra os `source_files` que seriam persistidos
- exibe `selection_mode`, prefixos normalizados, contagem por prefixo e total resolvido
- nao grava embeddings
- nao altera banco/estado
- com `--semantic-source-file` explicito, o `selection_mode` e `explicit_source_file`

Exemplo:

```bash
scripts/with-semantic-env.sh .venv/bin/python -m app.services.knowledge_ingest \
  --semantic-persist \
  --source-prefix continuity_docs_selected/ \
  --list-targets
```

Se nenhum `source_file` for resolvido:
- com `--strict-source-prefix`: falha com erro claro
- sem strict: no-op semantico (nao persiste nada) com resumo explicito

## Strict mode
Use `--strict-source-prefix` para falhar quando nenhum arquivo casar com os prefixos informados.

Exemplo:

```bash
scripts/ingest_knowledge.sh \
  --source-prefix nao_existe/ \
  --strict-source-prefix
```

Erro esperado (resumo):
- `strict-source-prefix habilitado e nenhum arquivo encontrado para: ...`

Exemplo de prefixo invalido:

```bash
scripts/ingest_knowledge.sh --source-prefix ../segredo
```

Erro esperado (resumo):
- `source-prefix inválido (path traversal): ...`

## Boas praticas
- usar prefixos curtos e canônicos por rodada (ex.: `continuity_docs_selected/`)
- evitar prefixos ambiguos
- em automacoes, registrar no log os prefixos usados
- manter artefato de validacao com contagens (`found/processed/skipped/chunks`)

## Planejamento unificado da rodada
Para pre-visualizacao unificada (ingestao + persistencia semantica) por prefixo, veja `docs/ROUND_PLAN_PREFIX_MODE.md`.

## Pipeline operacional da rodada
Para executar o fluxo completo `plan -> run -> validate` com artefatos de rodada, veja `docs/KNOWLEDGE_PIPELINE_V1.md`.
