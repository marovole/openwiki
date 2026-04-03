# ============================================================
# Pytest Configuration & Fixtures
# ============================================================

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, text

from app.db import Base
from app.models.material import Material, MaterialStatus
from app.models.wiki_entry import WikiEntry
from app.models.concept import Concept, Tag

# Test database URL
TEST_DB_URL = "postgresql+asyncpg://openwiki:openwiki_dev@localhost:5432/openwiki_test"


@pytest_asyncio.fixture
async def db_session():
    """Create a test database session."""
    engine = create_async_engine(TEST_DB_URL, echo=False)

    # Create pgvector extension and all tables
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()