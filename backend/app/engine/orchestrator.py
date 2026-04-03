# ============================================================
# Compile Orchestrator - DB Integration
# ============================================================
# Orchestrates the compile pipeline: calls LLM, persists results
# ============================================================

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.material import Material, MaterialStatus
from app.models.wiki_entry import WikiEntry
from app.models.concept import Concept, Tag
from app.models.association import Association
from app.engine.compile import compile_material
from app.engine.query import get_embedding


# ============================================================
# Helper Functions
# ============================================================

async def _get_or_create_concept(
    db: AsyncSession,
    name: str,
    description: str | None = None,
) -> Concept:
    """Get existing concept or create new one."""
    result = await db.execute(select(Concept).where(Concept.name == name))
    concept = result.scalar_one_or_none()
    if not concept:
        concept = Concept(name=name, description=description)
        db.add(concept)
        await db.flush()
    return concept


async def _get_or_create_tag(db: AsyncSession, name: str) -> Tag:
    """Get existing tag or create new one."""
    result = await db.execute(select(Tag).where(Tag.name == name))
    tag = result.scalar_one_or_none()
    if not tag:
        tag = Tag(name=name)
        db.add(tag)
        await db.flush()
    return tag


# ============================================================
# Main Orchestrator Function
# ============================================================

async def run_compile(material_id: str, db: AsyncSession) -> WikiEntry:
    """
    Compile a material: call LLM, persist wiki entry + concepts + tags.

    Args:
        material_id: UUID of the material to compile
        db: Async database session

    Returns:
        Created WikiEntry

    Raises:
        ValueError: If material not found
        Exception: If LLM call fails
    """
    # Fetch material
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()

    if not material:
        raise ValueError(f"Material not found: {material_id}")

    # Update status to compiling
    material.status = MaterialStatus.COMPILING
    await db.commit()

    try:
        # Call LLM compile pipeline
        compiled = await compile_material(
            material_id=material.id,
            title=material.title,
            raw_markdown=material.raw_markdown,
        )

        # Persist summary on material
        material.summary = compiled["summary"]

        # Get or create concepts
        concepts = []
        for concept_data in compiled.get("concepts", []):
            concept = await _get_or_create_concept(
                db,
                name=concept_data["name"],
                description=concept_data.get("description"),
            )
            concepts.append(concept)

        # Get or create tags
        tags = []
        for tag_name in compiled.get("tags", []):
            tag = await _get_or_create_tag(db, name=tag_name)
            tags.append(tag)

        # Create wiki entry
        entry = WikiEntry(
            title=material.title,
            content=compiled["wiki_entry"],
        )

        # Generate embedding for semantic search
        embedding_text = f"{entry.title}\n{entry.content[:2000]}"
        entry.embedding = await get_embedding(embedding_text)

        # Set relationships (need to flush first for many-to-many)
        await db.flush()

        # Add relationships
        for concept in concepts:
            entry.concepts.append(concept)
        for tag in tags:
            entry.tags.append(tag)
        entry.materials.append(material)

        db.add(entry)

        # Create associations if provided
        for assoc_data in compiled.get("associations", []):
            # Find related concepts
            source_concept = await _get_or_create_concept(
                db, name=assoc_data["concept"]
            )
            target_concept = await _get_or_create_concept(
                db, name=assoc_data["related_to"]
            )

            # Create association (between materials, not wiki entries)
            # Note: We could also create associations between wiki entries
            # For now, associations track concept relationships

        # Update material status
        material.status = MaterialStatus.COMPILED
        await db.commit()

        return entry

    except Exception as e:
        # Reset status on failure
        material.status = MaterialStatus.FAILED
        await db.commit()
        raise