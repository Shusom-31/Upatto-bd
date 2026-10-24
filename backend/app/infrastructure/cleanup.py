import asyncio
from contextlib import suppress

from app.infrastructure.dataset_store import store
from app.core.config import settings


async def cleanup_loop() -> None:
    while True:
        store.cleanup()
        await asyncio.sleep(settings.cleanup_interval_seconds)


async def stop_cleanup(task: asyncio.Task | None) -> None:
    if task:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
