from typing import Callable

from dataclasses import dataclass

from contextvars import ContextVar

from .clients.coordinator_client import CoordinatorClient


schedule_context: ContextVar = ContextVar("schedule_context", default=None)
caller_type_context: ContextVar = ContextVar("caller_type_context", default=None)
update_progress_context: ContextVar = ContextVar(
    "update_progress_context", default=None
)
