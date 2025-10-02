#!/usr/bin/env python3
"""Initialize the forum database."""

import sys
from pathlib import Path
from sqlalchemy import create_engine

from forum_analyzer.collector.models import Base
from forum_analyzer.config.settings import get_settings

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def init_database():
    """Initialize the database with schema."""
    settings = get_settings()

    print(f"Initializing database at: {settings.database.url}")

    # Create database directory if needed
    if settings.database.url.startswith("sqlite:///"):
        db_path = Path(settings.database.url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create engine and tables
    engine = create_engine(settings.database.url, echo=settings.database.echo)
    Base.metadata.create_all(engine)

    print("Database initialized successfully!")
    print(f"Tables created: {', '.join(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    init_database()
