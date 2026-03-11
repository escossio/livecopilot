-- Continuity MVP schema (runs + canonical facts + semantic memory)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS project_runs (
    id bigserial PRIMARY KEY,
    project_name text NOT NULL,
    session_id text NOT NULL,
    actor text NOT NULL,
    run_type text NOT NULL,
    summary_short text NOT NULL,
    summary_full text NOT NULL,
    status_md_path text NOT NULL,
    checkpoint_path text NOT NULL,
    run_key text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (run_key)
);

CREATE TABLE IF NOT EXISTS project_facts (
    id bigserial PRIMARY KEY,
    run_id bigint NOT NULL REFERENCES project_runs(id) ON DELETE CASCADE,
    fact_type text NOT NULL,
    title text NOT NULL,
    body text NOT NULL,
    fact_status text NOT NULL,
    component text,
    priority text,
    source_path text,
    source_section text,
    fact_key text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (run_id, fact_key),
    CHECK (fact_type IN (
        'decision', 'milestone', 'issue', 'fix', 'pending',
        'insight', 'risk', 'checkpoint', 'hypothesis', 'abandoned_idea'
    )),
    CHECK (fact_status IN ('active', 'historical', 'partial', 'abandoned', 'superseded'))
);

CREATE TABLE IF NOT EXISTS project_memory_chunks (
    id bigserial PRIMARY KEY,
    run_id bigint NOT NULL REFERENCES project_runs(id) ON DELETE CASCADE,
    fact_id bigint REFERENCES project_facts(id) ON DELETE SET NULL,
    content text NOT NULL,
    embedding vector(1536),
    source_type text NOT NULL,
    source_path text,
    semantic_layer text,
    tags jsonb NOT NULL DEFAULT '[]'::jsonb,
    chunk_key text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (run_id, chunk_key)
);

CREATE INDEX IF NOT EXISTS idx_project_runs_project_created
    ON project_runs(project_name, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_project_facts_run_status_created
    ON project_facts(run_id, fact_status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_project_facts_type_status
    ON project_facts(fact_type, fact_status);

CREATE INDEX IF NOT EXISTS idx_project_memory_chunks_run_created
    ON project_memory_chunks(run_id, created_at DESC);
