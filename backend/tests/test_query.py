# ============================================================
# Query Engine Tests - Vector Search
# ============================================================

import pytest
from unittest.mock import patch, AsyncMock

from app.engine.query import get_embedding, semantic_search
from app.models.wiki_entry import WikiEntry
from app.models.material import Material, MaterialStatus


class TestGetEmbedding:
    """Test embedding generation."""

    @pytest.mark.asyncio
    async def test_get_embedding_returns_vector(self):
        """Embedding should return a 1024-dimensional vector."""
        vec = await get_embedding("What is a neural network?")
        assert isinstance(vec, list)
        assert len(vec) == 1024
        # All values should be floats
        assert all(isinstance(v, float) for v in vec)

    @pytest.mark.asyncio
    async def test_get_embedding_deterministic(self):
        """Same input should produce same embedding."""
        vec1 = await get_embedding("test input")
        vec2 = await get_embedding("test input")
        assert vec1 == vec2

    @pytest.mark.asyncio
    async def test_get_embedding_different_inputs(self):
        """Different inputs should produce different embeddings."""
        vec1 = await get_embedding("neural networks")
        vec2 = await get_embedding("cooking recipes")
        assert vec1 != vec2


class TestSemanticSearch:
    """Test semantic search functionality."""

    @pytest.mark.asyncio
    async def test_semantic_search_finds_relevant(self, db_session):
        """Semantic search should find relevant entries."""
        # Create entries with embeddings
        vec1 = await get_embedding("neural network deep learning AI")
        entry1 = WikiEntry(
            title="Neural Networks Guide",
            content="# Neural Networks\n\nNeural networks are computational models inspired by the brain.",
            embedding=vec1,
        )
        db_session.add(entry1)

        vec2 = await get_embedding("cooking recipes food kitchen")
        entry2 = WikiEntry(
            title="Cooking Recipes",
            content="# Recipes\n\nHow to cook delicious food.",
            embedding=vec2,
        )
        db_session.add(entry2)
        await db_session.commit()

        # Search for neural networks
        results = await semantic_search("how do neural nets work?", db_session, limit=5)

        assert len(results) >= 1
        # First result should be about neural networks
        assert "Neural" in results[0]["title"]

    @pytest.mark.asyncio
    async def test_semantic_search_excludes_null_embeddings(self, db_session):
        """Search should only return entries with embeddings."""
        # Entry with embedding
        vec = await get_embedding("machine learning")
        entry1 = WikiEntry(
            title="ML Guide",
            content="Machine learning content",
            embedding=vec,
        )
        db_session.add(entry1)

        # Entry without embedding
        entry2 = WikiEntry(
            title="No Embedding",
            content="This has no embedding",
            embedding=None,
        )
        db_session.add(entry2)
        await db_session.commit()

        results = await semantic_search("machine learning", db_session, limit=5)

        # Should only return entry with embedding
        assert len(results) == 1
        assert results[0]["title"] == "ML Guide"

    @pytest.mark.asyncio
    async def test_semantic_search_respects_limit(self, db_session):
        """Search should respect the limit parameter."""
        # Create multiple entries
        for i in range(10):
            vec = await get_embedding(f"document {i}")
            entry = WikiEntry(
                title=f"Doc {i}",
                content=f"Content {i}",
                embedding=vec,
            )
            db_session.add(entry)
        await db_session.commit()

        results = await semantic_search("document", db_session, limit=3)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_semantic_search_returns_structure(self, db_session):
        """Search results should have expected structure."""
        vec = await get_embedding("test content")
        entry = WikiEntry(
            title="Test Entry",
            content="Test content here",
            embedding=vec,
        )
        db_session.add(entry)
        await db_session.commit()

        results = await semantic_search("test", db_session, limit=1)

        assert len(results) == 1
        result = results[0]
        assert "id" in result
        assert "title" in result
        assert "content" in result
        assert result["title"] == "Test Entry"