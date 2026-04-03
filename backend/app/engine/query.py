# ============================================================
# Query Engine - Vector Embeddings + Semantic Search
# ============================================================
# Generates embeddings and performs pgvector similarity search
# ============================================================

import hashlib
import struct
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wiki_entry import WikiEntry
from app.models.material import Material


# ============================================================
# Embedding Generation
# ============================================================

async def get_embedding(text_input: str) -> List[float]:
    """
    Generate embedding vector for text input.

    Currently uses deterministic hash-based pseudo-embedding for dev/testing.
    In production, this should use:
    - Anthropic's embedding API (when available)
    - Or OpenAI text-embedding-3-small
    - Or a local embedding model

    Args:
        text_input: Text to embed

    Returns:
        1024-dimensional float vector
    """
    import math

    # Deterministic pseudo-embedding using SHA-512
    h = hashlib.sha512(text_input.encode()).digest()

    # Generate 1024 floats from hash
    vec = []
    offset = 0
    while len(vec) < 1024:
        # Use modulo to cycle through hash bytes
        i = offset % len(h)
        # Get two bytes and convert to float in [0, 1)
        val = (h[i] * 256 + h[(i + 1) % len(h)]) / 65536.0
        # Convert to [-1, 1] range
        normalized = val * 2.0 - 1.0
        # Ensure no NaN or Inf
        if math.isnan(normalized) or math.isinf(normalized):
            normalized = 0.0
        vec.append(normalized)
        offset += 1

    return vec[:1024]


# ============================================================
# Semantic Search
# ============================================================

async def semantic_search(
    query: str,
    db: AsyncSession,
    limit: int = 5,
) -> List[dict]:
    """
    Search wiki entries by semantic similarity.

    Args:
        query: Search query text
        db: Async database session
        limit: Maximum results to return

    Returns:
        List of dicts with id, title, content, topic
    """
    # Generate embedding for query
    query_vec = await get_embedding(query)

    # Build query with cosine distance ordering
    # pgvector provides cosine_distance function
    result = await db.execute(
        select(WikiEntry)
        .where(WikiEntry.embedding.isnot(None))
        .order_by(WikiEntry.embedding.cosine_distance(query_vec))
        .limit(limit)
    )
    entries = result.scalars().all()

    # Format results
    return [
        {
            "id": str(e.id),
            "title": e.title,
            "content": e.content,
        }
        for e in entries
    ]


async def semantic_search_materials(
    query: str,
    db: AsyncSession,
    limit: int = 5,
) -> List[dict]:
    """
    Search materials by semantic similarity.

    Args:
        query: Search query text
        db: Async database session
        limit: Maximum results to return

    Returns:
        List of dicts with id, title, summary, source_url
    """
    query_vec = await get_embedding(query)

    result = await db.execute(
        select(Material)
        .where(Material.embedding.isnot(None))
        .order_by(Material.embedding.cosine_distance(query_vec))
        .limit(limit)
    )
    materials = result.scalars().all()

    return [
        {
            "id": str(m.id),
            "title": m.title,
            "summary": m.summary,
            "source_url": m.source_url,
            "file_key": m.file_key,
        }
        for m in materials
    ]


# ============================================================
# Embedding Helper for Persistence
# ============================================================

async def embed_text_and_save(
    text: str,
    model: WikiEntry | Material,
    db: AsyncSession,
) -> None:
    """
    Generate embedding and save to model instance.

    Args:
        text: Text to embed (typically content or summary)
        model: Model instance to update
        db: Database session
    """
    embedding = await get_embedding(text)
    model.embedding = embedding
    await db.commit()