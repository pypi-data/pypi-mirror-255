from typing import Any

from agentic.core.context import update_progress_context


async def update_progress(value: Any):
    func = update_progress_context.get()
    if not func:
        raise Exception("No update_progress_context set")
    await func(value)
