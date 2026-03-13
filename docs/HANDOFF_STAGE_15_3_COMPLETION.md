# Handoff: Stage 15.3 Completion

Data: 2026-03-11
Status: concluida (validacao objetiva da base)

## Objetivo da subetapa
Validar de forma curta, objetiva e auditavel a base semantica quanto a:
- integridade estrutural;
- consistencia de metadados;
- deduplicacao previsivel;
- recuperacao semantica local-first.

## Bateria executada (amostra multipla)
Documentos reais usados:
- `duplicado_do_conteudo.md`
- `relatorio_final.docx`
- `teste_exportado.html`

Pipeline validado com persistencia semantica minima:
- `documents_selected=3`
- `documents_processed=3`
- `documents_validated=3`
- `documents_failed=0`
- `chunks_persisted=3`

## Evidencias de integridade
- `documents_total=39`
- `chunks_total=141`
- `orphan_chunks=0`
- Consistencia por documento da amostra:
  - cada `source_file` com `documents=1` e `chunks=1` no banco
  - `knowledge_state` e `knowledge_manifest` alinhados em `semantic_status=validated`, `semantic_chunk_count=1`, `semantic_document_id` coerente.
- Flags de base:
  - `knowledge_manifest.embedding_status=ready`
  - `knowledge_manifest.vector_store_status=built`

## Evidencias de deduplicacao
- Checagem global `source_file + checksum` encontrou 1 duplicata legada (`__smoke_openai__.md`).
- Correcao minima aplicada no banco: mantida apenas a linha mais recente.
- Revalidacao apos correcao: `duplicate_source_checksum_rows=[]`.

## Evidencias de recuperacao semantica
Queries e top-1 retornado:
- `conteudo local importacao automatizada` -> `duplicado_do_conteudo.md`
- `backend java aws` -> `relatorio_final.docx`
- `analytics product owner` -> `teste_exportado.html`

Conclusao de recuperacao:
- top resultados coerentes com documentos/chunks esperados na amostra.

## Criterios de aceite da 15.3 (atingidos)
- Integridade estrutural sem orfaos.
- Metadados essenciais alinhados entre banco/state/manifest na amostra.
- Deduplicacao previsivel comprovada e anomalia legada saneada.
- Recuperacao semantica coerente para queries diretas dos documentos ingeridos.

## O que fica para 15.4
- Integracao local-first no runtime com validacao operacional de ponta a ponta (`/ingest` e `/realtime/respond` usando base consolidada como caminho principal quando disponivel).
- Fechamento da Etapa 15 no escopo atual.
