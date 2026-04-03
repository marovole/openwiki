# ============================================================
# S3 Storage Client - MinIO/S3 Integration
# ============================================================
# Handles file uploads to S3-compatible storage (MinIO in dev)
# ============================================================

import boto3
from botocore.exceptions import ClientError
from typing import Optional
import uuid
from datetime import datetime

from app.config import settings


class S3Client:
    """S3-compatible storage client for file uploads."""

    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )
        self.bucket = settings.s3_bucket

    async def upload_file(
        self,
        content: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload a file to S3 and return the key.

        Args:
            content: File content as bytes
            filename: Original filename
            content_type: MIME type

        Returns:
            S3 key for the uploaded file
        """
        # Generate unique key with date prefix
        date_prefix = datetime.utcnow().strftime("%Y/%m/%d")
        unique_id = str(uuid.uuid4())[:8]
        key = f"{date_prefix}/{unique_id}-{filename}"

        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=content,
                ContentType=content_type,
            )
            return key
        except ClientError as e:
            raise RuntimeError(f"Failed to upload file to S3: {e}")

    async def get_file(self, key: str) -> bytes:
        """
        Download a file from S3.

        Args:
            key: S3 key

        Returns:
            File content as bytes
        """
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            raise RuntimeError(f"Failed to download file from S3: {e}")

    async def delete_file(self, key: str) -> None:
        """
        Delete a file from S3.

        Args:
            key: S3 key
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        except ClientError as e:
            raise RuntimeError(f"Failed to delete file from S3: {e}")

    async def file_exists(self, key: str) -> bool:
        """
        Check if a file exists in S3.

        Args:
            key: S3 key

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False


# Global client instance
s3_client: Optional[S3Client] = None


def get_s3_client() -> S3Client:
    """Get or create S3 client instance."""
    global s3_client
    if s3_client is None:
        s3_client = S3Client()
    return s3_client