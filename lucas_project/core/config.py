"""Application configuration using Pydantic settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration values for the application."""

    debug: bool = False
    database_url: str = "./lucas.db"
    llm_cache_path: Path = Path("./lucas_project/data/llm_cache.json")
    scheduler_timezone: str = "UTC"

    class Config:
        env_prefix = "LUCAS_"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""

    return Settings()
