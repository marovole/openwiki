# ============================================================
# Export API - Download Wiki as Markdown
# ============================================================

import io
import zipfile
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.db import SessionLocal
from app.models import WikiEntry

router = APIRouter(prefix="/export", tags=["export"])


@router.get("")
async def export_wiki():
    """
    Export all wiki entries as a ZIP of markdown files.

    Returns a downloadable ZIP file containing:
    - One .md file per wiki entry
    - Filename based on entry title (sanitized)
    """
    async with SessionLocal() as session:
        result = await session.execute(select(WikiEntry))
        entries = result.scalars().all()

    if not entries:
        # Return empty archive with README
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("README.txt", "No wiki entries to export.")
        zip_buffer.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=openwiki_export_{timestamp}.zip"
            },
        )

    # Create ZIP in memory
    zip_buffer = io.BytesIO()

    def sanitize_filename(title: str) -> str:
        """Convert title to safe filename."""
        # Replace common problematic characters
        safe = title.replace("/", "_").replace("\\", "_").replace(":", "_")
        safe = safe.replace('"', "_").replace("'", "_").replace("?", "_")
        safe = safe.replace("|", "_").replace("*", "_").replace("<", "_")
        safe = safe.replace(">", "_").replace("\n", "_").replace("\r", "_")
        # Collapse multiple underscores
        while "__" in safe:
            safe = safe.replace("__", "_")
        return safe.strip("_")[:100] or "untitled"

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for entry in entries:
            filename = sanitize_filename(entry.title)
            zf.writestr(f"{filename}.md", entry.content)

    zip_buffer.seek(0)

    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=openwiki_export_{timestamp}.zip"
        },
    )