#!/usr/bin/env python3
"""Test if community.shopify.com redirects to Portuguese forum"""

import requests

print("=" * 80)
print("TESTING BASE URL FROM api_client.py")
print("=" * 80)

# Test the exact URL structure used in the API client
base_url = "https://community.shopify.com"
category_path = "/c/webhooks-and-events/18.json"
full_url = base_url + category_path

print(f"\nBase URL from api_client.py: {base_url}")
print(f"Testing: {full_url}")
print()

# Make request with allow_redirects=True to follow redirects
response = requests.get(full_url, allow_redirects=True, timeout=10)

print(f"Status Code: {response.status_code}")
print(f"Final URL: {response.url}")

# Check redirect chain
if response.history:
    print(f"\nREDIRECTS DETECTED:")
    for i, resp in enumerate(response.history, 1):
        print(f"  {i}. [{resp.status_code}] {resp.url}")
    print(f"  Final: [{response.status_code}] {response.url}")
else:
    print("\nNo redirects - Direct response")

# Check content language
if response.status_code == 200:
    data = response.json()
    topics = data.get("topic_list", {}).get("topics", [])

    if topics:
        print(f"\nTopics found: {len(topics)}")
        print(f"\nFirst 3 titles:")
        for i, topic in enumerate(topics[:3], 1):
            print(f'  {i}. {topic.get("title", "")}')

        # Language detection
        all_titles = " ".join([t.get("title", "").lower() for t in topics[:5]])
        pt_words = ["código", "tamanho", "formulário", "morada"]
        is_portuguese = any(word in all_titles for word in pt_words)

        if is_portuguese:
            print("\n*** PORTUGUESE CONTENT DETECTED ***")
        else:
            print("\n*** ENGLISH CONTENT DETECTED ***")

print("\n" + "=" * 80)
