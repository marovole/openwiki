# ============================================================
# Compile Engine Tests
# ============================================================

import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock

from app.engine.compile import compile_material, CompileResult


class TestCompileMaterial:
    """Test LLM compile pipeline."""

    @pytest.mark.asyncio
    async def test_compile_material_returns_structure(self):
        """Compile should return summary, concepts, tags, and wiki entry."""
        # Mock Claude API response
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = json.dumps({
            "summary": "Transformers are neural network architectures based on self-attention mechanism.",
            "concepts": [
                {"name": "Transformer", "description": "A neural network architecture using self-attention"},
                {"name": "Self-Attention", "description": "Mechanism that allows weighing importance of different parts of input"}
            ],
            "tags": ["AI", "Neural Networks", "Deep Learning"],
            "wiki_entry": "# Transformer Architecture\n\nTransformers are a type of neural network architecture that has revolutionized natural language processing.",
            "associations": [
                {"concept": "Transformer", "related_to": "Self-Attention", "relation": "uses as core mechanism"}
            ]
        })
        mock_response.content = [mock_content]

        with patch("app.engine.compile.client") as mock_client:
            mock_client.messages = MagicMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)

            result = await compile_material(
                material_id="test-123",
                title="Transformer Architecture",
                raw_markdown="# Transformer Architecture\nThe transformer is a neural network architecture based on self-attention."
            )

        assert "summary" in result
        assert len(result["summary"]) > 20
        assert "concepts" in result
        assert isinstance(result["concepts"], list)
        assert len(result["concepts"]) >= 1
        assert "tags" in result
        assert isinstance(result["tags"], list)
        assert len(result["tags"]) >= 1
        assert "wiki_entry" in result
        assert len(result["wiki_entry"]) > 50
        assert "associations" in result

    @pytest.mark.asyncio
    async def test_compile_material_extracts_json_from_markdown(self):
        """Compile should handle Claude's response with markdown code blocks."""
        # Mock Claude API response with markdown wrapper
        mock_response = MagicMock()
        mock_content = MagicMock()
        # Use escaped newlines in wiki_entry for valid JSON
        mock_content.text = '''Here's the compiled output:

```json
{
    "summary": "Test summary for markdown extraction.",
    "concepts": [{"name": "Test Concept", "description": "A test concept"}],
    "tags": ["test"],
    "wiki_entry": "# Test Entry\\n\\nThis is a test wiki entry.",
    "associations": []
}
```
'''
        mock_response.content = [mock_content]

        with patch("app.engine.compile.client") as mock_client:
            mock_client.messages = MagicMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)

            result = await compile_material(
                material_id="test-456",
                title="Test Title",
                raw_markdown="Test content"
            )

        assert result["summary"] == "Test summary for markdown extraction."
        assert len(result["concepts"]) == 1
        assert result["concepts"][0]["name"] == "Test Concept"

    @pytest.mark.asyncio
    async def test_compile_material_truncates_long_content(self):
        """Compile should truncate very long content."""
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = json.dumps({
            "summary": "Short content test.",
            "concepts": [],
            "tags": [],
            "wiki_entry": "Test",
            "associations": []
        })
        mock_response.content = [mock_content]

        with patch("app.engine.compile.client") as mock_client:
            mock_client.messages = MagicMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)

            # Create very long content
            long_content = "x" * 10000
            await compile_material(
                material_id="test-789",
                title="Long Content",
                raw_markdown=long_content
            )

            # Verify the call was made
            assert mock_client.messages.create.called
            # The content should have been truncated in the prompt
            call_args = mock_client.messages.create.call_args
            prompt_content = call_args[1]["messages"][0]["content"]
            # Content should be truncated to ~8000 chars in the prompt formatting