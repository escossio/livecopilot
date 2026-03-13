# Handoff: Auditoria do pipeline existente de curadoria/ingestao de livros

Data: 2026-03-11
Escopo: auditoria factual sem mudanca funcional no pipeline

## Resposta curta (operacional)
- Procedimento canonico atual para novos livros: `colocar arquivos em data/knowledge_raw/` e executar `scripts/ingest_knowledge.sh` (ou `python3 -m app.services.knowledge_ingest`).
- Entrada oficial de livros brutos: `data/knowledge_raw/`.
- Sequencia de scripts/etapas: `knowledge_parsers` (parse) -> `knowledge_chunks` (chunking + tags + manifest) -> opcional `semantic_min_api` via `--semantic-persist` (persistencia vetorial minima).
- Artefatos finais: `data/knowledge_parsed/*.json`, `data/knowledge_chunks/*.chunks.json`, `data/knowledge_index/knowledge_manifest.json`, `data/knowledge_index/knowledge_state.json` (+ persistencia em `documents/chunks` no PostgreSQL quando `--semantic-persist`).
- Proximo comando correto para os livros novos: primeiro extrair/copiar para `data/knowledge_raw/`, depois rodar `scripts/ingest_knowledge.sh --semantic-persist --semantic-limit-docs <N>` (ou sem `--semantic-persist` se quiser so parse+chunks).

## Evidencias de codigo/documentacao
- Entrada oficial e saidas: `README.md` (secao "Ingestao local de conhecimento").
- Contrato operacional da etapa 15.1: `docs/STAGE_15_1_INGESTION_OPERATIONAL_CONTRACT.md`.
- Ponto de entrada canônico: `scripts/ingest_knowledge.sh` -> `app/services/knowledge_ingest.py`.
- Reingestao incremental/idempotente por hash e versao de pipeline: `app/services/knowledge_ingest.py` (`_needs_processing`, `knowledge_state.json`).
- Persistencia semantica minima opcional: `app/services/knowledge_ingest.py` + `app/services/semantic_min_api.py` (`ingest_knowledge_base_min`).
- Camada de triagem/selecao de "melhores documentos": `app/services/curated_sources.py` (review + `check-promotion` + `promote-candidate`) promovendo para `data/knowledge_raw/`.

## Estado dos livros novos (rodada)
- Arquivo detectado: `livros.zip` na raiz do projeto.
- Conteudo do zip inclui novos `.epub` (Docker/FastAPI) ainda nao presentes em `data/knowledge_raw/`.
- Conclusao: os livros novos **ainda nao estao no local canonico de entrada**; precisam ser extraidos/copiados para `data/knowledge_raw/` antes da ingestao.

## Observacao sobre selecao dos "melhores"
- Existe selecao de documentos na trilha de curadoria (`curated_sources`), com decisao humana e promocao manual para `knowledge`.
- No pipeline direto de `knowledge_raw`, nao ha etapa de "escolha de melhores" antes de parse/chunk; processa tudo que estiver no raw suportado.
