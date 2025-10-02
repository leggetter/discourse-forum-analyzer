#!/usr/bin/env python3
"""
Language Detection Debug Script
Tests various API endpoints and headers to determine why Portuguese content is returned.
"""

import requests
import json
from typing import Dict, List, Any


def print_separator(title: str):
    """Print a visual separator with title"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_endpoint(url: str, headers: Dict[str, str] = None, label: str = ""):
    """Test a single endpoint and return results"""
    print(f"\n🔍 Testing: {label if label else url}")
    print(f"   URL: {url}")
    if headers:
        print(f"   Headers: {headers}")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")

        # Check for redirects
        if response.history:
            print(f"   ⚠️  Redirects detected:")
            for i, r in enumerate(response.history):
                print(f"      {i+1}. {r.status_code} -> {r.url}")
            print(f"   Final URL: {response.url}")

        if response.status_code == 200:
            data = response.json()

            # Extract topics
            topics = data.get("topic_list", {}).get("topics", [])
            if topics:
                print(f"   ✅ Found {len(topics)} topics")
                print(f"\n   First 3 topic titles:")
                for i, topic in enumerate(topics[:3], 1):
                    title = topic.get("title", "NO TITLE")
                    print(f"      {i}. {title}")

                # Language detection
                print(f"\n   🌐 Language Analysis:")
                # Check for Portuguese indicators
                pt_keywords = [
                    "webhook",
                    "evento",
                    "erro",
                    "problema",
                    "como",
                    "quando",
                    "configurar",
                ]
                en_keywords = [
                    "webhook",
                    "event",
                    "error",
                    "problem",
                    "how",
                    "when",
                    "configure",
                ]

                all_titles = " ".join(
                    [t.get("title", "").lower() for t in topics[:10]]
                )

                pt_count = sum(1 for word in pt_keywords if word in all_titles)
                en_count = sum(1 for word in en_keywords if word in all_titles)

                print(f"      Portuguese indicators: {pt_count}")
                print(f"      English indicators: {en_count}")

                # Sample content inspection
                if topics:
                    first_topic = topics[0]
                    print(f"\n   📄 First Topic Details:")
                    print(f"      ID: {first_topic.get('id')}")
                    print(f"      Title: {first_topic.get('title')}")
                    print(f"      Slug: {first_topic.get('slug', 'N/A')}")

                    # Check excerpt for language
                    excerpt = first_topic.get("excerpt", "")
                    if excerpt:
                        print(f"      Excerpt: {excerpt[:100]}...")
            else:
                print(f"   ⚠️  No topics found in response")

            return {
                "success": True,
                "status": response.status_code,
                "topics_count": len(topics),
                "first_titles": [t.get("title") for t in topics[:3]],
                "redirected": len(response.history) > 0,
                "final_url": response.url,
                "data": data,
            }
        else:
            print(f"   ❌ Error: HTTP {response.status_code}")
            return {"success": False, "status": response.status_code}

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return {"success": False, "error": str(e)}


def main():
    print_separator("SHOPIFY FORUM API LANGUAGE INVESTIGATION")

    # Test 1: Original endpoint with no headers
    print_separator("TEST 1: Original Endpoint (No Headers)")
    result1 = test_endpoint(
        "https://community.shopify.dev/c/webhooks-and-events/18.json",
        label="Original endpoint, no headers",
    )

    # Test 2: Original endpoint with English headers
    print_separator("TEST 2: Original Endpoint (English Headers)")
    result2 = test_endpoint(
        "https://community.shopify.dev/c/webhooks-and-events/18.json",
        headers={"Accept-Language": "en-US,en;q=0.9"},
        label="Original endpoint, English headers",
    )

    # Test 3: Original endpoint with Portuguese headers
    print_separator("TEST 3: Original Endpoint (Portuguese Headers)")
    result3 = test_endpoint(
        "https://community.shopify.dev/c/webhooks-and-events/18.json",
        headers={"Accept-Language": "pt-BR,pt;q=0.9"},
        label="Original endpoint, Portuguese headers",
    )

    # Test 4: Alternative URL formats
    print_separator("TEST 4: Alternative URL Formats")

    alternative_urls = [
        ("https://community.shopify.dev/c/18.json", "Category ID only"),
        (
            "https://community.shopify.dev/c/webhooks-events/18.json",
            "Alternative slug",
        ),
        (
            "https://shopify.dev/community/c/webhooks-and-events/18.json",
            "Alternative domain path",
        ),
    ]

    alt_results = []
    for url, description in alternative_urls:
        result = test_endpoint(url, label=description)
        alt_results.append((description, result))

    # Test 5: Check sample file
    print_separator("TEST 5: Sample File Analysis")
    try:
        with open("data/samples/category_page_0.json", "r") as f:
            sample_data = json.load(f)
            topics = sample_data.get("topic_list", {}).get("topics", [])
            print(f"📁 Sample file has {len(topics)} topics")
            if topics:
                print(f"\nFirst 3 titles from sample:")
                for i, topic in enumerate(topics[:3], 1):
                    print(f"   {i}. {topic.get('title')}")
    except Exception as e:
        print(f"❌ Could not read sample file: {e}")

    # Summary
    print_separator("SUMMARY & FINDINGS")

    print("🔍 Key Observations:\n")

    # Compare results
    if result1.get("success") and result2.get("success"):
        titles1 = result1.get("first_titles", [])
        titles2 = result2.get("first_titles", [])

        if titles1 == titles2:
            print(
                "   ✅ Headers do NOT affect response - same content returned"
            )
        else:
            print(
                "   ⚠️  Headers DO affect response - different content returned"
            )

    if result1.get("redirected"):
        print(f"\n   ⚠️  URL redirects detected:")
        print(
            f"      Original: https://community.shopify.dev/c/webhooks-and-events/18.json"
        )
        print(f"      Final: {result1.get('final_url')}")

    print("\n📊 Language Detection Results:")
    print(
        f"   - No headers: {'Portuguese' if 'evento' in str(result1.get('first_titles', [])).lower() else 'English'}"
    )
    print(
        f"   - English headers: {'Portuguese' if 'evento' in str(result2.get('first_titles', [])).lower() else 'English'}"
    )
    print(
        f"   - Portuguese headers: {'Portuguese' if 'evento' in str(result3.get('first_titles', [])).lower() else 'English'}"
    )

    print("\n" + "=" * 80)
    print("\n💡 Next Steps:")
    print("   1. Review the titles above to confirm language")
    print("   2. Check if redirects are causing locale changes")
    print("   3. Verify category ID 18 is correct for English content")
    print(
        "   4. Consider checking browser network tab for actual endpoint used"
    )
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
