# Handoff: ingestao canonica controlada do recorte Docker

Data: 2026-03-12  
Escopo: ingestao canonica (`scripts/ingest_knowledge.sh`) do recorte `docker_docs_selected`, sem alterar pipeline

## Resumo objetivo
- Clone oficial confirmado em `data/knowledge_raw/_official_repo_clones/docker-docs`.
- Recorte aprovado montado em `data/knowledge_raw/docker_docs_selected` com `79` arquivos `.md`.
- `content/manuals/engine/container` nao existe no `docker/docs` atual.

## Execucao e evidencia
1) Primeira execucao canônica:
- Comando: `scripts/ingest_knowledge.sh`
- O pipeline varreu `knowledge_raw` inteiro e processou tambem o clone bruto.
- Evidencia (`/tmp/docker_ingest_20260311.log`):
  - `knowledge_file_processed` total: `1421`
  - `docker_docs_selected/*`: `79`
  - `_official_repo_clones/docker-docs/*`: `1342`
  - erros de parsing detectados no log: `0`

2) Execucao controlada final (sem mudar pipeline):
- Acao operacional: stash temporario do clone bruto fora de `knowledge_raw`, nova execucao canonica e restauracao do clone.
- Evidencia (`/tmp/docker_ingest_controlled_20260311.log`):
  - `Arquivos encontrados: 134`
  - `Arquivos processados: 0`
  - `Arquivos ignorados: 134`
  - `Erros de parsing: 0`
  - `Arquivos nao suportados: 0`
  - `Chunks gerados: 52390`

## Estado final validado
- `data/knowledge_parsed/`: `79` arquivos `docker_docs_selected__*.json`.
- `data/knowledge_chunks/`: `79` arquivos `docker_docs_selected__*.chunks.json`.
- `data/knowledge_index/knowledge_manifest.json`:
  - `document_count=134`
  - `chunk_document_count=134`
  - `chunk_count=52390`
- `data/knowledge_index/knowledge_state.json`:
  - `79` entradas `docker_docs_selected/*`
  - todas com `status=parsed`.

## Proximo comando correto (nao executado)
- Persistencia semantica opcional, sem mudar pipeline:
```bash
scripts/with-semantic-env.sh .venv/bin/python -m app.services.knowledge_ingest --semantic-persist --semantic-source-file "docker_docs_selected/content/manuals/build/building/multi-stage.md"
```
- Para lote completo do recorte, repetir `--semantic-source-file` para os `79` source_files de `docker_docs_selected/*`.

## Restricoes respeitadas
- sem alteracao de pipeline
- sem ingestao massiva do repo completo como estrategia final
- sem persistencia semantica nesta rodada
