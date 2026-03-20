import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8889

    # Ollama settings
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "deepseek-coder:latest"

    # ChromaDB settings
    chroma_persist_dir: str = "./data/chroma"
    collection_name: str = "jarvis_memory"

    # SQLite settings
    database_path: str = "./data/jarvis.db"

    # Caching settings
    cache_ttl_seconds: int = 60

    # Memory settings
    memory_limit: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()