# Shopify Developer Forum Analyzer

A Python tool for scraping and analyzing the Shopify Developer Forum (Discourse-based platform).

## Project Status

**Phase 1: Complete ✅**
- Data collection system fully operational
- 271 topics, 1,201 posts collected from Shopify Webhooks & Events forum
- Basic SQL-based analysis implemented

**Phase 2: In Progress 🔄**
- LLM-based problem analysis using Claude API
- Identifying common developer problems and themes

See [`.plan/PROGRESS_AND_NEXT_STEPS.md`](.plan/PROGRESS_AND_NEXT_STEPS.md) for detailed status.

## Documentation

- [`.plan/`](.plan/) - Planning documents and progress tracking
- [`.plan/reports/`](.plan/reports/) - Technical reports and validation docs
- [`reports/`](reports/) - Analysis outputs and generated reports
- [`schema.sql`](schema.sql) - Database schema reference (see models.py for implementation)

## Features

- **Async API Client**: Rate-limited HTTP client with retry logic
- **Database Storage**: SQLite database with SQLAlchemy ORM
- **Resumable Scraping**: Checkpoint system for fault-tolerant collection
- **Multi-Category Support**: Track multiple forum categories
- **Configuration Management**: YAML-based configuration with Pydantic validation

## Project Structure

```
shopify-dev-forum-analyzer/
├── src/
│   └── forum_analyzer/           # Main package
│       ├── collector/             # Data collection
│       │   ├── api_client.py     # API client with rate limiting
│       │   ├── checkpoint_manager.py
│       │   └── models.py         # SQLAlchemy models
│       ├── analyzer/              # Analysis (to be implemented)
│       └── config/                # Configuration
│           └── settings.py
├── config/
│   └── config.yaml               # Configuration file
├── data/
│   ├── database/                 # SQLite database
│   ├── checkpoints/              # Checkpoint files
│   └── samples/                  # Sample API responses
├── tests/                        # Test suite
├── scripts/
│   └── init_db.py               # Database initialization
├── schema.sql                    # Database schema
├── pyproject.toml               # Modern Python packaging
├── setup.py                     # Setup script
└── requirements.txt             # Dependencies
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Install Package

```bash
# Clone the repository
git clone <repository-url>
cd shopify-dev-forum-analyzer

# Install in editable mode
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### 1. Install the Package

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode
pip install -e .
```

This installs the `forum-analyzer` CLI command.

### 2. Initialize Database

```bash
forum-analyzer init-db
```

This creates the SQLite database at `data/database/forum.db` with all required tables.

### 3. Configure Settings

Copy the example configuration and add your API key:

```bash
cp config/config.example.yaml config/config.yaml
```

Edit `config/config.yaml`:

```yaml
# API Settings
api:
  base_url: "https://community.shopify.dev"
  rate_limit: 1.0
  timeout: 30.0
  max_retries: 3

# Database
database:
  url: "sqlite:///data/database/forum.db"

# Categories to scrape
categories:
  - id: 18
    name: "Webhooks and Events"
    slug: "webhooks-and-events"

# LLM Analysis (get API key from https://console.anthropic.com)
llm_analysis:
  api_key: "your-anthropic-api-key-here"
  model: "claude-opus-4"
  batch_size: 10
  max_tokens: 4096
  temperature: 0.0
```

### 4. Collect Forum Data

```bash
# Collect all topics and posts from default category
forum-analyzer collect

# Collect from a specific category
forum-analyzer collect --category-slug api-discussions --category-id 25

# Incremental update (fetch only new content)
forum-analyzer update

# Check collection status
forum-analyzer status
```

## CLI Commands

The CLI provides several commands for managing forum data collection:

### `forum-analyzer init-db`

Initialize the database schema.

```bash
# Create database
forum-analyzer init-db

# Force reinitialize (WARNING: deletes all data)
forum-analyzer init-db --force
```

### `forum-analyzer collect`

Collect all topics and posts from a category.

**Options:**
- `--category-slug` - Category slug to collect (default: webhooks-and-events)
- `--category-id` - Category ID (default: 18)
- `--resume/--no-resume` - Resume from checkpoint or start fresh (default: resume)
- `--page-limit` - Limit number of pages to collect (for testing, default: None = no limit)

**Examples:**
```bash
# Collect with defaults
forum-analyzer collect

# Collect specific category
forum-analyzer collect --category-slug api-discussions --category-id 25

# Start fresh, ignore checkpoints
forum-analyzer collect --no-resume

# Collect only first 2 pages (for testing)
forum-analyzer collect --page-limit 2
```

### `forum-analyzer update`

Incrementally update existing data with new posts.

**Options:**
- `--category-slug` - Category slug to update (default: webhooks-and-events)
- `--category-id` - Category ID (default: 18)

**Examples:**
```bash
# Update with defaults
forum-analyzer update

# Update specific category
forum-analyzer update --category-slug api-discussions --category-id 25
```

### `forum-analyzer status`

Show collection status and database statistics.

```bash
forum-analyzer status
```

Displays:
- Number of categories, topics, posts, users
- Latest topic timestamp
- Database size
- Active checkpoints

### `forum-analyzer clear-checkpoints`

Clear checkpoints to restart collection from beginning.

**Options:**
- `--category-slug` - Clear specific category (optional)

**Examples:**
```bash
# Clear all checkpoints
forum-analyzer clear-checkpoints

# Clear specific category checkpoint
forum-analyzer clear-checkpoints --category-slug webhooks-and-events
```

### `forum-analyzer llm-analyze`

Analyze forum topics using Claude API to identify problems.

**Options:**
- `--limit` - Maximum number of topics to analyze
- `--force` - Re-analyze already analyzed topics
- `--topic-id` - Analyze a specific topic by ID

**Examples:**
```bash
# Analyze all unanalyzed topics
forum-analyzer llm-analyze

# Analyze up to 50 topics
forum-analyzer llm-analyze --limit 50

# Re-analyze all topics
forum-analyzer llm-analyze --force

# Analyze a specific topic
forum-analyzer llm-analyze --topic-id 66
```

**Output:** For each topic, extracts:
- Core problem description
- Category (webhook_delivery, webhook_configuration, etc.)
- Severity (critical, high, medium, low)
- Key technical terms
- Root cause analysis

### `forum-analyzer themes`

Identify common problem themes across analyzed topics.

**Options:**
- `--min-topics` - Minimum number of topics to form a theme (default: 3)

**Examples:**
```bash
# Identify themes (minimum 3 topics per theme)
forum-analyzer themes

# Require more topics per theme
forum-analyzer themes --min-topics 5
```

**Output:** Groups related problems into themes with:
- Theme name and description
- Affected topic IDs
- Severity distribution
- Topic count

### `forum-analyzer ask`

Ask natural language questions about the analyzed forum data.

**Arguments:**
- `question` - Your question about the forum data

**Options:**
- `--context-limit` - Max topics to include in context

**Examples:**
```bash
# Ask a question
forum-analyzer ask "What are the most common webhook delivery failures?"

# Limit context for faster responses
forum-analyzer ask "What authentication issues exist?" --context-limit 20
```

## Programmatic Usage

### Use the API Client

```python
import asyncio
from forum_analyzer.collector.api_client import ForumAPIClient

async def main():
    async with ForumAPIClient(rate_limit=1.0) as client:
        # Fetch category metadata
        category = await client.fetch_category_metadata(18)
        print(f"Category: {category['name']}")
        
        # Fetch topics
        page = await client.fetch_category_page(18, page=0)
        print(f"Topics: {len(page['topic_list']['topics'])}")
        
        # Fetch specific topic
        topic = await client.fetch_topic(66)
        print(f"Topic: {topic['title']}")

asyncio.run(main())
```

## Database Schema

The database includes tables for:

- **categories**: Forum categories
- **topics**: Discussion topics
- **posts**: Individual posts
- **checkpoints**: Scraping progress tracking
- **users**: User statistics (derived from posts)

See [`schema.sql`](schema.sql) for the complete schema.

## Configuration

### Settings

Configuration is managed through [`config/config.yaml`](config/config.yaml) and loaded using Pydantic settings in [`src/forum_analyzer/config/settings.py`](src/forum_analyzer/config/settings.py:1).

Access settings in code:

```python
from forum_analyzer.config import get_settings

settings = get_settings()
print(settings.api.rate_limit)
print(settings.database.url)
```

### Environment Variables

Settings can also be overridden with environment variables (Pydantic settings pattern).

## API Client Features

### Rate Limiting

The [`ForumAPIClient`](src/forum_analyzer/collector/api_client.py:45) includes a token bucket rate limiter:

```python
async with ForumAPIClient(rate_limit=1.0) as client:
    # Requests are automatically rate-limited
    data = await client.fetch_category_page(18)
```

### Retry Logic

Automatic exponential backoff retry for failed requests using tenacity.

### Checkpoint System

The [`CheckpointManager`](src/forum_analyzer/collector/checkpoint_manager.py:16) enables resumable scraping:

```python
from sqlalchemy.orm import Session
from forum_analyzer.collector import CheckpointManager

checkpoint_mgr = CheckpointManager(session, checkpoint_dir=Path("data/checkpoints"))

# Save checkpoint
checkpoint_mgr.save_checkpoint(
    category_id=18,
    checkpoint_type="category_page",
    last_page=5,
    total_processed=150
)

# Resume from checkpoint
checkpoint = checkpoint_mgr.get_checkpoint(18, "category_page")
if checkpoint:
    start_page = checkpoint.last_page + 1
```

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=forum_analyzer

# Run specific test file
pytest tests/test_api_client.py
```

## Development

### Code Style

The project uses:

- **black**: Code formatting (79 char line length)
- **flake8**: Linting
- **isort**: Import sorting
- **mypy**: Type checking

### Running Linters

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

## API Validation

API validation results are documented in [`.plan/reports/API_VALIDATION_REPORT.md`](.plan/reports/API_VALIDATION_REPORT.md).

## Next Steps

This foundation provides:

- ✅ Proper Python package structure
- ✅ API client with rate limiting
- ✅ Database schema and ORM models
- ✅ Configuration system
- ✅ Checkpoint management
- ✅ Basic test structure

**To implement next:**

1. ✅ Collection orchestrator (use API client + checkpoint manager)
2. ✅ CLI interface
3. Data analysis modules
4. Reporting and visualization

## License

MIT

## Contributing

Contributions welcome! Please ensure:

1. Code passes all tests
2. Code is formatted with black
3. Type hints are included
4. Documentation is updated