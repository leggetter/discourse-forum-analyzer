#!/usr/bin/env python3
"""Test script for forum analyzer functionality."""

from pathlib import Path
from forum_analyzer.analyzer.reporter import ForumAnalyzer


def main():
    db_path = Path("data/database/forum.db")

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return

    print(f"✓ Using database: {db_path}")
    print()

    analyzer = ForumAnalyzer(str(db_path))

    # Test 1: Database stats
    print("=" * 60)
    print("TEST 1: Database Statistics")
    print("=" * 60)
    stats = analyzer.get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    # Test 2: Most discussed topics
    print("=" * 60)
    print("TEST 2: Most Discussed Topics (Top 5)")
    print("=" * 60)
    topics = analyzer.get_most_discussed_topics(limit=5)
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic['title']}")
        print(
            f"   Replies: {topic['reply_count']}, Views: {topic['views']}, Likes: {topic['likes']}"
        )
    print()

    # Test 3: Keywords
    print("=" * 60)
    print("TEST 3: Top Keywords (Top 10)")
    print("=" * 60)
    keywords = analyzer.get_frequent_keywords_from_titles(limit=10)
    for keyword, count in keywords:
        print(f"  {keyword}: {count}")
    print()

    # Test 4: Activity trends
    print("=" * 60)
    print("TEST 4: Activity Trends")
    print("=" * 60)
    trends = analyzer.get_topics_by_activity_trend()
    print(f"  Last week: {trends['last_week']}")
    print(f"  Last month: {trends['last_month']}")
    print(f"  Older: {trends['older']}")
    print(f"  Total: {trends['total']}")
    print()

    # Test 5: Unanswered topics
    print("=" * 60)
    print("TEST 5: Unanswered Topics (Top 5)")
    print("=" * 60)
    unanswered = analyzer.get_unanswered_topics(threshold=2)
    for topic in unanswered[:5]:
        print(
            f"  - {topic['title']} ({topic['reply_count']} replies, {topic['views']} views)"
        )
    print()

    # Test 6: Search
    print("=" * 60)
    print("TEST 6: Search for 'webhook'")
    print("=" * 60)
    search_results = analyzer.search_topics_by_keyword("webhook")
    print(f"  Found {len(search_results)} topics")
    for topic in search_results[:3]:
        print(f"  - {topic['title']} ({topic['reply_count']} replies)")
    print()

    # Test 7: Error patterns
    print("=" * 60)
    print("TEST 7: Error Patterns")
    print("=" * 60)
    patterns = analyzer.detect_common_error_patterns()
    for pattern_name, topics in patterns.items():
        if topics:
            print(f"  {pattern_name}: {len(topics)} topics")
    print()

    # Test 8: Category distribution
    print("=" * 60)
    print("TEST 8: Problem Categories")
    print("=" * 60)
    categories = analyzer.get_problem_category_distribution()
    total = sum(categories.values())
    for category, count in sorted(
        categories.items(), key=lambda x: x[1], reverse=True
    ):
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  {category}: {count} ({percentage:.1f}%)")
    print()

    # Test 9: Generate report
    print("=" * 60)
    print("TEST 9: Generate Summary Report")
    print("=" * 60)
    report = analyzer.generate_summary_report()
    print(f"  Report length: {len(report)} characters")
    print(f"  Lines: {len(report.splitlines())}")
    print()

    # Test 10: Export to markdown
    print("=" * 60)
    print("TEST 10: Export Report to Markdown")
    print("=" * 60)
    output_path = "reports/test_analysis.md"
    analyzer.export_report_to_markdown(output_path)
    output_file = Path(output_path)
    if output_file.exists():
        print(f"  ✓ Report saved to: {output_path}")
        print(f"  File size: {output_file.stat().st_size} bytes")
    else:
        print(f"  ❌ Failed to save report")
    print()

    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
