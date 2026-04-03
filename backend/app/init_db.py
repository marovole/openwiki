# ============================================================
# Database Initialization Script
# ============================================================
# Run this to create tables in the database
# Usage: uv run python -m app.init_db
# ============================================================

import asyncio
from sqlalchemy import text

from app.db import engine, Base
from app.models import Material, WikiEntry, Concept, Tag  # Import all models


async def init_db():
    """Create all tables and extensions."""
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    print("Database initialized successfully!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())