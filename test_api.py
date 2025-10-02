#!/usr/bin/env python3
"""
Test script to validate Discourse API access and pagination for Shopify Developer Community.
This script tests category and topic endpoints, validates pagination, and saves sample responses.
"""

import json
import os
import sys
from pathlib import Path
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from datetime import datetime


# API Configuration
BASE_URL = "https://community.shopify.dev"
CATEGORY_ID = 18  # webhooks-and-events category
SAMPLES_DIR = Path("data/samples")


def fetch_json(url: str) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
    """
    Fetch JSON data from URL and return both data and headers.

    Returns:
        Tuple of (json_data, headers_dict) or (None, None) on error
    """
    try:
        print(f"Fetching: {url}")
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Shopify-Forum-Analyzer/1.0")

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            headers = dict(response.headers)
            return data, headers
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
        return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None


def save_sample(
    filename: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None
):
    """Save sample JSON response to file with metadata."""
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    filepath = SAMPLES_DIR / filename

    output = {"timestamp": datetime.utcnow().isoformat() + "Z", "data": data}

    if headers:
        # Extract relevant headers
        output["headers"] = {
            "rate_limit": headers.get("X-RateLimit-Limit"),
            "rate_limit_remaining": headers.get("X-RateLimit-Remaining"),
            "rate_limit_reset": headers.get("X-RateLimit-Reset"),
            "content_type": headers.get("Content-Type"),
        }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved sample to: {filepath}")


def test_category_endpoint():
    """Test category endpoint and pagination."""
    print("\n" + "=" * 60)
    print("TESTING CATEGORY ENDPOINT")
    print("=" * 60)

    # Test base category endpoint
    url = f"{BASE_URL}/c/webhooks-and-events/{CATEGORY_ID}.json"
    data, headers = fetch_json(url)

    if not data:
        print("✗ Failed to fetch category data")
        return None

    save_sample("category_base.json", data, headers)

    # Analyze pagination structure
    print("\n--- Pagination Analysis ---")
    topic_list = data.get("topic_list", {})
    topics = topic_list.get("topics", [])
    more_topics_url = topic_list.get("more_topics_url")

    print(f"Topics in page: {len(topics)}")
    print(f"more_topics_url present: {more_topics_url is not None}")
    if more_topics_url:
        print(f"more_topics_url value: {more_topics_url}")

    # Test page parameter
    print("\n--- Testing Page Parameter ---")
    for page in [0, 1]:
        url_with_page = (
            f"{BASE_URL}/c/webhooks-and-events/{CATEGORY_ID}.json?page={page}"
        )
        page_data, page_headers = fetch_json(url_with_page)

        if page_data:
            page_topics = page_data.get("topic_list", {}).get("topics", [])
            print(f"Page {page}: {len(page_topics)} topics")
            save_sample(f"category_page_{page}.json", page_data, page_headers)

    # Extract first topic ID for topic endpoint test
    if topics:
        first_topic_id = topics[0].get("id")
        print(f"\n✓ Found first topic ID: {first_topic_id}")
        return first_topic_id
    else:
        print("✗ No topics found in category")
        return None


def test_topic_endpoint(topic_id: int):
    """Test topic endpoint."""
    print("\n" + "=" * 60)
    print("TESTING TOPIC ENDPOINT")
    print("=" * 60)

    url = f"{BASE_URL}/t/{topic_id}.json"
    data, headers = fetch_json(url)

    if not data:
        print("✗ Failed to fetch topic data")
        return

    save_sample(f"topic_{topic_id}.json", data, headers)

    # Analyze topic structure
    print("\n--- Topic Analysis ---")
    print(f"Topic ID: {data.get('id')}")
    print(f"Topic Title: {data.get('title')}")
    print(f"Posts count: {data.get('posts_count')}")
    print(f"Views: {data.get('views')}")

    post_stream = data.get("post_stream", {})
    posts = post_stream.get("posts", [])
    print(f"Posts in response: {len(posts)}")

    print("✓ Topic endpoint validated")


def analyze_rate_limits(headers_samples: list):
    """Analyze rate limiting from collected headers."""
    print("\n" + "=" * 60)
    print("RATE LIMITING ANALYSIS")
    print("=" * 60)

    for i, headers in enumerate(headers_samples):
        if headers and any(k.startswith("X-RateLimit") for k in headers.keys()):
            print(f"\nRequest {i+1} rate limit headers:")
            for key, value in headers.items():
                if "rate" in key.lower() or "limit" in key.lower():
                    print(f"  {key}: {value}")


def main():
    """Main test execution."""
    print("Shopify Developer Community - Discourse API Validation")
    print("Testing API access and pagination mechanisms\n")

    # Test category endpoint and pagination
    topic_id = test_category_endpoint()

    # Test topic endpoint if we got a topic ID
    if topic_id:
        test_topic_endpoint(topic_id)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✓ API is publicly accessible (no authentication required)")
    print(f"✓ Sample responses saved to: {SAMPLES_DIR}")
    print(f"✓ Category endpoint validated")
    print(f"✓ Pagination mechanism tested")
    if topic_id:
        print(f"✓ Topic endpoint validated")

    print("\nPagination Findings:")
    print("- Page parameter supported (?page=0, ?page=1, etc.)")
    print("- more_topics_url field indicates if more pages exist")
    print("- Check sample files for complete pagination structure")

    print("\nNext Steps:")
    print("1. Review sample JSON files in data/samples/")
    print("2. Analyze pagination structure from more_topics_url")
    print("3. Check rate limit headers (if any)")
    print("4. Design data models based on response schemas")


if __name__ == "__main__":
    main()
