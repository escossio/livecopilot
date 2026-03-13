# Stage 15.1: Contrato Operacional de Ingestao das Literaturas no Banco Semantico

Data: 2026-03-11  
Status: definido (sem implementacao funcional nova nesta rodada)

## 1) Objetivo da 15.1
Definir o contrato operacional minimo e auditavel para ingestao de literaturas no banco semantico, garantindo que a etapa 15.2 execute sem ambiguidade.

Resultado esperado da 15.1:
- regras claras de entrada, processamento, persistencia e validacao;
- campos obrigatorios de documento/chunk definidos;
- ciclo de estados da ingestao definido;
- criterio objetivo de sucesso/falha definido;
- relacao explicita com runtime local-first definida.

## 2) Diagnostico objetivo do estado atual (baseline)
Ja existe base parcial operacional de ingestao local:
- entrada de literaturas em `data/knowledge_raw/`;
- parse em `data/knowledge_parsed/`;
- chunking em `data/knowledge_chunks/*.chunks.json`;
- manifest/state em `data/knowledge_index/knowledge_manifest.json` e `data/knowledge_index/knowledge_state.json`;
- pipeline local em `app/services/knowledge_ingest.py` e `scripts/ingest_knowledge.sh`;
- schema semantico minimo em `scripts/semantic_schema.sql` (`documents`, `chunks`, `ingest_jobs`);
- API semantica minima em `app/services/semantic_min_api.py` (`/semantic/ingest-min`, `/semantic/search`);
- fallback local de recuperacao textual em `app/services/knowledge_search.py`.

Lacuna critica que abre a Etapa 15:
- acervo literario existe, mas o contrato unificado de como consolidar e validar a persistencia semantica ainda nao estava formalizado.

## 3) Escopo da ingestao (o que entra)
### 3.1 Fontes/documentos aceitos
- Literatura tecnica ja presente localmente (prioridade): `data/knowledge_raw/`.
- Materiais promovidos pela curadoria manual (quando `destination=knowledge`).
- Sem busca externa ampla nesta subetapa.

### 3.2 Formatos suportados (baseline atual)
- `.txt`, `.md`, `.pdf`, `.docx`, `.html`, `.htm`, `.epub`.

### 3.3 Unidade de entrada
- Unidade de entrada obrigatoria: **documento**.
- Identidade primaria de entrada: `source_file` relativo ao `knowledge_raw`.

### 3.4 Unidade de armazenamento/recuperacao
- Unidade minima de persistencia e recuperacao: **chunk**.
- Cada chunk deve ser rastreavel ao documento de origem.

## 4) Metadados obrigatorios

### 4.1 Metadados obrigatorios por documento
Campos minimos obrigatorios:
- `source_file` (string, relativo ao raw)
- `title` (string)
- `sha256` (string, hash do arquivo bruto)
- `file_type` (string)
- `status` (string)
- `parsed_path` (string)
- `chunk_path` (string)
- `processed_at` (ISO-8601)
- `tag_pipeline_version` (string)
- `chunk_count` (int >= 0)

Campos recomendados (quando houver persistencia semantica):
- `document_id` (id no banco semantico)
- `checksum` (hash do conteudo normalizado, quando aplicavel)
- `doc_type` (ex.: `knowledge`, `semantic-min`, `literature`)
- `metadata_json.ingest_mode`
- `metadata_json.embedding_model`

### 4.2 Metadados obrigatorios por chunk
Campos minimos obrigatorios:
- `chunk_id` (string)
- `source_file` (string)
- `title` (string)
- `sequence` (int >= 1)
- `content` (string nao vazia)
- `estimated_topic` (string)
- `tags` (objeto com `technology`, `domain`, `subtheme`, `all`)

Campos recomendados para trilha semantica:
- `document_id` (FK logica)
- `trecho_relevante` (string)
- `metadata_json.model` (embedding model)
- `metadata_json.embedding_status` (`pending|ok|error`)

## 5) Regra de IDs

### 5.1 document_id
- Fonte de verdade no banco semantico: `documents.id` (bigserial).
- Identificador logico recomendavel para trilha de ingestao: `doc::<source_file_norm>::<sha256_12>`.
- Regras:
  - mesmo `source_file` + mesmo `sha256` -> mesma identidade logica de documento;
  - mudanca de `sha256` -> nova versao logica do documento.

### 5.2 chunk_id
Padrao alvo da etapa 15:
- `chunk::<doc_key>::<sequence4>::<content_sha8>`.

Compatibilidade:
- IDs legados existentes em `knowledge_chunks` permanecem validos para leitura.
- Reingestoes futuras podem normalizar gradualmente para o padrao alvo sem quebrar leitura.

## 6) Versionamento, reingestao e update
- A reingestao e disparada quando qualquer condicao ocorrer:
  - `sha256` mudou;
  - `tag_pipeline_version` mudou;
  - `parsed_path`/`chunk_path` inexistente;
  - payload sem tags minimas;
  - mudanca relevante de pipeline de chunking.
- Em update de documento:
  - estado anterior deve ser substituido de forma idempotente;
  - chunks obsoletos devem ser removidos/invalidos para evitar drift;
  - caches de busca semantica devem ser invalidados apos escrita.

## 7) Deduplizacao
Regra minima obrigatoria (documento):
- duplicata primaria por `sha256` identico.

Regra auxiliar:
- mesmo `source_file` com `sha256` diferente = nova versao (nao duplicata).

Regra editorial:
- variantes da mesma obra com mesmo `identifier` curatorial devem convergir para um unico exemplar promovido, conforme politica de ingestao.

## 8) Ciclo de estados da ingestao
Estados oficiais da etapa 15:
1. `discovered` (documento detectado em fonte valida)
2. `extracted` (texto bruto extraido/normalizado)
3. `chunked` (chunks gerados com metadados minimos)
4. `embedded` (vetores calculados)
5. `persisted` (documents/chunks gravados no banco semantico)
6. `validated` (checks operacionais aprovados)
7. `failed` (erro terminal com motivo auditavel)

Regra operacional:
- todo `failed` deve registrar motivo curto (`failure_reason`) e etapa de falha (`failure_stage`).

## 9) Criterios de sucesso/falha

### 9.1 Sucesso minimo por documento
- `status` em manifest/state consistente com artefatos gerados;
- `chunk_count > 0` para documento nao vazio;
- `chunk_path` e `parsed_path` acessiveis;
- para trilha semantica: documento/chunks persistidos e `embedding` presente nos chunks esperados;
- documento recuperavel em busca local-first com metadados coerentes.

### 9.2 Falha minima
- parse vazio/erro sem fallback valido;
- chunking sem gerar chunks para documento nao vazio;
- erro de embedding sem fallback declarado;
- persistencia parcial inconsistente (ex.: documento sem chunks esperados);
- recuperacao retorna sem rastreabilidade de origem.

## 10) Evidencias minimas de validacao (auditavel)
Para considerar lote de ingestao valido:
1. `knowledge_manifest.json` atualizado com contagens coerentes.
2. `knowledge_state.json` atualizado com `processed_at`/`sha256`/`chunk_count` por documento.
3. Amostra de chunks com campos obrigatorios preenchidos.
4. Persistencia semantica (quando ativa) com:
   - contagem de `documents`/`chunks` inseridos;
   - `chunk_id` e `document_id` consultaveis.
5. Teste de recuperacao local-first em query tecnica com retorno de fonte/chunk.

## 11) Relacao com runtime local-first
Contrato de consumo da etapa 15:
- runtime deve priorizar base local consolidada;
- busca semantica local e camada primaria quando disponivel;
- fallback para busca lexical local permanece permitido;
- ausencia de camada semantica nao pode quebrar `/ingest` ou `/realtime/respond`.

Resultado esperado para 15.4:
- runtime usando base consolidada com trilha de metadados de recuperacao (`source_file`, `chunk_id`, score/similaridade, backend efetivo).

## 12) Fora de escopo explicito da 15.1
- implementacao completa do pipeline de ingestao (15.2);
- recalculo massivo de embeddings nesta rodada;
- tuning avancado de ranking/search;
- busca externa ampla, crawling/scraping irrestrito;
- refatoracao ampla de arquitetura/runtime.

## 13) Proximo passo oficial apos 15.1
- **15.2 Pipeline minimo de ingestao**:
  - consolidar fluxo unico `documento -> chunk -> embedding -> persistencia`;
  - aplicar estados oficiais e metadados obrigatorios;
  - produzir evidencia minima automatizavel para 15.3.
