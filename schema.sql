-- =====================================================
-- On-Chain News Provider - Supabase Schema
-- Run this in your Supabase SQL Editor
-- =====================================================

-- 1. Tokens Registry Table
CREATE TABLE IF NOT EXISTS tokens (
    id TEXT PRIMARY KEY,           -- Token slug (e.g., "bitcoin", "ethereum")
    name TEXT NOT NULL,            -- Display name
    enabled BOOLEAN DEFAULT TRUE,  -- Whether to scrape this token
    scrape_interval INT DEFAULT 60, -- Minutes between scrapes
    last_scraped TIMESTAMPTZ,      -- Last successful scrape time
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Insights Table (with sources)
-- If you already have an insights table, run this ALTER instead:
-- ALTER TABLE insights ADD COLUMN IF NOT EXISTS token_id TEXT;
-- ALTER TABLE insights ADD COLUMN IF NOT EXISTS sources JSONB DEFAULT '[]'::jsonb;

CREATE TABLE IF NOT EXISTS insights (
    id TEXT PRIMARY KEY,
    token_id TEXT,                 -- Which token this insight belongs to
    timestamp BIGINT,
    title TEXT,
    content TEXT,
    source_count INT DEFAULT 0,
    sources JSONB DEFAULT '[]'::jsonb,  -- Array of {url, title} objects
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries by token
CREATE INDEX IF NOT EXISTS idx_insights_token_id ON insights(token_id);
CREATE INDEX IF NOT EXISTS idx_insights_timestamp ON insights(timestamp DESC);

-- 3. Scraper State Table
CREATE TABLE IF NOT EXISTS scraper_state (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- Seed Initial Tokens (optional - customize as needed)
-- =====================================================
INSERT INTO tokens (id, name, enabled, scrape_interval) VALUES
    ('ethereum', 'Ethereum', TRUE, 60),
    ('bitcoin', 'Bitcoin', TRUE, 60),
    ('solana', 'Solana', TRUE, 60)
ON CONFLICT (id) DO NOTHING;
