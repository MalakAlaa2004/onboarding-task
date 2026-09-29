from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    PROJECT_NAME: str = "NovaGates Portfolio & AI Service"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/portfolio_db"
    MONGODB_DB_NAME: str = "portfolio_db"

    # Redis Cache & Broker
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_DEFAULT_TTL: int = 300  # 5 minutes

    # AI / LLM Integration (Ollama Cloud / OpenAI-compatible endpoint)
    OLLAMA_API_BASE: str = "https://api.ollama.com/v1"
    OLLAMA_API_KEY: str = ""
    OLLAMA_MODEL: str = "llama3.2"

    # Job Matching / External Search
    TAVILY_API_KEY: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
