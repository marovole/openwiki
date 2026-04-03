# OpenWiki

> LLM 编译的个人知识库

OpenWiki 将 URL 和文件转化为可搜索的 Wiki 知识库。通过 LLM 编译引擎提取概念、标签和结构化内容，支持语义搜索和带引用的问答。

## 功能特性

- **URL/文件导入** — 输入 URL 或上传文件，自动解析为结构化知识
- **LLM 编译引擎** — Claude API 提取概念、标签、生成 Wiki 条目
- **语义搜索** — pgvector 向量相似度搜索，精准匹配相关内容
- **问答系统** — 提问并获取带来源引用的回答
- **Markdown 导出** — 一键下载所有 Wiki 条目为 ZIP 压缩包

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async) |
| 前端 | Next.js 15, React, TailwindCSS |
| 数据库 | PostgreSQL + pgvector |
| 存储 | MinIO (S3 兼容) |
| LLM | Claude API (anthropic SDK) |

## 快速开始

### 环境要求

- Docker & Docker Compose
- Python 3.11+ (需要 uv)
- Node.js 18+ (需要 npm)
- Anthropic API Key

### 1. 启动基础设施

```bash
docker compose up -d
```

启动服务：
- PostgreSQL (pgvector) — 端口 5432
- MinIO 控制台 — 端口 9001

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 ANTHROPIC_API_KEY
```

### 3. 初始化数据库

```bash
cd backend
uv sync
uv run python -m app.init_db
```

### 4. 启动后端

```bash
uv run uvicorn app.main:app --reload --port 8000
```

### 5. 启动前端

```bash
cd ../frontend
npm install
npm run dev
```

打开 http://localhost:3000

## 使用指南

### 导入内容

1. 进入 **Inbox** 页面 (`/inbox`)
2. 粘贴 URL 或上传 `.md`/`.txt` 文件
3. 系统自动处理并存储

### 浏览 Wiki

1. 进入 **Wiki** 页面 (`/wiki`)
2. 浏览已编译的知识条目
3. 每个条目包含结构化内容、概念和标签

### 问答查询

1. 进入 **Ask** 页面 (`/ask`)
2. 输入问题
3. 获取带引用来源的回答

### 导出

点击导航栏的 **Export** 按钮下载所有 Wiki 条目的 ZIP 文件。

## 系统架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   前端      │────▶│   后端      │────▶│ PostgreSQL  │
│  (Next.js)  │     │  (FastAPI)  │     │  (pgvector) │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
              ┌─────┴─────┐ ┌─────┴─────┐
              │   MinIO   │ │   Claude  │
              │  (存储)   │ │   (LLM)   │
              └───────────┘ └───────────┘
```

### 数据流

```
URL/文件 → Material (原始内容) → LLM 编译 → Wiki Entry
              ↓                              ↓
         MinIO 存储                 Embedding (向量嵌入)
                                              ↓
                              问题 → 语义搜索 → 上下文 → LLM → 回答
```

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| `POST` | `/ingest/url` | 导入 URL，创建 Material |
| `POST` | `/ingest/upload` | 上传文件，创建 Material |
| `POST` | `/ask` | 提问，获取带引用的回答 |
| `GET` | `/export` | 下载所有 Wiki 条目为 ZIP |
| `GET` | `/health` | 健康检查 |

## 开发指南

### 运行测试

```bash
cd backend
uv run pytest tests/ -v
```

### 数据库 Schema

```sql
materials          -- 原始输入 (URL/文件内容)
├── id, title, source_url, raw_markdown, status, embedding

wiki_entries       -- 编译后的知识条目
├── id, title, content, embedding
├── concepts[]     -- 提取的概念
├── tags[]         -- 分类标签
└── materials[]    -- 来源材料

associations       -- 跨材料关联关系
├── source_id, target_id, relationship_type, confidence
```

## 环境变量

| 变量 | 描述 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接字符串 | `postgresql+asyncpg://...` |
| `S3_ENDPOINT` | MinIO 端点 | `http://localhost:9000` |
| `S3_ACCESS_KEY` | MinIO 访问密钥 | `minioadmin` |
| `S3_SECRET_KEY` | MinIO 密钥 | `minioadmin` |
| `S3_BUCKET` | 存储桶名称 | `openwiki-raw` |
| `ANTHROPIC_API_KEY` | Claude API 密钥 | — |

## 路线图

- [ ] 接入真实 Embedding API (OpenAI embeddings)
- [ ] Wiki 树状结构 (父子关系)
- [ ] 全文搜索 + 向量搜索混合
- [ ] 实时编译状态 (WebSocket)
- [ ] 用户认证
- [ ] 多用户支持

## 许可证

MIT

---

## English Version

> LLM-compiled personal knowledge base

OpenWiki transforms URLs and files into a searchable wiki using LLM-powered compilation.

### Features

- **URL/File Ingestion** — Drop a URL or upload a file, get structured knowledge
- **LLM Compile Engine** — Claude API extracts concepts, tags, and wiki entries
- **Semantic Search** — pgvector-powered similarity search
- **Q&A with Citations** — Ask questions, get answers with source references
- **Markdown Export** — Download all wiki entries as a ZIP

### Quick Start

```bash
# 1. Start infrastructure
docker compose up -d

# 2. Configure environment
cp .env.example .env
# Add your ANTHROPIC_API_KEY

# 3. Initialize database
cd backend && uv sync && uv run python -m app.init_db

# 4. Start backend
uv run uvicorn app.main:app --reload --port 8000

# 5. Start frontend
cd ../frontend && npm install && npm run dev
```

Open http://localhost:3000

### License

MIT