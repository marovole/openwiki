# ============================================================
# Database Engine & Session Management
# ============================================================
# SQLAlchemy async engine with pgvector support
# ============================================================

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

# Session factory
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


async def get_db():
    """Dependency for FastAPI endpoints."""
    async with SessionLocal() as session:
        yield session