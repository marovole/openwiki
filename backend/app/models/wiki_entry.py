# ============================================================
# Wiki Entry Model - Compiled Knowledge Article
# ============================================================
# LLM-compiled content from one or more materials
# ============================================================

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.db import Base
from app.models.concept import (
    wiki_entry_concepts,
    wiki_entry_tags,
    wiki_entry_materials,
)


class WikiEntry(Base):
    """Compiled wiki article from materials."""

    __tablename__ = "wiki_entries"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    title: Mapped[str] = mapped_column(String(500), index=True)
    content: Mapped[str] = mapped_column(Text)

    # Relationships
    concepts: Mapped[list["Concept"]] = relationship(
        "Concept",
        secondary=wiki_entry_concepts,
        back_populates="wiki_entries",
        uselist=True,
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=wiki_entry_tags,
        back_populates="wiki_entries",
        uselist=True,
    )
    materials: Mapped[list["Material"]] = relationship(
        "Material",
        secondary=wiki_entry_materials,
        back_populates="wiki_entries",
        uselist=True,
    )

    # Embedding for semantic search
    embedding = mapped_column(Vector(1024), nullable=True)

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
        return f"<WikiEntry {self.id[:8]} {self.title[:50]}>"