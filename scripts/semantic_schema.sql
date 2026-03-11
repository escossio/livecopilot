-- Minimal semantic schema for livecopilot (OpenAI text-embedding-3-small, 1536 dims)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id bigserial PRIMARY KEY,
    source_file text NOT NULL,
    title text,
    doc_type text,
    checksum text,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id bigserial PRIMARY KEY,
    document_id bigint NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_id text NOT NULL,
    sequence integer NOT NULL,
    title text,
    content text NOT NULL,
    trecho_relevante text,
    tags jsonb NOT NULL DEFAULT '[]'::jsonb,
    embedding vector(1536),
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ingest_jobs (
    id bigserial PRIMARY KEY,
    source_file text,
    status text NOT NULL,
    started_at timestamptz DEFAULT now(),
    finished_at timestamptz,
    notes text
);

CREATE INDEX IF NOT EXISTS idx_documents_source_file ON documents(source_file);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_id ON chunks(chunk_id);
CREATE INDEX IF NOT EXISTS idx_chunks_sequence ON chunks(sequence);
