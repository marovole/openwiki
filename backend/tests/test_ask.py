# ============================================================
# Ask API Tests - Conversational Q&A
# ============================================================

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock

from app.main import app
from app.models.wiki_entry import WikiEntry
from app.engine.query import get_embedding
from app.db import get_db, SessionLocal
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.db import Base


TEST_DB_URL = "postgresql+asyncpg://openwiki:openwiki_dev@localhost:5432/openwiki_test"


@pytest_asyncio.fixture
async def api_client():
    """Create a test client with database setup."""
    engine = create_async_engine(TEST_DB_URL, echo=False)

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def get_test_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


class TestAskEndpoint:
    """Test conversational Q&A endpoint."""

    @pytest.mark.asyncio
    async def test_ask_endpoint_with_results(self, api_client):
        """Test ask endpoint returns answer with citations."""
        # Mock semantic_search to return results
        mock_results = [
            {
                "id": "test-id-123",
                "title": "Neural Networks Guide",
                "content": "# Neural Networks\n\nNeural networks are computational models inspired by the brain.",
            }
        ]

        # Mock LLM response
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = """Based on the provided context:

Neural networks are computational models inspired by the brain. They consist of layers of interconnected nodes that process information.

**Sources:**
- Neural Networks Guide"""
        mock_response.content = [mock_content]

        with patch("app.api.ask.semantic_search", new_callable=AsyncMock) as mock_search:
            with patch("app.api.ask.client") as mock_client:
                mock_search.return_value = mock_results
                mock_client.messages = MagicMock()
                mock_client.messages.create = AsyncMock(return_value=mock_response)

                resp = await api_client.post("/ask", json={"question": "What are neural networks?"})

        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert "citations" in data
        assert isinstance(data["citations"], list)

    @pytest.mark.asyncio
    async def test_ask_endpoint_no_results(self, api_client):
        """Test ask endpoint handles no relevant results."""
        # Mock semantic_search to return empty results
        mock_results = []

        with patch("app.api.ask.semantic_search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_results

            resp = await api_client.post("/ask", json={"question": "What is quantum computing?"})

        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert "I don't have any relevant information" in data["answer"]
        assert data["citations"] == []