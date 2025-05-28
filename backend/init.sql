CREATE TABLE IF NOT EXISTS enrich_logs (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    unique_id TEXT NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT NOW()
);