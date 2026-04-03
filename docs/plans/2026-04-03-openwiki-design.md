# OpenWiki - Product Design

> Drop raw materials in, LLM compiles them into a structured knowledge network you can query anytime.

## Product Positioning

Other tools make you **manage** knowledge. OpenWiki lets LLM **compile** knowledge.
You just throw in raw materials — what comes out is a living, growing, queryable knowledge network.

**Core metaphor**: You are the curator, LLM is the editorial team.
You only collect — the editorial team organizes, categorizes, links, and maintains the index.
You can walk into the editorial room and ask anything, anytime.

---

## Target Users

- Researchers, analysts, writers, knowledge workers
- Currently using Obsidian / Notion / Readwise but frustrated by manual organization
- Mixed-type knowledge consumers: tech + business + creative + cross-domain
- Moderate intake (20-50 articles/week) with research bursts

## Core Pain Points Solved

1. **Collection-organization gap**: Raw materials pile up, manual tagging/summarizing/linking is too slow
2. **Isolated knowledge**: Notes don't connect to each other, no automatic cross-domain associations
3. **Retrieval by memory**: Keyword search can't understand semantics, can't find "that opinion I read about X"
4. **Output bottleneck**: Materials exist but can't be efficiently used when writing/researching

---

## Core Workflow (User Perspective)

```
1. INGEST
   Browser extension / URL paste / file upload
   Zero organization, zero annotation required.

2. COMPILE (LLM)
   Auto-triggered on new material:
   - Generate summary
   - Extract core concepts
   - Auto-classify and tag
   - Discover cross-material associations
   - Generate concept articles (wiki entries)
   - Maintain backlinks and index

3. EXPLORE
   Browse the compiled wiki in Web UI:
   - Knowledge graph visualization (concept nodes + association edges)
   - Multi-dimensional browsing by topic / time / source
   - Click any concept to jump to related articles and raw materials

4. ASK
   Conversational Q&A against your own knowledge base:
   - Every answer cites sources (click to jump to raw material or wiki entry)
   - Generate reports, comparative analyses, trend summaries
   - Query results can be archived back into wiki

5. EVOLVE
   - Query results flow back into the wiki
   - Periodic LLM health checks: find contradictions, fill gaps, suggest new associations
   - The more you use it, the smarter it gets
```

---

## System Architecture

```
+--------------------------------------------------+
|                  User Touch Points                |
|  Browser Extension | Web UI | CLI | API           |
+----------+----------------------------+----------+
           | ingest                      | ask/explore
           v                            v
+----------------------+  +----------------------------+
|   Ingestion Engine   |  |       Query Engine         |
|                      |  |                            |
|  - URL -> Markdown   |  |  - Semantic search         |
|  - PDF/image -> text |  |  - Conversational Q&A      |
|  - Denoise / clean   |  |  - Report generation       |
|  - Store to raw/     |  |  - Output flows back       |
+----------+-----------+  +------------^---------------+
           |                            |
           v                            | read
+-------------------------------------------+-------+
|             Compile Engine (CORE)                  |
|                                                    |
|  - Summary generation    - Concept extraction      |
|  - Auto classify/tag     - Cross-material linking  |
|  - Wiki entry generation - Backlink maintenance    |
|  - Auto index update     - Periodic health check   |
+-------------------------+-------------------------+
                          |
                          v
+---------------------------------------------------+
|                 Storage Layer                      |
|                                                    |
|  raw/   -> Raw materials (.md + attachments)       |
|  wiki/  -> Compiled knowledge network (.md + idx)  |
|  meta/  -> Vector index + relation graph + logs    |
+---------------------------------------------------+
```

### Engine Responsibilities

| Engine | Responsibility | Trigger |
|--------|---------------|---------|
| **Ingestion** | Convert any format to clean .md | User drops material in |
| **Compile** | Compile raw/ into wiki/, core differentiator | Auto after new material + manual trigger |
| **Query** | Semantic search + conversational Q&A + output | User asks questions |

---

## Web UI - Four Core Pages

### 1. Inbox
Raw materials stream not yet compiled. Each item shows title, source, time, compile status.
Default: auto-compile. Optional: manual review mode.

### 2. Wiki
Compiled output. Left sidebar: topic directory tree (auto-organized). Right: article content.
Each wiki entry contains:
- LLM-generated concept article
- List of associated raw materials
- Backlinks (which other entries reference this concept)
- Compile time and information sources

### 3. Graph
Visual concept relationship network. Nodes = concepts, edges = associations.
- Zoom/drag to explore
- Click node to jump to wiki entry
- Filter by topic/time
- Discover cross-domain connections you didn't know existed

### 4. Ask
Conversational interface to query your own knowledge base.
- Every answer cites sources (click to jump)
- Generate reports, comparisons, trend summaries
- One-click archive query results back to wiki

---

## Competitive Differentiation

| Competitor | What it does | OpenWiki's essential difference |
|-----------|-------------|-------------------------------|
| **Obsidian** | Manual notes, manual linking | OpenWiki's wiki is LLM-written, you don't touch it |
| **Notion AI** | AI layer on existing docs | OpenWiki compiles knowledge network from scratch |
| **Readwise/Reader** | Collect + highlight + review | Only handles "in", not "compile" — materials stay isolated |
| **ChatGPT Memory** | Vaguely remembers conversation history | OpenWiki is structured, browsable, with sources |
| **RAG toolchains** | Developer-built retrieval systems | OpenWiki is a finished product for normal users |
| **Google NotebookLM** | Upload docs then chat | No compilation, no knowledge network, no continuous evolution |

---

## MVP Scope (V1)

### V1 Build

| Feature | Minimum implementation |
|---------|----------------------|
| **Material import** | URL paste + file upload (browser extension later) |
| **Compile engine** | Summary + concept extraction + auto tags + association discovery + wiki entry generation |
| **Wiki browse** | Directory tree + article reading + backlinks |
| **Ask dialogue** | Semantic search + Q&A over wiki, answers with source citations |
| **Export** | One-click export to .md zip |

### V1 Cut

| Cut feature | Why |
|-------------|-----|
| Graph visualization | Nice to have, doesn't validate core value |
| Browser extension | URL paste is enough for import validation |
| Team collaboration | Validate personal use case first |
| Mobile app | Responsive web is sufficient |
| Health check / Linting | Only meaningful when knowledge base is large enough |

---

## Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Frontend** | Next.js + React | SSR, routing, deployment unified |
| **Backend** | Python (FastAPI) | Most mature LLM ecosystem, natural for compile engine |
| **Database** | PostgreSQL + pgvector | Structured data + vector search in one DB |
| **LLM** | Claude API primary | Best long context + structured output |
| **Storage** | S3-compatible object storage | Raw materials and attachments |
| **Deploy** | Vercel (frontend) + Railway/Fly.io (backend) | Fast launch, no K8s needed at MVP |

---

## Business Model

```
Free        -  50 materials/month, basic compile + Ask
Pro $12/mo  -  Unlimited materials, full compile, priority queue, export
Team $29/mo -  V2+, collaboration + shared knowledge bases
```

### Pricing Rationale

- Readwise Reader charges $8/mo for collection + highlights only
- Notion AI charges $10/mo for AI on existing notes only
- OpenWiki does deeper work than both, $12 is justified

---

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Data location | Cloud-first | Best UX: zero config, any device, instant access |
| Data portability | .md export anytime | Eliminate lock-in anxiety |
| Compile trigger | Auto by default | Minimize user friction, manual mode optional |
| Knowledge format | Markdown (.md) | Universal, portable, LLM-native |

---

## Key Assumptions to Validate

1. LLM-compiled wiki is useful enough that users actually browse and query it
2. Auto-discovered cross-domain associations provide genuine "aha" moments
3. Users trust cloud storage for personal knowledge
4. $12/mo pricing holds against free alternatives like NotebookLM
