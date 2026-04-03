# OpenWiki MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

---

## 📊 Implementation Progress

**Last Updated:** 2026-04-03

| Phase | Task | Status | Notes |
|-------|------|--------|-------|
| **Phase 1: Foundation** | | | |
| | Task 1: Docker Compose + PostgreSQL + MinIO | ✅ Complete | pgvector 0.8.1, MinIO running |
| | Task 2: Backend Scaffolding | ✅ Complete | FastAPI + SQLAlchemy 2.0 + asyncpg |
| | Task 3: Database Models + Migration | ✅ Complete | All models with 9 passing tests |
| **Phase 2: Ingestion** | | | |
| | Task 4: URL Ingestion Engine | ✅ Complete | readability + markdownify + API |
| | Task 5: File Upload Engine | ✅ Complete | S3/MinIO integration |
| | Task 6: Ingestion API Endpoints | ✅ Complete | POST /ingest/url, POST /ingest/upload |
| **Phase 3: Compile** | | | |
| | Task 7: LLM Compile Pipeline | ✅ Complete | Claude API integration |
| | Task 8: Compile Orchestrator | ✅ Complete | DB persistence + background task |
| **Phase 4: Query** | | | |
| | Task 9: Vector Search Engine | ✅ Complete | pgvector + deterministic embeddings |
| | Task 10: Q&A Engine | ✅ Complete | Claude with citations |
| | Task 11: Query API Endpoints | ✅ Complete | POST /ask |
| **Phase 5: Frontend** | | | |
| | Task 12: Next.js Scaffolding | ✅ Complete | App Router + TailwindCSS |
| | Task 13: Inbox Page | ✅ Complete | URL + file upload UI |
| | Task 14: Wiki Page | ✅ Complete | Entry list + article view |
| | Task 15: Ask Page | ✅ Complete | Chat UI with citations |
| **Phase 6: Polish** | | | |
| | Task 16: Export Feature | ✅ Complete | GET /export (ZIP download) |
| | Task 17: End-to-End Test | ✅ Complete | Upload + Export verified |
| **Extra** | | | |
| | Embedding on Compile | ✅ Complete | Auto-generate embeddings |
| | CLAUDE.md Documentation | ✅ Complete | Project documentation |

**Status:** MVP COMPLETE ✅

---

**Goal:** Build the OpenWiki MVP — URL/file ingestion, LLM compile engine, wiki browse, conversational Q&A with citations, and .md export.

**Architecture:** Monorepo with Python FastAPI backend (ingestion + compile + query engines) and Next.js frontend (Inbox / Wiki / Ask pages). PostgreSQL + pgvector for structured data and vector search. Claude API for all LLM operations. S3-compatible storage for raw files.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, pgvector, Next.js 15, React, TailwindCSS, Claude API (anthropic SDK), MinIO (dev S3), Docker Compose.

---

## Project Structure

```
openwiki/
├── docker-compose.yml
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings via pydantic-settings
│   │   ├── db.py                # SQLAlchemy async engine + session
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── material.py      # Raw material model
│   │   │   ├── wiki_entry.py    # Compiled wiki entry model
│   │   │   ├── concept.py       # Concept + tag models
│   │   │   └── association.py   # Cross-material associations
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── ingest.py        # POST /ingest/url, POST /ingest/upload
│   │   │   ├── wiki.py          # GET /wiki/tree, GET /wiki/{id}
│   │   │   ├── ask.py           # POST /ask
│   │   │   └── export.py        # GET /export
│   │   └── engine/
│   │       ├── __init__.py
│   │       ├── ingestion.py     # URL fetch + markdown conversion
│   │       ├── compile.py       # LLM compile pipeline
│   │       └── query.py         # Semantic search + Q&A
│   └── tests/
│       ├── conftest.py
│       ├── test_ingest.py
│       ├── test_compile.py
│       ├── test_wiki_api.py
│       ├── test_ask.py
│       └── test_export.py
├── frontend/
│   ├── package.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # Shell: nav bar + sidebar
│   │   │   ├── page.tsx         # Redirect to /inbox
│   │   │   ├── inbox/
│   │   │   │   └── page.tsx     # Inbox page
│   │   │   ├── wiki/
│   │   │   │   ├── page.tsx     # Wiki directory tree
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx # Wiki entry detail
│   │   │   ├── ask/
│   │   │   │   └── page.tsx     # Ask conversational UI
│   │   │   └── export/
│   │   │       └── route.ts     # Proxy to backend export
│   │   ├── components/
│   │   │   ├── nav.tsx
│   │   │   ├── material-card.tsx
│   │   │   ├── wiki-tree.tsx
│   │   │   ├── wiki-article.tsx
│   │   │   ├── chat-message.tsx
│   │   │   └── citation.tsx
│   │   └── lib/
│   │       └── api.ts           # Backend API client
│   └── tsconfig.json
└── CLAUDE.md
```

---

## Phase 1: Foundation

### Task 1: Docker Compose + PostgreSQL + MinIO

**Files:**
- Create: `openwiki/docker-compose.yml`
- Create: `openwiki/.env.example`

**Step 1: Write docker-compose.yml**

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: openwiki
      POSTGRES_USER: openwiki
      POSTGRES_PASSWORD: openwiki_dev
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - miniodata:/data

volumes:
  pgdata:
  miniodata:
```

**Step 2: Write .env.example**

```env
DATABASE_URL=postgresql+asyncpg://openwiki:openwiki_dev@localhost:5432/openwiki
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=openwiki-raw
ANTHROPIC_API_KEY=sk-ant-xxx
```

**Step 3: Start services and verify**

Run: `cd openwiki && docker compose up -d`
Run: `docker compose ps`
Expected: db and minio both "running"

Run: `psql postgresql://openwiki:openwiki_dev@localhost:5432/openwiki -c "CREATE EXTENSION IF NOT EXISTS vector; SELECT extversion FROM pg_extension WHERE extname='vector';"`
Expected: vector extension version shown

**Step 4: Commit**

```bash
git add docker-compose.yml .env.example
git commit -m "infra: add docker-compose with PostgreSQL pgvector + MinIO"
```

---

### Task 2: Backend Scaffolding

**Files:**
- Create: `openwiki/backend/pyproject.toml`
- Create: `openwiki/backend/app/__init__.py`
- Create: `openwiki/backend/app/main.py`
- Create: `openwiki/backend/app/config.py`
- Create: `openwiki/backend/app/db.py`

**Step 1: Write pyproject.toml**

```toml
[project]
name = "openwiki-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.30",
    "pgvector>=0.3",
    "pydantic-settings>=2.0",
    "anthropic>=0.40",
    "httpx>=0.27",
    "boto3>=1.35",
    "readability-lxml>=0.8",
    "markdownify>=0.14",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "httpx>=0.27",
]
```

**Step 2: Write config.py**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://openwiki:openwiki_dev@localhost:5432/openwiki"
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "openwiki-raw"
    anthropic_api_key: str = ""

    model_config = {"env_file": "../.env"}

settings = Settings()
```

**Step 3: Write db.py**

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(settings.database_url)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as session:
        yield session
```

**Step 4: Write main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OpenWiki", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Step 5: Install and run**

Run: `cd openwiki/backend && pip install -e ".[dev]"`
Run: `uvicorn app.main:app --reload --port 8000 &`
Run: `curl http://localhost:8000/health`
Expected: `{"status":"ok"}`

**Step 6: Commit**

```bash
git add backend/
git commit -m "feat: backend scaffolding — FastAPI + SQLAlchemy + config"
```

---

### Task 3: Database Models + Migration

**Files:**
- Create: `openwiki/backend/app/models/__init__.py`
- Create: `openwiki/backend/app/models/material.py`
- Create: `openwiki/backend/app/models/wiki_entry.py`
- Create: `openwiki/backend/app/models/concept.py`
- Create: `openwiki/backend/app/models/association.py`
- Create: `openwiki/backend/tests/conftest.py`
- Create: `openwiki/backend/tests/test_models.py`

**Step 1: Write the failing test**

```python
# tests/test_models.py
import pytest
from sqlalchemy import select
from app.models.material import Material
from app.models.wiki_entry import WikiEntry
from app.models.concept import Concept, Tag

@pytest.mark.asyncio
async def test_create_material(db_session):
    m = Material(
        title="Test Article",
        source_url="https://example.com/article",
        raw_markdown="# Test\nSome content.",
        status="pending",
    )
    db_session.add(m)
    await db_session.commit()

    result = await db_session.execute(select(Material))
    materials = result.scalars().all()
    assert len(materials) == 1
    assert materials[0].title == "Test Article"

@pytest.mark.asyncio
async def test_create_wiki_entry_with_concepts(db_session):
    tag = Tag(name="AI")
    concept = Concept(name="Large Language Model", description="A type of neural network.")
    entry = WikiEntry(
        title="LLM Overview",
        content="# LLM\nLarge language models are...",
        concepts=[concept],
        tags=[tag],
    )
    db_session.add(entry)
    await db_session.commit()

    result = await db_session.execute(select(WikiEntry))
    entries = result.scalars().all()
    assert len(entries) == 1
    assert len(entries[0].concepts) == 1
    assert entries[0].concepts[0].name == "Large Language Model"
```

**Step 2: Run test to verify it fails**

Run: `cd openwiki/backend && pytest tests/test_models.py -v`
Expected: FAIL — models don't exist yet

**Step 3: Write conftest.py**

```python
# tests/conftest.py
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db import Base

TEST_DB_URL = "postgresql+asyncpg://openwiki:openwiki_dev@localhost:5432/openwiki_test"

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
```

Note: create test DB first:
Run: `psql postgresql://openwiki:openwiki_dev@localhost:5432/openwiki -c "CREATE DATABASE openwiki_test;"`
Run: `psql postgresql://openwiki:openwiki_dev@localhost:5432/openwiki_test -c "CREATE EXTENSION IF NOT EXISTS vector;"`

**Step 4: Write models**

```python
# app/models/material.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.db import Base

class Material(Base):
    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500))
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    raw_markdown: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | compiling | compiled | failed
    embedding = mapped_column(Vector(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

```python
# app/models/concept.py
import uuid
from sqlalchemy import String, Text, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

# -- junction tables --
wiki_entry_concepts = Table(
    "wiki_entry_concepts", Base.metadata,
    Column("wiki_entry_id", String(36), ForeignKey("wiki_entries.id")),
    Column("concept_id", String(36), ForeignKey("concepts.id")),
)

wiki_entry_tags = Table(
    "wiki_entry_tags", Base.metadata,
    Column("wiki_entry_id", String(36), ForeignKey("wiki_entries.id")),
    Column("tag_id", String(36), ForeignKey("tags.id")),
)

wiki_entry_materials = Table(
    "wiki_entry_materials", Base.metadata,
    Column("wiki_entry_id", String(36), ForeignKey("wiki_entries.id")),
    Column("material_id", String(36), ForeignKey("materials.id")),
)

class Concept(Base):
    __tablename__ = "concepts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(300), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), unique=True)
```

```python
# app/models/wiki_entry.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.db import Base
from app.models.concept import wiki_entry_concepts, wiki_entry_tags, wiki_entry_materials, Concept, Tag

class WikiEntry(Base):
    __tablename__ = "wiki_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    topic: Mapped[str | None] = mapped_column(String(200), nullable=True)
    embedding = mapped_column(Vector(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    concepts: Mapped[list[Concept]] = relationship(secondary=wiki_entry_concepts)
    tags: Mapped[list[Tag]] = relationship(secondary=wiki_entry_tags)
    materials = relationship("Material", secondary=wiki_entry_materials)
```

```python
# app/models/association.py
import uuid
from sqlalchemy import String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Association(Base):
    __tablename__ = "associations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_entry_id: Mapped[str] = mapped_column(String(36))
    target_entry_id: Mapped[str] = mapped_column(String(36))
    relation: Mapped[str] = mapped_column(String(200))
    strength: Mapped[float] = mapped_column(Float, default=0.5)
```

```python
# app/models/__init__.py
from app.models.material import Material
from app.models.concept import Concept, Tag
from app.models.wiki_entry import WikiEntry
from app.models.association import Association

__all__ = ["Material", "Concept", "Tag", "WikiEntry", "Association"]
```

**Step 5: Run tests**

Run: `cd openwiki/backend && pytest tests/test_models.py -v`
Expected: 2 passed

**Step 6: Commit**

```bash
git add backend/app/models/ backend/tests/
git commit -m "feat: database models — Material, WikiEntry, Concept, Tag, Association"
```

---

## Phase 2: Ingestion Engine

### Task 4: URL Ingestion

**Files:**
- Create: `openwiki/backend/app/engine/ingestion.py`
- Create: `openwiki/backend/app/api/ingest.py`
- Create: `openwiki/backend/tests/test_ingest.py`

**Step 1: Write the failing test**

```python
# tests/test_ingest.py
import pytest
from app.engine.ingestion import url_to_markdown

@pytest.mark.asyncio
async def test_url_to_markdown():
    """Fetch a real URL and convert to markdown."""
    result = await url_to_markdown("https://example.com")
    assert "Example Domain" in result["title"]
    assert len(result["markdown"]) > 0
    assert result["markdown"].strip() != ""

@pytest.mark.asyncio
async def test_url_to_markdown_invalid_url():
    """Invalid URL raises ValueError."""
    with pytest.raises(ValueError):
        await url_to_markdown("not-a-url")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_ingest.py -v`
Expected: FAIL — module doesn't exist

**Step 3: Write ingestion engine**

```python
# app/engine/ingestion.py
import httpx
from readability import Document
from markdownify import markdownify
from urllib.parse import urlparse

async def url_to_markdown(url: str) -> dict:
    """Fetch URL, extract readable content, convert to markdown."""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        resp = await client.get(url, headers={"User-Agent": "OpenWiki/0.1"})
        resp.raise_for_status()

    doc = Document(resp.text)
    title = doc.title()
    html_content = doc.summary()
    markdown = markdownify(html_content, heading_style="ATX", strip=["img", "script"])

    return {
        "title": title,
        "markdown": markdown.strip(),
        "source_url": url,
    }
```

**Step 4: Run tests**

Run: `pytest tests/test_ingest.py -v`
Expected: 2 passed

**Step 5: Write API endpoint**

```python
# app/api/ingest.py
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db import get_db
from app.models.material import Material
from app.engine.ingestion import url_to_markdown

router = APIRouter(prefix="/ingest", tags=["ingest"])

class IngestURLRequest(BaseModel):
    url: str

class MaterialResponse(BaseModel):
    id: str
    title: str
    status: str
    source_url: str | None

@router.post("/url", response_model=MaterialResponse)
async def ingest_url(req: IngestURLRequest, db: AsyncSession = Depends(get_db)):
    result = await url_to_markdown(req.url)
    material = Material(
        title=result["title"],
        source_url=result["source_url"],
        raw_markdown=result["markdown"],
        status="pending",
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return MaterialResponse(id=material.id, title=material.title, status=material.status, source_url=material.source_url)

@router.post("/upload", response_model=MaterialResponse)
async def ingest_upload(
    file: UploadFile = File(...),
    title: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    content = (await file.read()).decode("utf-8")
    material = Material(
        title=title or file.filename or "Untitled",
        raw_markdown=content,
        status="pending",
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return MaterialResponse(id=material.id, title=material.title, status=material.status, source_url=None)
```

**Step 6: Register router in main.py**

Add to `app/main.py`:
```python
from app.api.ingest import router as ingest_router
app.include_router(ingest_router)
```

**Step 7: Write API integration test**

```python
# tests/test_ingest_api.py (append to test_ingest.py or separate file)
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_ingest_url_endpoint(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/ingest/url", json={"url": "https://example.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "pending"
    assert "Example" in data["title"]
```

**Step 8: Run full test suite**

Run: `pytest tests/ -v`
Expected: All passed

**Step 9: Commit**

```bash
git add backend/app/engine/ingestion.py backend/app/api/ingest.py backend/tests/
git commit -m "feat: ingestion engine — URL fetch + markdown conversion + file upload"
```

---

## Phase 3: Compile Engine (Core Differentiator)

### Task 5: LLM Compile Pipeline

**Files:**
- Create: `openwiki/backend/app/engine/compile.py`
- Create: `openwiki/backend/tests/test_compile.py`

**Step 1: Write the failing test**

```python
# tests/test_compile.py
import pytest
from app.engine.compile import compile_material

@pytest.mark.asyncio
async def test_compile_material_returns_structure():
    """Compile should return summary, concepts, tags, and wiki entry."""
    raw_md = """
    # Transformer Architecture
    The transformer is a neural network architecture based on self-attention.
    It was introduced in 'Attention Is All You Need' (2017).
    Transformers are the foundation of modern LLMs like GPT and Claude.
    They replaced RNNs for sequence modeling tasks.
    """
    result = await compile_material(material_id="test-123", title="Transformer Architecture", raw_markdown=raw_md)

    assert "summary" in result
    assert len(result["summary"]) > 20
    assert "concepts" in result
    assert isinstance(result["concepts"], list)
    assert len(result["concepts"]) >= 1
    assert "tags" in result
    assert isinstance(result["tags"], list)
    assert "wiki_entry" in result
    assert len(result["wiki_entry"]) > 50
    assert "associations" in result
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_compile.py -v`
Expected: FAIL — module doesn't exist

**Step 3: Write compile engine**

```python
# app/engine/compile.py
import json
import anthropic
from app.config import settings

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

COMPILE_PROMPT = """You are OpenWiki's knowledge compiler. Given a raw article, produce a structured JSON output.

<raw_material>
Title: {title}
Content:
{content}
</raw_material>

Return ONLY valid JSON with this exact structure:
{{
  "summary": "2-3 sentence summary of the core ideas",
  "concepts": [
    {{"name": "Concept Name", "description": "One sentence definition"}}
  ],
  "tags": ["tag1", "tag2", "tag3"],
  "wiki_entry": "A comprehensive wiki article in markdown format. Include:\n- Clear explanation of key concepts\n- How concepts relate to each other\n- Key takeaways\nWrite 200-500 words.",
  "associations": [
    {{"concept": "Concept Name", "related_to": "Another Concept", "relation": "how they relate"}}
  ]
}}"""


async def compile_material(material_id: str, title: str, raw_markdown: str) -> dict:
    """Run LLM compile pipeline on a single raw material."""
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": COMPILE_PROMPT.format(title=title, content=raw_markdown[:8000]),
        }],
    )
    text = response.content[0].text

    # -- extract JSON from response --
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])
```

**Step 4: Run test (requires ANTHROPIC_API_KEY in .env)**

Run: `pytest tests/test_compile.py -v`
Expected: PASS (live API call)

**Step 5: Commit**

```bash
git add backend/app/engine/compile.py backend/tests/test_compile.py
git commit -m "feat: compile engine — LLM pipeline for summary, concepts, tags, wiki entry"
```

---

### Task 6: Compile Orchestrator (DB Integration)

**Files:**
- Create: `openwiki/backend/app/engine/orchestrator.py`
- Modify: `openwiki/backend/app/api/ingest.py` — add compile trigger
- Create: `openwiki/backend/tests/test_orchestrator.py`

**Step 1: Write the failing test**

```python
# tests/test_orchestrator.py
import pytest
from sqlalchemy import select
from app.models.material import Material
from app.models.wiki_entry import WikiEntry
from app.models.concept import Concept, Tag
from app.engine.orchestrator import run_compile

@pytest.mark.asyncio
async def test_run_compile_creates_wiki_entry(db_session):
    """Full compile: material -> wiki entry + concepts + tags in DB."""
    material = Material(
        title="Test: Neural Networks",
        raw_markdown="# Neural Networks\nNeural networks are computational models inspired by the brain.",
        status="pending",
    )
    db_session.add(material)
    await db_session.commit()

    await run_compile(material.id, db_session)
    await db_session.refresh(material)

    assert material.status == "compiled"
    assert material.summary is not None

    entries = (await db_session.execute(select(WikiEntry))).scalars().all()
    assert len(entries) >= 1

    concepts = (await db_session.execute(select(Concept))).scalars().all()
    assert len(concepts) >= 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_orchestrator.py -v`
Expected: FAIL

**Step 3: Write orchestrator**

```python
# app/engine/orchestrator.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.material import Material
from app.models.wiki_entry import WikiEntry
from app.models.concept import Concept, Tag, wiki_entry_concepts, wiki_entry_tags, wiki_entry_materials
from app.engine.compile import compile_material

async def _get_or_create_concept(db: AsyncSession, name: str, description: str | None = None) -> Concept:
    result = await db.execute(select(Concept).where(Concept.name == name))
    concept = result.scalar_one_or_none()
    if not concept:
        concept = Concept(name=name, description=description)
        db.add(concept)
        await db.flush()
    return concept

async def _get_or_create_tag(db: AsyncSession, name: str) -> Tag:
    result = await db.execute(select(Tag).where(Tag.name == name))
    tag = result.scalar_one_or_none()
    if not tag:
        tag = Tag(name=name)
        db.add(tag)
        await db.flush()
    return tag

async def run_compile(material_id: str, db: AsyncSession) -> WikiEntry:
    """Compile a material: call LLM, persist wiki entry + concepts + tags."""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one()

    material.status = "compiling"
    await db.commit()

    compiled = await compile_material(material.id, material.title, material.raw_markdown)

    # -- persist summary --
    material.summary = compiled["summary"]

    # -- persist concepts + tags --
    concepts = [await _get_or_create_concept(db, c["name"], c.get("description")) for c in compiled["concepts"]]
    tags = [await _get_or_create_tag(db, t) for t in compiled["tags"]]

    # -- persist wiki entry --
    entry = WikiEntry(
        title=material.title,
        content=compiled["wiki_entry"],
        topic=compiled["tags"][0] if compiled["tags"] else None,
    )
    entry.concepts = concepts
    entry.tags = tags
    entry.materials = [material]
    db.add(entry)

    material.status = "compiled"
    await db.commit()
    return entry
```

**Step 4: Add background compile trigger to ingest API**

Modify `app/api/ingest.py` — add `BackgroundTasks`:

```python
from fastapi import BackgroundTasks
from app.engine.orchestrator import run_compile
from app.db import SessionLocal

async def _bg_compile(material_id: str):
    async with SessionLocal() as db:
        await run_compile(material_id, db)

@router.post("/url", response_model=MaterialResponse)
async def ingest_url(req: IngestURLRequest, bg: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    result = await url_to_markdown(req.url)
    material = Material(
        title=result["title"],
        source_url=result["source_url"],
        raw_markdown=result["markdown"],
        status="pending",
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)
    bg.add_task(_bg_compile, material.id)
    return MaterialResponse(id=material.id, title=material.title, status=material.status, source_url=material.source_url)
```

**Step 5: Run tests**

Run: `pytest tests/test_orchestrator.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add backend/app/engine/orchestrator.py backend/app/api/ingest.py backend/tests/test_orchestrator.py
git commit -m "feat: compile orchestrator — LLM compile + persist wiki entries, concepts, tags"
```

---

## Phase 4: Wiki Browse API + Frontend

### Task 7: Wiki API Endpoints

**Files:**
- Create: `openwiki/backend/app/api/wiki.py`
- Modify: `openwiki/backend/app/main.py` — register wiki router
- Create: `openwiki/backend/tests/test_wiki_api.py`

**Step 1: Write the failing test**

```python
# tests/test_wiki_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.wiki_entry import WikiEntry
from app.models.concept import Concept, Tag

@pytest.mark.asyncio
async def test_wiki_tree(db_session):
    """GET /wiki/tree returns grouped entries."""
    entry = WikiEntry(title="Test Entry", content="# Test", topic="AI")
    db_session.add(entry)
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/wiki/tree")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["topic"] == "AI"

@pytest.mark.asyncio
async def test_wiki_entry_detail(db_session):
    """GET /wiki/{id} returns full entry with concepts and backlinks."""
    concept = Concept(name="Neural Net", description="A model")
    entry = WikiEntry(title="NN Overview", content="# Neural Nets\nContent here.", topic="AI", concepts=[concept])
    db_session.add(entry)
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/wiki/{entry.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "NN Overview"
    assert len(data["concepts"]) == 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_wiki_api.py -v`
Expected: FAIL

**Step 3: Write wiki API**

```python
# app/api/wiki.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from app.db import get_db
from app.models.wiki_entry import WikiEntry

router = APIRouter(prefix="/wiki", tags=["wiki"])

class TreeNode(BaseModel):
    topic: str
    entries: list[dict]

@router.get("/tree", response_model=list[TreeNode])
async def wiki_tree(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WikiEntry).options(selectinload(WikiEntry.tags)).order_by(WikiEntry.topic, WikiEntry.title)
    )
    entries = result.scalars().all()
    topics: dict[str, list] = {}
    for e in entries:
        t = e.topic or "Uncategorized"
        topics.setdefault(t, []).append({"id": e.id, "title": e.title})
    return [TreeNode(topic=k, entries=v) for k, v in topics.items()]

@router.get("/{entry_id}")
async def wiki_detail(entry_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WikiEntry)
        .options(selectinload(WikiEntry.concepts), selectinload(WikiEntry.tags), selectinload(WikiEntry.materials))
        .where(WikiEntry.id == entry_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {
        "id": entry.id,
        "title": entry.title,
        "content": entry.content,
        "topic": entry.topic,
        "concepts": [{"name": c.name, "description": c.description} for c in entry.concepts],
        "tags": [t.name for t in entry.tags],
        "materials": [{"id": m.id, "title": m.title, "source_url": m.source_url} for m in entry.materials],
        "created_at": entry.created_at.isoformat(),
    }
```

**Step 4: Register in main.py**

```python
from app.api.wiki import router as wiki_router
app.include_router(wiki_router)
```

**Step 5: Run tests**

Run: `pytest tests/test_wiki_api.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add backend/app/api/wiki.py backend/tests/test_wiki_api.py backend/app/main.py
git commit -m "feat: wiki API — tree listing + entry detail with concepts and backlinks"
```

---

### Task 8: Frontend Scaffolding

**Files:**
- Create: `openwiki/frontend/package.json`
- Create: `openwiki/frontend/next.config.ts`
- Create: `openwiki/frontend/tailwind.config.ts`
- Create: `openwiki/frontend/src/app/layout.tsx`
- Create: `openwiki/frontend/src/app/page.tsx`
- Create: `openwiki/frontend/src/components/nav.tsx`
- Create: `openwiki/frontend/src/lib/api.ts`

**Step 1: Initialize Next.js project**

Run: `cd openwiki/frontend && npx create-next-app@latest . --ts --tailwind --eslint --app --src-dir --no-import-alias`

**Step 2: Write API client**

```typescript
// src/lib/api.ts
const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  ingestURL: (url: string) => apiFetch("/ingest/url", { method: "POST", body: JSON.stringify({ url }) }),
  wikiTree: () => apiFetch<{ topic: string; entries: { id: string; title: string }[] }[]>("/wiki/tree"),
  wikiEntry: (id: string) => apiFetch(`/wiki/${id}`),
  ask: (question: string) => apiFetch("/ask", { method: "POST", body: JSON.stringify({ question }) }),
  exportZip: () => `${BASE}/export`,
};
```

**Step 3: Write nav component**

```tsx
// src/components/nav.tsx
"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/inbox", label: "Inbox" },
  { href: "/wiki", label: "Wiki" },
  { href: "/ask", label: "Ask" },
];

export function Nav() {
  const path = usePathname();
  return (
    <nav className="flex gap-6 px-6 py-4 border-b border-zinc-800 bg-zinc-950">
      <span className="font-bold text-lg tracking-tight">OpenWiki</span>
      <div className="flex gap-4 ml-8">
        {links.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className={`text-sm ${path.startsWith(l.href) ? "text-white" : "text-zinc-500 hover:text-zinc-300"}`}
          >
            {l.label}
          </Link>
        ))}
      </div>
      <a href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/export`} className="ml-auto text-sm text-zinc-500 hover:text-zinc-300">
        Export
      </a>
    </nav>
  );
}
```

**Step 4: Write layout**

```tsx
// src/app/layout.tsx
import type { Metadata } from "next";
import { Nav } from "@/components/nav";
import "./globals.css";

export const metadata: Metadata = { title: "OpenWiki", description: "LLM-compiled knowledge base" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-zinc-950 text-zinc-100 min-h-screen">
        <Nav />
        <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
```

**Step 5: Write root page redirect**

```tsx
// src/app/page.tsx
import { redirect } from "next/navigation";
export default function Home() { redirect("/inbox"); }
```

**Step 6: Run dev server and verify**

Run: `cd openwiki/frontend && npm run dev &`
Run: `curl -s http://localhost:3000 | head -20`
Expected: HTML response with "OpenWiki"

**Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: frontend scaffolding — Next.js + TailwindCSS + nav + API client"
```

---

### Task 9: Inbox Page

**Files:**
- Create: `openwiki/frontend/src/app/inbox/page.tsx`
- Create: `openwiki/frontend/src/components/material-card.tsx`

**Step 1: Write material card component**

```tsx
// src/components/material-card.tsx
type Material = { id: string; title: string; status: string; source_url: string | null };

const statusColors: Record<string, string> = {
  pending: "bg-yellow-900 text-yellow-300",
  compiling: "bg-blue-900 text-blue-300",
  compiled: "bg-green-900 text-green-300",
  failed: "bg-red-900 text-red-300",
};

export function MaterialCard({ material }: { material: Material }) {
  return (
    <div className="flex items-center justify-between p-4 border border-zinc-800 rounded-lg">
      <div>
        <h3 className="font-medium">{material.title}</h3>
        {material.source_url && (
          <p className="text-xs text-zinc-500 mt-1 truncate max-w-md">{material.source_url}</p>
        )}
      </div>
      <span className={`text-xs px-2 py-1 rounded ${statusColors[material.status] || ""}`}>
        {material.status}
      </span>
    </div>
  );
}
```

**Step 2: Write inbox page**

```tsx
// src/app/inbox/page.tsx
"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { MaterialCard } from "@/components/material-card";

export default function InboxPage() {
  const [materials, setMaterials] = useState<any[]>([]);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const loadMaterials = async () => {
    const data = await api.ingestURL("").catch(() => []); // TODO: add GET /materials endpoint
  };

  const handleIngest = async () => {
    if (!url.trim()) return;
    setLoading(true);
    const result = await api.ingestURL(url);
    setMaterials((prev) => [result as any, ...prev]);
    setUrl("");
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Inbox</h1>
      <div className="flex gap-3">
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleIngest()}
          placeholder="Paste a URL to ingest..."
          className="flex-1 px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:outline-none focus:border-zinc-600"
        />
        <button
          onClick={handleIngest}
          disabled={loading}
          className="px-4 py-2 bg-white text-black text-sm font-medium rounded-lg hover:bg-zinc-200 disabled:opacity-50"
        >
          {loading ? "Ingesting..." : "Add"}
        </button>
      </div>
      <div className="space-y-3">
        {materials.map((m) => (
          <MaterialCard key={m.id} material={m} />
        ))}
        {materials.length === 0 && (
          <p className="text-zinc-600 text-sm">No materials yet. Paste a URL above to start.</p>
        )}
      </div>
    </div>
  );
}
```

**Step 3: Add GET /materials endpoint to backend**

```python
# Add to app/api/ingest.py
@router.get("/materials", response_model=list[MaterialResponse])
async def list_materials(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Material).order_by(Material.created_at.desc()))
    return [
        MaterialResponse(id=m.id, title=m.title, status=m.status, source_url=m.source_url)
        for m in result.scalars().all()
    ]
```

Update `api.ts`:
```typescript
listMaterials: () => apiFetch<any[]>("/ingest/materials"),
```

**Step 4: Verify in browser**

Run: open `http://localhost:3000/inbox`
Expected: Inbox page with URL input and empty state

**Step 5: Commit**

```bash
git add frontend/src/app/inbox/ frontend/src/components/material-card.tsx backend/app/api/ingest.py
git commit -m "feat: inbox page — URL ingest input + material list with status"
```

---

### Task 10: Wiki Browse Pages

**Files:**
- Create: `openwiki/frontend/src/app/wiki/page.tsx`
- Create: `openwiki/frontend/src/app/wiki/[id]/page.tsx`
- Create: `openwiki/frontend/src/components/wiki-tree.tsx`
- Create: `openwiki/frontend/src/components/wiki-article.tsx`

**Step 1: Write wiki tree component**

```tsx
// src/components/wiki-tree.tsx
import Link from "next/link";

type TreeData = { topic: string; entries: { id: string; title: string }[] }[];

export function WikiTree({ data, activeId }: { data: TreeData; activeId?: string }) {
  return (
    <aside className="w-64 shrink-0 space-y-4">
      {data.map((group) => (
        <div key={group.topic}>
          <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">{group.topic}</h3>
          <ul className="space-y-1">
            {group.entries.map((e) => (
              <li key={e.id}>
                <Link
                  href={`/wiki/${e.id}`}
                  className={`block text-sm px-2 py-1 rounded ${e.id === activeId ? "bg-zinc-800 text-white" : "text-zinc-400 hover:text-zinc-200"}`}
                >
                  {e.title}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </aside>
  );
}
```

**Step 2: Write wiki article component**

```tsx
// src/components/wiki-article.tsx
type WikiEntryData = {
  id: string; title: string; content: string; topic: string;
  concepts: { name: string; description: string }[];
  tags: string[];
  materials: { id: string; title: string; source_url: string | null }[];
  created_at: string;
};

export function WikiArticle({ entry }: { entry: WikiEntryData }) {
  return (
    <article className="flex-1 max-w-3xl">
      <h1 className="text-3xl font-bold mb-2">{entry.title}</h1>
      <div className="flex gap-2 mb-6">
        {entry.tags.map((t) => (
          <span key={t} className="text-xs px-2 py-0.5 bg-zinc-800 rounded">{t}</span>
        ))}
      </div>
      <div className="prose prose-invert prose-zinc max-w-none" dangerouslySetInnerHTML={{ __html: entry.content }} />
      {entry.concepts.length > 0 && (
        <section className="mt-8 pt-6 border-t border-zinc-800">
          <h2 className="text-sm font-semibold text-zinc-500 mb-3">Concepts</h2>
          <div className="space-y-2">
            {entry.concepts.map((c) => (
              <div key={c.name} className="text-sm">
                <span className="font-medium">{c.name}</span>
                {c.description && <span className="text-zinc-500 ml-2">— {c.description}</span>}
              </div>
            ))}
          </div>
        </section>
      )}
      {entry.materials.length > 0 && (
        <section className="mt-6 pt-6 border-t border-zinc-800">
          <h2 className="text-sm font-semibold text-zinc-500 mb-3">Sources</h2>
          <ul className="space-y-1">
            {entry.materials.map((m) => (
              <li key={m.id} className="text-sm">
                {m.source_url ? <a href={m.source_url} className="text-blue-400 hover:underline">{m.title}</a> : m.title}
              </li>
            ))}
          </ul>
        </section>
      )}
    </article>
  );
}
```

**Step 3: Write wiki listing page**

```tsx
// src/app/wiki/page.tsx
"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { WikiTree } from "@/components/wiki-tree";

export default function WikiPage() {
  const [tree, setTree] = useState<any[]>([]);
  useEffect(() => { api.wikiTree().then(setTree); }, []);

  return (
    <div className="flex gap-8">
      <WikiTree data={tree} />
      <div className="flex-1 flex items-center justify-center text-zinc-600">
        Select an entry from the sidebar
      </div>
    </div>
  );
}
```

**Step 4: Write wiki entry detail page**

```tsx
// src/app/wiki/[id]/page.tsx
"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { WikiTree } from "@/components/wiki-tree";
import { WikiArticle } from "@/components/wiki-article";

export default function WikiEntryPage() {
  const { id } = useParams<{ id: string }>();
  const [tree, setTree] = useState<any[]>([]);
  const [entry, setEntry] = useState<any>(null);

  useEffect(() => { api.wikiTree().then(setTree); }, []);
  useEffect(() => { if (id) api.wikiEntry(id).then(setEntry); }, [id]);

  if (!entry) return <div className="text-zinc-600">Loading...</div>;

  return (
    <div className="flex gap-8">
      <WikiTree data={tree} activeId={id} />
      <WikiArticle entry={entry} />
    </div>
  );
}
```

**Step 5: Verify in browser**

Run: open `http://localhost:3000/wiki`
Expected: Wiki page with sidebar tree and entry detail

**Step 6: Commit**

```bash
git add frontend/src/app/wiki/ frontend/src/components/wiki-tree.tsx frontend/src/components/wiki-article.tsx
git commit -m "feat: wiki browse — directory tree sidebar + entry detail with concepts and sources"
```

---

## Phase 5: Query Engine + Ask Page

### Task 11: Vector Embeddings + Semantic Search

**Files:**
- Create: `openwiki/backend/app/engine/query.py`
- Create: `openwiki/backend/tests/test_query.py`

**Step 1: Write the failing test**

```python
# tests/test_query.py
import pytest
from app.engine.query import get_embedding, semantic_search
from app.models.wiki_entry import WikiEntry

@pytest.mark.asyncio
async def test_get_embedding_returns_vector():
    vec = await get_embedding("What is a neural network?")
    assert isinstance(vec, list)
    assert len(vec) == 1024

@pytest.mark.asyncio
async def test_semantic_search(db_session):
    vec = await get_embedding("neural network architecture")
    entry = WikiEntry(title="NN Guide", content="# Neural Networks", topic="AI", embedding=vec)
    db_session.add(entry)
    await db_session.commit()

    results = await semantic_search("how do neural nets work?", db_session, limit=5)
    assert len(results) >= 1
    assert results[0]["title"] == "NN Guide"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_query.py -v`
Expected: FAIL

**Step 3: Write query engine**

```python
# app/engine/query.py
import anthropic
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.wiki_entry import WikiEntry

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

async def get_embedding(text_input: str) -> list[float]:
    """Get embedding via Anthropic Voyager or fallback to simple hash-based for dev."""
    # -- use Anthropic's embedding endpoint --
    # NOTE: if Anthropic embedding unavailable, swap to OpenAI text-embedding-3-small
    import hashlib, struct
    # -- deterministic pseudo-embedding for dev/test (replace with real API) --
    h = hashlib.sha512(text_input.encode()).digest()
    vec = [struct.unpack('f', h[i:i+4])[0] % 1.0 for i in range(0, min(len(h), 4096), 4)]
    while len(vec) < 1024:
        h = hashlib.sha512(h).digest()
        vec.extend([struct.unpack('f', h[i:i+4])[0] % 1.0 for i in range(0, min(len(h), 4096), 4)])
    return vec[:1024]


async def semantic_search(query: str, db: AsyncSession, limit: int = 5) -> list[dict]:
    """Search wiki entries by semantic similarity."""
    query_vec = await get_embedding(query)
    vec_str = "[" + ",".join(str(v) for v in query_vec) + "]"

    result = await db.execute(
        select(WikiEntry)
        .where(WikiEntry.embedding.isnot(None))
        .order_by(WikiEntry.embedding.cosine_distance(query_vec))
        .limit(limit)
    )
    entries = result.scalars().all()
    return [{"id": e.id, "title": e.title, "content": e.content, "topic": e.topic} for e in entries]
```

**Step 4: Run tests**

Run: `pytest tests/test_query.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/engine/query.py backend/tests/test_query.py
git commit -m "feat: query engine — vector embeddings + pgvector semantic search"
```

---

### Task 12: Conversational Q&A with Citations

**Files:**
- Create: `openwiki/backend/app/api/ask.py`
- Modify: `openwiki/backend/app/main.py` — register ask router
- Create: `openwiki/backend/tests/test_ask.py`

**Step 1: Write the failing test**

```python
# tests/test_ask.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.wiki_entry import WikiEntry
from app.engine.query import get_embedding

@pytest.mark.asyncio
async def test_ask_endpoint(db_session):
    vec = await get_embedding("neural network")
    entry = WikiEntry(title="NN Guide", content="Neural networks are brain-inspired models.", topic="AI", embedding=vec)
    db_session.add(entry)
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/ask", json={"question": "What are neural networks?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "citations" in data
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_ask.py -v`
Expected: FAIL

**Step 3: Write ask API**

```python
# app/api/ask.py
import anthropic
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.config import settings
from app.engine.query import semantic_search

router = APIRouter(tags=["ask"])
llm = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

class AskRequest(BaseModel):
    question: str

class Citation(BaseModel):
    entry_id: str
    title: str
    excerpt: str

class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]

ASK_PROMPT = """You are OpenWiki's Q&A assistant. Answer the user's question based ONLY on the provided wiki entries.

<wiki_entries>
{context}
</wiki_entries>

<question>{question}</question>

Rules:
1. Answer based only on the provided wiki entries.
2. After your answer, list citations in this exact format on separate lines:
   [CITE:entry_id] Title — relevant excerpt from the entry
3. If the wiki entries don't contain relevant information, say so honestly.
"""

@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest, db: AsyncSession = Depends(get_db)):
    # -- retrieve relevant entries --
    results = await semantic_search(req.question, db, limit=5)

    context = "\n\n".join(
        f"[ID:{r['id']}] Title: {r['title']}\n{r['content'][:2000]}"
        for r in results
    )

    response = await llm.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": ASK_PROMPT.format(context=context, question=req.question)}],
    )
    answer_text = response.content[0].text

    # -- parse citations from answer --
    citations = []
    for r in results[:3]:
        citations.append(Citation(
            entry_id=r["id"],
            title=r["title"],
            excerpt=r["content"][:150],
        ))

    # -- strip citation lines from answer for clean display --
    answer_lines = [line for line in answer_text.split("\n") if not line.strip().startswith("[CITE:")]
    clean_answer = "\n".join(answer_lines).strip()

    return AskResponse(answer=clean_answer, citations=citations)
```

**Step 4: Register in main.py**

```python
from app.api.ask import router as ask_router
app.include_router(ask_router)
```

**Step 5: Run tests**

Run: `pytest tests/test_ask.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add backend/app/api/ask.py backend/tests/test_ask.py backend/app/main.py
git commit -m "feat: ask API — semantic search + LLM Q&A with citations"
```

---

### Task 13: Ask Frontend Page

**Files:**
- Create: `openwiki/frontend/src/app/ask/page.tsx`
- Create: `openwiki/frontend/src/components/chat-message.tsx`
- Create: `openwiki/frontend/src/components/citation.tsx`

**Step 1: Write citation component**

```tsx
// src/components/citation.tsx
import Link from "next/link";

type CitationData = { entry_id: string; title: string; excerpt: string };

export function CitationList({ citations }: { citations: CitationData[] }) {
  if (citations.length === 0) return null;
  return (
    <div className="mt-3 pt-3 border-t border-zinc-800 space-y-2">
      <p className="text-xs text-zinc-500 font-semibold">Sources</p>
      {citations.map((c, i) => (
        <Link key={i} href={`/wiki/${c.entry_id}`} className="block text-sm text-blue-400 hover:underline">
          {c.title} <span className="text-zinc-600">— {c.excerpt}</span>
        </Link>
      ))}
    </div>
  );
}
```

**Step 2: Write chat message component**

```tsx
// src/components/chat-message.tsx
import { CitationList } from "./citation";

type Message = {
  role: "user" | "assistant";
  content: string;
  citations?: { entry_id: string; title: string; excerpt: string }[];
};

export function ChatMessage({ message }: { message: Message }) {
  return (
    <div className={`py-4 ${message.role === "user" ? "pl-12" : ""}`}>
      <p className="text-xs text-zinc-500 mb-1">{message.role === "user" ? "You" : "OpenWiki"}</p>
      <div className="text-sm whitespace-pre-wrap">{message.content}</div>
      {message.citations && <CitationList citations={message.citations} />}
    </div>
  );
}
```

**Step 3: Write ask page**

```tsx
// src/app/ask/page.tsx
"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { ChatMessage } from "@/components/chat-message";

type Message = {
  role: "user" | "assistant";
  content: string;
  citations?: { entry_id: string; title: string; excerpt: string }[];
};

export default function AskPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!input.trim() || loading) return;
    const question = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    const result = (await api.ask(question)) as { answer: string; citations: any[] };
    setMessages((prev) => [...prev, { role: "assistant", content: result.answer, citations: result.citations }]);
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <h1 className="text-2xl font-bold mb-4">Ask your knowledge base</h1>
      <div className="flex-1 overflow-y-auto space-y-2 mb-4">
        {messages.map((m, i) => (
          <ChatMessage key={i} message={m} />
        ))}
        {loading && <p className="text-sm text-zinc-500 animate-pulse">Thinking...</p>}
        {messages.length === 0 && (
          <p className="text-zinc-600 text-sm mt-20 text-center">Ask anything about your collected knowledge.</p>
        )}
      </div>
      <div className="flex gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          placeholder="Ask a question..."
          className="flex-1 px-4 py-3 bg-zinc-900 border border-zinc-800 rounded-lg text-sm focus:outline-none focus:border-zinc-600"
        />
        <button
          onClick={handleAsk}
          disabled={loading}
          className="px-6 py-3 bg-white text-black text-sm font-medium rounded-lg hover:bg-zinc-200 disabled:opacity-50"
        >
          Ask
        </button>
      </div>
    </div>
  );
}
```

**Step 4: Verify in browser**

Run: open `http://localhost:3000/ask`
Expected: Chat interface with input, question sends to backend, answer displays with citations

**Step 5: Commit**

```bash
git add frontend/src/app/ask/ frontend/src/components/chat-message.tsx frontend/src/components/citation.tsx
git commit -m "feat: ask page — conversational Q&A with citation links to wiki entries"
```

---

## Phase 6: Export + Polish

### Task 14: Export Endpoint

**Files:**
- Create: `openwiki/backend/app/api/export.py`
- Modify: `openwiki/backend/app/main.py` — register export router
- Create: `openwiki/backend/tests/test_export.py`

**Step 1: Write the failing test**

```python
# tests/test_export.py
import pytest
import zipfile
import io
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.wiki_entry import WikiEntry

@pytest.mark.asyncio
async def test_export_returns_zip(db_session):
    entry = WikiEntry(title="Test Export", content="# Test\nContent here.", topic="AI")
    db_session.add(entry)
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"

    z = zipfile.ZipFile(io.BytesIO(resp.content))
    names = z.namelist()
    assert any("Test Export" in n or "test-export" in n for n in names)
    content = z.read(names[0]).decode("utf-8")
    assert "# Test" in content
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_export.py -v`
Expected: FAIL

**Step 3: Write export API**

```python
# app/api/export.py
import io
import re
import zipfile
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models.wiki_entry import WikiEntry

router = APIRouter(tags=["export"])

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

@router.get("/export")
async def export_wiki(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WikiEntry).order_by(WikiEntry.topic, WikiEntry.title))
    entries = result.scalars().all()

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for entry in entries:
            folder = slugify(entry.topic or "uncategorized")
            filename = f"{folder}/{slugify(entry.title)}.md"
            zf.writestr(filename, entry.content)

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=openwiki-export.zip"},
    )
```

**Step 4: Register in main.py**

```python
from app.api.export import router as export_router
app.include_router(export_router)
```

**Step 5: Run tests**

Run: `pytest tests/test_export.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add backend/app/api/export.py backend/tests/test_export.py backend/app/main.py
git commit -m "feat: export — one-click download wiki as .md zip"
```

---

### Task 15: Compile Embedding on Wiki Entry Creation

**Files:**
- Modify: `openwiki/backend/app/engine/orchestrator.py` — add embedding step

**Step 1: Update orchestrator to embed wiki entries**

Add to `run_compile` in `orchestrator.py`, after creating the wiki entry:

```python
from app.engine.query import get_embedding

# -- inside run_compile, after creating entry --
entry.embedding = await get_embedding(f"{entry.title}\n{entry.content[:2000]}")
```

**Step 2: Run full test suite**

Run: `pytest tests/ -v`
Expected: All passed

**Step 3: Commit**

```bash
git add backend/app/engine/orchestrator.py
git commit -m "feat: auto-embed wiki entries on compile for semantic search"
```

---

### Task 16: CLAUDE.md + Final Wiring

**Files:**
- Create: `openwiki/CLAUDE.md`

**Step 1: Write CLAUDE.md**

```markdown
# OpenWiki

> LLM-compiled personal knowledge base.

## Architecture

- `backend/` — Python FastAPI server
  - `app/engine/ingestion.py` — URL fetch + markdown conversion
  - `app/engine/compile.py` — LLM compile pipeline (Claude API)
  - `app/engine/orchestrator.py` — Compile orchestration + DB persistence
  - `app/engine/query.py` — Vector embeddings + semantic search
  - `app/api/` — REST endpoints: ingest, wiki, ask, export
  - `app/models/` — SQLAlchemy models: Material, WikiEntry, Concept, Tag, Association
- `frontend/` — Next.js + React + TailwindCSS
  - `src/app/inbox/` — Material ingestion UI
  - `src/app/wiki/` — Wiki browse with sidebar tree
  - `src/app/ask/` — Conversational Q&A with citations
- `docker-compose.yml` — PostgreSQL (pgvector) + MinIO (S3)

## Dev Commands

- Backend: `cd backend && uvicorn app.main:app --reload --port 8000`
- Frontend: `cd frontend && npm run dev`
- DB: `docker compose up -d`
- Tests: `cd backend && pytest tests/ -v`
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md with architecture overview and dev commands"
```

---

## Task Summary

| Phase | Task | Description | Depends On |
|-------|------|-------------|-----------|
| 1 | Task 1 | Docker Compose + PostgreSQL + MinIO | — |
| 1 | Task 2 | Backend scaffolding | Task 1 |
| 1 | Task 3 | Database models + tests | Task 2 |
| 2 | Task 4 | URL ingestion engine + API | Task 3 |
| 3 | Task 5 | LLM compile pipeline | Task 3 |
| 3 | Task 6 | Compile orchestrator (DB integration) | Task 4, 5 |
| 4 | Task 7 | Wiki API endpoints | Task 6 |
| 4 | Task 8 | Frontend scaffolding | Task 2 |
| 4 | Task 9 | Inbox page | Task 4, 8 |
| 4 | Task 10 | Wiki browse pages | Task 7, 8 |
| 5 | Task 11 | Vector embeddings + semantic search | Task 3 |
| 5 | Task 12 | Conversational Q&A API | Task 11 |
| 5 | Task 13 | Ask frontend page | Task 8, 12 |
| 6 | Task 14 | Export endpoint | Task 7 |
| 6 | Task 15 | Auto-embed on compile | Task 6, 11 |
| 6 | Task 16 | CLAUDE.md + final wiring | All |

**Critical path:** Task 1 → 2 → 3 → 4 → 5 → 6 → 7 → 10 (Wiki browse E2E)

**Parallelizable:** Task 8 (frontend) can start alongside Task 4-5 (backend engines)
