# Shopify Webhooks & Events Forum Analysis Example

**Terminology Note:** This example analyzes the Shopify "Webhooks & Events" **category** (a Discourse forum section). See the [main glossary](../../README.md#appendix-glossary) for terminology definitions.

This example demonstrates analyzing the [Shopify Webhooks & Events forum](https://community.shopify.dev/c/webhooks-and-events/18) to identify webhook reliability issues, event handling challenges, and integration problems.

## What You'll Learn

- How to initialize a project for a specific Discourse forum category
- Collecting forum data with checkpoint-based recovery
- Discovering themes from real forum discussions
- LLM-powered analysis of developer pain points
- Querying results with natural language

## Prerequisites

See the [main README](../../README.md#requirements) for installation instructions.

**You'll need:**
- Python 3.10+
- Anthropic API key (optional, only for LLM features - costs ~$0.05 for this example)

## Quick Start

```bash
# 1. Install the tool
pip install -e .

# 2. Create and initialize project
mkdir shopify-webhooks-analysis
cd shopify-webhooks-analysis
forum-analyzer init

# When prompted, enter:
#   Forum URL: https://community.shopify.dev
#   Category path: c
#   Category ID: 18
#   API key: (your key, or skip for collection-only)

# 3. Collect data (~5 minutes)
forum-analyzer collect

# 4. Discover themes and analyze (requires API key)
forum-analyzer themes discover
forum-analyzer llm-analyze

# 5. Query results
forum-analyzer ask "What are the most critical webhook issues?"
```

For the complete workflow, see the [main README's Quick Start](../../README.md#quick-start).

## Step-by-Step Guide

### 1. Project Setup

See [Project Initialization](../../README.md#1-initialize-a-new-project) in the main README.

**For this example:**
```bash
mkdir shopify-webhooks-analysis
cd shopify-webhooks-analysis
forum-analyzer init
```

Use these values when prompted:
- **Forum URL**: `https://community.shopify.dev`
- **Category path**: `c`
- **Category ID**: `18`
- **API key**: Your Anthropic key (or skip for collection-only)

### 2. Data Collection

See [Data Collection](../../README.md#data-collection) in the main README for all options.

```bash
forum-analyzer collect
```

**Expected for this category:**
- ~270 topics
- ~1,200 posts
- ~5-10 minutes collection time

### 3. Theme Discovery

See [Theme Management](../../README.md#theme-management) in the main README.

```bash
forum-analyzer themes discover --min-topics 3
```

### 4. LLM Analysis

See [Topic Analysis](../../README.md#topic-analysis) in the main README.

```bash
forum-analyzer llm-analyze
```

### 5. Query Results

See [Querying](../../README.md#querying) in the main README.

```bash
forum-analyzer ask "What are the top webhook reliability issues?"
forum-analyzer status  # View statistics
```

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

## Analysis Results

This example includes pre-generated reports from analyzing the Shopify Webhooks & Events forum:

- **[Collection Report](COLLECTION_REPORT.md)**: 271 topics, 1,201 posts, top contributors, activity patterns
- **[LLM Analysis Report](LLM_ANALYSIS_REPORT.md)**: 15 problem themes, severity distributions, key findings

### Summary of Findings

**Top Issues Identified:**
1. Webhook delivery reliability (25.1% of topics)
2. Configuration challenges
3. Missing/incomplete payload fields
4. Event timing and ordering issues
5. Authentication and security concerns

**Severity Distribution:**
- Critical: 18 topics (6.6%)
- High: 67 topics (24.7%)
- Medium: 138 topics (50.9%)
- Low: 48 topics (17.7%)

See the full [LLM Analysis Report](LLM_ANALYSIS_REPORT.md) for detailed insights.

## Troubleshooting

For common issues, see the [main README's Troubleshooting section](../../README.md#troubleshooting).

**Example-specific tips:**

**Finding the category path and ID:**
Visit the category in your browser: https://community.shopify.dev/c/webhooks-and-events/18
- Category path: `c` (the part after the domain, before the category slug)
- Category ID: `18` (the number at the end of the URL)

**Collection takes longer than expected:**
The Webhooks & Events category has grown significantly. Initial collection of 270+ topics may take 10-15 minutes due to rate limiting.

**LLM analysis costs:**
- Expected cost: ~$0.05-0.10 for full analysis
- Uses Claude Opus 4 (high quality, moderate cost)
- Can be reduced by using `--limit` flag for testing

## Next Steps

1. Try analyzing other Shopify categories (e.g., `api-and-sdks`, category ID 12)
2. Set up automated weekly updates with `forum-analyzer update`
3. Export data for external analysis: `sqlite3 forum.db .dump > backup.sql`
4. Compare findings across multiple time periods

## Additional Resources

- [Main README](../../README.md) - Full documentation and command reference
- [Architecture Diagram](.plan/architecture-diagram.md) - System design overview
- [Glossary](../../README.md#appendix-glossary) - Terminology reference