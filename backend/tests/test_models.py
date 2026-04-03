# ============================================================
# Database Models Tests
# ============================================================

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.material import Material, MaterialStatus
from app.models.wiki_entry import WikiEntry
from app.models.concept import Concept, Tag


class TestMaterialModel:
    """Test Material model CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_material(self, db_session):
        """Test creating a basic material."""
        material = Material(
            title="Test Article",
            source_url="https://example.com/article",
            raw_markdown="# Test\n\nSome content.",
            status=MaterialStatus.PENDING,
        )
        db_session.add(material)
        await db_session.commit()

        # Query back
        result = await db_session.execute(select(Material))
        materials = result.scalars().all()

        assert len(materials) == 1
        assert materials[0].title == "Test Article"
        assert materials[0].status == MaterialStatus.PENDING
        assert materials[0].id is not None

    @pytest.mark.asyncio
    async def test_material_status_enum(self, db_session):
        """Test material status enum values."""
        material = Material(
            title="Status Test",
            raw_markdown="content",
            status=MaterialStatus.COMPILING,
        )
        db_session.add(material)
        await db_session.commit()

        result = await db_session.execute(select(Material))
        material = result.scalar_one()

        assert material.status == MaterialStatus.COMPILING

    @pytest.mark.asyncio
    async def test_material_with_file_key(self, db_session):
        """Test material with S3 file key."""
        material = Material(
            title="Uploaded File",
            file_key="uploads/test.pdf",
            raw_markdown="Extracted content",
            status=MaterialStatus.PENDING,
        )
        db_session.add(material)
        await db_session.commit()

        result = await db_session.execute(select(Material))
        material = result.scalar_one()

        assert material.file_key == "uploads/test.pdf"
        assert material.source_url is None


class TestConceptAndTag:
    """Test Concept and Tag models."""

    @pytest.mark.asyncio
    async def test_create_concept(self, db_session):
        """Test creating a concept."""
        concept = Concept(
            name="Large Language Model",
            description="A type of neural network for text generation.",
        )
        db_session.add(concept)
        await db_session.commit()

        result = await db_session.execute(select(Concept))
        concepts = result.scalars().all()

        assert len(concepts) == 1
        assert concepts[0].name == "Large Language Model"

    @pytest.mark.asyncio
    async def test_create_tag(self, db_session):
        """Test creating a tag."""
        tag = Tag(name="AI")
        db_session.add(tag)
        await db_session.commit()

        result = await db_session.execute(select(Tag))
        tags = result.scalars().all()

        assert len(tags) == 1
        assert tags[0].name == "AI"

    @pytest.mark.asyncio
    async def test_unique_concept_name(self, db_session):
        """Test that concept names must be unique."""
        concept1 = Concept(name="Machine Learning")
        concept2 = Concept(name="Machine Learning")

        db_session.add(concept1)
        await db_session.commit()

        db_session.add(concept2)
        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()


class TestWikiEntry:
    """Test WikiEntry model with relationships."""

    @pytest.mark.asyncio
    async def test_create_wiki_entry(self, db_session):
        """Test creating a basic wiki entry."""
        entry = WikiEntry(
            title="Introduction to AI",
            content="# AI Overview\n\nArtificial intelligence is...",
        )
        db_session.add(entry)
        await db_session.commit()

        result = await db_session.execute(select(WikiEntry))
        entries = result.scalars().all()

        assert len(entries) == 1
        assert entries[0].title == "Introduction to AI"

    @pytest.mark.asyncio
    async def test_wiki_entry_with_concepts_and_tags(self, db_session):
        """Test wiki entry with concepts and tags."""
        from sqlalchemy import insert
        from app.models.concept import wiki_entry_concepts, wiki_entry_tags

        # Create concepts and tags
        concept = Concept(name="Neural Network", description="A computational model.")
        tag = Tag(name="Deep Learning")
        db_session.add_all([concept, tag])
        await db_session.flush()

        # Create wiki entry
        entry = WikiEntry(
            title="Neural Networks Explained",
            content="# Neural Networks\n\nA neural network consists of...",
        )
        db_session.add(entry)
        await db_session.flush()

        # Add relationships using insert
        await db_session.execute(
            insert(wiki_entry_concepts).values(
                wiki_entry_id=entry.id, concept_id=concept.id
            )
        )
        await db_session.execute(
            insert(wiki_entry_tags).values(
                wiki_entry_id=entry.id, tag_id=tag.id
            )
        )
        await db_session.commit()

        # Query with relationships using selectinload
        result = await db_session.execute(
            select(WikiEntry)
            .where(WikiEntry.title == "Neural Networks Explained")
            .options(selectinload(WikiEntry.concepts), selectinload(WikiEntry.tags))
        )
        entry = result.scalar_one()

        assert len(entry.concepts) == 1
        assert entry.concepts[0].name == "Neural Network"
        assert len(entry.tags) == 1
        assert entry.tags[0].name == "Deep Learning"

    @pytest.mark.asyncio
    async def test_wiki_entry_with_materials(self, db_session):
        """Test wiki entry with source materials."""
        from sqlalchemy import insert
        from app.models.concept import wiki_entry_materials

        # Create materials
        material1 = Material(
            title="Source 1",
            raw_markdown="Content 1",
            status=MaterialStatus.COMPILED,
        )
        material2 = Material(
            title="Source 2",
            raw_markdown="Content 2",
            status=MaterialStatus.COMPILED,
        )
        db_session.add_all([material1, material2])
        await db_session.flush()

        # Create wiki entry
        entry = WikiEntry(
            title="Combined Knowledge",
            content="Synthesized content",
        )
        db_session.add(entry)
        await db_session.flush()

        # Add relationships using insert
        await db_session.execute(
            insert(wiki_entry_materials).values(
                wiki_entry_id=entry.id, material_id=material1.id
            )
        )
        await db_session.execute(
            insert(wiki_entry_materials).values(
                wiki_entry_id=entry.id, material_id=material2.id
            )
        )
        await db_session.commit()

        # Query with selectinload
        result = await db_session.execute(
            select(WikiEntry).options(selectinload(WikiEntry.materials))
        )
        entry = result.scalar_one()

        assert len(entry.materials) == 2
        assert entry.materials[0].title == "Source 1"