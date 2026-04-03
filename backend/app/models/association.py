# ============================================================
# Cross-Material Association Model
# ============================================================
# Discovered relationships between materials
# ============================================================

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Association(Base):
    """Cross-material association discovered by LLM."""

    __tablename__ = "associations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # Source and target materials
    source_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("materials.id"),
        index=True,
    )
    target_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("materials.id"),
        index=True,
    )

    # Association metadata
    relationship_type: Mapped[str] = mapped_column(String(100))  # e.g., "contradicts", "supports", "extends"
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    source: Mapped["Material"] = relationship(
        "Material",
        foreign_keys=[source_id],
        back_populates="outgoing_associations",
    )
    target: Mapped["Material"] = relationship(
        "Material",
        foreign_keys=[target_id],
        back_populates="incoming_associations",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Association {self.source_id[:8]} -> {self.target_id[:8]}>"