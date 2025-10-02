"""CLI interface for Shopify Forum Analyzer."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

from forum_analyzer.collector.models import (
    Base,
    Category,
    Topic,
    Post,
    User,
)
from forum_analyzer.collector.orchestrator import (
    collect_category,
    incremental_update,
)
from forum_analyzer.config.settings import get_settings
from forum_analyzer.analyzer.reporter import ForumAnalyzer
from forum_analyzer.analyzer.llm_analyzer import LLMAnalyzer

console = Console()


def get_db_path() -> Path:
    """Get database path from settings."""
    settings = get_settings()
    # Extract path from SQLite URL (format: sqlite:///path/to/db.db)
    db_url = settings.database.url
    if db_url.startswith("sqlite:///"):
        return Path(db_url.replace("sqlite:///", ""))
    return Path("data/database/forum.db")


def ensure_database_exists() -> bool:
    """Ensure database directory and schema exist.

    Returns:
        True if database is initialized, False if initialization is needed.
    """
    db_path = get_db_path()

    # Create directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if database file exists and has tables
    if db_path.exists():
        try:
            engine = create_engine(f"sqlite:///{db_path}")
            with Session(engine) as session:
                # Try to query a table to see if schema exists
                session.execute(select(Category).limit(1))
            return True
        except Exception:
            # Database exists but schema might be missing
            return False

    return False


def init_database(force: bool = False) -> None:
    """Initialize the database schema.

    Args:
        force: If True, reinitialize even if database exists.
    """
    db_path = get_db_path()

    if db_path.exists() and not force:
        console.print(
            "[yellow]Database already exists. "
            "Use --force to reinitialize.[/yellow]"
        )
        return

    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        console.print(f"[green]✓[/green] Database initialized at {db_path}")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to initialize database: {e}")
        sys.exit(1)


def display_config(category_slug: str, category_id: int) -> None:
    """Display current configuration."""
    settings = get_settings()

    config_table = Table(title="Configuration", show_header=False)
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")

    config_table.add_row("Database", str(get_db_path()))
    config_table.add_row("Base URL", settings.api.base_url)
    config_table.add_row("Category Slug", category_slug)
    config_table.add_row("Category ID", str(category_id))
    config_table.add_row("Batch Size", str(settings.scraping.batch_size))
    config_table.add_row("Checkpoint Dir", settings.scraping.checkpoint_dir)

    console.print(config_table)
    console.print()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Shopify Forum Analyzer - Collect and analyze forum data."""
    pass


@cli.command()
@click.option(
    "--category-slug",
    default="webhooks-and-events",
    help="Category slug to collect",
)
@click.option("--category-id", default=18, type=int, help="Category ID")
@click.option(
    "--resume/--no-resume",
    default=True,
    help="Resume from checkpoint if available",
)
@click.option(
    "--page-limit",
    type=int,
    default=None,
    help="Limit number of pages to collect (for testing)",
)
def collect(
    category_slug: str,
    category_id: int,
    resume: bool,
    page_limit: Optional[int],
):
    """Collect all topics and posts from a category.

    This command performs a full collection of all topics and posts from the
    specified category. It supports checkpointing and can resume interrupted
    collections.

    Examples:
        forum-analyzer collect
        forum-analyzer collect --category-slug api-discussions --category-id 25
        forum-analyzer collect --no-resume  # Start fresh, ignore checkpoints
    """
    console.print(
        Panel.fit(
            f"[bold]Collecting Category Data[/bold]\n"
            f"Category: {category_slug} (ID: {category_id})",
            border_style="blue",
        )
    )
    console.print()

    # Ensure database is initialized
    if not ensure_database_exists():
        console.print(
            "[yellow]Database not initialized. Initializing now...[/yellow]"
        )
        init_database()
        console.print()

    display_config(category_slug, category_id)

    try:
        # Run the async collection function
        stats = asyncio.run(
            collect_category(
                category_id=category_id,
                full_fetch=not resume,  # Invert: --no-resume = full fetch
                page_limit=page_limit,
            )
        )

        console.print()
        console.print(
            Panel(
                f"[bold green]✓ Collection completed successfully!"
                f"[/bold green]\n"
                f"Topics processed: {stats.get('topics_processed', 0)}\n"
                f"Posts collected: {stats.get('posts_collected', 0)}",
                border_style="green",
            )
        )

        # Show summary
        show_database_stats()

    except KeyboardInterrupt:
        console.print(
            "\n[yellow]Collection interrupted by user. "
            "Progress saved to checkpoint.[/yellow]"
        )
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]✗ Collection failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--category-slug",
    default="webhooks-and-events",
    help="Category slug to update",
)
@click.option("--category-id", default=18, type=int, help="Category ID")
def update(category_slug: str, category_id: int):
    """Incrementally update existing data with new posts.

    This command fetches only new topics and posts since the last collection,
    making it efficient for regular updates.

    Examples:
        forum-analyzer update
        forum-analyzer update --category-slug api-discussions --category-id 25
    """
    console.print(
        Panel.fit(
            f"[bold]Incremental Update[/bold]\n"
            f"Category: {category_slug} (ID: {category_id})",
            border_style="blue",
        )
    )
    console.print()

    # Ensure database exists
    if not ensure_database_exists():
        console.print(
            "[red]✗ Database not found. "
            "Run 'forum-analyzer collect' first.[/red]"
        )
        sys.exit(1)

    display_config(category_slug, category_id)

    try:
        # Run the async update function
        stats = asyncio.run(incremental_update(category_id=category_id))

        console.print()
        console.print(
            Panel(
                f"[bold green]✓ Update completed successfully![/bold green]\n"
                f"Topics updated: {stats.get('topics_updated', 0)}\n"
                f"Posts added: {stats.get('posts_added', 0)}",
                border_style="green",
            )
        )

        # Show summary
        show_database_stats()

    except KeyboardInterrupt:
        console.print("\n[yellow]Update interrupted by user.[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]✗ Update failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--force", is_flag=True, help="Force reinitialization if database exists"
)
def init_db(force: bool):
    """Initialize the database schema.

    Creates the database file and all necessary tables. Use --force to
    reinitialize an existing database (WARNING: this will delete all data).

    Examples:
        forum-analyzer init-db
        forum-analyzer init-db --force  # Reinitialize (deletes data!)
    """
    console.print(
        Panel.fit("[bold]Database Initialization[/bold]", border_style="blue")
    )
    console.print()

    if force:
        if not click.confirm(
            "⚠️  This will delete all existing data. Continue?", default=False
        ):
            console.print("[yellow]Aborted.[/yellow]")
            return

    init_database(force=force)


@cli.command()
@click.option(
    "--category-slug",
    help="Category to clear checkpoints for (clears all if not specified)",
)
def clear_checkpoints(category_slug: Optional[str]):
    """Clear checkpoints to restart collection from beginning.

    Removes checkpoint files to allow a fresh start. Can target a specific
    category or clear all checkpoints.

    Examples:
        forum-analyzer clear-checkpoints  # Clear all
        forum-analyzer clear-checkpoints --category-slug webhooks-and-events
    """
    settings = get_settings()
    checkpoint_dir = Path(settings.scraping.checkpoint_dir)

    if not checkpoint_dir.exists():
        console.print("[yellow]No checkpoints found.[/yellow]")
        return

    try:
        if category_slug:
            # Clear specific category checkpoint
            checkpoint_file = checkpoint_dir / f"{category_slug}.json"
            if checkpoint_file.exists():
                checkpoint_file.unlink()
                console.print(
                    f"[green]✓[/green] Cleared checkpoint for "
                    f"category: {category_slug}"
                )
            else:
                console.print(
                    f"[yellow]No checkpoint found for "
                    f"category: {category_slug}[/yellow]"
                )
        else:
            # Clear all checkpoints
            count = 0
            for checkpoint_file in checkpoint_dir.glob("*.json"):
                checkpoint_file.unlink()
                count += 1

            if count > 0:
                console.print(
                    f"[green]✓[/green] Cleared {count} checkpoint(s)"
                )
            else:
                console.print("[yellow]No checkpoints found.[/yellow]")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to clear checkpoints: {e}")
        sys.exit(1)


@cli.command()
def status():
    """Show collection status and database statistics.

    Displays comprehensive statistics about the collected data, including
    counts of categories, topics, posts, users, and active checkpoints.

    Examples:
        forum-analyzer status
    """
    console.print(
        Panel.fit("[bold]Database Status[/bold]", border_style="blue")
    )
    console.print()

    db_path = get_db_path()

    if not db_path.exists():
        console.print(
            "[yellow]Database not found. "
            "Run 'forum-analyzer init-db' first.[/yellow]"
        )
        return

    show_database_stats()
    show_checkpoint_status()


def show_database_stats():
    """Display database statistics."""
    db_path = get_db_path()

    try:
        engine = create_engine(f"sqlite:///{db_path}")

        with Session(engine) as session:
            # Get counts
            category_count = (
                session.scalar(select(func.count()).select_from(Category)) or 0
            )
            topic_count = (
                session.scalar(select(func.count()).select_from(Topic)) or 0
            )
            post_count = (
                session.scalar(select(func.count()).select_from(Post)) or 0
            )
            user_count = (
                session.scalar(select(func.count()).select_from(User)) or 0
            )

            # Get latest topic
            latest_topic = session.scalar(
                select(Topic).order_by(Topic.created_at.desc()).limit(1)
            )

            # Create statistics table
            stats_table = Table(title="Database Statistics", show_header=False)
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Count", style="green", justify="right")

            stats_table.add_row("Categories", str(category_count))
            stats_table.add_row("Topics", str(topic_count))
            stats_table.add_row("Posts", str(post_count))
            stats_table.add_row("Users", str(user_count))

            if latest_topic and latest_topic.created_at:
                stats_table.add_row(
                    "Latest Topic",
                    f"{latest_topic.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                )

            stats_table.add_row(
                "Database Size",
                f"{db_path.stat().st_size / 1024 / 1024:.2f} MB",
            )

            console.print(stats_table)

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to query database: {e}")


def show_checkpoint_status():
    """Display checkpoint status."""
    settings = get_settings()
    checkpoint_dir = Path(settings.scraping.checkpoint_dir)

    if not checkpoint_dir.exists() or not any(checkpoint_dir.glob("*.json")):
        console.print("\n[dim]No active checkpoints[/dim]")
        return

    console.print()
    checkpoint_table = Table(title="Active Checkpoints", show_header=True)
    checkpoint_table.add_column("Category", style="cyan")
    checkpoint_table.add_column("File", style="yellow")
    checkpoint_table.add_column("Size", style="green")

    try:
        for checkpoint_file in sorted(checkpoint_dir.glob("*.json")):
            category_slug = checkpoint_file.stem
            file_size = checkpoint_file.stat().st_size
            checkpoint_table.add_row(
                category_slug, checkpoint_file.name, f"{file_size} bytes"
            )

        console.print(checkpoint_table)

    except Exception as e:
        console.print(
            f"[yellow]Warning: Could not read checkpoints: {e}[/yellow]"
        )


@cli.command()
@click.option(
    "--limit",
    default=20,
    type=int,
    help="Number of results to show in report sections",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Save report to markdown file",
)
def analyze(limit: int, output: Optional[str]):
    """Analyze forum data and generate insights report.

    Generates a comprehensive analysis report including:
    - Most discussed topics
    - Common keywords and patterns
    - Problem categorization
    - Trending issues
    - Unanswered questions

    Examples:
        forum-analyzer analyze
        forum-analyzer analyze --limit 30
        forum-analyzer analyze --output reports/analysis.md
    """
    console.print(
        Panel.fit("[bold]Forum Data Analysis[/bold]", border_style="blue")
    )
    console.print()

    db_path = get_db_path()

    if not db_path.exists():
        console.print(
            "[red]✗ Database not found. "
            "Run 'forum-analyzer collect' first.[/red]"
        )
        sys.exit(1)

    try:
        analyzer = ForumAnalyzer(str(db_path))

        # Generate report
        with console.status("[bold green]Analyzing forum data..."):
            report = analyzer.generate_summary_report()

        # Display report
        console.print()
        md = Markdown(report)
        console.print(md)

        # Save to file if requested
        if output:
            output_path = Path(output)
            analyzer.export_report_to_markdown(str(output_path))
            console.print()
            console.print(f"[green]✓[/green] Report saved to: {output_path}")

    except Exception as e:
        console.print(f"[red]✗ Analysis failed: {e}[/red]")
        import traceback

        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument("keyword")
@click.option(
    "--limit",
    default=20,
    type=int,
    help="Maximum number of results to show",
)
def search(keyword: str, limit: int):
    """Search topics by keyword.

    Searches for topics containing the specified keyword in their title.
    Useful for finding specific error patterns or topics.

    Examples:
        forum-analyzer search webhook
        forum-analyzer search "authentication error"
        forum-analyzer search timeout --limit 10
    """
    console.print(
        Panel.fit(
            f"[bold]Searching for: '{keyword}'[/bold]", border_style="blue"
        )
    )
    console.print()

    db_path = get_db_path()

    if not db_path.exists():
        console.print(
            "[red]✗ Database not found. "
            "Run 'forum-analyzer collect' first.[/red]"
        )
        sys.exit(1)

    try:
        analyzer = ForumAnalyzer(str(db_path))
        results = analyzer.search_topics_by_keyword(keyword)

        if not results:
            console.print(
                f"[yellow]No topics found matching '{keyword}'[/yellow]"
            )
            return

        # Display results in a table
        table = Table(
            title=f"Search Results for '{keyword}' ({len(results)} found)"
        )
        table.add_column("Title", style="cyan", no_wrap=False)
        table.add_column("Replies", style="green", justify="right")
        table.add_column("Views", style="yellow", justify="right")
        table.add_column("Likes", style="magenta", justify="right")
        table.add_column("Solved", style="green", justify="center")

        for topic in results[:limit]:
            solved = "✓" if topic["accepted_answer"] else ""
            table.add_row(
                topic["title"],
                str(topic["reply_count"]),
                str(topic["views"]),
                str(topic["likes"]),
                solved,
            )

        console.print(table)

        if len(results) > limit:
            console.print(
                f"\n[dim]Showing {limit} of {len(results)} results. "
                f"Use --limit to see more.[/dim]"
            )

    except Exception as e:
        console.print(f"[red]✗ Search failed: {e}[/red]")
        sys.exit(1)


@cli.command()
def patterns():
    """Show common error patterns detected in forum topics.

    Analyzes forum topics to detect common error patterns such as:
    - Webhook delivery failures
    - Authentication issues
    - Timeout/performance problems
    - Payload/data issues
    - Configuration problems
    - API errors

    Examples:
        forum-analyzer patterns
    """
    console.print(
        Panel.fit("[bold]Common Error Patterns[/bold]", border_style="blue")
    )
    console.print()

    db_path = get_db_path()

    if not db_path.exists():
        console.print(
            "[red]✗ Database not found. "
            "Run 'forum-analyzer collect' first.[/red]"
        )
        sys.exit(1)

    try:
        analyzer = ForumAnalyzer(str(db_path))

        # Get error patterns
        with console.status("[bold green]Detecting patterns..."):
            patterns_data = analyzer.detect_common_error_patterns()
            categories = analyzer.get_problem_category_distribution()

        # Display category distribution
        console.print("[bold]Problem Categories:[/bold]")
        console.print()

        cat_table = Table(show_header=True)
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Count", style="green", justify="right")
        cat_table.add_column("Percentage", style="yellow", justify="right")

        total = sum(categories.values())
        for category, count in sorted(
            categories.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / total * 100) if total > 0 else 0
            cat_name = category.replace("_", " ").title()
            cat_table.add_row(cat_name, str(count), f"{percentage:.1f}%")

        console.print(cat_table)

        # Display specific error patterns
        if patterns_data:
            console.print()
            console.print("[bold]Detected Error Patterns:[/bold]")
            console.print()

            for pattern_name, topics in sorted(
                patterns_data.items(), key=lambda x: len(x[1]), reverse=True
            ):
                if topics:
                    pattern_title = pattern_name.replace("_", " ").title()
                    console.print(
                        f"[cyan]● {pattern_title}[/cyan] "
                        f"[dim]({len(topics)} topics)[/dim]"
                    )

                    # Show top 3 examples
                    for topic in topics[:3]:
                        console.print(
                            f"  - {topic['title']} "
                            f"[dim]({topic['reply_count']} replies)[/dim]"
                        )

                    console.print()
        else:
            console.print(
                "[yellow]No specific error patterns detected.[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]✗ Pattern detection failed: {e}[/red]")
        sys.exit(1)


@cli.command(name="llm-analyze")
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Maximum number of topics to analyze",
)
@click.option(
    "--force",
    is_flag=True,
    help="Re-analyze already analyzed topics",
)
@click.option(
    "--topic-id",
    type=int,
    default=None,
    help="Analyze a specific topic by ID",
)
def llm_analyze(limit: Optional[int], force: bool, topic_id: Optional[int]):
    """Analyze forum topics using Claude API to identify problems.

    Uses AI to analyze topics and extract:
    - Core problem descriptions
    - Problem categories
    - Severity levels
    - Key technical terms
    - Root cause analysis

    Examples:
        forum-analyzer llm-analyze
        forum-analyzer llm-analyze --limit 50
        forum-analyzer llm-analyze --topic-id 66
        forum-analyzer llm-analyze --force
    """
    console.print(
        Panel.fit(
            "[bold]LLM-Based Problem Analysis[/bold]",
            border_style="blue",
        )
    )
    console.print()

    db_path = get_db_path()
    if not db_path.exists():
        console.print(
            "[red]✗ Database not found. "
            "Run 'forum-analyzer collect' first.[/red]"
        )
        sys.exit(1)

    settings = get_settings()
    if not settings.llm_analysis.api_key:
        console.print("[red]✗ No API key configured.[/red]")
        console.print(
            "Please add your Anthropic API key to config/config.yaml"
        )
        sys.exit(1)

    try:
        analyzer = LLMAnalyzer(settings)

        if topic_id:
            console.print(f"[cyan]Analyzing topic {topic_id}...[/cyan]")
            result = analyzer.analyze_topic(topic_id, force=force)
            if result:
                console.print("[green]✓ Analysis complete[/green]")
                console.print(
                    f"\n[bold]Core Problem:[/bold] "
                    f"{result['core_problem']}"
                )
                console.print(f"[bold]Category:[/bold] {result['category']}")
                console.print(f"[bold]Severity:[/bold] {result['severity']}")
                console.print(
                    f"[bold]Key Terms:[/bold] "
                    f"{', '.join(result['key_terms'])}"
                )
            else:
                console.print(
                    "[yellow]Topic skipped (already analyzed)[/yellow]"
                )
        else:
            limit_text = f" (limit: {limit})" if limit else ""
            console.print(
                f"[cyan]Starting batch analysis{limit_text}...[/cyan]"
            )
            results = analyzer.analyze_batch(limit=limit, force=force)

            console.print("\n[green]✓ Analysis complete[/green]")
            console.print(f"Total topics: {results['total']}")
            console.print(f"Analyzed: {results['analyzed']}")
            console.print(f"Skipped: {results['skipped']}")
            console.print(f"Errors: {results['errors']}")

            if results["categories"]:
                console.print("\n[bold]Categories:[/bold]")
                for category, count in results["categories"].items():
                    console.print(f"  {category}: {count}")

            if results["severities"]:
                console.print("\n[bold]Severities:[/bold]")
                for severity, count in results["severities"].items():
                    console.print(f"  {severity}: {count}")

    except Exception as e:
        console.print(f"[red]✗ Analysis failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--min-topics",
    type=int,
    default=3,
    help="Minimum number of topics to form a theme",
)
def themes(min_topics: int):
    """Identify common problem themes across analyzed topics.

    Groups related problems into themes based on LLM analysis results.
    Requires topics to be analyzed first with 'llm-analyze' command.

    Examples:
        forum-analyzer themes
        forum-analyzer themes --min-topics 5
    """
    console.print(
        Panel.fit(
            "[bold]Problem Theme Identification[/bold]",
            border_style="blue",
        )
    )
    console.print()

    db_path = get_db_path()
    if not db_path.exists():
        console.print(
            "[red]✗ Database not found. "
            "Run 'forum-analyzer collect' first.[/red]"
        )
        sys.exit(1)

    settings = get_settings()
    if not settings.llm_analysis.api_key:
        console.print("[red]✗ No API key configured.[/red]")
        console.print(
            "Please add your Anthropic API key to config/config.yaml"
        )
        sys.exit(1)

    try:
        analyzer = LLMAnalyzer(settings)

        console.print(
            f"[cyan]Identifying themes (min {min_topics} topics)...[/cyan]"
        )
        themes_list = analyzer.identify_themes(min_topics=min_topics)

        if not themes_list:
            console.print("[yellow]No themes identified[/yellow]")
            return

        console.print(f"\n[green]✓ Found {len(themes_list)} themes[/green]\n")

        for i, theme in enumerate(themes_list, 1):
            console.print(f"[bold]{i}. {theme['theme_name']}[/bold]")
            console.print(f"   Description: {theme['description']}")
            console.print(f"   Topics: {len(theme['affected_topic_ids'])}")

            severity_dist = theme.get("severity_distribution", {})
            if severity_dist:
                console.print("   Severity: ", end="")
                parts = [f"{k}={v}" for k, v in severity_dist.items() if v > 0]
                console.print(", ".join(parts))
            console.print()

    except Exception as e:
        console.print(f"[red]✗ Theme identification failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("question")
@click.option(
    "--context-limit",
    type=int,
    default=None,
    help="Maximum number of topics to include in context",
)
def ask(question: str, context_limit: Optional[int]):
    """Ask a question about the analyzed forum data.

    Query the analyzed topics using natural language. Requires topics
    to be analyzed first with 'llm-analyze' command.

    Examples:
        forum-analyzer ask "What are the most common webhook problems?"
        forum-analyzer ask "How many critical issues exist?" --context-limit 20
    """
    console.print(
        Panel.fit(
            "[bold]Ask Question About Forum Data[/bold]",
            border_style="blue",
        )
    )
    console.print()

    db_path = get_db_path()
    if not db_path.exists():
        console.print(
            "[red]✗ Database not found. "
            "Run 'forum-analyzer collect' first.[/red]"
        )
        sys.exit(1)

    settings = get_settings()
    if not settings.llm_analysis.api_key:
        console.print("[red]✗ No API key configured.[/red]")
        console.print(
            "Please add your Anthropic API key to config/config.yaml"
        )
        sys.exit(1)

    try:
        analyzer = LLMAnalyzer(settings)

        console.print(f"[cyan]Question: {question}[/cyan]\n")
        answer = analyzer.ask_question(question, context_limit)

        console.print(f"[bold]Answer:[/bold]\n{answer}")

    except Exception as e:
        console.print(f"[red]✗ Question failed: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
