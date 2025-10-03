# Discourse Forum Analyzer

A Python tool for collecting and analyzing discussions from Discourse-based forums using LLM-powered analysis.

## Overview

This tool automates the collection of forum data from Discourse forums (which provide JSON representations of pages) and uses Claude AI to analyze discussions, identify common problems, and extract insights. While initially built to analyze Shopify's webhook forum, it works with any publicly accessible Discourse installation.

## Features

### Data Collection
- Automated scraping via Discourse JSON endpoints
- Rate-limited HTTP client with retry logic
- Checkpoint-based recovery for interrupted operations
- Incremental updates (collect only new content)
- SQLite storage with SQLAlchemy ORM

### LLM Analysis
- Problem extraction from discussion threads
- Automatic categorization by topic type
- Severity assessment (critical, high, medium, low)
- Theme identification across multiple discussions
- Natural language query interface

### Reporting
- Markdown reports with statistics
- Problem theme grouping
- JSON and CSV export options

## Requirements

- Python 3.10 or higher
- Anthropic API key (for LLM analysis features)

## Installation

```bash
git clone <repository-url>
cd discourse-forum-analyzer

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -e .
```

## Configuration

Copy the example configuration:
```bash
cp config/config.example.yaml config/config.yaml
```

Edit `config/config.yaml`:
```yaml
api:
  base_url: "https://your-discourse-site.com"
  rate_limit: 1.0  # requests per second
  timeout: 30.0
  max_retries: 3

database:
  url: "sqlite:///data/database/forum.db"

categories:
  - id: 18
    name: "Category Name"
    slug: "category-slug"

llm_analysis:
  api_key: "your-anthropic-api-key"  # Get from https://console.anthropic.com
  model: "claude-opus-4"
  batch_size: 10
  max_tokens: 4096
  temperature: 0.0
```

## Usage

### Initialize Database
```bash
forum-analyzer init-db
```

### Collect Forum Data
```bash
# Collect from default category
forum-analyzer collect

# Collect from specific category
forum-analyzer collect --category-slug api-discussions --category-id 25

# Collect with page limit (for testing)
forum-analyzer collect --page-limit 2

# Disable checkpoint resume
forum-analyzer collect --no-resume
```

### Update Existing Data
```bash
# Fetch only new/updated content
forum-analyzer update

# Update specific category
forum-analyzer update --category-slug category-name
```

### View Collection Status
```bash
forum-analyzer status
```

### Analyze Topics
```bash
# Analyze all unanalyzed topics
forum-analyzer llm-analyze

# Analyze limited number
forum-analyzer llm-analyze --limit 50

# Re-analyze existing
forum-analyzer llm-analyze --force

# Analyze specific topic
forum-analyzer llm-analyze --topic-id 66
```

### Identify Themes
```bash
# Find common themes (minimum 3 topics per theme)
forum-analyzer themes

# Require more topics per theme
forum-analyzer themes --min-topics 5
```

### Query Data
```bash
# Ask questions about the data
forum-analyzer ask "What are the most common authentication issues?"
forum-analyzer ask "Show critical problems" --context-limit 20
```

### Clear Checkpoints
```bash
# Clear all checkpoints
forum-analyzer clear-checkpoints

# Clear specific category
forum-analyzer clear-checkpoints --category-slug webhooks-and-events
```

## Architecture

```
┌─────────────────────┐
│  Discourse Forum    │
│  (JSON endpoints)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Rate-Limited      │
│   HTTP Client       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Checkpoint        │
│   Manager           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   SQLite Database   │
│   (SQLAlchemy)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐     ┌──────────────┐
│   LLM Analyzer      │────▶│  Claude API  │
└──────────┬──────────┘     └──────────────┘
           │
           ▼
┌─────────────────────┐
│  Reports & Themes   │
└─────────────────────┘
```

### Technology Stack
- **Language**: Python 3.10+
- **Database**: SQLite with SQLAlchemy
- **HTTP**: httpx (async)
- **LLM**: Claude API (Anthropic)
- **CLI**: Click
- **Config**: Pydantic + YAML

## Project Structure

```
discourse-forum-analyzer/
├── src/forum_analyzer/
│   ├── analyzer/              # LLM analysis
│   │   ├── llm_analyzer.py
│   │   └── reporter.py
│   ├── collector/             # Data collection
│   │   ├── api_client.py
│   │   ├── checkpoint_manager.py
│   │   ├── models.py
│   │   └── orchestrator.py
│   ├── config/
│   │   └── settings.py
│   └── cli.py
├── config/
│   ├── config.yaml
│   └── config.example.yaml
├── data/
│   ├── database/
│   └── checkpoints/
└── tests/
```

## Database Schema

### Forum Data Tables
- `categories` - Forum categories being tracked
- `topics` - Discussion threads with metadata
- `posts` - Individual posts and replies
- `users` - Forum user information

### Analysis Tables
- `llm_analysis` - Per-topic analysis results
- `problem_themes` - Grouped problem patterns

### Operational Tables
- `checkpoints` - Recovery state
- `fetch_history` - Collection audit trail

The schema auto-migrates when using LLM analysis features.

## Example Application: Shopify Developer Forum

This tool was demonstrated by analyzing Shopify's webhook discussions as an example. The same approach works for any Discourse forum.

**Example dataset:**
- **Topics**: 271
- **Posts**: 1,201
- **Users**: 324
- **Date Range**: September 2024 - October 2025

**Example analysis results:**
- 15 distinct problem themes identified
- 18 critical issues found
- Top issue: Configuration challenges (25.1% of topics)

See complete example analysis: [examples/shopify-webhooks/LLM_ANALYSIS_REPORT.md](examples/shopify-webhooks/LLM_ANALYSIS_REPORT.md)

### Performance Metrics
- API cost: $0.05 total (~$0.0002 per topic)
- Processing time: ~10 minutes for 271 topics
- Success rate: 100% (0 failures)

## Development

### Running Tests
```bash
pytest
pytest --cov=forum_analyzer
pytest tests/test_api_client.py
```

### Code Quality
```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

### Development Installation
```bash
pip install -e ".[dev]"
pre-commit install
```

## Troubleshooting

**Rate Limiting**
- Adjust `rate_limit` in config.yaml (default: 1 req/sec)
- Tool automatically respects API limits

**Database Locked**
- Only one instance can run at a time
- Clear stale checkpoints: `forum-analyzer clear-checkpoints`

**API Errors**
- Verify Discourse site is publicly accessible
- Check base_url in config.yaml
- Ensure category ID exists

**LLM Analysis Errors**
- Verify Anthropic API key is valid
- Check API quota and billing
- Use `--limit` flag for testing with smaller datasets

## API Requirements

This tool requires:
- Public Discourse forum (no authentication required)
- Accessible JSON endpoints (Discourse provides JSON representations by appending `.json` to URLs):
  - `/c/{category_id}.json` - Category listings
  - `/t/{topic_id}.json` - Topic details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run linters and tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Documentation

- [API Validation](.plan/API_VALIDATION_REPORT.md)
- [Project Planning](.plan/)