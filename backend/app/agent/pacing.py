"""Artificial per-step delay so the stubbed pipeline streams like real work.

Async (not time.sleep) so the SSE writer flushes each `active` event before the
step's `done` event. Tests set DELAY = 0 to run instantly.
"""

import asyncio

DELAY = 0.6


async def step_pause() -> None:
    if DELAY:
        await asyncio.sleep(DELAY)
