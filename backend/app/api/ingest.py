# ============================================================
# Ingestion API Endpoints
# ============================================================
# URL ingestion and file upload endpoints
# ============================================================

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl
from typing import Optional

from app.db import get_db, SessionLocal
from app.models.material import Material, MaterialStatus
from app.engine.ingestion import url_to_markdown


router = APIRouter(prefix="/ingest", tags=["ingest"])


# ============================================================
# Background Tasks
# ============================================================

async def _bg_compile(material_id: str):
    """Background task to compile material after ingestion."""
    from app.engine.orchestrator import run_compile

    async with SessionLocal() as db:
        try:
            await run_compile(material_id, db)
        except Exception as e:
            # Log error but don't crash
            print(f"Compile failed for {material_id}: {e}")


# ============================================================
# Request/Response Models
# ============================================================

class IngestURLRequest(BaseModel):
    """Request model for URL ingestion."""
    url: str
    compile: bool = True  # Auto-compile after ingestion


class MaterialResponse(BaseModel):
    """Response model for created material."""
    id: str
    title: str
    status: str
    source_url: Optional[str] = None
    file_key: Optional[str] = None


# ============================================================
# Endpoints
# ============================================================

@router.post("/url", response_model=MaterialResponse)
async def ingest_url(
    req: IngestURLRequest,
    bg: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest content from a URL.

    Fetches the URL, extracts readable content, converts to markdown,
    and stores as a new Material. Optionally triggers background compilation.
    """
    try:
        result = await url_to_markdown(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch URL: {str(e)}")

    material = Material(
        title=result["title"],
        source_url=result["source_url"],
        raw_markdown=result["markdown"],
        status=MaterialStatus.PENDING,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)

    # Trigger background compile if requested
    if req.compile:
        bg.add_task(_bg_compile, material.id)

    return MaterialResponse(
        id=material.id,
        title=material.title,
        status=material.status.value,
        source_url=material.source_url,
        file_key=material.file_key,
    )


@router.post("/upload", response_model=MaterialResponse)
async def ingest_upload(
    file: UploadFile = File(...),
    title: str = Form(""),
    compile: bool = Form(True),
    bg: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest content from an uploaded file.

    Uploads file to S3-compatible storage and stores metadata in database.
    For text/markdown files, also stores content directly for LLM processing.
    Optionally triggers background compilation.
    """
    from app.engine.storage import get_s3_client

    # Validate file type
    if file.content_type and not file.content_type.startswith(
        ("text/", "application/octet-stream", "application/pdf")
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}",
        )

    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read file: {str(e)}",
        )

    # Upload to S3
    s3_client = get_s3_client()
    try:
        file_key = await s3_client.upload_file(
            content=content,
            filename=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}",
        )

    # Create material with file_key
    raw_markdown = None
    if file.content_type and file.content_type.startswith("text/"):
        try:
            raw_markdown = content.decode("utf-8")
        except UnicodeDecodeError:
            pass  # Binary file, skip content extraction

    material = Material(
        title=title or file.filename or "Untitled",
        file_key=file_key,
        raw_markdown=raw_markdown or f"[File stored at {file_key}]",
        status=MaterialStatus.PENDING,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)

    # Trigger background compile if requested
    if compile and bg and raw_markdown:
        bg.add_task(_bg_compile, material.id)

    return MaterialResponse(
        id=material.id,
        title=material.title,
        status=material.status.value,
        source_url=material.source_url,
        file_key=material.file_key,
    )