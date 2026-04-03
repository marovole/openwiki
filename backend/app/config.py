# ============================================================
# Configuration Management
# ============================================================
# Environment-based settings via pydantic-settings
# ============================================================

from pydantic_settings import BaseSettings


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


settings = Settings()