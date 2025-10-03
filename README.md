# Discourse Forum Analyzer

A Python tool for collecting and analyzing discussions from Discourse-based forums using LLM-powered analysis.

## Overview

This tool automates the collection of forum data from Discourse forums (which provide JSON representations of pages) and uses Claude AI to analyze discussions, identify common problems, and extract insights. While initially built to analyze Shopify's webhook forum, it works with any publicly accessible Discourse installation.

**New to this tool?** It's recommended to read the [Glossary](#glossary) to understand key terminology.

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
git clone https://github.com/your-repo/discourse-forum-analyzer.git
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

Edit `config/config.yaml` with your forum's details and your Anthropic API key:
```yaml
discourse:
  base_url: "https://community.shopify.dev"
  category_slug: "webhooks-and-events"
  category_id: 18

llm_analysis:
  api_key: "your-anthropic-api-key"
  # ... other settings
```

## Usage

### Recommended Workflow

The recommended workflow ensures the most accurate and relevant analysis by first discovering themes from your specific data.

```bash
# 1. Initialize the database
forum-analyzer init-db

# 2. Collect forum data
forum-analyzer collect

# 3. Discover natural categories from the data
forum-analyzer themes discover --min-topics 3

# 4. Analyze all topics using the discovered categories
forum-analyzer llm-analyze

# 5. Ask questions about your analysis
forum-analyzer ask "What are the main authentication issues?"
```

### All Commands

A full list of commands and their options are available below.

#### Database Initialization
```bash
# Creates the database schema
forum-analyzer init-db
```

#### Data Collection
```bash
# Collect from the category in your config
forum-analyzer collect

# Collect from a specific category
forum-analyzer collect --category-slug api-discussions --category-id 25

# Collect with a page limit (for testing)
forum-analyzer collect --page-limit 2
```

#### Incremental Updates
```bash
# Fetch only new/updated content
forum-analyzer update
```

#### Status
```bash
# View collection status and statistics
forum-analyzer status
```

#### Theme Management
```bash
# Discover common themes (minimum 3 topics per theme)
forum-analyzer themes discover

# Analyze more topics for better pattern discovery
forum-analyzer themes discover --context-limit 100

# List themes already discovered
forum-analyzer themes list

# Delete all themes (prompts for confirmation)
forum-analyzer themes clean
```

#### Topic Analysis
```bash
# Analyze all unanalyzed topics
forum-analyzer llm-analyze

# Re-analyze topics that have already been analyzed
forum-analyzer llm-analyze --force

# Analyze a specific topic by its ID
forum-analyzer llm-analyze --topic-id 66
```

#### Querying
```bash
# Ask questions about the analyzed data
forum-analyzer ask "What are the most common authentication issues?"
```

#### Maintenance
```bash
# Clear all collection checkpoints
forum-analyzer clear-checkpoints
```

## Technical Details

### Architecture

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

### Project Structure
```
discourse-forum-analyzer/
├── src/forum_analyzer/
│   ├── analyzer/              # LLM analysis
│   ├── collector/             # Data collection
│   ├── config/
│   └── cli.py
├── config/
│   ├── config.yaml
│   └── config.example.yaml
├── data/
│   ├── database/
│   └── checkpoints/
└── tests/
```

### Database Schema
The schema is managed by SQLAlchemy models and is split into three categories:

- **Forum Data Tables**: `categories`, `topics`, `posts`, `users`
- **Analysis Tables**: `llm_analysis`, `problem_themes`
- **Operational Tables**: `checkpoints`, `fetch_history`

The schema auto-migrates when using LLM analysis features.

## Example Application: Shopify Developer Forum

This tool was demonstrated by analyzing Shopify's webhook discussions.

- **Topics**: 271
- **Posts**: 1,201
- **Users**: 324
- **Date Range**: September 2024 - October 2025

**Example analysis results:**
- 15 distinct problem themes identified
- 18 critical issues found
- Top issue: Configuration challenges (25.1% of topics)

See the complete example analysis: [examples/shopify-webhooks/LLM_ANALYSIS_REPORT.md](examples/shopify-webhooks/LLM_ANALYSIS_REPORT.md)

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

## Troubleshooting

**Rate Limiting**
- Adjust `rate_limit` in config.yaml (default: 1 req/sec).

**Database Locked**
- Only one instance can run at a time.
- Clear stale checkpoints: `forum-analyzer clear-checkpoints`.

**LLM Analysis Errors**
- Verify your Anthropic API key is valid and has credit.
- Use the `--limit` flag for testing with smaller datasets.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Appendix: Glossary

Understanding the terminology used in this tool:

### Discourse Forum Terms

**Category**  
A top-level organizational unit in Discourse forums (e.g., "Webhooks & Events").

**Topic**  
A discussion thread within a category.

**Post**  
An individual message within a topic. The first post is the topic starter; subsequent posts are replies.

### Analysis Terms

**Classification**
The LLM-assigned type of problem or discussion in a topic (e.g., "webhook_delivery", "authentication").

**Theme**  
A higher-level pattern grouping multiple related topics (e.g., "Webhook Delivery Failures").

**Severity**  
The urgency/impact level assigned to a topic (critical, high, medium, low).

### Workflow Terms

**Collection**  
The process of downloading forum data (`forum-analyzer collect`).

**Analysis**  
The process of using the LLM to extract insights from topics (`forum-analyzer llm-analyze`).

**Theme Identification**  
The process of grouping topics into common patterns (`forum-analyzer themes discover`).