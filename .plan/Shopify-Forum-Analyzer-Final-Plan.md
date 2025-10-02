# ⚠️ IMPLEMENTATION UPDATE

**Date:** October 2, 2025

**Status:** Phase 1 complete, Phase 2 in progress

**Note:** This plan originally proposed traditional NLP/vector DB approach. 
Project has pivoted to **LLM-based analysis using Claude API** for better semantic understanding.

See [PROGRESS_AND_NEXT_STEPS.md](PROGRESS_AND_NEXT_STEPS.md) for current implementation status.

### What Changed
- ✅ Phase 1 (Data Collection): Implemented as planned
- 🔄 Phase 2 (Analysis): Using Claude API instead of spaCy/ChromaDB/embeddings
- ⏳ Phase 3: Comprehensive problems report generation

---

[Original plan continues below...]

# Shopify Forum Analyzer - Final Execution Plan

## Executive Summary
Build a **production-ready Python application** to collect and analyze data from the Shopify Developers Forum, starting with "Webhooks & Events" category but designed for **multi-category expansion**. The system uses Discourse's JSON API with robust error handling, incremental updates, and AI-driven cross-category insights.

---

## 🎯 Project Goals

### Primary Objectives
1. **Collect all forum data** from Webhooks & Events category (18)
2. **Store structured data** supporting AI analysis
3. **Enable incremental updates** for new posts/replies
4. **Generate insights** on common problems and patterns
5. **Support multi-category expansion** without refactoring

### Success Metrics
- ✅ 100% topic coverage in target categories
- ✅ >95% API success rate with automatic recovery
- ✅ <100ms query response time for analysis
- ✅ Zero data loss on failures
- ✅ Daily automated insight reports

---

## 🏗️ System Architecture

### Technology Stack (Python-Based)
```yaml
Core:
  language: Python 3.10+
  database: SQLite (dev) → PostgreSQL (prod)
  vector_db: ChromaDB (local) or Qdrant (cloud)
  
Libraries:
  http_client: httpx (async)
  orm: SQLAlchemy 2.0
  nlp: spaCy, sentence-transformers
  cli: Click + Rich
  config: Pydantic + YAML
  testing: pytest + pytest-asyncio
  monitoring: structlog + Prometheus
```

### Project Structure
```
shopify-forum-analyzer/
├── config/
│   ├── config.yaml              # Main configuration
│   └── categories.yaml          # Category definitions
├── collector/
│   ├── __init__.py
│   ├── api_client.py           # Rate-limited Discourse API
│   ├── checkpoint_manager.py   # Recovery system
│   ├── database.py             # Database operations
│   ├── models.py               # SQLAlchemy models
│   ├── multi_category.py       # Multi-category collector
│   └── updater.py              # Incremental updates
├── analyzer/
│   ├── __init__.py
│   ├── text_processor.py       # Text cleaning/NLP
│   ├── embeddings.py           # Vector generation
│   ├── insights.py             # Analysis queries
│   ├── cross_category.py       # Cross-category analysis
│   └── exporters.py            # Export utilities
├── monitoring/
│   ├── metrics.py              # Prometheus metrics
│   └── health.py               # Health checks
├── tests/
├── notebooks/                   # Jupyter exploration
├── data/
│   ├── database/               # SQLite files
│   ├── checkpoints/            # Recovery state
│   ├── raw_json/               # JSON backups
│   └── exports/                # Analysis outputs
├── main.py                     # CLI entry point
├── schema.sql                  # Database schema
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 📊 Data Model (Multi-Category Support)

### Core Schema

#### Categories Table
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    last_fetched_at TIMESTAMP,
    topic_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initial data
INSERT INTO categories VALUES 
    (18, 'webhooks-and-events', 'Webhooks & Events', true, 1, NULL, 0, 0, CURRENT_TIMESTAMP);
```

#### Topics Table
```sql
CREATE TABLE topics (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    slug TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    created_at TIMESTAMP NOT NULL,
    last_posted_at TIMESTAMP,
    fetch_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    views INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,
    op_user_id INTEGER REFERENCES users(id),
    is_solved BOOLEAN DEFAULT FALSE,
    has_accepted_answer BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_closed BOOLEAN DEFAULT FALSE,
    raw_json TEXT
);
```

#### Posts Table
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES topics(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    post_number INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    raw TEXT,                -- Cleaned text
    cooked TEXT,             -- HTML version
    reply_to_post_number INTEGER,
    like_count INTEGER DEFAULT 0,
    is_solution BOOLEAN DEFAULT FALSE,
    mentions TEXT,           -- JSON array
    links TEXT,             -- JSON array
    code_blocks TEXT,       -- JSON array
    error_messages TEXT,    -- JSON array
    UNIQUE(topic_id, post_number)
);
```

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    name TEXT,
    trust_level INTEGER DEFAULT 0,
    flair_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Cross-Category Tables
```sql
-- Topic relationships across categories
CREATE TABLE topic_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id_1 INTEGER NOT NULL REFERENCES topics(id),
    topic_id_2 INTEGER NOT NULL REFERENCES topics(id),
    relationship_type TEXT NOT NULL, -- 'similar', 'duplicate', 'related'
    similarity_score FLOAT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(topic_id_1, topic_id_2, relationship_type)
);

-- User expertise per category
CREATE TABLE user_category_expertise (
    user_id INTEGER NOT NULL REFERENCES users(id),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    posts_count INTEGER DEFAULT 0,
    solutions_count INTEGER DEFAULT 0,
    expertise_score FLOAT,
    PRIMARY KEY (user_id, category_id)
);
```

### Operational Tables
```sql
-- Fetch history for monitoring
CREATE TABLE fetch_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER REFERENCES categories(id),
    fetch_type TEXT NOT NULL,  -- 'initial', 'update', 'retry'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    topics_fetched INTEGER DEFAULT 0,
    posts_fetched INTEGER DEFAULT 0,
    new_topics INTEGER DEFAULT 0,
    new_posts INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',
    checkpoint_data TEXT
);

-- Checkpoints for recovery
CREATE TABLE fetch_checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetch_history_id INTEGER NOT NULL REFERENCES fetch_history(id),
    checkpoint_type TEXT NOT NULL,
    checkpoint_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Performance Indexes
```sql
CREATE INDEX idx_topics_category ON topics(category_id);
CREATE INDEX idx_topics_last_posted ON topics(last_posted_at);
CREATE INDEX idx_topics_solved ON topics(is_solved);
CREATE INDEX idx_posts_topic ON posts(topic_id);
CREATE INDEX idx_posts_user ON posts(user_id);
CREATE INDEX idx_posts_solution ON posts(is_solution);
```

---

## ⚙️ Configuration

### config.yaml
```yaml
# API Configuration
discourse:
  base_url: "https://community.shopify.dev"
  user_agent: "ShopifyForumAnalyzer/1.0"
  
# Categories (extensible)
categories:
  - id: 18
    slug: "webhooks-and-events"
    name: "Webhooks & Events"
    enabled: true
    priority: 1
  
  # Future categories (disabled initially)
  - id: 12
    slug: "shopify-apis-and-sdks"
    name: "Shopify APIs and SDKs"
    enabled: false
    priority: 2

# Rate Limiting
rate_limiting:
  requests_per_minute: 30
  retry_attempts: 3
  backoff_factor: 2.0
  timeout_seconds: 30

# Database
database:
  type: "sqlite"
  sqlite_path: "data/database/forum.db"
  backup_raw_json: true
  raw_json_path: "data/raw_json/"

# Checkpoints
checkpoints:
  enabled: true
  checkpoint_dir: "data/checkpoints/"

# Text Processing
text_processing:
  min_post_length: 50
  languages: ["en"]
  extract_code: true
  extract_links: true

# Vector Database
embeddings:
  enabled: true
  model: "all-MiniLM-L6-v2"
  vector_db: "chromadb"
  chromadb_path: "data/chromadb/"

# Analysis
analysis:
  similarity_threshold: 0.8
  cross_category_enabled: true

# Monitoring
monitoring:
  health_check_port: 5000
  log_level: "INFO"
```

---

## 🚀 Implementation Roadmap

### Week 1: Foundation & Core Collection

#### Day 1-2: Setup & API Validation
- [ ] Validate Discourse API access (no auth required)
- [ ] Test endpoints and save sample responses
- [ ] Create project structure
- [ ] Initialize Git repository

#### Day 3-4: Database & Models
- [ ] Implement multi-category database schema
- [ ] Create SQLAlchemy models
- [ ] Write migration scripts
- [ ] Add seed data for categories

#### Day 5: Core API Client
- [ ] Build rate-limited async API client
- [ ] Implement exponential backoff
- [ ] Add request/response logging
- [ ] Test with real API

### Week 2: Robust Collection & Recovery

#### Day 6-7: Checkpoint System
- [ ] Implement checkpoint manager
- [ ] Add recovery from failures
- [ ] Test interrupt/resume scenarios
- [ ] Document checkpoint format

#### Day 8-9: Multi-Category Collector
- [ ] Build category-specific collectors
- [ ] Implement parallel collection
- [ ] Add incremental update logic
- [ ] Test with Webhooks & Events category

#### Day 10: Monitoring & Logging
- [ ] Set up structured logging
- [ ] Add Prometheus metrics
- [ ] Create health check endpoints
- [ ] Build collection dashboard

### Week 3: Analysis & Processing

#### Day 11-12: Text Processing
- [ ] Implement HTML cleaning
- [ ] Add code extraction
- [ ] Build error detection
- [ ] Create boilerplate removal

#### Day 13-14: Embeddings & Vector Search
- [ ] Set up ChromaDB
- [ ] Generate embeddings for posts
- [ ] Implement similarity search
- [ ] Add duplicate detection

#### Day 15: Analysis Queries
- [ ] Build trending topics query
- [ ] Create expert identification
- [ ] Add unanswered questions finder
- [ ] Implement cross-category analysis

### Week 4: Production & Deployment

#### Day 16-17: CLI Interface
- [ ] Create Click CLI commands
- [ ] Add Rich progress output
- [ ] Implement export functions
- [ ] Write usage documentation

#### Day 18-19: Docker & Deployment
- [ ] Create Dockerfile
- [ ] Set up docker-compose
- [ ] Add environment configs
- [ ] Test containerized deployment

#### Day 20: Testing & Documentation
- [ ] Write unit tests (80% coverage)
- [ ] Add integration tests
- [ ] Create user documentation
- [ ] Generate API documentation

---

## 🔄 Data Collection Workflow

### Initial Collection
```python
async def initial_collection(category_id: int):
    """Collect all data from a category"""
    
    # 1. Initialize
    checkpoint = load_checkpoint()
    if checkpoint:
        start_page = checkpoint['page']
    else:
        start_page = 0
    
    # 2. Fetch category pages
    all_topics = []
    page = start_page
    while True:
        try:
            data = await fetch_category_page(category_id, page)
            all_topics.extend(data['topic_list']['topics'])
            
            # Save checkpoint
            save_checkpoint({'page': page, 'topics': all_topics})
            
            if not data.get('more_topics_url'):
                break
            page += 1
            
        except Exception as e:
            logger.error(f"Failed at page {page}: {e}")
            raise
    
    # 3. Fetch each topic
    for topic_summary in all_topics:
        if not topic_exists(topic_summary['id']):
            topic_data = await fetch_topic(topic_summary['id'])
            store_topic(topic_data)
            save_checkpoint({'last_topic': topic_summary['id']})
    
    # 4. Generate embeddings
    generate_embeddings_for_category(category_id)
    
    # 5. Clear checkpoint on success
    clear_checkpoint()
```

### Incremental Updates
```python
async def incremental_update(category_id: int):
    """Update only changed topics"""
    
    last_fetch = get_last_successful_fetch(category_id)
    updated_topics = []
    
    # Find updated topics
    page = 0
    while True:
        data = await fetch_category_page(category_id, page)
        
        for topic in data['topic_list']['topics']:
            if parse_date(topic['last_posted_at']) > last_fetch:
                updated_topics.append(topic['id'])
        
        if not data.get('more_topics_url'):
            break
        page += 1
    
    # Fetch only updated topics
    for topic_id in updated_topics:
        topic_data = await fetch_topic(topic_id)
        update_topic_posts(topic_data)
    
    update_embeddings(updated_topics)
```

---

## 📈 Analysis Features

### Core Analysis Capabilities

1. **Trending Topics** - Identify sudden activity spikes
2. **Unanswered Questions** - Find topics without solutions
3. **Expert Contributors** - Identify helpful users
4. **Common Errors** - Pattern detection in error messages
5. **Duplicate Detection** - Find similar issues via embeddings
6. **Resolution Time** - Track time to solution
7. **Cross-Category Patterns** - Issues spanning categories

### Sample Analysis Queries

```python
# Find webhook-specific issues
def analyze_webhook_problems():
    query = """
    SELECT 
        t.title,
        COUNT(DISTINCT p.id) as mentions,
        AVG(t.reply_count) as avg_replies
    FROM topics t
    JOIN posts p ON t.id = p.topic_id
    WHERE t.category_id = 18
    AND (p.raw LIKE '%HMAC%' 
         OR p.raw LIKE '%signature%'
         OR p.raw LIKE '%webhook%')
    GROUP BY t.id
    ORDER BY mentions DESC
    """
    return execute_query(query)

# Cross-category duplicate detection
def find_cross_category_duplicates(threshold=0.85):
    all_embeddings = get_all_topic_embeddings()
    duplicates = []
    
    for i, emb1 in enumerate(all_embeddings):
        for j, emb2 in enumerate(all_embeddings[i+1:], i+1):
            if emb1.category_id != emb2.category_id:
                similarity = cosine_similarity(emb1.vector, emb2.vector)
                if similarity > threshold:
                    duplicates.append({
                        'topic1': emb1.topic_id,
                        'topic2': emb2.topic_id,
                        'similarity': similarity
                    })
    
    return duplicates
```

---

## 🔧 CLI Commands

```bash
# Initial collection for Webhooks & Events
python main.py collect --category webhooks-and-events --mode initial

# Update all enabled categories
python main.py collect --all-enabled --mode update

# Analyze specific category
python main.py analyze --category webhooks-and-events --report trending

# Cross-category analysis
python main.py analyze --mode cross-category --report duplicates

# Semantic search
python main.py search --query "HMAC validation error" --limit 10

# Export data
python main.py export --format parquet --categories all

# Health check
python main.py health --category webhooks-and-events
```

---

## 🚨 Error Handling & Recovery

### Checkpoint System
- Save progress after each page/topic
- Resume from exact failure point
- Archive successful checkpoints
- Support manual checkpoint inspection

### Error Categories
1. **Recoverable** (retry with backoff)
   - Rate limiting (429)
   - Server errors (5xx)
   - Network timeouts

2. **Non-Recoverable** (skip & log)
   - Not found (404)
   - Forbidden (403)
   - Malformed data

3. **Data Errors** (clean & continue)
   - Invalid UTF-8
   - Missing fields
   - Malformed HTML

---

## 📊 Monitoring & Observability

### Key Metrics
```yaml
Collection:
  - topics_per_minute
  - posts_per_minute
  - api_error_rate
  - checkpoint_saves

Storage:
  - database_size
  - query_latency
  - cache_hit_ratio

Analysis:
  - embeddings_generated
  - insights_per_day
  - search_latency
```

### Health Checks
```python
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'database': check_db_connection(),
        'vector_db': check_vector_db(),
        'last_fetch': get_last_fetch_time(),
        'error_rate': get_error_rate_24h()
    }
```

---

## 🔮 Future Enhancements

### Phase 2 (Month 2)
- Add more categories (APIs & SDKs, App Development)
- Implement real-time webhook monitoring
- Build web dashboard
- Add email/Slack notifications

### Phase 3 (Month 3)
- LLM integration for summaries
- Automatic FAQ generation
- Predictive issue detection
- API for external tools

---

## 📋 Deliverables

1. **Source Code** - Modular Python application
2. **Database** - SQLite with migration to PostgreSQL
3. **Documentation** - Setup, usage, API reference
4. **Docker Setup** - Production-ready containers
5. **Analysis Reports** - Sample insights and visualizations
6. **Test Suite** - 80% coverage minimum

---

## ✅ Implementation Checklist

### Immediate Actions (Week 1)
- [ ] Test Discourse API access
- [ ] Set up project repository
- [ ] Create database schema
- [ ] Build API client with rate limiting
- [ ] Implement basic collection for Webhooks & Events

### Core Features (Week 2-3)
- [ ] Add checkpoint/recovery system
- [ ] Implement incremental updates
- [ ] Build text processing pipeline
- [ ] Set up vector database
- [ ] Create analysis queries

### Production Ready (Week 4)
- [ ] Complete CLI interface
- [ ] Add monitoring/health checks
- [ ] Write comprehensive tests
- [ ] Create Docker deployment
- [ ] Document everything

---

## 🎯 Success Criteria

- **Collection**: 100% of Webhooks & Events topics collected
- **Updates**: Daily incremental updates running automatically
- **Analysis**: Weekly insight reports generated
- **Performance**: <100ms query response, <5min update cycle
- **Reliability**: 99.9% uptime, zero data loss
- **Scalability**: Ready for 5+ categories without refactoring

---

## 📝 Notes

- Start with Webhooks & Events (category 18)
- Design for multi-category from day one
- Prioritize data quality over speed
- Keep raw JSON backups
- Plan for PostgreSQL migration
- Consider GDPR/privacy from start