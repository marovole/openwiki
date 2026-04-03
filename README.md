# OpenWiki

> LLM-compiled personal knowledge base.

OpenWiki transforms URLs and files into a searchable wiki using LLM-powered compilation. Ask questions about your knowledge base and get answers with source citations.

## Features

- **URL/File Ingestion** — Drop a URL or upload a file, get structured knowledge
- **LLM Compile Engine** — Claude API extracts concepts, tags, and wiki entries
- **Semantic Search** — pgvector-powered similarity search for relevant context
- **Q&A with Citations** — Ask questions, get answers with source references
- **Markdown Export** — Download all wiki entries as a ZIP of `.md` files

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async) |
| Frontend | Next.js 15, React, TailwindCSS |
| Database | PostgreSQL + pgvector |
| Storage | MinIO (S3-compatible) |
| LLM | Claude API (anthropic SDK) |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for uv)
- Node.js 18+ (for npm)
- Anthropic API key

### 1. Start Infrastructure

```bash
docker compose up -d
```

This starts:
- PostgreSQL with pgvector on port 5432
- MinIO console on port 9001 (admin UI)

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Initialize Database

```bash
cd backend
uv sync
uv run python -m app.init_db
```

### 4. Start Backend

```bash
uv run uvicorn app.main:app --reload --port 8000
```

### 5. Start Frontend

```bash
cd ../frontend
npm install
npm run dev
```

Open http://localhost:3000

## Usage

### Ingest Content

1. Navigate to **Inbox** (`/inbox`)
2. Paste a URL or upload a `.md`/`.txt` file
3. Content is processed and stored

### Browse Wiki

1. Navigate to **Wiki** (`/wiki`)
2. Browse compiled knowledge entries
3. Each entry contains structured content, concepts, and tags

### Ask Questions

1. Navigate to **Ask** (`/ask`)
2. Type your question
3. Get an answer with citations pointing to source materials

### Export

Click **Export** in the navigation bar to download all wiki entries as a ZIP file.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│ PostgreSQL  │
│  (Next.js)  │     │  (FastAPI)  │     │  (pgvector) │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
              ┌─────┴─────┐ ┌─────┴─────┐
              │   MinIO   │ │   Claude  │
              │  (Storage)│ │   (LLM)   │
              └───────────┘ └───────────┘
```

### Data Flow

```
URL/File → Material (raw) → LLM Compile → Wiki Entry
                ↓                              ↓
           MinIO Storage              Embedding (pgvector)
                                              ↓
                              Question → Semantic Search → Context → LLM → Answer
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/ingest/url` | Ingest URL, create Material |
| `POST` | `/ingest/upload` | Upload file, create Material |
| `POST` | `/ask` | Ask question, get answer with citations |
| `GET` | `/export` | Download all wiki entries as ZIP |
| `GET` | `/health` | Health check |

## Development

### Run Tests

```bash
cd backend
uv run pytest tests/ -v
```

### Database Schema

```sql
materials          -- Raw input (URL/file content)
├── id, title, source_url, raw_markdown, status, embedding

wiki_entries       -- Compiled knowledge
├── id, title, content, embedding
├── concepts[]     -- Extracted concepts
├── tags[]         -- Categorization tags
└── materials[]     -- Source materials

associations       -- Cross-material relationships
├── source_id, target_id, relationship_type, confidence
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `S3_ENDPOINT` | MinIO endpoint | `http://localhost:9000` |
| `S3_ACCESS_KEY` | MinIO access key | `minioadmin` |
| `S3_SECRET_KEY` | MinIO secret key | `minioadmin` |
| `S3_BUCKET` | Storage bucket | `openwiki-raw` |
| `ANTHROPIC_API_KEY` | Claude API key | — |

## Roadmap

- [ ] Real embedding API (OpenAI embeddings)
- [ ] Wiki tree structure (parent/child relationships)
- [ ] Full-text search alongside vector search
- [ ] Real-time compile status (WebSocket)
- [ ] User authentication
- [ ] Multi-user support

## License

MIT

## Acknowledgments

Inspired by the need for a personal knowledge base that actually understands your content.