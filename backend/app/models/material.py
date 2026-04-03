# ============================================================
# Material Model - Raw Content Before Compilation
# ============================================================
# Ingested URLs/files stored as markdown with metadata
# ============================================================

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
import enum

from app.db import Base


class MaterialStatus(str, enum.Enum):
    """Material processing status."""
    PENDING = "pending"
    COMPILING = "compiling"
    COMPILED = "compiled"
    FAILED = "failed"


class Material(Base):
    """Raw material ingested from URL or file upload."""

    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    title: Mapped[str] = mapped_column(String(500))
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    file_key: Mapped[str | None] = mapped_column(String(500), nullable=True)  # S3 key
    raw_markdown: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[MaterialStatus] = mapped_column(
        SQLEnum(MaterialStatus),
        default=MaterialStatus.PENDING,
    )

    # Embedding for semantic search (1024 dimensions for Claude embeddings)
    embedding = mapped_column(Vector(1024), nullable=True)

    # Relationships
    wiki_entries: Mapped[list["WikiEntry"]] = relationship(
        "WikiEntry",
        secondary="wiki_entry_materials",
        back_populates="materials",
        uselist=True,
    )
    outgoing_associations: Mapped[list["Association"]] = relationship(
        "Association",
        foreign_keys="Association.source_id",
        back_populates="source",
        uselist=True,
    )
    incoming_associations: Mapped[list["Association"]] = relationship(
        "Association",
        foreign_keys="Association.target_id",
        back_populates="target",
        uselist=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Material {self.id[:8]} {self.title[:50]}>"