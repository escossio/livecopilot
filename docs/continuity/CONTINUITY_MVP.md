# Continuity MVP (PostgreSQL)

## Problema que resolve
O projeto ja mantem checkpoints humanos em `STATUS.md`, mas perde continuidade quando o chat muda ou cresce demais.
Este MVP adiciona persistencia estruturada em PostgreSQL para registrar rodadas, fatos canonicos e memoria semantica resumida.

## Arquitetura do MVP
O MVP tem 3 niveis:

1. `project_runs`: registro operacional da rodada.
2. `project_facts`: fatos canonicos extraidos da rodada.
3. `project_memory_chunks`: memoria semantica resumida e recuperavel.

`STATUS.md` continua como artefato humano. O banco vira a camada estruturada de continuidade.

## Tabelas
Schema SQL: `scripts/continuity_schema.sql`

### project_runs
Campos principais:
- `id`, `project_name`, `session_id`, `actor`, `run_type`
- `summary_short`, `summary_full`
- `status_md_path`, `checkpoint_path`
- `run_key` (idempotencia)
- `created_at`

### project_facts
Campos principais:
- `id`, `run_id`
- `fact_type`, `title`, `body`, `fact_status`
- `component`, `priority`
- `source_path`, `source_section`
- `fact_key` (idempotencia por rodada)
- `created_at`

Taxonomia minima de `fact_type` suportada:
- `decision`, `milestone`, `issue`, `fix`, `pending`, `insight`, `risk`, `checkpoint`, `hypothesis`, `abandoned_idea`

Taxonomia minima de `fact_status` suportada:
- `active`, `historical`, `partial`, `abandoned`, `superseded`

### project_memory_chunks
Campos principais:
- `id`, `run_id`, `fact_id`
- `content`, `embedding`
- `source_type`, `source_path`, `semantic_layer`, `tags`
- `chunk_key` (idempotencia por rodada)
- `created_at`

Notas:
- `embedding` usa `vector(1536)` com `pgvector`, alinhado ao schema semantico ja existente.
- se embedding nao estiver disponivel, o chunk e persistido com `embedding=NULL`.

## Fluxo operacional
1. Preparar schema:
```bash
psql "$SEMANTIC_PG_DSN" -f scripts/continuity_schema.sql
```

2. Registrar uma rodada (ingest):
```bash
./.venv/bin/python scripts/continuity_ingest.py --input docs/continuity/examples/sample_run_payload.json
```

3. Recuperar contexto recente:
```bash
./.venv/bin/python scripts/continuity_recall.py --project livecopilot --runs 5 --facts 10
```

## Payload canonico
Exemplo oficial:
- `docs/continuity/examples/sample_run_payload.json`
- `docs/continuity/examples/sample_facts.json` (facts explicitos para uso com builder)

Campos minimos obrigatorios:
- `project_name`, `session_id`, `actor`, `run_type`
- `summary_short`, `summary_full`
- `status_md_path`, `checkpoint_path`
- `facts[]` com `fact_type`, `title`, `body`, `fact_status`

Contrato de facts explicitos:
- `docs/continuity/FACTS_CONTRACT.md`

## Script de ingestao
Arquivo:
- `scripts/continuity_ingest.py`

Responsabilidades:
- ler payload JSON
- validar campos minimos e taxonomias
- inserir/atualizar `project_runs`
- inserir/atualizar `project_facts`
- gerar chunks minimos (`run_summary` + `fact`)
- gerar embedding opcional quando houver `OPENAI_API_KEY`
- inserir/atualizar `project_memory_chunks`

Idempotencia basica:
- `run_key` unico em `project_runs`
- `fact_key` unico por `run_id`
- `chunk_key` unico por `run_id`

## Script de recuperacao
Arquivo:
- `scripts/continuity_recall.py`

Capacidades:
- listar ultimas rodadas
- listar fatos ativos recentes
- buscar por texto (`ILIKE`) em summaries/fatos/chunks
- busca semantica opcional (`--semantic`) quando houver `OPENAI_API_KEY` e embeddings gravados

## Limitacoes atuais
- integracao ao fluxo operacional e sem refactor amplo (semi-automatizada) foi adicionada por wrapper/script dedicado; ainda depende de invocacao explicita ao fim da rodada
- embeddings dependem de OpenAI e podem ficar nulos no fallback
- nao ha consolidacao automatica de conflitos semanticos entre fatos
- chunking semantico e propositalmente simples nesta fase

## Integracao operacional minima (nova)
Arquivos:
- `scripts/continuity_build_payload.py`
- `scripts/run_continuity_capture.sh`
- `docs/continuity/payloads/`

Fluxo semi-automatico:
1. gerar payload canonico auditavel por rodada;
2. persistir payload em `docs/continuity/payloads/`;
3. ingerir o payload em `project_runs`/`project_facts`/`project_memory_chunks`.

Exemplo:
```bash
./scripts/run_continuity_capture.sh \
  --session-id agent-livecopilot \
  --actor codex \
  --run-type implementation \
  --summary-short "Integracao minima da continuidade ao fluxo operacional." \
  --summary-full "Payload canônico gerado por script e ingestão executada via wrapper." \
  --checkpoint-path docs/continuity/ROUND_SUMMARY_CONTINUITY_AUTOMATION.md \
  --facts-file docs/continuity/examples/sample_facts.json
```

Notas:
- o wrapper preserva fallback manual (`continuity_build_payload.py` + `continuity_ingest.py`);
- `run_key` e deterministico no payload canonico;
- fatos minimos sao garantidos mesmo sem facts extras informados.
- quando `--facts-file` e fornecido, os facts entram no payload sem inferencia por markdown.

## Proximos passos sugeridos
1. adicionar chamada opcional do wrapper no encerramento do loop principal.
2. adicionar politica de retencao/prioridade de fatos historicos.
3. criar endpoint HTTP de recall para abrir novo chat com contexto inicial.
4. adicionar testes automatizados para schema e scripts de continuidade.
