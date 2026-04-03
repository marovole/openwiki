# ============================================================
# Ingestion API Integration Tests
# ============================================================

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

from app.main import app
from app.db import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text


# Test database URL
TEST_DB_URL = "postgresql+asyncpg://openwiki:openwiki_dev@localhost:5432/openwiki_test"


@pytest_asyncio.fixture
async def api_client():
    """Create a test client with database setup."""
    # Create engine and tables
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Override the get_db dependency
    async def get_test_db():
        async with session_factory() as session:
            yield session

    from app.main import app
    from app.db import get_db
    app.dependency_overrides[get_db] = get_test_db

    # Create client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Cleanup
    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


class TestIngestAPI:
    """Test ingestion API endpoints."""

    @pytest.mark.asyncio
    async def test_ingest_url_endpoint(self, api_client):
        """Test POST /ingest/url endpoint."""
        mock_html = """
        <html>
            <head><title>Test Article</title></head>
            <body><article><h1>Hello</h1><p>World</p></article></body>
        </html>
        """

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = AsyncMock()
            mock_response.text = mock_html
            mock_response.raise_for_status = lambda: None
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            resp = await api_client.post("/ingest/url", json={"url": "https://example.com"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "pending"
        assert "Test Article" in data["title"]
        assert data["source_url"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_ingest_url_invalid_url(self, api_client):
        """Test POST /ingest/url with invalid URL."""
        resp = await api_client.post("/ingest/url", json={"url": "not-a-url"})

        assert resp.status_code == 400
        assert "Invalid URL" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_ingest_upload_endpoint(self, api_client):
        """Test POST /ingest/upload endpoint."""
        resp = await api_client.post(
            "/ingest/upload",
            files={"file": ("test.md", b"# Test\n\nThis is test content.", "text/markdown")},
            data={"title": "Test Upload"},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "pending"
        assert data["title"] == "Test Upload"
        assert data["source_url"] is None

    @pytest.mark.asyncio
    async def test_ingest_upload_default_title(self, api_client):
        """Test POST /ingest/upload uses filename as default title."""
        resp = await api_client.post(
            "/ingest/upload",
            files={"file": ("my-note.md", b"# My Note", "text/markdown")},
            data={},  # No title provided
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "my-note.md"