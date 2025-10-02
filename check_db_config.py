#!/usr/bin/env python3
"""Check database content and configuration to identify language mismatch"""

import sqlite3
import yaml

print("=" * 80)
print("DATABASE & CONFIGURATION ANALYSIS")
print("=" * 80)

# Check database
print("\n1. DATABASE CONTENT:")
try:
    conn = sqlite3.connect("data/database/forum.db")
    cursor = conn.cursor()

    # Get category IDs
    cursor.execute("SELECT DISTINCT category_id FROM topics")
    category_ids = [r[0] for r in cursor.fetchall()]
    print(f"   Category IDs in database: {category_ids}")

    # Get sample topics by category
    for cat_id in category_ids:
        cursor.execute(
            "SELECT id, title FROM topics WHERE category_id = ? LIMIT 3",
            (cat_id,),
        )
        topics = cursor.fetchall()
        print(f"\n   Category {cat_id} - Sample topics:")
        for topic_id, title in topics:
            print(f"      {topic_id}: {title}")

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM topics")
    total = cursor.fetchone()[0]
    print(f"\n   Total topics in database: {total}")

    conn.close()
except Exception as e:
    print(f"   ERROR: {e}")

# Check config
print("\n2. CONFIGURATION FILE:")
try:
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    category_id = config.get("collector", {}).get("category_id")
    print(f"   Configured category_id: {category_id}")

    base_url = config.get("collector", {}).get("base_url")
    print(f"   Configured base_url: {base_url}")

except Exception as e:
    print(f"   ERROR: {e}")

# Check checkpoint
print("\n3. CHECKPOINT FILE:")
try:
    with open("data/checkpoints/checkpoint_18_category_page.json", "r") as f:
        import json

        checkpoint = json.load(f)

    print(f"   Last page processed: {checkpoint.get('current_page')}")
    print(f"   More pages: {checkpoint.get('has_more')}")

except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 80)
print("ANALYSIS SUMMARY:")
print("=" * 80)
print(
    "\n🔍 The API is returning ENGLISH content (verified by debug_language.py)"
)
print("🔍 The database contains PORTUGUESE content")
print("\nPOSSIBLE CAUSES:")
print("   1. Wrong category_id in config.yaml")
print("   2. Database populated from a different category")
print("   3. Previous test run with Portuguese forum category")
print("\n" + "=" * 80)
