# ============================================================
# FastAPI Application Entry
# ============================================================
# OpenWiki backend API server
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ingest import router as ingest_router
from app.api.ask import router as ask_router
from app.api.export import router as export_router

app = FastAPI(
    title="OpenWiki",
    version="0.1.0",
    description="Personal knowledge management with LLM-powered compilation",
)

# CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(ingest_router)
app.include_router(ask_router)
app.include_router(export_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}