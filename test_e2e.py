#!/usr/bin/env python3
"""End-to-end testing script for the forum analyzer."""

import sqlite3
import os

DB_PATH = "data/database/forum.db"


def verify_database_schema():
    """Verify that all required tables exist in the database."""
    print("=" * 60)
    print("DATABASE SCHEMA VERIFICATION")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found at {DB_PATH}")
        return False

    print(f"✓ Database file exists at {DB_PATH}")
    print(f"  Size: {os.path.getsize(DB_PATH)} bytes")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"\n✓ Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")

    # Expected tables
    expected_tables = ["categories", "topics", "posts", "users", "checkpoints"]
    missing_tables = set(expected_tables) - set(tables)

    if missing_tables:
        print(f"\n❌ Missing tables: {missing_tables}")
        conn.close()
        return False

    print("\n✓ All expected tables exist")

    # Check schema for each table
    print("\nTable Schemas:")
    for table in expected_tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"\n  {table} ({len(columns)} columns):")
        for col in columns:
            print(f"    - {col[1]} ({col[2]})")

    conn.close()
    return True


def check_database_stats():
    """Check current database statistics."""
    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables = ["categories", "topics", "posts", "users", "checkpoints"]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:15} : {count:6} rows")

    conn.close()


if __name__ == "__main__":
    if verify_database_schema():
        check_database_stats()
        print("\n✓ Database verification complete")
    else:
        print("\n❌ Database verification failed")
        exit(1)
