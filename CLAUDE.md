# OpenWiki

> LLM-compiled personal knowledge base.

## Architecture

```
openwiki/
├── backend/                    # Python FastAPI server
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── config.py          # Settings via pydantic-settings
│   │   ├── db.py              # SQLAlchemy async engine
│   │   ├── init_db.py         # Database initialization
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── material.py    # Raw material (URL/file input)
│   │   │   ├── wiki_entry.py  # Compiled wiki entry
│   │   │   ├── concept.py     # Concepts & tags
│   │   │   └── association.py  # Cross-material associations
│   │   ├── api/               # REST endpoints
│   │   │   ├── ingest.py      # POST /ingest/url, /ingest/upload
│   │   │   ├── ask.py         # POST /ask
│   │   │   └── export.py      # GET /export
│   │   └── engine/            # Core engines
│   │       ├── ingestion.py   # URL fetch + markdown conversion
│   │       ├── storage.py     # S3/MinIO client
│   │       ├── compile.py     # LLM compile pipeline (Claude)
│   │       ├── orchestrator.py # Compile orchestration + DB persistence
│   │       └── query.py       # Vector embeddings + semantic search
│   └── tests/                 # Test suite
├── frontend/                   # Next.js 15 App Router
│   ├── src/app/
│   │   ├── layout.tsx         # App shell with Nav
│   │   ├── page.tsx           # Redirect to /inbox
│   │   ├── inbox/page.tsx     # Material ingestion
│   │   ├── wiki/page.tsx      # Wiki browser
│   │   └── ask/page.tsx       # Q&A with citations
│   ├── src/components/
│   │   └── nav.tsx             # Navigation component
│   └── src/lib/
│       └── api.ts              # Backend API client
└── docker-compose.yml          # PostgreSQL + MinIO
```

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), pgvector
- **Frontend:** Next.js 15, React, TailwindCSS
- **LLM:** Claude API (anthropic SDK)
- **Storage:** PostgreSQL (pgvector), MinIO (S3-compatible)
- **Infrastructure:** Docker Compose

## Data Flow

```
1. Ingestion
   URL/File → Material (raw_markdown) → MinIO storage

2. Compile (background task)
   Material → LLM → WikiEntry + Concepts + Tags
   └─> Embedding generated for semantic search

3. Query
   Question → Embedding → pgvector search → Context → LLM → Answer + Citations

4. Export
   WikiEntries → ZIP of .md files
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /ingest/url | Ingest URL, create Material |
| POST | /ingest/upload | Upload file, create Material |
| POST | /ask | Ask question, get answer with citations |
| GET | /export | Download all wiki entries as ZIP |
| GET | /health | Health check |

## Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://openwiki:openwiki_dev@localhost:5432/openwiki
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=openwiki-raw
ANTHROPIC_API_KEY=sk-ant-xxx
```

## Quick Start

```bash
# Start infrastructure
docker compose up -d

# Initialize database
cd backend && uv run python -m app.init_db

# Start backend
cd backend && uv run uvicorn app.main:app --reload

# Start frontend
cd frontend && npm run dev
```

## Testing

```bash
cd backend
uv run pytest tests/ -v
```

## Key Design Decisions

1. **Deterministic Pseudo-Embeddings (Testing)**: Production should use real embedding API (OpenAI/Claude). Current implementation uses deterministic hash-based vectors for testing.

2. **Background Compile**: Compile runs as background task to avoid blocking API responses.

3. **get_or_create Pattern**: Concepts and tags are deduplicated across materials.

4. **Embedding on Compile**: Wiki entries get embeddings automatically after creation for semantic search.

## Future Improvements

- [ ] Real embedding API integration (OpenAI embeddings)
- [ ] Wiki tree structure (parent/child relationships)
- [ ] Full-text search alongside vector search
- [ ] Real-time compile status updates (WebSocket)
- [ ] User authentication
- [ ] Multi-user support