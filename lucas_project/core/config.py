"""Application configuration using Pydantic settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration values for the application."""

    debug: bool = False
    database_url: str = "./lucas.db"
    llm_cache_path: Path = Path("./lucas_project/data/llm_cache.json")
    scheduler_timezone: str = "UTC"
    github_token: str | None = None
    whois_api_key: str | None = None
    estibot_api_key: str | None = None
    humbleworth_api_key: str | None = None

    model_config = SettingsConfigDict(env_prefix="LUCAS_")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""

    return Settings()
