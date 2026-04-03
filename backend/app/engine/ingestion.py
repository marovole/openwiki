# ============================================================
# Ingestion Engine - URL Fetch & Markdown Conversion
# ============================================================
# Fetches URLs, extracts readable content, converts to markdown
# ============================================================

import ssl
import certifi
import httpx
from readability import Document
from markdownify import markdownify
from urllib.parse import urlparse
from typing import TypedDict


class IngestResult(TypedDict):
    """Result of URL ingestion."""
    title: str
    markdown: str
    source_url: str


async def url_to_markdown(url: str) -> IngestResult:
    """
    Fetch URL, extract readable content, convert to markdown.

    Args:
        url: The URL to fetch and process

    Returns:
        Dictionary with title, markdown content, and source URL

    Raises:
        ValueError: If URL is invalid
        httpx.HTTPStatusError: If HTTP request fails
    """
    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")

    # Create SSL context with certifi certificates
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    # Fetch URL
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=30,
        verify=ssl_context,
    ) as client:
        resp = await client.get(
            url,
            headers={
                "User-Agent": "OpenWiki/0.1 (https://github.com/openwiki)",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        resp.raise_for_status()

    # Extract readable content
    doc = Document(resp.text)
    title = doc.title() or "Untitled"
    html_content = doc.summary()

    # Convert to markdown
    markdown = markdownify(
        html_content,
        heading_style="ATX",  # Use # style headers
        strip=["img", "script", "style", "nav", "footer"],  # Strip non-content elements
        escape_asterisks=False,
        escape_underscores=False,
    )

    return {
        "title": title.strip(),
        "markdown": markdown.strip(),
        "source_url": url,
    }