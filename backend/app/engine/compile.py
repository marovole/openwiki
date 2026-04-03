# ============================================================
# Compile Engine - LLM Knowledge Compiler
# ============================================================
# Transforms raw materials into structured wiki entries
# using Claude API for intelligent extraction and synthesis
# ============================================================

import json
import anthropic
from typing import TypedDict, List
from app.config import settings


# ============================================================
# Type Definitions
# ============================================================

class Concept(TypedDict):
    """Extracted concept."""
    name: str
    description: str


class Association(TypedDict):
    """Relationship between concepts."""
    concept: str
    related_to: str
    relation: str


class CompileResult(TypedDict):
    """Result of compile pipeline."""
    summary: str
    concepts: List[Concept]
    tags: List[str]
    wiki_entry: str
    associations: List[Association]


# ============================================================
# Claude Client
# ============================================================

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


# ============================================================
# Compile Prompt
# ============================================================

COMPILE_PROMPT = """You are OpenWiki's knowledge compiler. Your job is to transform raw materials into structured, interconnected knowledge.

Given a raw article, produce a structured JSON output that captures:
1. A concise summary (2-3 sentences)
2. Key concepts with definitions
3. Relevant tags for categorization
4. A comprehensive wiki entry
5. Relationships between concepts

<raw_material>
Title: {title}
Content:
{content}
</raw_material>

Return ONLY valid JSON with this exact structure (no markdown, no code blocks, just pure JSON):
{{
  "summary": "2-3 sentence summary capturing the core ideas and significance",
  "concepts": [
    {{"name": "Concept Name", "description": "One sentence definition explaining what it is and why it matters"}}
  ],
  "tags": ["tag1", "tag2", "tag3"],
  "wiki_entry": "A comprehensive wiki article in markdown format. Include:\\n- Clear explanation of key concepts\\n- How concepts relate to each other\\n- Practical applications or implications\\n- Key takeaways\\n\\nWrite 200-500 words in a clear, educational style.",
  "associations": [
    {{"concept": "Concept A", "related_to": "Concept B", "relation": "How they are related"}}
  ]
}}

Guidelines:
- Extract 3-7 key concepts
- Use 3-5 relevant tags
- Make associations meaningful (not just "related to")
- Write wiki entry in clear, accessible language
- Focus on practical understanding

Remember: Output ONLY the JSON object, no other text."""


# ============================================================
# Main Compile Function
# ============================================================

async def compile_material(
    material_id: str,
    title: str,
    raw_markdown: str,
) -> CompileResult:
    """
    Run LLM compile pipeline on a single raw material.

    Args:
        material_id: UUID of the material (for logging/tracking)
        title: Title of the material
        raw_markdown: Raw markdown content to compile

    Returns:
        CompileResult with summary, concepts, tags, wiki_entry, associations

    Raises:
        ValueError: If JSON parsing fails
        anthropic.APIError: If Claude API fails
    """
    # Truncate content to avoid token limits (Claude has large context but be safe)
    max_content_length = 8000
    truncated_content = raw_markdown[:max_content_length]
    if len(raw_markdown) > max_content_length:
        truncated_content += "\n\n[Content truncated...]"

    # Call Claude API
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": COMPILE_PROMPT.format(
                title=title,
                content=truncated_content,
            ),
        }],
    )

    # Extract text from response
    text = response.content[0].text

    # Parse JSON from response (handle potential markdown code blocks)
    # Claude sometimes wraps JSON in ```json ... ```
    text = text.strip()
    if text.startswith("```"):
        # Remove code block markers
        lines = text.split("\n")
        # Remove first line (```json or ```)
        if lines[0].startswith("```"):
            lines = lines[1:]
        # Remove last line (```)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    # Find JSON object boundaries
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON object found in response: {text[:200]}")

    json_str = text[start:end]

    try:
        result = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}\nResponse: {json_str[:500]}")

    # Validate required fields
    required_fields = ["summary", "concepts", "tags", "wiki_entry", "associations"]
    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing required field: {field}")

    return CompileResult(
        summary=result["summary"],
        concepts=result["concepts"],
        tags=result["tags"],
        wiki_entry=result["wiki_entry"],
        associations=result["associations"],
    )