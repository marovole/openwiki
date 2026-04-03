# ============================================================
# Concept & Tag Models - Knowledge Organization
# ============================================================
# Concepts: Named entities extracted from materials
# Tags: Simple categorization labels
# ============================================================

import uuid
from sqlalchemy import String, Text, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


# ============================================================
# Junction Tables (Many-to-Many Relationships)
# ============================================================

wiki_entry_concepts = Table(
    "wiki_entry_concepts",
    Base.metadata,
    Column("wiki_entry_id", String(36), ForeignKey("wiki_entries.id"), primary_key=True),
    Column("concept_id", String(36), ForeignKey("concepts.id"), primary_key=True),
)

wiki_entry_tags = Table(
    "wiki_entry_tags",
    Base.metadata,
    Column("wiki_entry_id", String(36), ForeignKey("wiki_entries.id"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("tags.id"), primary_key=True),
)

wiki_entry_materials = Table(
    "wiki_entry_materials",
    Base.metadata,
    Column("wiki_entry_id", String(36), ForeignKey("wiki_entries.id"), primary_key=True),
    Column("material_id", String(36), ForeignKey("materials.id"), primary_key=True),
)


# ============================================================
# Models
# ============================================================

class Concept(Base):
    """Named concept extracted from materials."""

    __tablename__ = "concepts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    wiki_entries: Mapped[list["WikiEntry"]] = relationship(
        "WikiEntry",
        secondary=wiki_entry_concepts,
        back_populates="concepts",
        uselist=True,
    )

    def __repr__(self) -> str:
        return f"<Concept {self.name}>"


class Tag(Base):
    """Simple categorization tag."""

    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # Relationships
    wiki_entries: Mapped[list["WikiEntry"]] = relationship(
        "WikiEntry",
        secondary=wiki_entry_tags,
        back_populates="tags",
        uselist=True,
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"