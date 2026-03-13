# Handoff: Stage 15.2 Completion

Data: 2026-03-11
Status: concluida (escopo minimo)

## Objetivo da subetapa
Consolidar um pipeline minimo, unico e auditavel para ingestao semantica de literaturas:
`documento -> chunk -> embedding -> persistencia -> validacao`.

## O que foi consolidado
- Ponto de entrada canonico via `app/services/knowledge_ingest.py` (`scripts/ingest_knowledge.sh`) com flags:
  - `--semantic-persist`
  - `--semantic-limit-docs`
  - `--semantic-max-chunks-per-doc`
  - `--semantic-source-file`
  - `--semantic-embedding-mode (auto|openai|mock)`
- Persistencia semantica minima por documento usando chunks existentes (sem recriar chunk sem necessidade).
- Regras minimas de deduplicacao/reingestao previsivel por `source_file + checksum`.
- Atualizacao de `knowledge_state.json` e `knowledge_manifest.json` com estado semantico por documento.

## Evidencia objetiva executada
Documento validado: `duplicado_do_conteudo.md`

Execucao 1:
- `documents_selected=1`
- `documents_validated=1`
- `chunks_persisted=1`
- estado final: `validated`

Execucao 2 (mesmo documento):
- reingestao previsivel sem duplicacao indevida
- contagem final no banco: `documents=1`, `chunks=1` para o `source_file`

Estado apos validacao:
- `knowledge_state.files[duplicado_do_conteudo.md].semantic_status=validated`
- `knowledge_manifest.documents[*].semantic_status=validated` para o documento
- `knowledge_manifest.embedding_status=ready`
- `knowledge_manifest.vector_store_status=built`

## Fora de escopo mantido
- tuning avancado de retrieval/ranking;
- ingestao em massa do acervo completo;
- busca externa;
- redesign arquitetural.

## Proximo passo oficial
- **15.3 Validacao da base** (bateria objetiva de integridade, cobertura minima e recuperacao local-first).
