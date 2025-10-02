-- Shopify Developer Forum Database Schema
-- Multi-category support with comprehensive tracking

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    topic_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    last_scraped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Topics table
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    slug TEXT NOT NULL,
    created_at TIMESTAMP,
    last_posted_at TIMESTAMP,
    reply_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    accepted_answer BOOLEAN DEFAULT FALSE,
    closed BOOLEAN DEFAULT FALSE,
    archived BOOLEAN DEFAULT FALSE,
    pinned BOOLEAN DEFAULT FALSE,
    visible BOOLEAN DEFAULT TRUE,
    scraped_at TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Posts table
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER NOT NULL,
    post_number INTEGER NOT NULL,
    username TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    reply_count INTEGER DEFAULT 0,
    quote_count INTEGER DEFAULT 0,
    incoming_link_count INTEGER DEFAULT 0,
    reads INTEGER DEFAULT 0,
    readers_count INTEGER DEFAULT 0,
    score REAL DEFAULT 0.0,
    like_count INTEGER DEFAULT 0,
    cooked TEXT,
    raw TEXT,
    is_accepted_answer BOOLEAN DEFAULT FALSE,
    scraped_at TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(id),
    UNIQUE (topic_id, post_number)
);

-- Checkpoints table for resumable scraping
CREATE TABLE IF NOT EXISTS checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    checkpoint_type TEXT NOT NULL, -- 'category_page' or 'topic'
    last_page INTEGER,
    last_topic_id INTEGER,
    total_processed INTEGER DEFAULT 0,
    status TEXT DEFAULT 'in_progress', -- 'in_progress', 'completed', 'error'
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Users table (derived from posts)
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    post_count INTEGER DEFAULT 0,
    topic_count INTEGER DEFAULT 0,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_topics_category ON topics(category_id);
CREATE INDEX IF NOT EXISTS idx_topics_created ON topics(created_at);
CREATE INDEX IF NOT EXISTS idx_posts_topic ON posts(topic_id);
CREATE INDEX IF NOT EXISTS idx_posts_username ON posts(username);
CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at);
CREATE INDEX IF NOT EXISTS idx_checkpoints_category ON checkpoints(category_id);
CREATE INDEX IF NOT EXISTS idx_checkpoints_status ON checkpoints(status);