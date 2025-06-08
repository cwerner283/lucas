"""Shared utility helpers."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger with the given name."""

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.propagate = False
    return logger


def rate_limiter(max_calls: int, period: float) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Rate limit calls to an async function."""

    semaphore = asyncio.Semaphore(max_calls)
    interval = period / max_calls
    last_called = 0.0
    lock = asyncio.Lock()

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            nonlocal last_called
            async with semaphore:
                async with lock:
                    now = asyncio.get_event_loop().time()
                    wait_time = interval - (now - last_called)
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)
                    last_called = asyncio.get_event_loop().time()
            return await func(*args, **kwargs)

        return wrapper

    return decorator


class TokenBucket:
    """Asynchronous token bucket rate limiter."""

    def __init__(self, rate: int, per: float) -> None:
        self.capacity = rate
        self.tokens = float(rate)
        self.rate_per_sec = rate / per
        self.updated_at = time.monotonic()
        self.lock = asyncio.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.updated_at
        self.updated_at = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate_per_sec)

    async def acquire(self, tokens: int = 1) -> None:
        while True:
            async with self.lock:
                self._refill()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                deficit = tokens - self.tokens
                wait_time = deficit / self.rate_per_sec
            await asyncio.sleep(wait_time)


def token_bucket(rate: int, per: float) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Decorate async functions with a token bucket limiter."""

    bucket = TokenBucket(rate, per)

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            await bucket.acquire()
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def retry(retries: int = 3, backoff: float = 1.0) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Retry an async function on failure using exponential backoff."""

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception:  # pragma: no cover - thin wrapper
                    attempt += 1
                    if attempt > retries:
                        raise
                    await asyncio.sleep(backoff * attempt)

        return wrapper

    return decorator


def circuit_breaker(
    max_failures: int, reset_timeout: float
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Simple circuit breaker for async functions."""

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        failures = 0
        opened_at: float | None = None

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            nonlocal failures, opened_at
            loop = asyncio.get_event_loop()
            now = loop.time()

            if opened_at and now - opened_at < reset_timeout:
                raise RuntimeError("Circuit breaker open")
            if opened_at and now - opened_at >= reset_timeout:
                failures = 0
                opened_at = None

            try:
                result = await func(*args, **kwargs)
                failures = 0
                return result
            except Exception:
                failures += 1
                if failures >= max_failures:
                    opened_at = loop.time()
                raise

        return wrapper

    return decorator
