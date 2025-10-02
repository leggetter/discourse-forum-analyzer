#!/usr/bin/env python3
"""Test redirect handling in the API client."""

import asyncio
import logging
from forum_analyzer.collector.api_client import ForumAPIClient

# Set up logging to see redirect information
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


async def test_redirect():
    """Test that redirects are handled correctly."""
    print("Testing API redirect handling...")
    print("=" * 60)

    async with ForumAPIClient() as client:
        try:
            # Test fetching category metadata (this should trigger redirect)
            data = await client.fetch_category_metadata(18)

            print("\n✓ Successfully fetched category metadata")
            print(f"Category: {data.get('name')}")
            print(f"ID: {data.get('id')}")
            print(f"Topic Count: {data.get('topic_count')}")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(test_redirect())
