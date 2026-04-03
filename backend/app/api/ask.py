# ============================================================
# Ask API - Conversational Q&A with Citations
# ============================================================

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

import anthropic

from app.db import get_db
from app.config import settings
from app.engine.query import semantic_search


router = APIRouter(tags=["ask"])

# Claude client
client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


# ============================================================
# Request/Response Models
# ============================================================

class AskRequest(BaseModel):
    """Request model for Q&A."""
    question: str
    limit: int = 5


class Citation(BaseModel):
    """Citation to source material."""
    id: str
    title: str


class AskResponse(BaseModel):
    """Response model for Q&A."""
    answer: str
    citations: List[Citation]


# ============================================================
# System Prompt
# ============================================================

ASK_SYSTEM_PROMPT = """You are OpenWiki's Q&A assistant. Your role is to answer questions based on the provided knowledge base context.

Guidelines:
1. Only use information from the provided context
2. If the context doesn't contain relevant information, say so
3. Be concise but thorough
4. Cite sources using [ID:xxx] format when referencing specific entries
5. At the end, list sources used

Format your response as:
1. Direct answer to the question
2. Supporting details from context
3. Sources section listing the titles used"""


# ============================================================
# Endpoint
# ============================================================

@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest, db: AsyncSession = Depends(get_db)):
    """
    Ask a question and get an answer with citations.

    1. Searches for relevant wiki entries
    2. Uses Claude to generate answer with citations
    3. Returns structured response
    """
    # Retrieve relevant entries
    results = await semantic_search(req.question, db, limit=req.limit)

    # Build context from results
    if not results:
        return AskResponse(
            answer="I don't have any relevant information about that topic in my knowledge base.",
            citations=[],
        )

    context = "\n\n".join(
        f"[ID:{r['id']}] Title: {r['title']}\n{r['content'][:2000]}"
        for r in results
    )

    # Create prompt for Claude
    prompt = f"""Context from knowledge base:
{context}

Question: {req.question}

Please answer the question based on the provided context. Use [ID:xxx] citations when referencing specific entries."""

    # Call Claude
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=ASK_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": prompt,
        }],
    )

    answer = response.content[0].text

    # Extract citations from results
    citations = [
        Citation(id=r["id"], title=r["title"])
        for r in results
    ]

    return AskResponse(
        answer=answer,
        citations=citations,
    )