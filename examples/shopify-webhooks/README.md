# Shopify Webhooks & Events Forum Analysis Example


**Terminology Note:** This example analyzes the Shopify "Webhooks & Events" **category** (a Discourse forum section) to identify problem **classifications** (LLM-assigned types). See the [main glossary](../../README.md#glossary) for terminology definitions.

This example demonstrates how to use the Discourse Forum Analyzer to collect and analyze discussions from Shopify's developer forum, specifically focusing on the Webhooks & Events category.

## What This Example Demonstrates

- **Data Collection**: Scraping forum posts, topics, and metadata from a Discourse forum
- **LLM-Powered Analysis**: Using Claude to analyze developer pain points and sentiment
- **Theme Identification**: Discovering common patterns and issues in forum discussions
- **Interactive Querying**: Using natural language to explore forum data

The analysis focuses on the [Shopify Webhooks & Events category](https://community.shopify.dev/c/webhooks-and-events/18), which contains developer discussions about webhook reliability, event handling, and integration challenges.

## Prerequisites

- **Python 3.10 or higher**
- **Anthropic API key** (optional, only needed for LLM analysis features)
  - Get your API key from [console.anthropic.com](https://console.anthropic.com)
  - Free tier available; this example costs approximately $0.05 to run

## Quick Start

```bash
# From the examples/shopify-webhooks directory, navigate to project root
cd ../..

# Install the tool and dependencies
pip install -e .

# Copy the example configuration
cp examples/shopify-webhooks/config.yaml config/config.yaml

# Add your Anthropic API key to config/config.yaml (optional, only for LLM features)
# Edit config/config.yaml and add your API key to the llm_analysis.api_key field

# Initialize the database
forum-analyzer init-db

# Collect forum data (takes ~5 minutes)
forum-analyzer collect

# Optional: Discover categories from the data (RECOMMENDED before LLM analysis)
forum-analyzer themes --min-topics 3

# Optional: Analyze with LLM using discovered categories (takes ~10 minutes, requires API key)
forum-analyzer llm-analyze

# Optional: Query the data with natural language (requires LLM analysis)
forum-analyzer ask "What are the most critical webhook reliability issues?"
```

## Detailed Setup and Usage

### Step 1: Installation

For complete installation instructions, see the [main README](../../README.md#installation). Quick version:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/yourusername/discourse-forum-analyzer.git
cd discourse-forum-analyzer

# Install with pip
pip install -e .
```

### Step 2: Configuration

Copy the example configuration file:

```bash
cp examples/shopify-webhooks/config.yaml config/config.yaml
```

The configuration file includes:

- **Discourse API Settings**: Forum URL and category to analyze
  - `base_url`: The Discourse forum URL (`https://community.shopify.dev`)
  - `category_slug`: URL-friendly category name (`webhooks-and-events`)
  - `category_id`: Numeric category identifier (18)

- **Rate Limiting**: Protects against API throttling
  - `requests_per_second`: 1.0 (respects forum API limits)
  - `max_retries`: 3 attempts for failed requests
  - `backoff_factor`: Exponential backoff multiplier

- **Database Configuration**: Where collected data is stored
  - `path`: SQLite database location (`data/database/forum_data.sqlite`)

- **Checkpoint System**: Enables resumable data collection
  - `enabled`: true (can resume interrupted collections)
  - `directory`: Checkpoint file storage location

- **LLM Analysis Configuration** (optional):
  - `api_key`: Your Anthropic API key (leave empty if not using LLM features)
  - `model`: Claude model to use (`claude-opus-4-20250514`)
  - `batch_size`: Number of posts per analysis batch
  - `temperature`: 0.0 for consistent, deterministic analysis

**Adding Your API Key** (for LLM features):

1. Get an API key from [console.anthropic.com](https://console.anthropic.com)
2. Edit `config/config.yaml`
3. Add your key to the `llm_analysis.api_key` field:
   ```yaml
   llm_analysis:
     api_key: "sk-ant-..."  # Your actual API key here
   ```

### Step 3: Initialize Database

Create the SQLite database schema:

```bash
forum-analyzer init-db
```

This creates:
- `data/database/forum_data.sqlite` - Main database file
- Database tables for categories, topics, posts, users, and analysis results

### Step 4: Collect Forum Data

Scrape the forum data:

```bash
forum-analyzer collect
```

**What happens:**
- Fetches all topics from the Webhooks & Events category
- Downloads each topic's posts and metadata
- Stores data in the SQLite database
- Creates checkpoints for resumability

**Expected timing:**
- ~5 minutes for ~100 topics with ~500 posts
- Respects rate limits (1 request/second)

**Resuming interrupted collections:**
The tool automatically saves checkpoints. If collection is interrupted, simply run `forum-analyzer collect` again to resume from the last checkpoint.

**Collection output:**
```
Starting collection process...
Fetching category: webhooks-and-events
Found 98 topics in category
Processing topics: 100%|████████████| 98/98
Collected 487 posts from 98 topics
Collection complete!

View collection report:
  forum-analyzer report collection
```

### Step 5: Discover Categories (Optional but Recommended)

Discover natural categories from the collected data:

```bash
forum-analyzer themes --min-topics 3
```

**What it does:**
- Analyzes topics to identify common problem themes
- Groups similar issues together
- Creates categories based on actual forum content
- Enables better categorization in LLM analysis

**Note:** Running this before LLM analysis allows Claude to use discovered themes as categories, producing more relevant and accurate categorization than generic categories.

### Step 6: LLM Analysis (Optional)

Analyze the collected data with Claude using discovered categories:

```bash
forum-analyzer llm-analyze
```

**Requirements:**
- Anthropic API key configured in `config.yaml`
- Collected forum data in database

**What it does:**
- Uses discovered themes as categories (if themes step was run)
- Falls back to free-form categorization if no themes exist
- Analyzes each topic for core problems and severity
- Identifies technical issues and patterns
- Stores analysis in database for querying

**Expected timing:**
- ~10 minutes for ~500 posts
- Processes posts in batches of 10

**Estimated cost:**
- ~$0.05 for this example (depends on post length and model)
- Uses Claude Opus 4 for high-quality analysis

**Analysis output:**
```
Starting LLM analysis...
Processing posts: 100%|████████████| 487/487
Analysis complete!

View analysis report:
  forum-analyzer report llm
```

### Step 7: Explore Results

#### View Reports

```bash
# Collection statistics and overview
forum-analyzer report collection

# LLM analysis insights (requires llm-analyze)
forum-analyzer report llm
```

#### Identify Common Themes

```bash
forum-analyzer themes
```

Discovers recurring patterns like:
- Webhook reliability issues
- Event delivery failures
- Rate limiting concerns
- Authentication problems

#### Query with Natural Language

```bash
# Ask questions about the forum data
forum-analyzer ask "What are the most common webhook problems?"
forum-analyzer ask "Which issues are marked as urgent?"
forum-analyzer ask "What features do developers request most?"
```

#### Direct Database Access

The SQLite database is at `data/database/forum_data.sqlite`. You can query it directly:

```bash
sqlite3 data/database/forum_data.sqlite

# Example queries
SELECT COUNT(*) FROM topics;
SELECT COUNT(*) FROM posts;
SELECT title, view_count FROM topics ORDER BY view_count DESC LIMIT 10;
```

**Database schema:**
- `categories` - Forum categories
- `topics` - Discussion threads
- `posts` - Individual posts/replies
- `users` - Forum participants
- `llm_post_analyses` - LLM analysis results (if analysis was run)

## Results from This Example

This example includes pre-generated reports from analyzing the Shopify Webhooks & Events forum:

- **[Collection Report](COLLECTION_REPORT.md)**: Data collection statistics, most active topics, top contributors, and time-based patterns
- **[LLM Analysis Report](LLM_ANALYSIS_REPORT.md)**: Sentiment analysis, pain points, critical issues, and feature requests

### Key Findings Summary

From the LLM analysis of 487 posts across 98 topics:

**Top Pain Points:**
1. Webhook delivery reliability (mentioned in 45% of posts)
2. Event ordering and timing issues
3. Missing or delayed webhook events
4. Rate limiting and throttling
5. Authentication and security concerns

**Sentiment Distribution:**
- Frustrated: 32%
- Neutral: 41%
- Satisfied: 27%

**Most Critical Issues:**
- Missing order fulfillment webhooks
- Duplicate webhook deliveries
- Webhook timeout problems
- Inconsistent event triggers

## Customization

### Analyzing Different Categories

To analyze a different Discourse category, update `config.yaml`:

```yaml
discourse:
  base_url: "https://community.shopify.dev"
  category_slug: "api-development"  # Change this
  category_id: 12                    # And this
```

**Finding category ID and slug:**
1. Visit the category page in your browser
2. The URL format is: `https://forum.example.com/c/category-slug/ID`
3. Example: `https://community.shopify.dev/c/webhooks-and-events/18`
   - Slug: `webhooks-and-events`
   - ID: `18`

### Analyzing Different Forums

To analyze a completely different Discourse forum:

```yaml
discourse:
  base_url: "https://discuss.example.com"  # Change the forum URL
  category_slug: "support"
  category_id: 5
```

### Adjusting Rate Limiting

If you encounter rate limiting errors or want to be more conservative:

```yaml
rate_limiting:
  requests_per_second: 0.5  # Slower (2 seconds between requests)
  max_retries: 5            # More retry attempts
  backoff_factor: 3.0       # Longer waits between retries
```

### Modifying LLM Analysis

**Note**: The LLM analysis prompts are currently hardcoded in the source code. To modify them:

1. Edit `src/forum_analyzer/analyzer/llm_analyzer.py`
2. Find the `_analyze_post_batch` method
3. Modify the system prompt and user prompt as needed
4. Reinstall: `pip install -e .`

**Future enhancement**: Configurable prompts through config file (see [known limitations](../../README.md#known-limitations))

## Troubleshooting

### "Database is locked" Error

**Problem**: SQLite database is locked by another process

**Solution**:
```bash
# Find and close any open database connections
lsof data/database/forum_data.sqlite

# Or remove the lock file (if safe)
rm data/database/forum_data.sqlite-wal
rm data/database/forum_data.sqlite-shm
```

### "Rate limited by API" Error

**Problem**: Making requests too quickly

**Solution**:
- The tool should automatically retry with backoff
- If persisting, reduce `requests_per_second` in config
- Wait a few minutes and try again

### "Invalid API key" Error (LLM Analysis)

**Problem**: Anthropic API key is missing or incorrect

**Solution**:
1. Verify your API key at [console.anthropic.com](https://console.anthropic.com)
2. Check `config/config.yaml` has the correct key in `llm_analysis.api_key`
3. Ensure no extra spaces or quotes around the key

### Collection Interrupted

**Problem**: Collection stopped before completing

**Solution**:
- Simply run `forum-analyzer collect` again
- The checkpoint system will resume from where it left off
- Check `data/checkpoints/` for checkpoint files

### No Results from LLM Analysis

**Problem**: `llm-analyze` completes but queries return no results

**Solution**:
1. Verify analysis completed: `forum-analyzer report llm`
2. Check database: `sqlite3 data/database/forum_data.sqlite "SELECT COUNT(*) FROM llm_post_analyses;"`
3. Re-run analysis if needed: `forum-analyzer llm-analyze --force`

### Import Errors

**Problem**: `ModuleNotFoundError` when running commands

**Solution**:
```bash
# Reinstall in editable mode
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

## Next Steps

After completing this example:

1. **Explore the data**: Try different queries with `forum-analyzer ask`
2. **Analyze other categories**: Update config to study different topics
3. **Export results**: Query the database to create custom reports
4. **Automate collection**: Set up scheduled runs to track trends over time

## Need Help?

- Check the [main README](../../README.md) for additional documentation
- Review the [project summary](.plan/PROJECT_SUMMARY.md) for architecture details
- Open an issue on GitHub for bugs or feature requests

## License

This example is part of the Discourse Forum Analyzer project. See the main repository for license information.