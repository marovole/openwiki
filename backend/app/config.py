# ============================================================
# Configuration Management
# ============================================================
# Environment-based settings via pydantic-settings
# ============================================================

from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://openwiki:openwiki_dev@localhost:5432/openwiki"

    # S3 Storage
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "openwiki-raw"

    # LLM
    anthropic_api_key: str = ""

    # App
    app_env: str = "development"
    debug: bool = True

    model_config = {"env_file": "../.env", "extra": "ignore"}

    @field_validator("anthropic_api_key")
    @classmethod
    def validate_api_key(cls, v: str, info) -> str:
        """在非测试/开发环境下强制要求 API Key。"""
        # 允许测试环境和开发环境跳过校验
        app_env = info.data.get("app_env", "development")
        if app_env in ("test", "testing"):
            return v
        if app_env == "development" and not v:
            # 开发环境允许为空，但打印警告
            print("⚠️  WARNING: ANTHROPIC_API_KEY not set, LLM features disabled")
            return v
        if not v:
            raise ValueError("ANTHROPIC_API_KEY is required in production")
        return v


settings = Settings()