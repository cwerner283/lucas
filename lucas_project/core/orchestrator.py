"""Task orchestration and websocket broadcasting."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Set

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import WebSocket

from .utils import get_logger

scheduler = AsyncIOScheduler()
try:
    scheduler.start()
except RuntimeError:
    # scheduler may be imported without an event loop (e.g. during migrations)
    pass


class WebSocketBroadcaster:
    """Manage websocket connections and broadcast messages."""

    def __init__(self) -> None:
        self.connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a websocket connection."""

        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a websocket connection."""

        self.connections.discard(websocket)

    async def broadcast(self, message: str) -> None:
        """Send ``message`` to all active connections."""

        for ws in list(self.connections):
            try:
                await ws.send_text(message)
            except Exception:
                self.disconnect(ws)


broadcaster = WebSocketBroadcaster()


def register_job(*, trigger: str = "interval", **trigger_args: Any) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Register an async function as a scheduled job."""

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        logger = get_logger(func.__module__)

        async def wrapped(*args: Any, **kwargs: Any) -> None:
            try:
                await func(*args, **kwargs)
            except Exception:
                logger.exception("Scheduled job %s failed", func.__name__)

        scheduler.add_job(wrapped, trigger, **trigger_args)
        return wrapped

    return decorator


async def shutdown() -> None:
    """Gracefully stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
