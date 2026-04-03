# ============================================================
# Ingestion Engine Tests
# ============================================================

import pytest
from unittest.mock import patch, AsyncMock
from app.engine.ingestion import url_to_markdown


class TestUrlToMarkdown:
    """Test URL to Markdown conversion."""

    @pytest.mark.asyncio
    async def test_url_to_markdown_invalid_url(self):
        """Invalid URL raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL"):
            await url_to_markdown("not-a-url")

    @pytest.mark.asyncio
    async def test_url_to_markdown_success(self):
        """Successful URL fetch and conversion."""
        mock_html = """
        <html>
            <head><title>Test Article</title></head>
            <body>
                <article>
                    <h1>Hello World</h1>
                    <p>This is a test article with some content.</p>
                </article>
            </body>
        </html>
        """

        with patch("httpx.AsyncClient") as mock_client:
            # Mock the async context manager
            mock_instance = AsyncMock()
            mock_response = AsyncMock()
            mock_response.text = mock_html
            mock_response.raise_for_status = lambda: None
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await url_to_markdown("https://example.com/test")

            assert result["title"] == "Test Article"
            assert "Hello World" in result["markdown"]
            assert "test article" in result["markdown"]
            assert result["source_url"] == "https://example.com/test"

    @pytest.mark.asyncio
    async def test_url_to_markdown_extracts_content(self):
        """Content extraction focuses on main content."""
        mock_html = """
        <html>
            <head><title>Example Page</title></head>
            <body>
                <nav>Navigation</nav>
                <main>
                    <h1>Main Content</h1>
                    <p>This is the important content.</p>
                </main>
                <footer>Footer</footer>
            </body>
        </html>
        """

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_response = AsyncMock()
            mock_response.text = mock_html
            mock_response.raise_for_status = lambda: None
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            result = await url_to_markdown("https://example.com")

            # Should extract readable content
            assert "Example Page" in result["title"]
            # Should not contain HTML tags after markdown conversion
            assert "<html>" not in result["markdown"]
            assert "<body>" not in result["markdown"]

    @pytest.mark.asyncio
    async def test_url_to_markdown_http_error(self):
        """HTTP errors are propagated."""
        import httpx

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            # Make get() raise an HTTP error
            mock_instance.get = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "404 Not Found",
                    request=httpx.Request("GET", "https://example.com/not-found"),
                    response=httpx.Response(404, text="Not Found"),
                )
            )
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client.return_value = mock_instance

            with pytest.raises(httpx.HTTPStatusError):
                await url_to_markdown("https://example.com/not-found")