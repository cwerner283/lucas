"""Simple JSON-based cache for LLM responses."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import get_settings


class LLMCache:
    """Disk backed JSON cache."""

    def __init__(self, path: Path | None = None) -> None:
        settings = get_settings()
        self.path = path or settings.llm_cache_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _read(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _write(self, data: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

    def lookup(self, key: str) -> Any | None:
        """Return cached value for ``key`` or ``None``."""

        return self._read().get(key)

    def store(self, key: str, value: Any) -> None:
        """Store ``value`` under ``key``."""

        data = self._read()
        data[key] = value
        self._write(data)


def get_cache(path: Path | None = None) -> LLMCache:
    """Return a cache instance."""

    return LLMCache(path)


cache = LLMCache()
