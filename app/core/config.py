from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_name: str = "genai-production-platform"
    app_version: str = "1.0.0"
    app_api_key: str = Field(default="change-me", min_length=1)
    log_level: str = "INFO"

    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"

    database_url: str = "postgresql+asyncpg://app:app@postgres:5432/genai"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "knowledge_chunks"
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    max_upload_mb: int = Field(default=10, ge=1, le=100)
    top_k: int = Field(default=6, ge=1, le=20)
    min_evidence_score: float = Field(default=0.25, ge=0, le=1)
    request_timeout_seconds: float = Field(default=45, gt=1, le=180)
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
