# ============================================================
# Compile Orchestrator Tests
# ============================================================

import pytest
from sqlalchemy import select
from unittest.mock import patch, AsyncMock, MagicMock

from app.models.material import Material, MaterialStatus
from app.models.wiki_entry import WikiEntry
from app.models.concept import Concept, Tag
from app.engine.orchestrator import run_compile
from app.engine.compile import CompileResult


class TestRunCompile:
    """Test compile orchestrator."""

    @pytest.mark.asyncio
    async def test_run_compile_creates_wiki_entry(self, db_session):
        """Full compile: material -> wiki entry + concepts + tags in DB."""
        # Create test material
        material = Material(
            title="Test: Neural Networks",
            raw_markdown="# Neural Networks\nNeural networks are computational models inspired by the brain. They learn patterns from data.",
            status=MaterialStatus.PENDING,
        )
        db_session.add(material)
        await db_session.commit()

        # Mock compile_material to return structured data
        mock_result = CompileResult(
            summary="Neural networks are computational models that learn from data.",
            concepts=[
                {"name": "Neural Network", "description": "A computational model inspired by biological neurons"},
                {"name": "Deep Learning", "description": "A subset of machine learning using neural networks"},
            ],
            tags=["AI", "Machine Learning", "Neural Networks"],
            wiki_entry="# Neural Networks\n\nNeural networks are computational models inspired by the brain. They consist of layers of interconnected nodes.\n\n## Key Concepts\n\n- **Architecture**: Input, hidden, and output layers\n- **Training**: Learning through backpropagation\n- **Applications**: Image recognition, NLP, and more",
            associations=[
                {"concept": "Neural Network", "related_to": "Deep Learning", "relation": "Foundation of deep learning"}
            ],
        )

        with patch("app.engine.orchestrator.compile_material", new_callable=AsyncMock) as mock_compile:
            mock_compile.return_value = mock_result

            await run_compile(material.id, db_session)

        # Refresh material
        await db_session.refresh(material)

        # Verify material status updated
        assert material.status == MaterialStatus.COMPILED
        assert material.summary is not None
        assert "Neural networks" in material.summary

        # Verify wiki entry created
        result = await db_session.execute(select(WikiEntry))
        entries = result.scalars().all()
        assert len(entries) >= 1

        entry = entries[0]
        assert entry.title == "Test: Neural Networks"
        assert "Neural networks" in entry.content

        # Verify concepts created
        result = await db_session.execute(select(Concept))
        concepts = result.scalars().all()
        assert len(concepts) >= 1
        concept_names = [c.name for c in concepts]
        assert "Neural Network" in concept_names

        # Verify tags created
        result = await db_session.execute(select(Tag))
        tags = result.scalars().all()
        assert len(tags) >= 1
        tag_names = [t.name for t in tags]
        assert "AI" in tag_names

    @pytest.mark.asyncio
    async def test_run_compile_reuses_existing_concepts(self, db_session):
        """Compile should reuse existing concepts instead of creating duplicates."""
        # Create existing concept
        existing_concept = Concept(
            name="Neural Network",
            description="Already existing concept",
        )
        db_session.add(existing_concept)
        await db_session.commit()

        # Create material
        material = Material(
            title="Deep Learning",
            raw_markdown="# Deep Learning\nDeep learning uses neural networks.",
            status=MaterialStatus.PENDING,
        )
        db_session.add(material)
        await db_session.commit()

        # Mock compile result with same concept name
        mock_result = CompileResult(
            summary="Deep learning overview.",
            concepts=[
                {"name": "Neural Network", "description": "A new description"},
            ],
            tags=["AI"],
            wiki_entry="# Deep Learning\nContent here.",
            associations=[],
        )

        with patch("app.engine.orchestrator.compile_material", new_callable=AsyncMock) as mock_compile:
            mock_compile.return_value = mock_result

            await run_compile(material.id, db_session)

        # Verify concept count (should be 1, not 2)
        result = await db_session.execute(select(Concept))
        concepts = result.scalars().all()
        assert len(concepts) == 1
        assert concepts[0].name == "Neural Network"
        # Original description should be preserved
        assert concepts[0].description == "Already existing concept"

    @pytest.mark.asyncio
    async def test_run_compile_handles_failure(self, db_session):
        """Compile should handle LLM failures gracefully."""
        material = Material(
            title="Test Failure",
            raw_markdown="Content",
            status=MaterialStatus.PENDING,
        )
        db_session.add(material)
        await db_session.commit()

        # Mock compile_material to raise exception
        with patch("app.engine.orchestrator.compile_material", new_callable=AsyncMock) as mock_compile:
            mock_compile.side_effect = Exception("LLM API failed")

            with pytest.raises(Exception, match="LLM API failed"):
                await run_compile(material.id, db_session)

        # Verify material status is set to FAILED
        await db_session.refresh(material)
        assert material.status == MaterialStatus.FAILED