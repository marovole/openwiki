# ============================================================
# S3 Storage Tests
# ============================================================

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.engine.storage import S3Client


class TestS3Client:
    """Test S3 storage client."""

    def test_s3_client_init(self):
        """Test S3 client initialization."""
        with patch("app.engine.storage.boto3.client") as mock_boto3:
            client = S3Client()
            assert mock_boto3.called
            assert client.bucket == "openwiki-raw"

    @pytest.mark.asyncio
    async def test_upload_file(self):
        """Test file upload to S3."""
        with patch("app.engine.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_boto3.return_value = mock_s3

            client = S3Client()
            key = await client.upload_file(
                content=b"test content",
                filename="test.md",
                content_type="text/markdown",
            )

            assert key.endswith("test.md")
            assert "/" in key  # Should have date prefix
            mock_s3.put_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_file(self):
        """Test file download from S3."""
        with patch("app.engine.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_response = {"Body": MagicMock()}
            mock_response["Body"].read.return_value = b"test content"
            mock_s3.get_object.return_value = mock_response
            mock_boto3.return_value = mock_s3

            client = S3Client()
            content = await client.get_file("2024/01/01/test.md")

            assert content == b"test content"
            mock_s3.get_object.assert_called_once_with(
                Bucket="openwiki-raw", Key="2024/01/01/test.md"
            )

    @pytest.mark.asyncio
    async def test_delete_file(self):
        """Test file deletion from S3."""
        with patch("app.engine.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_boto3.return_value = mock_s3

            client = S3Client()
            await client.delete_file("2024/01/01/test.md")

            mock_s3.delete_object.assert_called_once_with(
                Bucket="openwiki-raw", Key="2024/01/01/test.md"
            )

    @pytest.mark.asyncio
    async def test_file_exists(self):
        """Test file existence check."""
        from botocore.exceptions import ClientError

        with patch("app.engine.storage.boto3.client") as mock_boto3:
            mock_s3 = MagicMock()
            mock_boto3.return_value = mock_s3

            client = S3Client()

            # Test existing file
            exists = await client.file_exists("2024/01/01/test.md")
            assert exists is True
            mock_s3.head_object.assert_called_once()

            # Test non-existing file (ClientError)
            mock_s3.head_object.side_effect = ClientError(
                {"Error": {"Code": "404", "Message": "Not Found"}},
                "head_object",
            )
            exists = await client.file_exists("2024/01/01/nonexistent.md")
            assert exists is False